import ast
import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

PLACEHOLDER_TEXT = "TODO: add documentation."
PLACEHOLDER_LITERAL = f'"""{PLACEHOLDER_TEXT}"""'
CLEANUP_PATTERN = re.compile(r'("""TODO: add documentation.""")[^\n]*')
TARGET_ROOTS = [Path("src"), Path("tests")]


@dataclass
class Replacement:
    start: int
    end: int
    text: str


def gather_python_files(paths: Sequence[Path]) -> list[Path]:
    files: list[Path] = []
    for base in paths:
        if base.is_file() and base.suffix == ".py":
            files.append(base)
        elif base.is_dir():
            for file_path in base.rglob("*.py"):
                if "__pycache__" in file_path.parts:
                    continue
                files.append(file_path)
    return files


def get_docstring_expr(node: ast.AST) -> ast.Expr | None:
    body = getattr(node, "body", None)
    if not body:
        return None
    first_stmt = body[0]
    if isinstance(first_stmt, ast.Expr) and isinstance(first_stmt.value, ast.Constant):
        if isinstance(first_stmt.value.value, str):
            return first_stmt
    return None


def compute_line_offsets(text: str) -> list[int]:
    offsets = [0]
    for idx, char in enumerate(text):
        if char == "\n":
            offsets.append(idx + 1)
    return offsets


def to_offset(line_offsets: Sequence[int], line: int, column: int) -> int:
    return line_offsets[line - 1] + column


def sanitize_docstrings(path: Path) -> bool:
    try:
        original_text = path.read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        print(f"[WARN] Unable to read {path}: {exc}")
        return False

    try:
        tree = ast.parse(original_text)
    except SyntaxError as exc:
        print(f"[WARN] Skipping {path} due to SyntaxError: {exc}")
        return False

    nodes_to_check: list[ast.AST] = [tree]
    nodes_to_check.extend(
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    )

    replacements: list[Replacement] = []
    line_offsets = compute_line_offsets(original_text)

    for node in nodes_to_check:
        expr = get_docstring_expr(node)
        if expr is None:
            continue

        doc_value = expr.value
        assert isinstance(doc_value, ast.Constant)
        current_text = doc_value.value
        if current_text == PLACEHOLDER_TEXT:
            continue

        if not hasattr(expr, "lineno") or not hasattr(expr, "end_lineno"):
            continue

        start_offset = to_offset(line_offsets, expr.lineno, expr.col_offset)
        end_offset = to_offset(line_offsets, expr.end_lineno, expr.end_col_offset)

        replacements.append(Replacement(start=start_offset, end=end_offset, text=PLACEHOLDER_LITERAL))

    if not replacements:
        return False

    new_text = original_text
    for repl in sorted(replacements, key=lambda item: item.start, reverse=True):
        new_text = new_text[: repl.start] + repl.text + new_text[repl.end :]

    cleaned_text = CLEANUP_PATTERN.sub(r"\1", new_text)

    if cleaned_text != original_text:
        path.write_text(cleaned_text, encoding="utf-8")
        return True
    return False


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    targets = [project_root / root for root in TARGET_ROOTS]
    files = gather_python_files(targets)

    updated_files: list[Path] = []
    for file_path in files:
        if sanitize_docstrings(file_path):
            updated_files.append(file_path)

    if updated_files:
        print("[INFO] Docstring sanitizer applied to the following files:")
        for file_path in updated_files:
            print(f"  {file_path.relative_to(project_root)}")
        print(f"[INFO] Total files updated: {len(updated_files)}")
    else:
        print("[INFO] No docstrings required updates.")


if __name__ == "__main__":
    main()
