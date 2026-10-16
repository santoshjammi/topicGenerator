"""Runtime configuration for the keyword generator.

Configuration is resolved relative to this module so commands work from any
working directory.  Paths in ``config.ini`` remain user-configurable.
"""
from configparser import ConfigParser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
config = ConfigParser()
config.read(BASE_DIR / "config.ini", encoding="utf-8")

user_agent = config.get("Network and Connection", "user_agent")
timeout = config.getint("Network and Connection", "timeout")

input_file = str(BASE_DIR / config.get("Working Files", "input_keywords"))
output_file = str(BASE_DIR / config.get("Working Files", "output_keywords"))
log_file = str(BASE_DIR / config.get("Working Files", "log_file"))
