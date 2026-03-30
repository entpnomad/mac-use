"""mac-use: MCP server for controlling macOS apps via Accessibility APIs."""

import json
import shutil
import subprocess
import re
import datetime
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "mac-use",
    instructions="Control any macOS app via Accessibility APIs (System Events / AppleScript)",
)

# Track which app was last activated to skip redundant activations
_last_frontmost_app: str = ""


def _run_applescript(script: str, timeout: int = 30) -> str:
    """Execute an AppleScript via osascript and return stdout."""
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            stderr = result.stderr.strip()
            if "not allowed assistive access" in stderr.lower():
                raise RuntimeError(
                    "Accessibility access denied. Grant permission in "
                    "System Settings > Privacy & Security > Accessibility."
                )
            raise RuntimeError(f"AppleScript error: {stderr}")
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        raise RuntimeError(
            f"AppleScript timed out after {timeout}s. "
            "The target app may be unresponsive."
        )


def _escape_applescript_string(s: str) -> str:
    """Escape a string for safe embedding in AppleScript."""
    return s.replace("\\", "\\\\").replace('"', '\\"')


def _set_clipboard(text: str) -> None:
    """Set the macOS clipboard to the given text via pbcopy."""
    subprocess.run(
        ["pbcopy"],
        input=text.encode("utf-8"),
        timeout=5,
    )


def _activate_block(app_name: str) -> str:
    """Return AppleScript to activate an app, skipping if already frontmost."""
    global _last_frontmost_app
    escaped = _escape_applescript_string(app_name)
    if app_name == _last_frontmost_app:
        return ""
    _last_frontmost_app = app_name
    return f'''        set frontmost to true
        delay 0.1
'''


@mcp.tool()
def list_windows() -> str:
    """List all open application windows with their process names.

    Returns every visible window across all running applications, including
    the process name (as seen by System Events), the window title, and the
    window index. This is useful for identifying the correct process name
    to pass to other tools -- especially for Java apps that may appear as
    "JavaApplicationStub" instead of their display name.
    """
    script = '''
tell application "System Events"
    set output to ""
    set procList to every process whose visible is true
    repeat with proc in procList
        set procName to name of proc
        try
            set winList to every window of proc
            repeat with i from 1 to count of winList
                set w to item i of winList
                set winTitle to ""
                try
                    set winTitle to name of w
                end try
                set output to output & procName & "\\t" & i & "\\t" & winTitle & "\\n"
            end repeat
        end try
    end repeat
    return output
end tell
'''
    raw = _run_applescript(script)
    if not raw:
        return "No visible windows found."

    lines = [l for l in raw.split("\n") if l.strip()]
    results = []
    for line in lines:
        parts = line.split("\t")
        if len(parts) >= 3:
            results.append({
                "process": parts[0],
                "window_index": parts[1],
                "title": parts[2],
            })
        elif len(parts) == 2:
            results.append({
                "process": parts[0],
                "window_index": parts[1],
                "title": "",
            })

    return json.dumps(results, indent=2)


