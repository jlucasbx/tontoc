from pathlib import Path


def read_file(file_path: str | Path) -> str:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo '{file_path}' não encontrado.")
    if path.is_dir():
        raise IsADirectoryError(f"'{file_path}' é um diretório.")
    return path.read_text(encoding="utf-8")
