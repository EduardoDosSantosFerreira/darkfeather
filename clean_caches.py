import shutil
from pathlib import Path


CACHE_DIR_NAMES = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".nox",
    "htmlcov",
    "build",
}

CACHE_FILE_NAMES = {
    ".coverage",
}

CACHE_SUFFIXES = {
    ".egg-info",
}


def remove_path(path: Path):
    try:
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
            print(f"[REMOVED DIR] {path}")
        elif path.is_file():
            path.unlink(missing_ok=True)
            print(f"[REMOVED FILE] {path}")
    except Exception as e:
        print(f"[ERROR] {path} -> {e}")


def clean_project(root: Path):
    for path in root.rglob("*"):
        if path.is_dir() and path.name in CACHE_DIR_NAMES:
            remove_path(path)

        elif path.is_file() and path.name in CACHE_FILE_NAMES:
            remove_path(path)

        elif path.is_dir() and any(path.name.endswith(suffix) for suffix in CACHE_SUFFIXES):
            remove_path(path)


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent
    clean_project(project_root)
    print("\nCleanup completed.")