@mcp.tool()
def get_ui_elements(
    app_name: str,
    window_index: int = 1,
    max_depth: int = 5,
    filter_roles: str = "",
) -> str:
    """Get the UI element tree of a specific application window.

    Reads the Accessibility hierarchy and returns a structured list of
    interactable elements (buttons, text fields, menus, checkboxes, etc.)
    with their types, names, and path within the element tree.

    Args:
        app_name: The process name as shown by list_windows (e.g. "Safari", "Finder").
        window_index: Which window to inspect (1-based, default 1).
        max_depth: How many levels deep to traverse the UI tree (default 5).
        filter_roles: Comma-separated AX roles to include (e.g. "AXTextField,AXButton,AXCheckBox").
                      If empty, returns all elements. Use this to dramatically speed up
                      queries on complex apps by only returning what you need.
    """
    escaped = _escape_applescript_string(app_name)
    activate = _activate_block(app_name)

    if filter_roles:
        # Filtered walk: much faster for complex apps
        roles = [r.strip() for r in filter_roles.split(",")]
        role_checks = " or ".join(
            f'elemRole is "{_escape_applescript_string(r)}"' for r in roles
        )
        script = f'''
on walkTree(parentElem, depth, maxD, appName)
    if depth > maxD then return ""
    set output to ""
    try
        set children to UI elements of parentElem
    on error
        return ""
    end try
    repeat with uiElem in children
        try
            set elemRole to role of uiElem as text
            if {role_checks} then
                set elemName to ""
                try
                    set elemName to name of uiElem
                end try
                set elemVal to ""
                try
                    set elemVal to value of uiElem as text
                end try
                set elemDesc to ""
                try
                    set elemDesc to description of uiElem
                end try
                set output to output & elemRole & "\\t" & elemName & "\\t" & elemVal & "\\t" & elemDesc & "\\n"
            end if
        end try
        set output to output & my walkTree(uiElem, depth + 1, maxD, appName)
    end repeat
    return output
end walkTree

tell application "System Events"
    tell process "{escaped}"
{activate}        set output to my walkTree(window {window_index}, 0, {max_depth}, "{escaped}")
        return output
    end tell
end tell
'''
        raw = _run_applescript(script, timeout=60)
        if not raw:
            return f"No matching elements found for '{app_name}' window {window_index}."

        lines = [l for l in raw.split("\n") if l.strip()]
        elements = []
        for line in lines:
            parts = line.split("\t")
            if len(parts) >= 4:
                role, name, value, desc = parts[0], parts[1], parts[2], parts[3]
                entry = role
                if name:
                    entry += f' "{name}"'
                if value:
                    entry += f" = {value}"
                if desc and desc != name:
                    entry += f" ({desc})"
                elements.append(entry)

        return "\n".join(elements)

    else:
        # Unfiltered: use entire contents (slower but complete)
        script = f'''
tell application "System Events"
    tell process "{escaped}"
{activate}        get entire contents of window {window_index}
    end tell
end tell
'''
        raw = _run_applescript(script, timeout=60)
        if not raw:
            return f"No UI elements found for '{app_name}' window {window_index}."

        elements = []
        for item in raw.split(", "):
            item = item.strip()
            if not item:
                continue
            proc_suffix = f"of application process {app_name}"
            clean = item.replace(proc_suffix, "").strip()
            if clean:
                elements.append(clean)

        max_elements = max_depth * 100
        if len(elements) > max_elements:
            elements = elements[:max_elements]
            elements.append(f"... ({len(elements)} elements shown, increase max_depth for more)")

        return "\n".join(elements)


