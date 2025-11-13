import json
import re
import subprocess
import sys
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol


@dataclass
class Diagnostic:
    filename: Path
    code: str
    message: str
    row: int
    column: int


@dataclass
class FileEditSession:
    path: Path
    lines: list[str]
    changes: list[str] = field(default_factory=list)

    @classmethod
    def load(cls, path: Path) -> FileEditSession:
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines(keepends=True)
        return cls(path=path, lines=lines)

    def save(self) -> None:
        self.path.write_text("".join(self.lines), encoding="utf-8")


class RuleFixer(Protocol):
    code: str

    def apply(self, session: FileEditSession, diagnostic: Diagnostic) -> bool:
        ...


class BareExceptFixer:
    code = "E722"
    _pattern = re.compile(r"^(?P<indent>\s*)except\s*:(?P<trail>\s*(#.*)?)$")

    def apply(self, session: FileEditSession, diagnostic: Diagnostic) -> bool:
        index = diagnostic.row - 1
        if not (0 <= index < len(session.lines)):
            log_warn(f"Row out of range for {session.path}: {diagnostic.row}")
            return False

        original = session.lines[index]
        match = self._pattern.match(original.rstrip("\n"))
        if not match:
            return False

        indent = match.group("indent")
        trail = match.group("trail") or ""
        replacement = f"{indent}except Exception:{trail}\n"
        session.lines[index] = replacement
        session.changes.append(f"line {diagnostic.row}: bare except -> except Exception")
        return True


class UnionPipeFixer:
    code = "UP007"
    _pattern = re.compile(r"(?P<prefix>\b(?:typing\.)?Union)\[(?P<body>[^\]]+)\]")

    def apply(self, session: FileEditSession, diagnostic: Diagnostic) -> bool:
        index = diagnostic.row - 1
        if not (0 <= index < len(session.lines)):
            log_warn(f"Row out of range for {session.path}: {diagnostic.row}")
            return False

        original = session.lines[index]
        updated = self._pattern.sub(self._replace_union, original)
        if updated == original:
            return False

        session.lines[index] = updated
        session.changes.append(f"line {diagnostic.row}: Union[...] -> pipe syntax")
        return True

    def _replace_union(self, match: re.Match[str]) -> str:
        parts = self._split_body(match.group("body"))
        if len(parts) < 2:
            return match.group(0)
        return " | ".join(parts)

    def _split_body(self, body: str) -> list[str]:
        parts: list[str] = []
        current: list[str] = []
        depth = 0
        for char in body:
            if char in "[({":
                depth += 1
            elif char in "])}":
                depth = max(depth - 1, 0)
            if char == "," and depth == 0:
                parts.append("".join(current).strip())
                current = []
            else:
                current.append(char)
        if current:
            parts.append("".join(current).strip())
        return parts


class UnusedArgumentFixer:
    code = "ARG"
    _name_pattern = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)")

    def apply(self, session: FileEditSession, diagnostic: Diagnostic) -> bool:
        index = diagnostic.row - 1
        if not (0 <= index < len(session.lines)):
            log_warn(f"Row out of range for {session.path}: {diagnostic.row}")
            return False

        line = session.lines[index]
        prefix = line[: diagnostic.column - 1]
        suffix = line[diagnostic.column - 1 :]
        match = self._name_pattern.match(suffix)
        if not match:
            return False

        original_name = match.group(1)
        if original_name.startswith("_"):
            return False

        replacement = prefix + "_" + original_name + suffix[match.end() :]
        session.lines[index] = replacement
        session.changes.append(f"line {diagnostic.row}: {original_name} -> _{original_name}")
        return True


FIXERS: dict[str, RuleFixer] = {
    BareExceptFixer.code: BareExceptFixer(),
    UnionPipeFixer.code: UnionPipeFixer(),
}

ARG_FIXER = UnusedArgumentFixer()
SUPPORTED_CODES = {"E722", "UP007", "ARG001", "ARG002"}
DEFAULT_PATHS: list[Path] = [Path("src"), Path("tests")]


def log_info(message: str) -> None:
    print(f"[INFO] {message}")


def log_warn(message: str) -> None:
    print(f"[WARN] {message}")


def collect_diagnostics(root: Path, paths: Iterable[Path]) -> list[Diagnostic]:
    target_paths = [str(path) for path in paths]
    command = [sys.executable, "-m", "ruff", "check", *target_paths, "--output-format", "json"]
    log_info("Executing Ruff: " + " ".join(command))

    result = subprocess.run(command, capture_output=True, text=True)
    output = result.stdout.strip()
    diagnostics_json = json.loads(output) if output else []

    diagnostics: list[Diagnostic] = []
    for item in diagnostics_json:
        code = item.get("code")
        if not code or code not in SUPPORTED_CODES:
            continue
        filename = root / item["filename"]
        location = item.get("location", {})
        diagnostics.append(
            Diagnostic(
                filename=filename,
                code=code,
                message=item.get("message", ""),
                row=int(location.get("row", 0)),
                column=int(location.get("column", 0)),
            )
        )

    if result.returncode not in (0, 1):
        log_warn("Ruff returned unexpected exit code")
        if result.stderr:
            log_warn(result.stderr.strip())

    log_info(f"Collected {len(diagnostics)} diagnostics for supported rules")
    return diagnostics


def apply_fixes(diagnostics: list[Diagnostic]) -> dict[str, dict[str, int]]:
    sessions: dict[Path, FileEditSession] = {}
    summary: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for diagnostic in diagnostics:
        fixer = select_fixer(diagnostic.code)
        if fixer is None:
            continue

        session = sessions.get(diagnostic.filename)
        if session is None:
            session = FileEditSession.load(diagnostic.filename)
            sessions[diagnostic.filename] = session

        if fixer.apply(session, diagnostic):
            key = diagnostic.code if diagnostic.code.startswith("ARG") else fixer.code
            summary[str(diagnostic.filename)][key] += 1

    for session in sessions.values():
        session.save()

    print_summary(sessions, summary)
    return summary


def select_fixer(code: str) -> RuleFixer | None:
    if code.startswith("ARG"):
        return ARG_FIXER
    return FIXERS.get(code)


def print_summary(sessions: dict[Path, FileEditSession], summary: dict[str, dict[str, int]]) -> None:
    if not summary:
        log_info("No changes were applied")
        return

    log_info("Applied fixes summary:")
    for path, count_by_code in summary.items():
        log_info(path)
        for code, count in sorted(count_by_code.items()):
            log_info(f"  {code}: {count}")
        for change in sessions[Path(path)].changes:
            log_info(f"    - {change}")


def run_ruff_check(paths: Iterable[Path]) -> None:
    target_paths = [str(path) for path in paths]
    command = [sys.executable, "-m", "ruff", "check", *target_paths]
    log_info("Re-running Ruff check")
    subprocess.run(command, check=False)


def main() -> None:
    root = Path.cwd()
    paths = [root / path for path in DEFAULT_PATHS]

    diagnostics = collect_diagnostics(root, paths)
    if not diagnostics:
        log_info("No supported diagnostics detected")
        run_ruff_check(paths)
        return

    apply_fixes(diagnostics)
    run_ruff_check(paths)


if __name__ == "__main__":
    main()
