from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select, Static

from chops_tui.models import TOOL_CONFIGS, ToolConfig


SKILL_TEMPLATE = """---
name: {name}
description: ""
---

# {name}

"""


class NewSkillScreen(ModalScreen[Path | None]):
    """Modal dialog for creating a new skill."""

    BINDINGS = [("escape", "cancel", "Cancel")]

    def compose(self) -> ComposeResult:
        tool_options = [
            (f"{cfg.icon}  {cfg.label}", cfg.source.value) for cfg in TOOL_CONFIGS
        ]
        with Vertical(id="new-skill-dialog"):
            yield Static("Create New Skill", id="dialog-title")
            yield Label("Target Tool:")
            yield Select(tool_options, id="tool-select", prompt="Select a tool...")
            yield Label("Skill Name:")
            yield Input(placeholder="my-awesome-skill", id="skill-name-input")
            yield Button("Create", variant="primary", id="create-btn")
            yield Button("Cancel", id="cancel-btn")
            yield Static("", id="dialog-error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel-btn":
            self.dismiss(None)
            return
        if event.button.id == "create-btn":
            self._create_skill()

    def action_cancel(self) -> None:
        self.dismiss(None)

    def _create_skill(self) -> None:
        select = self.query_one("#tool-select", Select)
        name_input = self.query_one("#skill-name-input", Input)
        error_label = self.query_one("#dialog-error", Static)

        if select.value is Select.BLANK:
            error_label.update("Please select a tool")
            return
        if not name_input.value.strip():
            error_label.update("Please enter a skill name")
            return

        tool_value = str(select.value)
        skill_name = name_input.value.strip()
        safe_name = skill_name.replace(" ", "-").lower()

        target_config: ToolConfig | None = None
        for cfg in TOOL_CONFIGS:
            if cfg.source.value == tool_value:
                target_config = cfg
                break

        if target_config is None:
            error_label.update("Invalid tool selection")
            return

        target_dir: Path | None = None
        for p in target_config.paths:
            if p.exists() and p.is_dir():
                target_dir = p
                break

        if target_dir is None:
            target_dir = target_config.paths[0]
            try:
                target_dir.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                error_label.update(f"Cannot create directory: {exc}")
                return

        file_path = target_dir / f"{safe_name}.md"
        if file_path.exists():
            error_label.update(f"Skill already exists: {file_path.name}")
            return

        try:
            content = SKILL_TEMPLATE.format(name=skill_name)
            file_path.write_text(content, encoding="utf-8")
            self.dismiss(file_path)
        except OSError as exc:
            error_label.update(f"Failed to create: {exc}")