@mcp.tool()
def click_element(app_name: str, element_description: str) -> str:
    """Click a UI element (button, checkbox, menu item, etc.) in an application.

    Supports two modes:
    - Path mode: provide an AppleScript element path like "button 1 of group 2 of window 1"
    - Name search mode: provide a human-readable description and the tool will find
      the first element whose name or description contains the search text.
      Prefix with the element type for precision, e.g. "button:Save" or "checkbox:Enable".

    Args:
        app_name: The process name (e.g. "Safari").
        element_description: Either an AppleScript path or a search string (optionally prefixed with type, e.g. "button:Save").
    """
    escaped_app = _escape_applescript_string(app_name)
    activate = _activate_block(app_name)

    # Determine if this looks like an AppleScript path or a name search
    is_path = bool(re.match(r"^(button|text field|checkbox|radio button|group|scroll|tab|menu|pop up|combo|static text|image|slider|splitter|table|row|column|outline|UI element|toolbar)\s+\d+", element_description, re.IGNORECASE))
    is_path = is_path or " of " in element_description

    if is_path:
        escaped_desc = _escape_applescript_string(element_description)
        script = f'''
tell application "System Events"
    tell process "{escaped_app}"
{activate}        try
            click {escaped_desc}
            return "Clicked: {escaped_desc}"
        on error
            try
                perform action "AXPress" of {escaped_desc}
                return "Pressed (AXPress): {escaped_desc}"
            on error errMsg
                error errMsg
            end try
        end try
    end tell
end tell
'''
    else:
        # Name search mode
        search_role = ""
        search_name = element_description
        if ":" in element_description:
            parts = element_description.split(":", 1)
            search_role = parts[0].strip().lower()
            search_name = parts[1].strip()

        escaped_name = _escape_applescript_string(search_name)
        role_filter = ""
        if search_role:
            role_map = {
                "button": "AXButton",
                "checkbox": "AXCheckBox",
                "radio": "AXRadioButton",
                "text field": "AXTextField",
                "text area": "AXTextArea",
                "menu item": "AXMenuItem",
                "pop up": "AXPopUpButton",
                "combo": "AXComboBox",
                "tab": "AXTabGroup",
                "link": "AXLink",
                "slider": "AXSlider",
                "image": "AXImage",
                "static text": "AXStaticText",
            }
            ax_role = role_map.get(search_role, "")
            if ax_role:
                role_filter = f'and role of uiElem is "{ax_role}" '

        script = f'''
on findAndClick(parentElem, searchName, depth)
    if depth > 8 then return false
    try
        set children to UI elements of parentElem
    on error
        return false
    end try
    repeat with uiElem in children
        try
            set elemName to ""
            try
                set elemName to name of uiElem
            end try
            if elemName is "" then
                try
                    set elemName to description of uiElem
                end try
            end if
            if elemName is "" then
                try
                    set elemName to title of uiElem
                end try
            end if
            if elemName contains searchName {role_filter}then
                click uiElem
                return true
            end if
        end try
        if my findAndClick(uiElem, searchName, depth + 1) then return true
    end repeat
    return false
end findAndClick

tell application "System Events"
    tell process "{escaped_app}"
{activate}        if my findAndClick(window 1, "{escaped_name}", 0) then
            return "Clicked element matching: {escaped_name}"
        else
            return "ERROR: No element found matching: {escaped_name}"
        end if
    end tell
end tell
'''

    result = _run_applescript(script, timeout=30)
    return result


@mcp.tool()
def type_text(app_name: str, text: str, field_name: str = "") -> str:
    """Type text into a text field in an application.

    If field_name is provided, the tool first finds and focuses that field.
    Otherwise, it types into whatever field currently has focus.

    Args:
        app_name: The process name (e.g. "Safari").
        text: The text to type.
        field_name: Optional name of the text field to target.
    """
    escaped_app = _escape_applescript_string(app_name)
    escaped_text = _escape_applescript_string(text)
    activate = _activate_block(app_name)

    if field_name:
        escaped_field = _escape_applescript_string(field_name)

        # Pre-set clipboard for paste fallback (works for Java Swing)
        _set_clipboard(text)

        script = f'''
on findField(parentElem, searchName, depth)
    if depth > 8 then return missing value
    try
        set children to UI elements of parentElem
    on error
        return missing value
    end try
    repeat with uiElem in children
        try
            set elemRole to role of uiElem
            if elemRole is "AXTextField" or elemRole is "AXTextArea" then
                set elemName to ""
                try
                    set elemName to name of uiElem
                end try
                if elemName is "" then
                    try
                        set elemName to description of uiElem
                    end try
                end if
                if elemName contains "{escaped_field}" then
                    return uiElem
                end if
            end if
        end try
        set found to my findField(uiElem, searchName, depth + 1)
        if found is not missing value then return found
    end repeat
    return missing value
end findField

tell application "System Events"
    tell process "{escaped_app}"
{activate}        set targetField to my findField(window 1, "{escaped_field}", 0)
        if targetField is missing value then
            return "ERROR: No text field found matching: {escaped_field}"
        end if
        -- Tier 1: set value directly (fastest, works for most native fields)
        try
            set focused of targetField to true
            set value of targetField to "{escaped_text}"
            -- Verify value was actually set (Java Swing silently ignores)
            delay 0.1
            set currentVal to ""
            try
                set currentVal to value of targetField as text
            end try
            if currentVal is "{escaped_text}" then
                return "Typed text into field: {escaped_field}"
            end if
        end try
        -- Tier 2: focus + keystroke with longer delay (works for Java Swing)
        try
            set focused of targetField to true
            delay 0.5
            keystroke "a" using command down
            delay 0.05
            key code 51
            delay 0.1
            keystroke "{escaped_text}"
            delay 0.3
            set currentVal to ""
            try
                set currentVal to value of targetField as text
            end try
            if currentVal is not "" then
                return "Typed text into field: {escaped_field}"
            end if
        end try
        -- Tier 3: focus + clipboard paste (Cmd+V)
        try
            set focused of targetField to true
            delay 0.5
            keystroke "a" using command down
            delay 0.05
            keystroke "v" using command down
            delay 0.3
            return "Typed text into field (paste): {escaped_field}"
        end try
        -- Tier 4: cliclick at field coordinates + clipboard paste
        try
            set fieldPos to position of targetField
            set fieldSize to size of targetField
            set clickX to (item 1 of fieldPos) + ((item 1 of fieldSize) / 2) as integer
            set clickY to (item 2 of fieldPos) + ((item 2 of fieldSize) / 2) as integer
            do shell script "cliclick c:" & clickX & "," & clickY
            delay 0.5
            keystroke "a" using command down
            delay 0.05
            keystroke "v" using command down
            delay 0.3
            return "Typed text into field (click+paste): {escaped_field}"
        on error errMsg
            return "ERROR: All typing methods failed for: {escaped_field} - " & errMsg
        end try
    end tell
end tell
'''
    else:
        script = f'''
tell application "System Events"
    tell process "{escaped_app}"
{activate}        keystroke "{escaped_text}"
    end tell
end tell
return "Typed text into focused field"
'''

    return _run_applescript(script)


