"""Filter generated suggestions by seed keyword."""
from pathlib import Path


def load_input_keywords(input_file):
    try:
        return [line.strip().casefold() for line in Path(input_file).read_text(encoding="utf-8").splitlines() if line.strip()]
    except (FileNotFoundError, OSError) as exc:
        print(f"Error reading {input_file}: {exc}")
        return []


def filter_output_keywords(input_keywords, output_file, filtered_output_file):
    try:
        lines = Path(output_file).read_text(encoding="utf-8").splitlines()
        matched = sorted({line.strip() for line in lines if line.strip() and any(
            keyword in line.casefold() for keyword in input_keywords
        )})
        destination = Path(filtered_output_file)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text("".join(f"{line}\n" for line in matched), encoding="utf-8")
        print(f"Processed {len(lines)} lines; wrote {len(matched)} matches to {destination}")
        return True
    except (FileNotFoundError, OSError) as exc:
        print(f"Error processing files: {exc}")
        return False


def main():
    input_keywords = load_input_keywords("input-keywords.txt")
    if input_keywords:
        return filter_output_keywords(input_keywords, "output-keywords.txt", "filtered-output-keywords.txt")
    print("No input keywords found. Exiting.")
    return False


if __name__ == "__main__":
    main()
