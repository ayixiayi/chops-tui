from __future__ import annotations

from collections import defaultdict

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Footer, Header, Static

from chops_tui.models import Skill, ToolSource
from chops_tui.scanner import SkillScanner
from chops_tui.watcher import SkillWatcher
from chops_tui.widgets.detail import DetailPanel
from chops_tui.widgets.new_skill import NewSkillScreen
from chops_tui.widgets.sidebar import Sidebar
from chops_tui.widgets.skill_list import SkillList


class ChopsApp(App[None]):
    """Chops TUI - AI agent skill manager."""

    TITLE = "Chops TUI"
    CSS_PATH = "chops.tcss"

    BINDINGS = [
        Binding("ctrl+f", "focus_search", "Search", show=True),
        Binding("ctrl+s", "save", "Save", show=True),
        Binding("ctrl+n", "new_skill", "New Skill", show=True),
        Binding("ctrl+q", "quit", "Quit", show=True),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._scanner = SkillScanner()
        self._skills: list[Skill] = []
        self._watcher: SkillWatcher | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main-container"):
            yield Sidebar(id="sidebar")
            yield SkillList(id="skill-list")
            yield DetailPanel(id="detail-panel")
        yield Footer()

    def on_mount(self) -> None:
        self._scan_and_refresh()
        self._watcher = SkillWatcher(callback=self._on_fs_change)
        self._watcher.start()

    def on_unmount(self) -> None:
        if self._watcher:
            self._watcher.stop()

    def _scan_and_refresh(self) -> None:
        self._skills = self._scanner.scan()
        skill_list = self.query_one("#skill-list", SkillList)
        skill_list.set_skills(self._skills)
        self._update_sidebar_counts()
        self._update_status()

    def _on_fs_change(self) -> None:
        self.call_from_thread(self._scan_and_refresh)

    def _update_sidebar_counts(self) -> None:
        counts: dict[str | None, int] = defaultdict(int)
        counts[None] = len(self._skills)
        for skill in self._skills:
            for source in skill.tool_sources:
                counts[source.value] += 1
        sidebar = self.query_one("#sidebar", Sidebar)
        sidebar.update_counts(counts)

    def _update_status(self) -> None:
        total = len(self._skills)
        self.sub_title = f"{total} skills found"

    def on_sidebar_filter_changed(self, event: Sidebar.FilterChanged) -> None:
        skill_list = self.query_one("#skill-list", SkillList)
        skill_list.set_filter(event.source_key)

    def on_skill_list_skill_selected(self, event: SkillList.SkillSelected) -> None:
        detail = self.query_one("#detail-panel", DetailPanel)
        detail.show_skill(event.skill)

    def action_focus_search(self) -> None:
        skill_list = self.query_one("#skill-list", SkillList)
        skill_list.focus_search()

    def action_save(self) -> None:
        detail = self.query_one("#detail-panel", DetailPanel)
        if detail.save_current():
            self.notify("Skill saved!", severity="information")
        elif detail.current_skill is None:
            self.notify("No skill selected", severity="warning")
        elif not detail.has_unsaved:
            self.notify("No unsaved changes", severity="information")
        else:
            self.notify("Failed to save!", severity="error")

    def action_new_skill(self) -> None:
        self.push_screen(NewSkillScreen(), callback=self._on_new_skill_created)

    def _on_new_skill_created(self, result: object) -> None:
        if result is not None:
            self._scan_and_refresh()
            self.notify("Skill created!", severity="information")