@mcp.tool()
def read_element(app_name: str, element_description: str) -> str:
    """Read the value or content of a UI element in an application.

    Can read the value of text fields, labels, checkboxes, and other elements.

    Args:
        app_name: The process name (e.g. "Safari").
        element_description: An AppleScript element path (e.g. "text field 1 of window 1")
                             or a search string (e.g. "Search" to find by name).
    """
    escaped_app = _escape_applescript_string(app_name)
    activate = _activate_block(app_name)

    is_path = " of " in element_description or bool(
        re.match(r"^(button|text field|checkbox|radio button|group|static text|UI element|image|slider|pop up|combo|text area)\s+\d+", element_description, re.IGNORECASE)
    )

    if is_path:
        escaped_desc = _escape_applescript_string(element_description)
        script = f'''
tell application "System Events"
    tell process "{escaped_app}"
{activate}        set elem to {escaped_desc}
        set output to ""
        try
            set output to output & "role: " & (role of elem) & "\\n"
        end try
        try
            set output to output & "name: " & (name of elem) & "\\n"
        end try
        try
            set output to output & "title: " & (title of elem) & "\\n"
        end try
        try
            set output to output & "value: " & (value of elem as text) & "\\n"
        end try
        try
            set output to output & "description: " & (description of elem) & "\\n"
        end try
        try
            set output to output & "enabled: " & (enabled of elem as text) & "\\n"
        end try
        try
            set output to output & "focused: " & (focused of elem as text) & "\\n"
        end try
        return output
    end tell
end tell
'''
    else:
        escaped_name = _escape_applescript_string(element_description)
        script = f'''
on findElement(parentElem, searchName, depth)
    if depth > 8 then return missing value
    try
        set children to UI elements of parentElem
    on error
        return missing value
    end try
    repeat with uiElem in children
        try
            set elemName to ""
            try
                set elemName to name of uiElem
            end try
            if elemName is "" then
                try
                    set elemName to description of uiElem
                end try
            end if
            if elemName is "" then
                try
                    set elemName to title of uiElem
                end try
            end if
            if elemName contains searchName then
                return uiElem
            end if
        end try
        set found to my findElement(uiElem, searchName, depth + 1)
        if found is not missing value then return found
    end repeat
    return missing value
end findElement

tell application "System Events"
    tell process "{escaped_app}"
{activate}        set elem to my findElement(window 1, "{escaped_name}", 0)
        if elem is missing value then
            return "ERROR: No element found matching: {escaped_name}"
        end if
        set output to ""
        try
            set output to output & "role: " & (role of elem) & "\\n"
        end try
        try
            set output to output & "name: " & (name of elem) & "\\n"
        end try
        try
            set output to output & "title: " & (title of elem) & "\\n"
        end try
        try
            set output to output & "value: " & (value of elem as text) & "\\n"
        end try
        try
            set output to output & "description: " & (description of elem) & "\\n"
        end try
        try
            set output to output & "enabled: " & (enabled of elem as text) & "\\n"
        end try
        try
            set output to output & "focused: " & (focused of elem as text) & "\\n"
        end try
        return output
    end tell
end tell
'''

    return _run_applescript(script)


