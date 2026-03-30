# mac-use

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**Automate your desktop job. Let AI click, type, and read any macOS app.**

---

## What is mac-use?

mac-use is an [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server that gives AI assistants direct control over any macOS application through the native Accessibility API.

Instead of taking screenshots and guessing where to click based on pixel coordinates (like [Anthropic's computer use](https://docs.anthropic.com/en/docs/agents-and-tools/computer-use)), mac-use reads the actual UI element tree of any application using macOS System Events and AppleScript. It knows the names, types, and hierarchy of every button, text field, menu item, checkbox, and label in the target application. It can click elements by name, read their values, type into fields, navigate menus, and press keyboard shortcuts -- all through the structured accessibility interface that macOS provides to assistive technologies.

Think of it as **Playwright for desktop apps**: precise and reliable because it operates on the real UI structure rather than visual approximation.

## How it compares to Anthropic Computer Use

| | mac-use | Anthropic Computer Use |
|---|---|---|
| **UI understanding** | Structured element tree (names, roles, hierarchy) | Screenshots (pixel analysis) |
| **Element targeting** | By name, role, or path (e.g. "click button Save") | By pixel coordinates (e.g. "click at 340, 520") |
| **Speed** | Direct API calls, no image processing | Requires screenshot capture and vision model per action |
| **Accuracy** | Exact -- elements are identified unambiguously | Approximate -- coordinates can miss, especially after layout changes |
| **Cost** | Minimal -- text-only tool calls | Expensive -- each action requires a vision model call |
| **Resolution independence** | Works at any display scale | Sensitive to resolution and scaling |
| **Platform** | macOS only | Cross-platform |
| **Requirements** | Accessibility permissions | Screen recording permissions |

## You spend hours clicking through apps that don't talk to each other

You know the drill. Copy from this app, paste into that one. Click through 14 screens to submit a form. Export to CSV -- oh wait, there's no export. Do it again tomorrow.

An office worker [automated their admin work and it went viral](https://reddit.com/r/BestofRedditorUpdates/comments/1s23k0o/facing_disciplinary_investigation_sack_for/) (2,300+ upvotes) -- not because it was technically impressive, but because *everyone recognized the pain*. In healthcare, the problem is so bad it has a name: ["Death by 1,000 Clicks"](https://reddit.com/r/programming/comments/bcr3g5/bad_software_can_kill_death_by_1000_clicks_where/) (1,900+ upvotes) -- doctors spending more time navigating EHR software than treating patients, with UI fatigue literally causing medical errors.

These apps have no API. No CLI. No export. Just a GUI that someone has to sit in front of and click through. Until now.

mac-use lets an AI agent drive any macOS application the same way a human would -- without errors and 24/7. If you can see it on screen, mac-use can read it, click it, and type into it.

### What people are automating

- **Government and tax software** -- fill tax returns in desktop apps like eTax or ELSTER that offer no API, no scripting, just forms
- **Accounting and enterprise apps** -- enter data into GnuCash, QuickBooks Desktop, SAP GUI, or any legacy business software
- **Data entry across apps** -- move data between apps without copy-paste. Scan a shipping email, extract the tracking number, fill it into your receiving software. There's an entire [freelancer market paying $0.50/task](https://reddit.com/r/freelance_forhire/comments/1kxjxgj/hiring_paypertask_050_100_for_2_minute_copypaste/) for this kind of work (856 applicants)
- **Data extraction from locked-down apps** -- export your [iMessage history](https://reddit.com/r/applesucks/comments/1s1avhv/you_cannot_export_your_own_imessage_history_in/) that Apple won't let you export, pull transactions from banking apps, read dashboards in legacy Java apps
- **Hardware and vendor software** -- configure apps like Logitech G Hub that have [terrible UX and no alternative](https://reddit.com/r/LogitechG/comments/1ll327d/why_logitech_g_hub_is_the_worst_software/)
- **QA and accessibility testing** -- test native macOS apps, verify element states, audit whether buttons have proper labels

### Why not AppleScript or Shortcuts?

Apple [disbanded the AppleScript team](https://reddit.com/r/Automator/comments/1fuwaby/automator_applescript_or_any_other_macos_ideas/). Automator is deprecated. Shortcuts on Mac is [half-baked](https://reddit.com/r/shortcuts/comments/1pxpbd2/finally_dynamic_homekit_control_in_siri_shortcuts/). The entire macOS automation stack is in decay.

mac-use uses the Accessibility API layer that Apple actively maintains (it's required for disability compliance). No need for apps to expose Shortcuts actions or AppleScript dictionaries. If the app has a window, mac-use can control it.

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

### fill_form

Fill multiple form fields in a single call. Instead of one round-trip per field, all fields are filled in one execution -- significantly faster for data entry tasks like tax forms or account creation.

```
fill_form(app_name="JavaApplicationStub", fields={
    "First Name": "John",
    "Last Name": "Doe",
    "Email": "john@example.com",
    "Phone": "+1 555 0123"
})
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
