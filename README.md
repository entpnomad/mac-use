# mac-use

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**Control any macOS app from Claude Code via Accessibility APIs**

---

## What is mac-use?

mac-use is an [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server that gives AI assistants direct control over any macOS application through the native Accessibility API.

Instead of taking screenshots and guessing where to click based on pixel coordinates (like [Anthropic's computer use](https://docs.anthropic.com/en/docs/agents-and-tools/computer-use)), mac-use reads the actual UI element tree of any application using macOS System Events and AppleScript. It knows the names, types, and hierarchy of every button, text field, menu item, checkbox, and label in the target application. It can click elements by name, read their values, type into fields, navigate menus, and press keyboard shortcuts -- all through the structured accessibility interface that macOS provides to assistive technologies.

Think of it as **Playwright for desktop apps**: precise, fast, and reliable because it operates on the real UI structure rather than visual approximation.

## How it compares to Anthropic Computer Use

| | mac-use | Anthropic Computer Use |
|---|---|---|
| **UI understanding** | Structured element tree (names, roles, hierarchy) | Screenshots (pixel analysis) |
| **Element targeting** | By name, role, or path (e.g. "click button Save") | By pixel coordinates (e.g. "click at 340, 520") |
| **Speed** | Fast -- direct API calls, no image processing | Slow -- requires screenshot capture and vision model |
| **Accuracy** | Exact -- elements are identified unambiguously | Approximate -- coordinates can miss, especially after layout changes |
| **Cost** | Minimal -- text-only tool calls | Expensive -- each action requires a vision model call |
| **Resolution independence** | Works at any display scale | Sensitive to resolution and scaling |
| **Platform** | macOS only | Cross-platform |
| **Requirements** | Accessibility permissions | Screen recording permissions |

## Use cases

**Automate legacy and desktop apps that have no API**
- Fill tax forms in government desktop software (e.g., eTax, ELSTER) -- no API, no CLI, just a GUI
- Enter data into accounting apps like GnuCash, QuickBooks Desktop, or SAP GUI
- Configure hardware companion apps (Logitech G Hub, printer utilities) that offer no scripting

**Extract data from apps that trap it**
- Export your iMessage history, Apple Journal entries, or any app that shows data on screen but has no export button
- Pull transaction history from banking apps, read values from dashboards in legacy Java apps
- Read text from apps that block copy-paste

**Cross-app workflow orchestration**
- Move data between apps: scan a shipping email, extract the tracking number, paste it into your receiving software
- Automate the copy-paste data entry that people currently do by hand (or [pay freelancers $0.50/task to do](https://reddit.com/r/freelance_forhire/comments/1kxjxgj/hiring_paypertask_050_100_for_2_minute_copypaste/))

**Fill the gap Apple left behind**
- AppleScript is abandoned, Automator is deprecated, Shortcuts is limited on Mac -- mac-use works with any app via the Accessibility API layer that Apple actively maintains for disability compliance
- No need for apps to expose Shortcuts actions or AppleScript dictionaries

**QA and accessibility testing**
- Test native macOS apps: click through flows, verify element states, catch regressions
- Audit accessibility -- use `get_ui_elements` to check if buttons and fields have proper labels

## Quick start

### Install with pip (recommended)

```bash
pip install mac-use
mac-use
```

### Or install with uvx

```bash
uvx mac-use
```

### Configure in Claude Code

Add to your Claude Code MCP configuration (`~/.claude.json`):

```json
{
  "mcpServers": {
    "mac-use": {
      "command": "mac-use"
    }
  }
}
```

If using uvx instead:

```json
{
  "mcpServers": {
    "mac-use": {
      "command": "uvx",
      "args": ["mac-use"]
    }
  }
}
```

### Grant Accessibility permissions

mac-use requires Accessibility access to read and interact with application UI elements.

1. Open **System Settings** (or System Preferences on older macOS)
2. Go to **Privacy & Security > Accessibility**
3. Add and enable your terminal application (Terminal, iTerm2, Ghostty, etc.) or the Claude Code process

Without this permission, all tools will return an "assistive access denied" error.

## Tools

### list_windows

List all open application windows with their process names, window indices, and titles.

```
list_windows()
```

This is typically your first call -- it tells you the exact process name to use with other tools. This is especially important for Java applications (like eTax) that may appear as "JavaApplicationStub" instead of their display name.

### get_ui_elements

Get the full UI element tree of an application window. Returns element types, names, values, and their paths in the hierarchy.

```
get_ui_elements(app_name="Safari")
get_ui_elements(app_name="Finder", window_index=2, max_depth=3)
```

### click_element

Click a button, checkbox, or any other interactable element. Supports two modes:

**Path mode** -- use an AppleScript element path:
```
click_element(app_name="Safari", element_description="button 2 of group 1 of window 1")
```

**Name search mode** -- find and click by name (with optional type prefix):
```
click_element(app_name="Finder", element_description="New Folder")
click_element(app_name="Safari", element_description="button:Downloads")
click_element(app_name="TextEdit", element_description="checkbox:Wrap to Page")
```

### type_text

Type text into a field. Types into the currently focused field, or targets a specific field by name.

```
type_text(app_name="Safari", text="https://example.com", field_name="Address and Search")
type_text(app_name="TextEdit", text="Hello, world!")
```

### read_element

Read the value, name, role, and state of any UI element.

```
read_element(app_name="Safari", element_description="text field 1 of window 1")
read_element(app_name="Calculator", element_description="Display")
```

### activate_app

Bring an application to the foreground.

```
activate_app(app_name="Finder")
```

### press_key

Press a keyboard key or shortcut.

```
press_key(key="return")
press_key(key="s", modifiers="command")
press_key(key="f", modifiers="command,shift")
press_key(key="tab")
press_key(key="down arrow")
```

### menu_action

Click a menu bar item by path.

```
menu_action(app_name="TextEdit", menu_path="File > Save")
menu_action(app_name="Safari", menu_path="File > New Window")
menu_action(app_name="Finder", menu_path="Edit > Select All")
```

### screenshot

Capture a screenshot of a specific app window or the full screen. Saves to `/tmp/` and returns the file path.

```
screenshot(app_name="Safari")
screenshot(full_screen=True)
```

## Requirements

- **macOS** (any recent version -- Ventura, Sonoma, Sequoia)
- **Python 3.10+**
- **Accessibility permissions** granted to the calling process (see Quick Start above)

No external dependencies beyond the `mcp` Python package. All macOS interaction is done through the built-in `osascript` command.

## Development

```bash
git clone https://github.com/entpnomad/mac-use.git
cd mac-use
pip install -e .
mac-use
```

## License

MIT -- see [LICENSE](LICENSE).

## Author

[entpnomad](https://github.com/entpnomad)
