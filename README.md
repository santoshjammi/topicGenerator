# topicGenerator

Offline-safe helpers and command-line scripts for collecting and prioritizing
keyword suggestions.

## Setup

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

The scripts resolve their bundled configuration relative to the repository, so
they can be launched from any directory. Network-facing collectors use request
parameters (rather than interpolated URLs), timeouts, HTTP status checks, and
record failures in `log.txt`.

## Commands

- `python getInputs.py` imports unique non-empty lines from the keyword files in
  `texts/*.txt`; `tooling_keywords.txt` is a keyword source, not a dependency
  manifest.
- `python main.py` collects suggestions for `input-keywords.txt`.
- `python filter_keywords.py` creates `filtered-output-keywords.txt`.
- `python filter_keywords_inplace.py` filters in place after confirmation and
  creates an `output-keywords.txt.backup` before replacing the file.
- `python -m pytest -q` runs the offline regression suite.

Google Trends scripts require the dependencies in `requirements.txt` and make
live external requests; they are not run as part of the offline test suite.
Generated CSV, log, cache, and backup files are intentionally ignored by Git.
