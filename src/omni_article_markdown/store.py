import json
from pathlib import Path
from typing import Any


class Store:
    def __init__(self, base_dir_name: str = ".ommimd"):
        self.path = Path.home() / base_dir_name

    def save(self, key: str, obj: Any):
        self.path.mkdir(parents=True, exist_ok=True)
        file_path = self.path / f"{key}.json"
        with open(file_path, "w", encoding="utf8") as f:
            json.dump(obj, f, indent=4, ensure_ascii=False)

    def load(self, key: str) -> Any | None:
        file_path = self.path / f"{key}.json"
        if not file_path.exists() or not file_path.is_file():
            return None
        with open(file_path, encoding="utf8") as f:
            return json.load(f)
