"""Generate search-engine suggestions for seed keywords."""
from pathlib import Path
from string import ascii_lowercase

import config
from search_engines import SearchEngineSuggestions as SES

SEARCH_ENGINES = {
    "Google": SES.get_google,
    "Bing": SES.get_bing,
    "Yahoo": SES.get_yahoo,
    "Ask": SES.get_ask,
    "DuckDuckGo": SES.get_duckduckgo,
    "Ecosia": SES.get_ecosia,
    "Brave": SES.get_brave,
}


def load_keywords(path: str) -> list[str]:
    return [line.strip() for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def collect_suggestions(input_keywords: list[str], search_engines=SEARCH_ENGINES) -> set[str]:
    suggestions = set()
    for keyword in input_keywords:
        for letter in ascii_lowercase:
            expanded = f"{keyword} {letter}"
            for getter in search_engines.values():
                suggestions.update(SES.kw_results(getter, expanded))
    return suggestions


def run(input_file: str = config.input_file, output_file: str = config.output_file) -> int:
    input_path = Path(input_file)
    if not input_path.exists():
        input_path.write_text("", encoding="utf-8")
        print(f"Created {input_path}; add one keyword per line and run again.")
        return 0

    keywords = load_keywords(str(input_path))
    if not keywords:
        print(f"Please insert at least one keyword in {input_path}.")
        return 0

    suggestions = collect_suggestions(keywords)
    output_path = Path(output_file)
    existing = set(output_path.read_text(encoding="utf-8").splitlines()) if output_path.exists() else set()
    output_path.write_text("".join(f"{value}\n" for value in sorted(existing | suggestions)), encoding="utf-8")
    print(f"{len(suggestions)} new unique keywords found; results saved to {output_path}.")
    return len(suggestions)


if __name__ == "__main__":
    run()
