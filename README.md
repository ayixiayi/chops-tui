# Chops TUI

A terminal-based manager for AI agent skills.

Chops TUI is a terminal (TUI) clone of [Shpigford/chops](https://github.com/Shpigford/chops), the macOS app for managing AI coding agent skills. It provides a centralized interface to discover, view, edit, and create skills for various AI coding assistants. Built with Python and the Textual framework.

## Features

- **Skill Scanning**: Automatically discovers skills from multiple AI agent tool directories.
- **Multi-Tool Support**: Integrated support for Claude Code, OpenCode, Cursor, Windsurf, Codex, and Amp.
- **Live Filtering**: Filter skills by tool source using the sidebar or search across names, descriptions, and content.
- **Real-time Updates**: Automatically watches for file system changes and refreshes the skill list.
- **Skill Editor**: View and edit skill content directly in the terminal with unsaved change indicators.
- **Skill Creation**: Create new skills for specific tools using a guided modal dialog.
- **Responsive UI**: A clean three-column layout designed for efficient terminal workflows.

## Supported Tools

| Tool | Icon | Scanned Directories |
| :--- | :---: | :--- |
| Claude Code | 🟣 | `~/.claude/skills`, `~/.agents/skills` |
| OpenCode | 🟢 | `~/.config/opencode/skills` |
| Cursor | 🔵 | `~/.cursor/skills`, `~/.cursor/rules` |
| Windsurf | 🟡 | `~/.codeium/windsurf/memories`, `~/.windsurf/rules` |
| Codex | 🟠 | `~/.codex` |
| Amp | 🔴 | `~/.config/amp` |

## Installation

### Method 1: Using uv (Recommended)

Install directly from the repository:

```bash
uv tool install git+https://github.com/ayixiayi/chops-tui
```

### Method 2: Local Installation

Clone the repository and install locally:

```bash
git clone https://github.com/ayixiayi/chops-tui
cd chops-tui
uv tool install .
```

## Usage

Once installed, launch the application by running:

```bash
chops-tui
```

## Keybindings

| Key | Action |
| :--- | :--- |
| `Ctrl+F` | Focus search bar |
| `Ctrl+S` | Save current skill changes |
| `Ctrl+N` | Create a new skill |
| `Ctrl+Q` | Quit the application |
| `Esc` | Cancel or close modal dialogs |

## Project Structure

```text
src/chops_tui/
├── app.py           # Main application logic and TUI setup
├── models.py        # Data models for Skills and Tool configurations
├── scanner.py       # Logic for discovering skill files on disk
├── parser.py        # Markdown and MDC file parsing
├── watcher.py       # File system observer for real-time updates
└── widgets/
    ├── sidebar.py   # Tool filtering sidebar
    ├── skill_list.py # Searchable list of skills
    ├── detail.py    # Skill metadata and content editor
    └── new_skill.py # Modal dialog for skill creation
```

## Requirements

- Python 3.12 or higher
- Dependencies (automatically handled by installation):
  - `pyyaml`
  - `textual`
  - `watchdog`

## Credits

- Inspired by [Shpigford/chops](https://github.com/Shpigford/chops).
- Built with [Textual](https://textual.textualize.io/).

## License

MIT
