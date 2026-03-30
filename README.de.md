# mac-use

🌐 [English](README.md) | [Español](README.es.md) | [Français](README.fr.md) | [Italiano](README.it.md) | [Português](README.pt.md) | [Deutsch](README.de.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**Automatisiere deinen Desktop-Job. Lass KI in jeder macOS-App klicken, tippen und lesen.**

---

## Was ist mac-use?

mac-use ist ein [MCP (Model Context Protocol)](https://modelcontextprotocol.io) Server, der KI-Assistenten direkte Kontrolle ueber jede macOS-Anwendung ueber die native Accessibility API gibt.

Statt Screenshots zu machen und anhand von Pixel-Koordinaten zu raten, wo geklickt werden soll (wie bei [Anthropic's computer use](https://docs.anthropic.com/en/docs/agents-and-tools/computer-use)), liest mac-use den tatsaechlichen UI-Element-Baum jeder Anwendung ueber macOS System Events und AppleScript. Es kennt die Namen, Typen und Hierarchie jedes Buttons, Textfelds, Menuepunkts, Kontrollkaestchens und Labels in der Zielanwendung. Es kann Elemente per Name anklicken, ihre Werte lesen, in Felder tippen, durch Menues navigieren und Tastenkombinationen druecken -- alles ueber die strukturierte Accessibility-Schnittstelle, die macOS fuer assistive Technologien bereitstellt.

Stell es dir vor wie **Playwright fuer Desktop-Apps**: praezise und zuverlaessig, weil es auf der echten UI-Struktur arbeitet statt auf visueller Annaeherung.

## Vergleich mit Anthropic Computer Use

| | mac-use | Anthropic Computer Use |
|---|---|---|
| **UI-Verstaendnis** | Strukturierter Element-Baum (Namen, Rollen, Hierarchie) | Screenshots (Pixel-Analyse) |
| **Element-Targeting** | Per Name, Rolle oder Pfad (z.B. "click button Save") | Per Pixel-Koordinaten (z.B. "click at 340, 520") |
| **Geschwindigkeit** | Direkte API-Aufrufe, keine Bildverarbeitung | Erfordert Screenshot-Aufnahme und Vision-Modell pro Aktion |
| **Genauigkeit** | Exakt -- Elemente werden eindeutig identifiziert | Ungefaehr -- Koordinaten koennen daneben liegen, besonders nach Layout-Aenderungen |
| **Kosten** | Minimal -- reine Text-Tool-Aufrufe | Teuer -- jede Aktion erfordert einen Vision-Modell-Aufruf |
| **Aufloesungsunabhaengigkeit** | Funktioniert bei jeder Display-Skalierung | Empfindlich gegenueber Aufloesung und Skalierung |
| **Plattform** | Nur macOS | Plattformuebergreifend |
| **Voraussetzungen** | Accessibility-Berechtigungen | Bildschirmaufnahme-Berechtigungen |

## Du verbringst Stunden damit, durch Apps zu klicken, die nicht miteinander reden

Du kennst das Spiel. Aus dieser App kopieren, in jene einfuegen. Durch 14 Bildschirme klicken, um ein Formular abzuschicken. Als CSV exportieren -- ach Moment, es gibt keinen Export. Morgen das Ganze nochmal.

Ein Bueroangestellter hat [seine Admin-Arbeit automatisiert und es ging viral](https://reddit.com/r/BestofRedditorUpdates/comments/1s23k0o/facing_disciplinary_investigation_sack_for/) (2.300+ Upvotes) -- nicht weil es technisch beeindruckend war, sondern weil *jeder den Schmerz kannte*. Im Gesundheitswesen ist das Problem so schlimm, dass es einen Namen hat: ["Death by 1,000 Clicks"](https://reddit.com/r/programming/comments/bcr3g5/bad_software_can_kill_death_by_1000_clicks_where/) (1.900+ Upvotes) -- Aerzte verbringen mehr Zeit mit der Navigation durch EHR-Software als mit der Behandlung von Patienten, wobei die UI-Ermuedung buchstaeblich zu medizinischen Fehlern fuehrt.

Diese Apps haben keine API. Kein CLI. Keinen Export. Nur eine GUI, vor der sich jemand hinsetzen und durchklicken muss. Bis jetzt.

mac-use laesst einen KI-Agenten jede macOS-Anwendung genauso bedienen wie ein Mensch -- ohne Fehler und rund um die Uhr. Wenn du es auf dem Bildschirm sehen kannst, kann mac-use es lesen, anklicken und hineintippen.

### Was Leute automatisieren

- **Steuer- und Behoerden-Software** -- Steuererklaerungen in Desktop-Apps wie eTax oder ELSTER ausfuellen, die keine API bieten, kein Scripting, nur Formulare
- **Buchhaltung und Unternehmens-Apps** -- Daten in GnuCash, QuickBooks Desktop, SAP GUI oder jede andere Legacy-Business-Software eingeben
- **Dateneingabe zwischen Apps** -- Daten zwischen Anwendungen verschieben ohne Kopieren und Einfuegen. Eine Versand-E-Mail scannen, die Trackingnummer extrahieren, sie in deine Wareneingangssoftware eintragen. Es gibt einen ganzen [Freelancer-Markt, der $0.50/Aufgabe zahlt](https://reddit.com/r/freelance_forhire/comments/1kxjxgj/hiring_paypertask_050_100_for_2_minute_copypaste/) fuer diese Art von Arbeit (856 Bewerber)
- **Datenextraktion aus gesperrten Apps** -- deinen [iMessage-Verlauf](https://reddit.com/r/applesucks/comments/1s1avhv/you_cannot_export_your_own_imessage_history_in/) exportieren, den Apple nicht exportieren laesst, Transaktionen aus Banking-Apps ziehen, Dashboards in Legacy-Java-Apps auslesen
- **Hardware- und Hersteller-Software** -- Apps wie Logitech G Hub konfigurieren, die eine [furchtbare UX und keine Alternative](https://reddit.com/r/LogitechG/comments/1ll327d/why_logitech_g_hub_is_the_worst_software/) haben
- **QA und Accessibility-Tests** -- native macOS-Apps testen, Element-Zustaende ueberpruefen, pruefen ob Buttons korrekte Labels haben

### Warum nicht AppleScript oder Shortcuts?

Apple hat [das AppleScript-Team aufgeloest](https://reddit.com/r/Automator/comments/1fuwaby/automator_applescript_or_any_other_macos_ideas/). Automator ist veraltet. Shortcuts auf dem Mac ist [halbfertig](https://reddit.com/r/shortcuts/comments/1pxpbd2/finally_dynamic_homekit_control_in_siri_shortcuts/). Der gesamte macOS-Automatisierungs-Stack verfaellt.

mac-use nutzt die Accessibility-API-Schicht, die Apple aktiv pflegt (sie ist fuer die Einhaltung der Barrierefreiheit vorgeschrieben). Apps muessen keine Shortcuts-Aktionen oder AppleScript-Woerterbuecher bereitstellen. Wenn die App ein Fenster hat, kann mac-use sie steuern.

## Schnellstart

### Mit pip installieren (empfohlen)

```bash
pip install mac-use
mac-use
```

### Oder mit uvx installieren

```bash
uvx mac-use
```

### In Claude Code konfigurieren

Fuege dies zu deiner Claude Code MCP-Konfiguration hinzu (`~/.claude.json`):

```json
{
  "mcpServers": {
    "mac-use": {
      "command": "mac-use"
    }
  }
}
```

Wenn du stattdessen uvx verwendest:

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

### Accessibility-Berechtigungen erteilen

mac-use benoetigt Accessibility-Zugriff, um UI-Elemente von Anwendungen lesen und damit interagieren zu koennen.

1. Oeffne **Systemeinstellungen** (oder Systemeinstellungen bei aelteren macOS-Versionen)
2. Gehe zu **Datenschutz & Sicherheit > Bedienungshilfen**
3. Fuege deine Terminal-Anwendung hinzu und aktiviere sie (Terminal, iTerm2, Ghostty, etc.) oder den Claude Code Prozess

Ohne diese Berechtigung geben alle Tools einen "assistive access denied"-Fehler zurueck.

## Tools

### list_windows

Listet alle offenen Anwendungsfenster mit ihren Prozessnamen, Fenster-Indizes und Titeln auf.

```
list_windows()
```

Das ist typischerweise dein erster Aufruf -- er sagt dir den genauen Prozessnamen fuer die Verwendung mit anderen Tools. Das ist besonders wichtig bei Java-Anwendungen (wie eTax), die als "JavaApplicationStub" statt ihres Anzeigenamens erscheinen koennen.

### get_ui_elements

Holt den vollstaendigen UI-Element-Baum eines Anwendungsfensters. Gibt Element-Typen, Namen, Werte und ihre Pfade in der Hierarchie zurueck.

```
get_ui_elements(app_name="Safari")
get_ui_elements(app_name="Finder", window_index=2, max_depth=3)
get_ui_elements(app_name="JavaApplicationStub", filter_roles="AXTextField,AXButton,AXCheckBox")
```

Verwende `filter_roles`, um nur bestimmte Element-Typen zurueckzugeben -- drastisch schneller bei komplexen Apps wie Java Swing, wo ein vollstaendiger Baum-Dump 10-30 Sekunden dauern kann.

### click_element

Klickt auf einen Button, ein Kontrollkaestchen oder jedes andere interaktive Element. Unterstuetzt zwei Modi:

**Pfad-Modus** -- verwende einen AppleScript-Element-Pfad:
```
click_element(app_name="Safari", element_description="button 2 of group 1 of window 1")
```

**Namenssuche-Modus** -- finde und klicke per Name (mit optionalem Typ-Praefix):
```
click_element(app_name="Finder", element_description="New Folder")
click_element(app_name="Safari", element_description="button:Downloads")
click_element(app_name="TextEdit", element_description="checkbox:Wrap to Page")
```

### type_text

Tippt Text in ein Feld. Tippt in das aktuell fokussierte Feld oder zielt auf ein bestimmtes Feld per Name.

```
type_text(app_name="Safari", text="https://example.com", field_name="Address and Search")
type_text(app_name="TextEdit", text="Hello, world!")
```

### read_element

Liest den Wert, Namen, die Rolle und den Zustand eines beliebigen UI-Elements.

```
read_element(app_name="Safari", element_description="text field 1 of window 1")
read_element(app_name="Calculator", element_description="Display")
```

### activate_app

Bringt eine Anwendung in den Vordergrund.

```
activate_app(app_name="Finder")
```

### press_key

Drueckt eine Taste oder Tastenkombination.

```
press_key(key="return")
press_key(key="s", modifiers="command")
press_key(key="f", modifiers="command,shift")
press_key(key="tab")
press_key(key="down arrow")
```

### menu_action

Klickt auf einen Menueleisten-Eintrag per Pfad.

```
menu_action(app_name="TextEdit", menu_path="File > Save")
menu_action(app_name="Safari", menu_path="File > New Window")
menu_action(app_name="Finder", menu_path="Edit > Select All")
```

### fill_form

Fuellt mehrere Formularfelder in einem einzigen Aufruf aus. Statt eines Roundtrips pro Feld werden alle Felder in einer Ausfuehrung ausgefuellt -- deutlich schneller fuer Dateneingabe-Aufgaben wie Steuerformulare oder Kontoerstellung.

```
fill_form(app_name="JavaApplicationStub", fields={
    "First Name": "John",
    "Last Name": "Doe",
    "Email": "john@example.com",
    "Phone": "+1 555 0123"
})
```

### screenshot

Macht einen Screenshot eines bestimmten App-Fensters oder des gesamten Bildschirms. Speichert unter `/tmp/` und gibt den Dateipfad zurueck.

```
screenshot(app_name="Safari")
screenshot(full_screen=True)
```

## Voraussetzungen

- **macOS** (jede aktuelle Version -- Ventura, Sonoma, Sequoia)
- **Python 3.10+**
- **Accessibility-Berechtigungen** fuer den aufrufenden Prozess erteilt (siehe Schnellstart oben)

Keine externen Abhaengigkeiten ausser dem Python-Paket `mcp`. Die gesamte macOS-Interaktion erfolgt ueber den integrierten Befehl `osascript`.

## Entwicklung

```bash
git clone https://github.com/entpnomad/mac-use.git
cd mac-use
pip install -e .
mac-use
```

## Lizenz

MIT -- siehe [LICENSE](LICENSE).

## Autor

[entpnomad](https://github.com/entpnomad)