@mcp.tool()
def activate_app(app_name: str) -> str:
    """Bring an application to the foreground.

    Args:
        app_name: The application name (e.g. "Safari", "Finder", "Terminal").
                  For Java apps, use the process name from list_windows (e.g. "JavaApplicationStub").
    """
    global _last_frontmost_app
    escaped = _escape_applescript_string(app_name)
    # First try via System Events process (works for Java apps and all processes)
    try:
        result = _run_applescript(f'''
tell application "System Events"
    set procExists to exists process "{escaped}"
    if procExists then
        tell process "{escaped}"
            set frontmost to true
        end tell
        delay 0.15
        return "Activated via process: {escaped}"
    end if
end tell
return "NOT_FOUND"
''')
        if "NOT_FOUND" not in result:
            _last_frontmost_app = app_name
            return result
    except RuntimeError:
        pass

    # Fall back to tell application (works for standard apps)
    script = f'''
tell application "{escaped}"
    activate
end tell
delay 0.15
return "Activated: {escaped}"
'''
    _last_frontmost_app = app_name
    return _run_applescript(script)


@mcp.tool()
def press_key(key: str, modifiers: str = "") -> str:
    """Press a keyboard key or shortcut.

    Args:
        key: The key to press. Use names for special keys: "return", "tab", "escape",
             "space", "delete", "up arrow", "down arrow", "left arrow", "right arrow",
             "f1" through "f12". For regular characters, just pass the character.
        modifiers: Comma-separated modifier keys: "command", "shift", "option", "control".
                   Example: "command,shift" for Cmd+Shift. Leave empty for no modifiers.
    """
    special_keys = {
        "return": "return",
        "enter": "return",
        "tab": "tab",
        "escape": "escape",
        "esc": "escape",
        "space": "space",
        "delete": "delete",
        "backspace": "delete",
        "forward delete": "forward delete",
        "up arrow": "up arrow",
        "down arrow": "down arrow",
        "left arrow": "left arrow",
        "right arrow": "right arrow",
        "home": "home",
        "end": "end",
        "page up": "page up",
        "page down": "page down",
        "f1": "f1", "f2": "f2", "f3": "f3", "f4": "f4",
        "f5": "f5", "f6": "f6", "f7": "f7", "f8": "f8",
        "f9": "f9", "f10": "f10", "f11": "f11", "f12": "f12",
    }

    key_lower = key.lower().strip()

    mod_list = []
    if modifiers:
        for m in modifiers.split(","):
            m = m.strip().lower()
            if m in ("command", "cmd"):
                mod_list.append("command down")
            elif m in ("shift",):
                mod_list.append("shift down")
            elif m in ("option", "alt"):
                mod_list.append("option down")
            elif m in ("control", "ctrl"):
                mod_list.append("control down")

    using_clause = ""
    if mod_list:
        using_clause = " using {" + ", ".join(mod_list) + "}"

    mod_desc = f" with {modifiers}" if modifiers else ""
    escaped_key_desc = _escape_applescript_string(key)

    if key_lower in special_keys:
        key_code = _key_code_for(key_lower)
        script = f'''
tell application "System Events"
    key code {key_code}{using_clause}
end tell
return "Pressed: {escaped_key_desc}{mod_desc}"
'''
    else:
        escaped_key = _escape_applescript_string(key)
        script = f'''
tell application "System Events"
    keystroke "{escaped_key}"{using_clause}
end tell
return "Pressed: {escaped_key}{mod_desc}"
'''

    return _run_applescript(script)


