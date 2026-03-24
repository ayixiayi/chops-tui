from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from chops_tui.models import TOOL_CONFIGS


class _SkillEventHandler(FileSystemEventHandler):
    def __init__(self, callback: Callable[[], None]) -> None:
        self._callback = callback

    def on_any_event(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        src = event.src_path
        src_path = Path(str(src))
        if src_path.suffix.lower() in {".md", ".mdc"}:
            self._callback()


class SkillWatcher:
    def __init__(self, callback: Callable[[], None]) -> None:
        self._callback = callback
        self._observer: Observer | None = None  # type: ignore[type-arg]

    def start(self) -> None:
        if self._observer is not None:
            return

        observer = Observer()
        handler = _SkillEventHandler(self._callback)
        watched_dirs = self._existing_dirs()
        for directory in watched_dirs:
            observer.schedule(handler, str(directory), recursive=True)

        observer.daemon = True
        observer.start()
        self._observer = observer

    def stop(self) -> None:
        if self._observer is None:
            return
        self._observer.stop()
        self._observer.join(timeout=1)
        self._observer = None

    def _existing_dirs(self) -> set[Path]:
        directories: set[Path] = set()
        for config in TOOL_CONFIGS:
            for path in config.paths:
                if path.exists() and path.is_dir():
                    directories.add(path)
        return directories
