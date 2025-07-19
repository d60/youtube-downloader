import time
from pathlib import Path


class FileCleaner:
    def __init__(self, dir: Path, all_limit: float, downloaded_limit: float) -> None:
        self.dir = dir
        self.all_limit = all_limit
        self.downloaded_limit = downloaded_limit
        self.downloaded_queue: list[Path] = []

    def check_all(self, now):
        for file in self.dir.iterdir():
            if not file.exists():
                continue
            if (now - file.stat().st_mtime) > self.all_limit:
                try:
                    file.unlink()
                except:
                    pass

    def check_downloaded(self, now):
        for file in self.downloaded_queue:
            if not file.exists():
                self.downloaded_queue.remove(file)
                continue
            if (now - file.stat().st_mtime) > self.downloaded_limit:
                try:
                    file.unlink()
                except:
                    pass
                else:
                    self.downloaded_queue.remove(file)

    def check(self):
        now = time.time()
        self.check_all(now)
        self.check_downloaded(now)