def _key_code_for(key_name: str) -> int:
    """Return the macOS virtual key code for a named key."""
    codes = {
        "return": 36,
        "tab": 48,
        "space": 49,
        "delete": 51,
        "escape": 53,
        "forward delete": 117,
        "up arrow": 126,
        "down arrow": 125,
        "left arrow": 123,
        "right arrow": 124,
        "home": 115,
        "end": 119,
        "page up": 116,
        "page down": 121,
        "f1": 122, "f2": 120, "f3": 99, "f4": 118,
        "f5": 96, "f6": 97, "f7": 98, "f8": 100,
        "f9": 101, "f10": 109, "f11": 103, "f12": 111,
    }
    return codes.get(key_name, 36)


@mcp.tool()
def menu_action(app_name: str, menu_path: str) -> str:
    """Click a menu bar item in an application.

    Navigates the menu bar hierarchy and clicks the final item.

    Args:
        app_name: The process name (e.g. "Safari").
        menu_path: Menu path separated by " > " (e.g. "File > Save", "Edit > Find > Find...").
    """
    escaped_app = _escape_applescript_string(app_name)
    activate = _activate_block(app_name)
    parts = [p.strip() for p in menu_path.split(">")]

    if len(parts) < 2:
        return "ERROR: menu_path must have at least two parts (e.g. 'File > Save')"

    nav = 'menu bar item "' + _escape_applescript_string(parts[0]) + '" of menu bar 1'

    for i, part in enumerate(parts[1:], 1):
        escaped_part = _escape_applescript_string(part)
        parent_escaped = _escape_applescript_string(parts[i - 1])
        nav = f'menu item "{escaped_part}" of menu "{parent_escaped}" of {nav}'

    script = f'''
tell application "System Events"
    tell process "{escaped_app}"
{activate}        click {nav}
    end tell
end tell
return "Clicked menu: {_escape_applescript_string(menu_path)}"
'''
    return _run_applescript(script)


