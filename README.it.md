# mac-use

🌐 [English](README.md) | [Español](README.es.md) | [Français](README.fr.md) | [Italiano](README.it.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**Automatizza il tuo lavoro al computer. Lascia che l'IA clicchi, digiti e legga qualsiasi app macOS.**

---

## Cos'e mac-use?

mac-use e un server [MCP (Model Context Protocol)](https://modelcontextprotocol.io) che da agli assistenti IA il controllo diretto su qualsiasi applicazione macOS attraverso l'API nativa di Accessibilita.

Invece di fare screenshot e indovinare dove cliccare in base alle coordinate dei pixel (come [Anthropic's computer use](https://docs.anthropic.com/en/docs/agents-and-tools/computer-use)), mac-use legge l'albero reale degli elementi di interfaccia di qualsiasi applicazione usando macOS System Events e AppleScript. Conosce i nomi, i tipi e la gerarchia di ogni pulsante, campo di testo, voce di menu, checkbox ed etichetta nell'applicazione. Puo cliccare sugli elementi per nome, leggere i loro valori, digitare nei campi, navigare i menu e premere scorciatoie da tastiera -- il tutto attraverso l'interfaccia di accessibilita strutturata che macOS fornisce alle tecnologie assistive.

Pensalo come **Playwright per le app desktop**: preciso e affidabile perche opera sulla struttura reale dell'interfaccia piuttosto che su un'approssimazione visiva.

## Confronto con Anthropic Computer Use

| | mac-use | Anthropic Computer Use |
|---|---|---|
| **Comprensione della UI** | Albero di elementi strutturato (nomi, ruoli, gerarchia) | Screenshot (analisi dei pixel) |
| **Selezione degli elementi** | Per nome, ruolo o percorso (es. "click button Save") | Per coordinate pixel (es. "click at 340, 520") |
| **Velocita** | Chiamate API dirette, nessuna elaborazione di immagini | Richiede cattura dello schermo e modello di visione per ogni azione |
| **Precisione** | Esatta -- gli elementi vengono identificati senza ambiguita | Approssimativa -- le coordinate possono mancare il bersaglio, soprattutto dopo cambiamenti di layout |
| **Costo** | Minimo -- chiamate di strumenti solo testo | Costoso -- ogni azione richiede una chiamata al modello di visione |
| **Indipendenza dalla risoluzione** | Funziona a qualsiasi scala di visualizzazione | Sensibile alla risoluzione e al ridimensionamento |
| **Piattaforma** | Solo macOS | Multipiattaforma |
| **Requisiti** | Permessi di accessibilita | Permessi di registrazione schermo |

## Passi ore a cliccare su app che non comunicano tra loro

Conosci la storia. Copia da questa app, incolla in quella. Clicca su 14 schermate per inviare un modulo. Esporta in CSV -- ah no, non c'e l'esportazione. Ricomincia domani.

Un impiegato ha [automatizzato il suo lavoro amministrativo ed e diventato virale](https://reddit.com/r/BestofRedditorUpdates/comments/1s23k0o/facing_disciplinary_investigation_sack_for/) (2.300+ upvotes) -- non perche fosse tecnicamente impressionante, ma perche *tutti hanno riconosciuto il dolore*. Nella sanita, il problema e cosi grave che ha un nome: ["Death by 1,000 Clicks"](https://reddit.com/r/programming/comments/bcr3g5/bad_software_can_kill_death_by_1000_clicks_where/) (1.900+ upvotes) -- medici che passano piu tempo a navigare software di cartelle cliniche che a curare i pazienti, con l'affaticamento da interfaccia che causa letteralmente errori medici.

Queste app non hanno API. Non hanno CLI. Non hanno esportazione. Solo un'interfaccia grafica davanti alla quale qualcuno deve sedersi e cliccare. Fino ad ora.

mac-use permette a un agente IA di guidare qualsiasi applicazione macOS nello stesso modo in cui lo farebbe un umano -- senza errori e 24/7. Se puoi vederlo sullo schermo, mac-use puo leggerlo, cliccarlo e digitarci dentro.

### Cosa stanno automatizzando le persone

- **Software fiscale e governativo** -- compilare dichiarazioni dei redditi in app desktop come eTax o ELSTER che non offrono API, ne scripting, solo moduli
- **Contabilita e app aziendali** -- inserire dati in GnuCash, QuickBooks Desktop, SAP GUI o qualsiasi software aziendale legacy
- **Inserimento dati tra app** -- spostare dati tra applicazioni senza copia-incolla. Scansionare un'email di spedizione, estrarre il numero di tracciamento, inserirlo nel tuo software di ricezione. C'e un intero [mercato di freelancer che paga $0.50/attivita](https://reddit.com/r/freelance_forhire/comments/1kxjxgj/hiring_paypertask_050_100_for_2_minute_copypaste/) per questo tipo di lavoro (856 candidati)
- **Estrazione dati da app bloccate** -- esportare la tua [cronologia iMessage](https://reddit.com/r/applesucks/comments/1s1avhv/you_cannot_export_your_own_imessage_history_in/) che Apple non ti lascia esportare, estrarre transazioni da app bancarie, leggere dashboard in app Java legacy
- **Software hardware e fornitori** -- configurare app come Logitech G Hub che hanno [una UX terribile e nessuna alternativa](https://reddit.com/r/LogitechG/comments/1ll327d/why_logitech_g_hub_is_the_worst_software/)
- **QA e test di accessibilita** -- testare app macOS native, verificare gli stati degli elementi, controllare se i pulsanti hanno etichette appropriate

### Perche non AppleScript o Shortcuts?

Apple ha [sciolto il team AppleScript](https://reddit.com/r/Automator/comments/1fuwaby/automator_applescript_or_any_other_macos_ideas/). Automator e deprecato. Shortcuts su Mac e [fatto a meta](https://reddit.com/r/shortcuts/comments/1pxpbd2/finally_dynamic_homekit_control_in_siri_shortcuts/). L'intero stack di automazione macOS e in declino.

mac-use usa il livello API di Accessibilita che Apple mantiene attivamente (e obbligatorio per la conformita alle norme sull'accessibilita). Non serve che le app espongano azioni Shortcuts o dizionari AppleScript. Se l'app ha una finestra, mac-use puo controllarla.

## Avvio rapido

### Installare con pip (consigliato)

```bash
pip install mac-use
mac-use
```

### Oppure installare con uvx

```bash
uvx mac-use
```

### Configurare in Claude Code

Aggiungi alla tua configurazione MCP di Claude Code (`~/.claude.json`):

```json
{
  "mcpServers": {
    "mac-use": {
      "command": "mac-use"
    }
  }
}
```

Se usi uvx:

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

### Concedere i permessi di Accessibilita

mac-use richiede l'accesso di Accessibilita per leggere e interagire con gli elementi di interfaccia delle applicazioni.

1. Apri **Impostazioni di Sistema** (o Preferenze di Sistema nelle versioni precedenti di macOS)
2. Vai su **Privacy e sicurezza > Accessibilita**
3. Aggiungi e abilita la tua applicazione terminale (Terminal, iTerm2, Ghostty, ecc.) o il processo Claude Code

Senza questo permesso, tutti gli strumenti restituiranno un errore "assistive access denied".

## Strumenti

### list_windows

Elenca tutte le finestre delle applicazioni aperte con i nomi dei processi, gli indici delle finestre e i titoli.

```
list_windows()
```

Questa e tipicamente la tua prima chiamata -- ti indica il nome esatto del processo da usare con gli altri strumenti. Questo e particolarmente importante per le applicazioni Java (come eTax) che possono apparire come "JavaApplicationStub" invece del loro nome visualizzato.

### get_ui_elements

Ottiene l'albero completo degli elementi di interfaccia di una finestra dell'applicazione. Restituisce tipi di elementi, nomi, valori e i loro percorsi nella gerarchia.

```
get_ui_elements(app_name="Safari")
get_ui_elements(app_name="Finder", window_index=2, max_depth=3)
get_ui_elements(app_name="JavaApplicationStub", filter_roles="AXTextField,AXButton,AXCheckBox")
```

Usa `filter_roles` per restituire solo tipi di elementi specifici -- drasticamente piu veloce su app complesse come Java Swing, dove un dump completo dell'albero puo richiedere 10-30 secondi.

### click_element

Clicca su un pulsante, checkbox o qualsiasi altro elemento interattivo. Supporta due modalita:

**Modalita percorso** -- usa un percorso di elemento AppleScript:
```
click_element(app_name="Safari", element_description="button 2 of group 1 of window 1")
```

**Modalita ricerca per nome** -- trova e clicca per nome (con prefisso di tipo opzionale):
```
click_element(app_name="Finder", element_description="New Folder")
click_element(app_name="Safari", element_description="button:Downloads")
click_element(app_name="TextEdit", element_description="checkbox:Wrap to Page")
```

### type_text

Digita testo in un campo. Digita nel campo attualmente selezionato, o punta a un campo specifico per nome.

```
type_text(app_name="Safari", text="https://example.com", field_name="Address and Search")
type_text(app_name="TextEdit", text="Hello, world!")
```

### read_element

Legge il valore, nome, ruolo e stato di qualsiasi elemento di interfaccia.

```
read_element(app_name="Safari", element_description="text field 1 of window 1")
read_element(app_name="Calculator", element_description="Display")
```

### activate_app

Porta un'applicazione in primo piano.

```
activate_app(app_name="Finder")
```

### press_key

Preme un tasto o una scorciatoia da tastiera.

```
press_key(key="return")
press_key(key="s", modifiers="command")
press_key(key="f", modifiers="command,shift")
press_key(key="tab")
press_key(key="down arrow")
```

### menu_action

Clicca su una voce della barra dei menu per percorso.

```
menu_action(app_name="TextEdit", menu_path="File > Save")
menu_action(app_name="Safari", menu_path="File > New Window")
menu_action(app_name="Finder", menu_path="Edit > Select All")
```

### fill_form

Compila piu campi di un modulo in una singola chiamata. Invece di un viaggio di andata e ritorno per campo, tutti i campi vengono compilati in un'unica esecuzione -- significativamente piu veloce per attivita di inserimento dati come moduli fiscali o creazione di account.

```
fill_form(app_name="JavaApplicationStub", fields={
    "First Name": "John",
    "Last Name": "Doe",
    "Email": "john@example.com",
    "Phone": "+1 555 0123"
})
```

### screenshot

Cattura uno screenshot di una finestra specifica dell'app o dell'intero schermo. Salva in `/tmp/` e restituisce il percorso del file.

```
screenshot(app_name="Safari")
screenshot(full_screen=True)
```

## Requisiti

- **macOS** (qualsiasi versione recente -- Ventura, Sonoma, Sequoia)
- **Python 3.10+**
- **Permessi di accessibilita** concessi al processo chiamante (vedi Avvio rapido qui sopra)

Nessuna dipendenza esterna oltre al pacchetto Python `mcp`. Tutta l'interazione con macOS avviene tramite il comando integrato `osascript`.

## Sviluppo

```bash
git clone https://github.com/entpnomad/mac-use.git
cd mac-use
pip install -e .
mac-use
```

## Licenza

MIT -- vedi [LICENSE](LICENSE).

## Autore

[entpnomad](https://github.com/entpnomad)
