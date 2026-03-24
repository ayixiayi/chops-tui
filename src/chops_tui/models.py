from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path


class ToolSource(str, Enum):
    CLAUDE = "claude"
    OPENCODE = "opencode"
    CURSOR = "cursor"
    WINDSURF = "windsurf"
    CODEX = "codex"
    AMP = "amp"


@dataclass(frozen=True)
class ToolConfig:
    source: ToolSource
    label: str
    icon: str
    color: str
    paths: tuple[Path, ...]


@dataclass
class Skill:
    name: str
    description: str
    content: str
    file_path: Path
    tool_sources: list[ToolSource]
    modified_time: datetime


TOOL_CONFIGS: tuple[ToolConfig, ...] = (
    ToolConfig(
        source=ToolSource.CLAUDE,
        label="Claude Code",
        icon="🟣",
        color="#b07cff",
        paths=(
            Path("~/.claude/skills").expanduser(),
            Path("~/.agents/skills").expanduser(),
        ),
    ),
    ToolConfig(
        source=ToolSource.OPENCODE,
        label="OpenCode",
        icon="🟢",
        color="#5fd17d",
        paths=(Path("~/.config/opencode/skills").expanduser(),),
    ),
    ToolConfig(
        source=ToolSource.CURSOR,
        label="Cursor",
        icon="🔵",
        color="#66a8ff",
        paths=(
            Path("~/.cursor/skills").expanduser(),
            Path("~/.cursor/rules").expanduser(),
        ),
    ),
    ToolConfig(
        source=ToolSource.WINDSURF,
        label="Windsurf",
        icon="🟡",
        color="#f0d35c",
        paths=(
            Path("~/.codeium/windsurf/memories").expanduser(),
            Path("~/.windsurf/rules").expanduser(),
        ),
    ),
    ToolConfig(
        source=ToolSource.CODEX,
        label="Codex",
        icon="🟠",
        color="#ff9c54",
        paths=(Path("~/.codex").expanduser(),),
    ),
    ToolConfig(
        source=ToolSource.AMP,
        label="Amp",
        icon="🔴",
        color="#ff6d6d",
        paths=(Path("~/.config/amp").expanduser(),),
    ),
)

TOOL_CONFIG_BY_SOURCE: dict[ToolSource, ToolConfig] = {
    config.source: config for config in TOOL_CONFIGS
}