@mcp.tool()
def screenshot(app_name: str = "", full_screen: bool = False) -> str:
    """Capture a screenshot of a specific application window or the full screen.

    The screenshot is saved to /tmp/ with a timestamp in the filename.

    Args:
        app_name: The application name to capture. If empty and full_screen is False,
                  captures the frontmost window.
        full_screen: If True, capture the entire screen instead of a single window.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"/tmp/screenshot_{timestamp}.png"

    if full_screen:
        cmd = ["screencapture", "-x", filepath]
    elif app_name:
        escaped = _escape_applescript_string(app_name)
        # Combined: activate app and get window ID in a single JXA call
        window_id = None
        try:
            jxa_script = f'''
ObjC.import("CoreGraphics");
var app = Application("System Events");
var procs = app.processes.whose({{name: "{escaped}"}});
if (procs.length > 0) {{
    procs[0].frontmost = true;
    delay(0.15);
}}
var windows = ObjC.deepUnwrap(
    $.CGWindowListCopyWindowInfo($.kCGWindowListOptionOnScreenOnly, $.kCGNullWindowID)
);
var wid = "";
for (var i = 0; i < windows.length; i++) {{
    if (windows[i].kCGWindowOwnerName === "{escaped}") {{
        wid = String(windows[i].kCGWindowNumber);
        break;
    }}
}}
wid;
'''
            result = subprocess.run(
                ["osascript", "-l", "JavaScript", "-e", jxa_script],
                capture_output=True, text=True, timeout=10,
            )
            wid = result.stdout.strip()
            if wid and wid.isdigit():
                window_id = wid
        except Exception:
            # Fallback: activate via AppleScript
            try:
                _run_applescript(f'''
tell application "System Events"
    if exists process "{escaped}" then
        tell process "{escaped}"
            set frontmost to true
        end tell
        delay 0.15
    end if
end tell
''')
            except RuntimeError:
                pass

        if window_id:
            cmd = ["screencapture", "-x", "-l", window_id, filepath]
        else:
            cmd = ["screencapture", "-x", "-o", filepath]
    else:
        cmd = ["screencapture", "-x", "-o", filepath]

    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    except subprocess.TimeoutExpired:
        return "ERROR: screencapture timed out."

    if Path(filepath).exists():
        return f"Screenshot saved: {filepath}"
    else:
        return "ERROR: Screenshot file was not created. screencapture may have been cancelled."


@mcp.tool()
def fill_form(app_name: str, fields: dict[str, str], window_index: int = 1) -> str:
    """Fill multiple form fields in a single call. Much faster than calling
    type_text repeatedly, because all fields are found in one tree walk and
    filled in one AppleScript execution.

    Args:
        app_name: The process name (e.g. "JavaApplicationStub", "Safari").
        fields: A dictionary mapping field names to values, e.g.
                {"First Name": "John", "Last Name": "Doe", "Email": "john@example.com"}.
        window_index: Which window to target (1-based, default 1).
    """
    escaped_app = _escape_applescript_string(app_name)
    activate = _activate_block(app_name)

    # Build parallel lists for field names and values
    field_names_as = "{"
    field_values_as = "{"
    ordered_values = []
    for i, (field_name, field_value) in enumerate(fields.items()):
        escaped_name = _escape_applescript_string(field_name)
        escaped_value = _escape_applescript_string(field_value)
        ordered_values.append(field_value)
        if i > 0:
            field_names_as += ", "
            field_values_as += ", "
        field_names_as += f'"{escaped_name}"'
        field_values_as += f'"{escaped_value}"'
    field_names_as += "}"
    field_values_as += "}"

    # Single tree walk: collect all matching fields, then fill them
    # Uses a multi-tier fallback: set value → keystroke → clipboard paste → cliclick+paste
    script = f'''
on collectFields(parentElem, fieldNames, depth, resultList)
    if depth > 8 then return resultList
    try
        set children to UI elements of parentElem
    on error
        return resultList
    end try
    repeat with uiElem in children
        try
            set elemRole to role of uiElem
            if elemRole is "AXTextField" or elemRole is "AXTextArea" or elemRole is "AXComboBox" then
                set elemName to ""
                try
                    set elemName to name of uiElem
                end try
                if elemName is "" then
                    try
                        set elemName to description of uiElem
                    end try
                end if
                repeat with i from 1 to count of fieldNames
                    if elemName contains item i of fieldNames then
                        set end of resultList to {{uiElem, i}}
                    end if
                end repeat
            end if
        end try
        set resultList to my collectFields(uiElem, fieldNames, depth + 1, resultList)
    end repeat
    return resultList
end collectFields

on fillOneField(elem, targetValue, targetName)
    -- Tier 1: set value directly (fastest, works for most native fields)
    try
        set focused of elem to true
        set value of elem to targetValue
        delay 0.1
        set currentVal to ""
        try
            set currentVal to value of elem as text
        end try
        if currentVal is targetValue then
            return "OK: " & targetName
        end if
    end try
    -- Tier 2: focus + keystroke with longer delay (works for Java Swing)
    try
        set focused of elem to true
        delay 0.5
        keystroke "a" using command down
        delay 0.05
        key code 51
        delay 0.1
        keystroke targetValue
        delay 0.3
        set currentVal to ""
        try
            set currentVal to value of elem as text
        end try
        if currentVal is not "" then
            return "OK: " & targetName
        end if
    end try
    -- Tier 3: focus + clipboard paste (Cmd+V)
    try
        do shell script "echo -n " & quoted form of targetValue & " | pbcopy"
        set focused of elem to true
        delay 0.5
        keystroke "a" using command down
        delay 0.05
        keystroke "v" using command down
        delay 0.3
        return "OK: " & targetName
    end try
    -- Tier 4: cliclick at coordinates + clipboard paste
    try
        do shell script "echo -n " & quoted form of targetValue & " | pbcopy"
        set fieldPos to position of elem
        set fieldSize to size of elem
        set clickX to (item 1 of fieldPos) + ((item 1 of fieldSize) / 2) as integer
        set clickY to (item 2 of fieldPos) + ((item 2 of fieldSize) / 2) as integer
        do shell script "cliclick c:" & clickX & "," & clickY
        delay 0.5
        keystroke "a" using command down
        delay 0.05
        keystroke "v" using command down
        delay 0.3
        return "OK: " & targetName
    on error errMsg
        return "FAIL: " & targetName & " - " & errMsg
    end try
end fillOneField

tell application "System Events"
    tell process "{escaped_app}"
{activate}        set win to window {window_index}
        set fieldNames to {field_names_as}
        set fieldValues to {field_values_as}
        set output to ""
        set successCount to 0
        set failCount to 0

        -- Single tree walk to find all fields
        set foundFields to my collectFields(win, fieldNames, 0, {{}})

        -- Track which field names were found
        set foundIndices to {{}}
        repeat with pair in foundFields
            set elem to item 1 of pair
            set idx to item 2 of pair
            set targetValue to item idx of fieldValues
            set targetName to item idx of fieldNames
            set result to my fillOneField(elem, targetValue, targetName)
            if result starts with "OK:" then
                set successCount to successCount + 1
            else
                set failCount to failCount + 1
            end if
            set output to output & result & "\\n"
            set end of foundIndices to idx
        end repeat

        -- Report fields not found
        repeat with i from 1 to count of fieldNames
            if foundIndices does not contain i then
                set failCount to failCount + 1
                set output to output & "NOT FOUND: " & item i of fieldNames & "\\n"
            end if
        end repeat

        set output to output & "\\nFilled " & successCount & " of " & (successCount + failCount) & " fields."
        return output
    end tell
end tell
'''
    return _run_applescript(script, timeout=120)


@mcp.tool()
def click_at(x: int, y: int, click_type: str = "single") -> str:
    """Click at specific screen coordinates. Essential for Java Swing apps
    where UI elements are rendered on a canvas and not accessible as
    individual elements.

    Use get_ui_elements or read_element to find the position of an element,
    then click at those coordinates.

    Args:
        x: The x screen coordinate (in points, not pixels).
        y: The y screen coordinate (in points, not pixels).
        click_type: "single" for single click, "double" for double click,
                    "right" for right click. Default is "single".
    """
    # Check if cliclick is available
    cliclick_path = shutil.which("cliclick")
    if cliclick_path:
        cmd_map = {"single": "c", "double": "dc", "right": "rc"}
        cmd = cmd_map.get(click_type, "c")
        try:
            result = subprocess.run(
                [cliclick_path, f"{cmd}:{x},{y}"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return f"Clicked ({click_type}) at ({x}, {y})"
            # Fall through to AppleScript
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    # Fallback: AppleScript click at coordinates
    if click_type == "double":
        script = f'''
tell application "System Events"
    click at {{{x}, {y}}}
    delay 0.05
    click at {{{x}, {y}}}
end tell
return "Double-clicked at ({x}, {y})"
'''
    elif click_type == "right":
        script = f'''
tell application "System Events"
    key down control
    click at {{{x}, {y}}}
    key up control
end tell
return "Right-clicked at ({x}, {y})"
'''
    else:
        script = f'''
tell application "System Events"
    click at {{{x}, {y}}}
end tell
return "Clicked at ({x}, {y})"
'''
    return _run_applescript(script)


def main():
    """Entry point for the mac-use CLI."""
    mcp.run()


if __name__ == "__main__":
    main()
