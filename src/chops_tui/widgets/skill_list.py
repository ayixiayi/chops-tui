from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Input, Label, Static

from chops_tui.models import TOOL_CONFIG_BY_SOURCE, Skill


class SkillListItem(Static):
    """A single skill entry in the list."""

    class Selected(Message):
        def __init__(self, skill_index: int) -> None:
            super().__init__()
            self.skill_index = skill_index

    is_active: reactive[bool] = reactive(False)

    def __init__(self, skill: Skill, index: int, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self.skill = skill
        self.skill_index = index

    def compose(self) -> ComposeResult:
        badges = " ".join(
            TOOL_CONFIG_BY_SOURCE[s].icon for s in self.skill.tool_sources
        )
        desc = self.skill.description[:60]
        if len(self.skill.description) > 60:
            desc += "..."
        yield Label(f"{badges}  {self.skill.name}", classes="skill-name")
        yield Label(desc, classes="skill-desc")

    def on_click(self) -> None:
        self.post_message(self.Selected(self.skill_index))

    def watch_is_active(self, value: bool) -> None:
        self.set_class(value, "active")


class SkillList(Widget):
    """Middle column: search bar + skill list."""

    class SkillSelected(Message):
        def __init__(self, skill: Skill) -> None:
            super().__init__()
            self.skill = skill

    selected_index: reactive[int | None] = reactive(None)

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._skills: list[Skill] = []
        self._filtered: list[Skill] = []
        self._filter_source: str | None = None
        self._search_text: str = ""
        self._generation: int = 0

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search skills... (Ctrl+F)", id="search-input")
        yield VerticalScroll(id="skill-scroll")

    def set_skills(self, skills: list[Skill]) -> None:
        self._skills = skills
        self._apply_filters()

    def set_filter(self, source_key: str | None) -> None:
        self._filter_source = source_key
        self._apply_filters()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search-input":
            self._search_text = event.value.strip().lower()
            self._apply_filters()

    def _apply_filters(self) -> None:
        filtered = self._skills

        if self._filter_source:
            filtered = [
                s
                for s in filtered
                if any(t.value == self._filter_source for t in s.tool_sources)
            ]

        if self._search_text:
            query = self._search_text
            filtered = [
                s
                for s in filtered
                if query in s.name.lower()
                or query in s.description.lower()
                or query in s.content.lower()
            ]

        self._filtered = filtered
        self._rebuild_list()

    def _rebuild_list(self) -> None:
        scroll = self.query_one("#skill-scroll", VerticalScroll)
        scroll.remove_children()
        self._generation += 1
        gen = self._generation

        for i, skill in enumerate(self._filtered):
            item = SkillListItem(skill, i, id=f"skill-g{gen}-{i}")
            scroll.mount(item)

        if self.selected_index is not None and self.selected_index < len(
            self._filtered
        ):
            self._highlight(self.selected_index)
        else:
            self.selected_index = None

    def on_skill_list_item_selected(self, event: SkillListItem.Selected) -> None:
        self.selected_index = event.skill_index
        if event.skill_index < len(self._filtered):
            self.post_message(self.SkillSelected(self._filtered[event.skill_index]))

    def watch_selected_index(self, value: int | None) -> None:
        self._highlight(value)

    def _highlight(self, index: int | None) -> None:
        for item in self.query(SkillListItem):
            item.is_active = item.skill_index == index

    def focus_search(self) -> None:
        self.query_one("#search-input", Input).focus()

    @property
    def filtered_skills(self) -> list[Skill]:
        return self._filtered
