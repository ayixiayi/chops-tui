from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, Static

from chops_tui.models import TOOL_CONFIGS, ToolConfig, ToolSource


class ToolFilterItem(Static):
    """A single tool filter button in the sidebar."""

    class Selected(Message):
        def __init__(self, source_key: str) -> None:
            super().__init__()
            self.source_key = source_key

    is_active: reactive[bool] = reactive(False)

    def __init__(
        self,
        source_key: str,
        label: str,
        icon: str,
        color: str,
        count: int = 0,
        **kwargs: object,
    ) -> None:
        super().__init__(**kwargs)
        self.source_key = source_key
        self._label = label
        self._icon = icon
        self._color = color
        self._count = count

    def compose(self) -> ComposeResult:
        yield Label(f"{self._icon}  {self._label} [{self._count}]", id="filter-label")

    def update_count(self, count: int) -> None:
        self._count = count
        label = self.query_one("#filter-label", Label)
        label.update(f"{self._icon}  {self._label} [{self._count}]")

    def on_click(self) -> None:
        self.post_message(self.Selected(self.source_key))

    def watch_is_active(self, value: bool) -> None:
        self.set_class(value, "active")


class Sidebar(Widget):
    """Left sidebar with tool filters."""

    class FilterChanged(Message):
        def __init__(self, source_key: str | None) -> None:
            super().__init__()
            self.source_key = source_key

    selected_filter: reactive[str | None] = reactive(None)

    def compose(self) -> ComposeResult:
        yield Static("CHOPS", id="sidebar-title")
        with VerticalScroll(id="filter-list"):
            yield ToolFilterItem(
                source_key="all",
                label="All Skills",
                icon="*",
                color="#ffffff",
                id="filter-all",
            )
            for config in TOOL_CONFIGS:
                yield ToolFilterItem(
                    source_key=config.source.value,
                    label=config.label,
                    icon=config.icon,
                    color=config.color,
                    id=f"filter-{config.source.value}",
                )

    def on_tool_filter_item_selected(self, event: ToolFilterItem.Selected) -> None:
        key = None if event.source_key == "all" else event.source_key
        self.selected_filter = key
        self.post_message(self.FilterChanged(key))

    def watch_selected_filter(self, value: str | None) -> None:
        for item in self.query(ToolFilterItem):
            if value is None:
                item.is_active = item.source_key == "all"
            else:
                item.is_active = item.source_key == value

    def update_counts(self, counts: dict[str | None, int]) -> None:
        total = counts.get(None, 0)
        all_item = self.query_one("#filter-all", ToolFilterItem)
        all_item.update_count(total)
        for config in TOOL_CONFIGS:
            item = self.query_one(f"#filter-{config.source.value}", ToolFilterItem)
            item.update_count(counts.get(config.source.value, 0))

    def on_mount(self) -> None:
        self.selected_filter = None
