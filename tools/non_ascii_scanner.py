from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path
from tokenize import COMMENT, STRING, tokenize

# 中文注释：扫描指定目录下的 Python 文件，找出非 ASCII 字符（除注释外）


@dataclass
class Violation:
    path: Path
    line: int
    column: int
    token: str


def iter_python_files(paths: Sequence[Path]) -> Iterator[Path]:
    for base in paths:
        if base.is_file() and base.suffix == ".py":
            yield base
        elif base.is_dir():
            for file_path in base.rglob("*.py"):
                if "__pycache__" in file_path.parts:
                    continue
                yield file_path


def has_non_ascii(text: str) -> bool:
    return any(ord(ch) > 127 for ch in text)


def scan_file(path: Path) -> list[Violation]:
    violations: list[Violation] = []
    try:
        with path.open("rb") as fp:
            for token in tokenize(fp.readline):
                if token.type in (COMMENT,):
                    continue
                if token.type == STRING:
                    token_text = token.string
                else:
                    token_text = token.line[token.start[1] : token.end[1]]
                if has_non_ascii(token_text):
                    violations.append(
                        Violation(
                            path=path,
                            line=token.start[0],
                            column=token.start[1] + 1,
                            token=token_text.strip(),
                        )
                    )
    except Exception as exc:  # noqa: BLE001
        print(f"[WARN] Failed to scan {path}: {exc}")
    return violations


def scan(paths: Iterable[Path]) -> list[Violation]:
    all_paths = list(iter_python_files(list(paths)))
    results: list[Violation] = []
    for file_path in all_paths:
        file_violations = scan_file(file_path)
        results.extend(file_violations)
    return results


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    default_targets = [project_root / "src", project_root / "tests"]
    violations = scan(default_targets)

    if not violations:
        print("[INFO] No non-ASCII characters detected outside comments.")
        return

    print("[INFO] Non-ASCII characters detected (excluding comments):")
    for violation in violations:
        raw_snippet = violation.token
        if len(raw_snippet) > 80:
            raw_snippet = raw_snippet[:77] + "..."
        safe_snippet = raw_snippet.encode("unicode_escape", errors="ignore").decode("ascii")
        print(
            f"  {violation.path.relative_to(project_root)}: "
            f"line {violation.line}, column {violation.column}: {safe_snippet}"
        )
    print(f"[INFO] Total violations: {len(violations)}")


if __name__ == "__main__":
    main()
