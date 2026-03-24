from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class ParsedSkill:
    name: str
    description: str
    content: str


class FrontmatterParser:
    """Parse Markdown files with optional YAML frontmatter."""

    @staticmethod
    def parse(file_path: Path) -> ParsedSkill:
        content = file_path.read_text(encoding="utf-8")
        frontmatter, body = FrontmatterParser._split_frontmatter(content)
        metadata = FrontmatterParser._load_frontmatter(frontmatter)

        name = str(metadata.get("name") or file_path.stem)
        description = FrontmatterParser._extract_description(metadata, body)
        return ParsedSkill(name=name, description=description, content=content)

    @staticmethod
    def _split_frontmatter(content: str) -> tuple[str | None, str]:
        lines = content.splitlines()
        if not lines or lines[0].strip() != "---":
            return None, content

        end_index = None
        for index in range(1, len(lines)):
            if lines[index].strip() == "---":
                end_index = index
                break
        if end_index is None:
            return None, content

        frontmatter = "\n".join(lines[1:end_index])
        body = "\n".join(lines[end_index + 1 :])
        if content.endswith("\n"):
            body = f"{body}\n"
        return frontmatter, body

    @staticmethod
    def _load_frontmatter(frontmatter: str | None) -> dict[str, object]:
        if not frontmatter:
            return {}
        loaded = yaml.safe_load(frontmatter)
        if isinstance(loaded, dict):
            return loaded
        return {}

    @staticmethod
    def _extract_description(metadata: dict[str, object], body: str) -> str:
        for key in ("description", "summary"):
            value = metadata.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        first_paragraph = FrontmatterParser._first_paragraph(body)
        return first_paragraph or "No description"

    @staticmethod
    def _first_paragraph(body: str) -> str:
        chunks = [part.strip() for part in body.split("\n\n")]
        for chunk in chunks:
            if chunk:
                return " ".join(chunk.split())
        return ""


class MDCParser:
    """Cursor .mdc parser with frontmatter-compatible behavior."""

    @staticmethod
    def parse(file_path: Path) -> ParsedSkill:
        return FrontmatterParser.parse(file_path)
