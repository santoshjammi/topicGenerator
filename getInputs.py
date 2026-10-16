"""Import non-empty lines from ``texts/`` into the seed keyword file."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def collect_text_files(text_dir: Path) -> list[Path]:
    return sorted(path for path in text_dir.glob("*.txt") if path.is_file())


def append_unique_lines(files: list[Path], output_file: Path) -> int:
    existing = set()
    if output_file.exists():
        existing = {line.strip() for line in output_file.read_text(encoding="utf-8").splitlines() if line.strip()}
    before = len(existing)
    for path in files:
        existing.update(line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    output_file.write_text("".join(f"{line}\n" for line in sorted(existing)), encoding="utf-8")
    return len(existing) - before


def main(text_dir: Path = BASE_DIR / "texts", output_file: Path = BASE_DIR / "input-keywords.txt") -> int:
    files = collect_text_files(text_dir)
    added = append_unique_lines(files, output_file)
    print(f"Added {added} unique keywords from {len(files)} text files to {output_file}")
    return added


if __name__ == "__main__":
    main()
