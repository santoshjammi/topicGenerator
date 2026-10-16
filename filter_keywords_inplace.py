"""Safely filter output-keywords.txt in place, retaining a backup."""
import shutil
from pathlib import Path

from filter_keywords import load_input_keywords


def filter_and_replace_output_keywords(input_keywords, output_file):
    output = Path(output_file)
    backup = Path(f"{output}.backup")
    try:
        lines = output.read_text(encoding="utf-8").splitlines()
        matched = sorted({line.strip() for line in lines if line.strip() and any(
            keyword in line.casefold() for keyword in input_keywords
        )})
        shutil.copy2(output, backup)
        temporary = output.with_suffix(output.suffix + ".tmp")
        temporary.write_text("".join(f"{line}\n" for line in matched), encoding="utf-8")
        temporary.replace(output)
        print(f"Processed {len(lines)} lines; wrote {len(matched)} matches to {output}")
        return True
    except (FileNotFoundError, OSError) as exc:
        print(f"Error processing files: {exc}")
        return False


def main():
    keywords = load_input_keywords("input-keywords.txt")
    if not keywords:
        print("No input keywords found. Exiting.")
        return False
    response = input("This will modify output-keywords.txt. Continue? (y/N): ")
    if response.casefold() != "y":
        print("Operation cancelled.")
        return False
    return filter_and_replace_output_keywords(keywords, "output-keywords.txt")


if __name__ == "__main__":
    main()
