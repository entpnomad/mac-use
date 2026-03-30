# mac-use

🌐 [English](README.md) | [Español](README.es.md) | [Français](README.fr.md) | [Italiano](README.it.md) | [Português](README.pt.md) | [Deutsch](README.de.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**Automatisez votre travail de bureau. Laissez l'IA cliquer, taper et lire n'importe quelle app macOS.**

---

## Qu'est-ce que mac-use ?

mac-use est un serveur [MCP (Model Context Protocol)](https://modelcontextprotocol.io) qui donne aux assistants IA le controle direct sur n'importe quelle application macOS via l'API native d'Accessibilite.

Au lieu de prendre des captures d'ecran et de deviner ou cliquer a partir de coordonnees de pixels (comme [Anthropic's computer use](https://docs.anthropic.com/en/docs/agents-and-tools/computer-use)), mac-use lit l'arbre reel des elements d'interface de n'importe quelle application en utilisant macOS System Events et AppleScript. Il connait les noms, types et la hierarchie de chaque bouton, champ de texte, element de menu, case a cocher et etiquette dans l'application cible. Il peut cliquer sur des elements par nom, lire leurs valeurs, taper dans des champs, naviguer dans les menus et utiliser des raccourcis clavier -- le tout via l'interface d'accessibilite structuree que macOS fournit aux technologies d'assistance.

Voyez-le comme **Playwright pour les apps de bureau** : precis et fiable parce qu'il opere sur la vraie structure de l'interface plutot que sur une approximation visuelle.

## Comparaison avec Anthropic Computer Use

| | mac-use | Anthropic Computer Use |
|---|---|---|
| **Comprehension de l'UI** | Arbre d'elements structure (noms, roles, hierarchie) | Captures d'ecran (analyse de pixels) |
| **Ciblage des elements** | Par nom, role ou chemin (ex. "click button Save") | Par coordonnees de pixels (ex. "click at 340, 520") |
| **Vitesse** | Appels API directs, pas de traitement d'image | Necessite une capture d'ecran et un modele de vision par action |
| **Precision** | Exacte -- les elements sont identifies sans ambiguite | Approximative -- les coordonnees peuvent manquer leur cible, surtout apres des changements de mise en page |
| **Cout** | Minimal -- appels d'outils en texte seul | Couteux -- chaque action necessite un appel au modele de vision |
| **Independance de resolution** | Fonctionne a n'importe quelle echelle d'affichage | Sensible a la resolution et au redimensionnement |
| **Plateforme** | macOS uniquement | Multiplateforme |
| **Prerequis** | Permissions d'accessibilite | Permissions d'enregistrement d'ecran |

## Vous passez des heures a cliquer dans des apps qui ne se parlent pas

Vous connaissez la chanson. Copier depuis cette app, coller dans celle-la. Cliquer sur 14 ecrans pour soumettre un formulaire. Exporter en CSV -- ah non, il n'y a pas d'export. Recommencer demain.

Un employe de bureau a [automatise son travail administratif et c'est devenu viral](https://reddit.com/r/BestofRedditorUpdates/comments/1s23k0o/facing_disciplinary_investigation_sack_for/) (2 300+ upvotes) -- non pas parce que c'etait techniquement impressionnant, mais parce que *tout le monde a reconnu la galere*. Dans la sante, le probleme est si grave qu'il a un nom : ["Death by 1,000 Clicks"](https://reddit.com/r/programming/comments/bcr3g5/bad_software_can_kill_death_by_1000_clicks_where/) (1 900+ upvotes) -- des medecins qui passent plus de temps a naviguer dans les logiciels de dossiers medicaux qu'a soigner leurs patients, la fatigue d'interface causant litteralement des erreurs medicales.

Ces apps n'ont pas d'API. Pas de CLI. Pas d'export. Juste une interface graphique devant laquelle quelqu'un doit s'asseoir et cliquer. Jusqu'a maintenant.

mac-use permet a un agent IA de piloter n'importe quelle application macOS de la meme facon qu'un humain le ferait -- sans erreurs et 24h/24. Si vous pouvez le voir a l'ecran, mac-use peut le lire, cliquer dessus et y taper du texte.

### Ce que les gens automatisent

- **Logiciels fiscaux et gouvernementaux** -- remplir des declarations d'impots dans des apps de bureau comme eTax ou ELSTER qui n'offrent ni API, ni scripting, juste des formulaires
- **Comptabilite et apps d'entreprise** -- saisir des donnees dans GnuCash, QuickBooks Desktop, SAP GUI ou n'importe quel logiciel d'entreprise historique
- **Saisie de donnees entre apps** -- deplacer des donnees entre applications sans copier-coller. Scanner un email d'expedition, extraire le numero de suivi, le remplir dans votre logiciel de reception. Il existe tout un [marche de freelances payant $0.50/tache](https://reddit.com/r/freelance_forhire/comments/1kxjxgj/hiring_paypertask_050_100_for_2_minute_copypaste/) pour ce type de travail (856 candidats)
- **Extraction de donnees d'apps verrouillees** -- exporter votre [historique iMessage](https://reddit.com/r/applesucks/comments/1s1avhv/you_cannot_export_your_own_imessage_history_in/) qu'Apple ne vous laisse pas exporter, recuperer des transactions depuis des apps bancaires, lire des tableaux de bord dans des apps Java historiques
- **Logiciels materiel et fournisseurs** -- configurer des apps comme Logitech G Hub qui ont [une UX horrible et aucune alternative](https://reddit.com/r/LogitechG/comments/1ll327d/why_logitech_g_hub_is_the_worst_software/)
- **QA et tests d'accessibilite** -- tester des apps macOS natives, verifier les etats des elements, auditer si les boutons ont des etiquettes correctes

### Pourquoi pas AppleScript ou Shortcuts ?

Apple a [dissous l'equipe AppleScript](https://reddit.com/r/Automator/comments/1fuwaby/automator_applescript_or_any_other_macos_ideas/). Automator est deprecie. Shortcuts sur Mac est [bancal](https://reddit.com/r/shortcuts/comments/1pxpbd2/finally_dynamic_homekit_control_in_siri_shortcuts/). Toute la pile d'automatisation macOS est en declin.

mac-use utilise la couche API d'Accessibilite qu'Apple maintient activement (c'est obligatoire pour la conformite handicap). Pas besoin que les apps exposent des actions Shortcuts ou des dictionnaires AppleScript. Si l'app a une fenetre, mac-use peut la controler.

## Demarrage rapide

### Installer avec pip (recommande)

```bash
pip install mac-use
mac-use
```

### Ou installer avec uvx

```bash
uvx mac-use
```

### Configurer dans Claude Code

Ajoutez a votre configuration MCP de Claude Code (`~/.claude.json`) :

```json
{
  "mcpServers": {
    "mac-use": {
      "command": "mac-use"
    }
  }
}
```

Si vous utilisez uvx :

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

### Accorder les permissions d'Accessibilite

mac-use necessite l'acces Accessibilite pour lire et interagir avec les elements d'interface des applications.

1. Ouvrez **Reglages du systeme** (ou Preferences Systeme sur les anciennes versions de macOS)
2. Allez dans **Confidentialite et securite > Accessibilite**
3. Ajoutez et activez votre application de terminal (Terminal, iTerm2, Ghostty, etc.) ou le processus Claude Code

Sans cette permission, tous les outils retourneront une erreur "assistive access denied".

## Outils

### list_windows

Liste toutes les fenetres d'application ouvertes avec leurs noms de processus, indices de fenetre et titres.

```
list_windows()
```

C'est generalement votre premier appel -- il vous indique le nom exact du processus a utiliser avec les autres outils. C'est particulierement important pour les applications Java (comme eTax) qui peuvent apparaitre comme "JavaApplicationStub" au lieu de leur nom affiche.

### get_ui_elements

Obtient l'arbre complet des elements d'interface d'une fenetre d'application. Retourne les types d'elements, noms, valeurs et leurs chemins dans la hierarchie.

```
get_ui_elements(app_name="Safari")
get_ui_elements(app_name="Finder", window_index=2, max_depth=3)
get_ui_elements(app_name="JavaApplicationStub", filter_roles="AXTextField,AXButton,AXCheckBox")
```

Utilisez `filter_roles` pour ne retourner que des types d'elements specifiques -- considerablement plus rapide sur les apps complexes comme Java Swing, ou un dump complet de l'arbre peut prendre 10-30 secondes.

### click_element

Clique sur un bouton, une case a cocher ou tout autre element interactif. Supporte deux modes :

**Mode chemin** -- utilise un chemin d'element AppleScript :
```
click_element(app_name="Safari", element_description="button 2 of group 1 of window 1")
```

**Mode recherche par nom** -- trouve et clique par nom (avec prefixe de type optionnel) :
```
click_element(app_name="Finder", element_description="New Folder")
click_element(app_name="Safari", element_description="button:Downloads")
click_element(app_name="TextEdit", element_description="checkbox:Wrap to Page")
```

### type_text

Tape du texte dans un champ. Tape dans le champ actuellement selectionne, ou cible un champ specifique par nom.

```
type_text(app_name="Safari", text="https://example.com", field_name="Address and Search")
type_text(app_name="TextEdit", text="Hello, world!")
```

### read_element

Lit la valeur, le nom, le role et l'etat de n'importe quel element d'interface.

```
read_element(app_name="Safari", element_description="text field 1 of window 1")
read_element(app_name="Calculator", element_description="Display")
```

### activate_app

Met une application au premier plan.

```
activate_app(app_name="Finder")
```

### press_key

Appuie sur une touche ou un raccourci clavier.

```
press_key(key="return")
press_key(key="s", modifiers="command")
press_key(key="f", modifiers="command,shift")
press_key(key="tab")
press_key(key="down arrow")
```

### menu_action

Clique sur un element de la barre de menu par chemin.

```
menu_action(app_name="TextEdit", menu_path="File > Save")
menu_action(app_name="Safari", menu_path="File > New Window")
menu_action(app_name="Finder", menu_path="Edit > Select All")
```

### fill_form

Remplit plusieurs champs de formulaire en un seul appel. Au lieu d'un aller-retour par champ, tous les champs sont remplis en une seule execution -- nettement plus rapide pour les taches de saisie de donnees comme les formulaires fiscaux ou la creation de comptes.

```
fill_form(app_name="JavaApplicationStub", fields={
    "First Name": "John",
    "Last Name": "Doe",
    "Email": "john@example.com",
    "Phone": "+1 555 0123"
})
```

### screenshot

Capture une capture d'ecran d'une fenetre d'app specifique ou de l'ecran complet. Sauvegarde dans `/tmp/` et retourne le chemin du fichier.

```
screenshot(app_name="Safari")
screenshot(full_screen=True)
```

## Prerequis

- **macOS** (toute version recente -- Ventura, Sonoma, Sequoia)
- **Python 3.10+**
- **Permissions d'accessibilite** accordees au processus appelant (voir Demarrage rapide ci-dessus)

Aucune dependance externe au-dela du package Python `mcp`. Toute l'interaction avec macOS se fait via la commande integree `osascript`.

## Developpement

```bash
git clone https://github.com/entpnomad/mac-use.git
cd mac-use
pip install -e .
mac-use
```

## Licence

MIT -- voir [LICENSE](LICENSE).

## Auteur

[entpnomad](https://github.com/entpnomad)
