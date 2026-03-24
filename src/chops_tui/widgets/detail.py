from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, Static, TextArea

from chops_tui.models import TOOL_CONFIG_BY_SOURCE, Skill


class DetailPanel(Widget):
    """Right panel: skill metadata + content editor."""

    has_unsaved: reactive[bool] = reactive(False)

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._current_skill: Skill | None = None
        self._original_content: str = ""

    def compose(self) -> ComposeResult:
        yield Static("", id="detail-header")
        yield Static("", id="detail-meta")
        yield Static("", id="detail-unsaved")
        yield TextArea(id="detail-editor", language="markdown")
        yield Static("Select a skill from the list to view details", id="detail-empty")

    def show_skill(self, skill: Skill) -> None:
        self._current_skill = skill
        self._original_content = skill.content

        badges = " ".join(
            f"{TOOL_CONFIG_BY_SOURCE[s].icon} {TOOL_CONFIG_BY_SOURCE[s].label}"
            for s in skill.tool_sources
        )
        modified = skill.modified_time.strftime("%Y-%m-%d %H:%M")

        header = self.query_one("#detail-header", Static)
        header.update(f"  {skill.name}")

        meta = self.query_one("#detail-meta", Static)
        meta.update(f"  {badges}  |  {skill.file_path}  |  Modified: {modified}")

        editor = self.query_one("#detail-editor", TextArea)
        editor.load_text(skill.content)

        self.has_unsaved = False
        self.query_one("#detail-empty", Static).display = False
        self.query_one("#detail-header", Static).display = True
        self.query_one("#detail-meta", Static).display = True
        self.query_one("#detail-editor", TextArea).display = True

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        if self._current_skill is None:
            return
        current_text = event.text_area.text
        self.has_unsaved = current_text != self._original_content

    def watch_has_unsaved(self, value: bool) -> None:
        indicator = self.query_one("#detail-unsaved", Static)
        if value:
            indicator.update("  * Unsaved changes (Ctrl+S to save)")
            indicator.display = True
        else:
            indicator.update("")
            indicator.display = False

    def save_current(self) -> bool:
        if self._current_skill is None or not self.has_unsaved:
            return False
        editor = self.query_one("#detail-editor", TextArea)
        new_content = editor.text
        try:
            self._current_skill.file_path.write_text(new_content, encoding="utf-8")
            self._current_skill.content = new_content
            self._original_content = new_content
            self.has_unsaved = False
            return True
        except OSError:
            return False

    @property
    def current_skill(self) -> Skill | None:
        return self._current_skill
