import json
import os
import shutil
from pathlib import Path
from typing import Any


class Store:
    def __init__(self, dir_name: str = "ommimd", old_dir_name: str = ".ommimd"):
        appdata = os.getenv("APPDATA")
        if appdata:
            # Windows 环境: %APPDATA%/ommimd
            self.path = Path(appdata) / dir_name
        else:
            # macOS / Linux 环境: ~/.config/ommimd
            self.path = Path.home() / ".config" / dir_name

        self.old_path = Path.home() / old_dir_name
        self._migrate_if_needed()

    def _migrate_if_needed(self):
        """
        数据迁移逻辑：检查是否存在老的配置目录。
        如果存在，将其内容移动到新目录，并删除老目录。
        """
        if self.old_path.exists() and self.old_path.is_dir():
            self.path.mkdir(parents=True, exist_ok=True)

            for item in self.old_path.iterdir():
                dest = self.path / item.name
                # 如果目标位置由于某种原因已存在同名文件，先将其移除，防止 move 报错
                if dest.exists():
                    if dest.is_dir():
                        shutil.rmtree(dest)
                    else:
                        dest.unlink()
                shutil.move(str(item), str(self.path))
            shutil.rmtree(self.old_path, ignore_errors=True)

    def save(self, key: str, obj: list[dict[str, Any]]):
        self.path.mkdir(parents=True, exist_ok=True)
        file_path = self.path / f"{key}.json"
        with open(file_path, "w", encoding="utf8") as f:
            json.dump(obj, f, indent=2, ensure_ascii=False)

    def load(self, key: str) -> list[dict[str, Any]] | None:
        file_path = self.path / f"{key}.json"
        if not file_path.exists() or not file_path.is_file():
            return None
        with open(file_path, encoding="utf8") as f:
            return json.load(f)
