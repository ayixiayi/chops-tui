from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from pathlib import Path

from chops_tui.models import Skill, TOOL_CONFIGS, ToolSource
from chops_tui.parser import FrontmatterParser, MDCParser, ParsedSkill


class SkillScanner:
    def scan(self) -> list[Skill]:
        grouped_sources: dict[Path, set[ToolSource]] = defaultdict(set)
        alias_paths: dict[Path, Path] = {}

        for config in TOOL_CONFIGS:
            for directory in config.paths:
                if not directory.exists() or not directory.is_dir():
                    continue
                for file_path in self._discover_skill_files(directory):
                    resolved_path = file_path.resolve(strict=False)
                    grouped_sources[resolved_path].add(config.source)
                    alias_paths.setdefault(resolved_path, file_path)

        skills: list[Skill] = []
        for resolved_path, sources in grouped_sources.items():
            if not resolved_path.exists() or not resolved_path.is_file():
                continue
            parsed = self._parse_skill(resolved_path)
            if parsed is None:
                continue
            stats = resolved_path.stat()
            skills.append(
                Skill(
                    name=parsed.name,
                    description=parsed.description,
                    content=parsed.content,
                    file_path=resolved_path,
                    tool_sources=sorted(sources, key=lambda item: item.value),
                    modified_time=datetime.fromtimestamp(stats.st_mtime),
                )
            )

        return sorted(skills, key=lambda skill: skill.name.lower())

    _SKIP_PATTERNS = ("workspace", "antigravity-awesome-skills-lib")

    def _discover_skill_files(self, directory: Path) -> list[Path]:
        discovered: list[Path] = []
        for suffix in (".md", ".mdc"):
            for path in directory.rglob(f"*{suffix}"):
                if not (path.is_file() or path.is_symlink()):
                    continue
                rel = str(path.relative_to(directory))
                if any(skip in rel for skip in self._SKIP_PATTERNS):
                    continue
                discovered.append(path)
        return discovered

    def _parse_skill(self, file_path: Path) -> ParsedSkill | None:
        try:
            if file_path.suffix.lower() == ".mdc":
                return MDCParser.parse(file_path)
            return FrontmatterParser.parse(file_path)
        except (OSError, UnicodeDecodeError, ValueError):
            return None
