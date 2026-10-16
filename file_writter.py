"""Output helpers for generated suggestions."""
import time
from pathlib import Path

import config


class FileWriter:
    @staticmethod
    def write_txt(kws) -> None:
        """Merge suggestions into the output file without creating duplicates."""
        output = Path(config.output_file)
        existing = set()
        if output.exists():
            existing = {
                line.strip() for line in output.read_text(encoding="utf-8").splitlines()
                if line.strip()
            }
        existing.update(str(keyword).strip() for keyword in kws if str(keyword).strip())
        output.write_text("".join(f"{keyword}\n" for keyword in sorted(existing)), encoding="utf-8")

    @staticmethod
    def write_log(error: str) -> None:
        Path(config.log_file).parent.mkdir(parents=True, exist_ok=True)
        with open(config.log_file, mode="a", encoding="utf-8") as log:
            log.write(f"{time.ctime()}\nError: {error}\n\n")
