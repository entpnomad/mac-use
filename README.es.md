# mac-use

🌐 [English](README.md) | [Español](README.es.md) | [Français](README.fr.md) | [Italiano](README.it.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**Automatiza tu trabajo de escritorio. Deja que la IA haga clic, escriba y lea cualquier app de macOS.**

---

## ¿Qué es mac-use?

mac-use es un servidor [MCP (Model Context Protocol)](https://modelcontextprotocol.io) que da a los asistentes de IA control directo sobre cualquier aplicación de macOS a través de la API nativa de Accesibilidad.

En lugar de hacer capturas de pantalla y adivinar dónde hacer clic según coordenadas de píxeles (como [Anthropic's computer use](https://docs.anthropic.com/en/docs/agents-and-tools/computer-use)), mac-use lee el árbol real de elementos de interfaz de cualquier aplicación usando macOS System Events y AppleScript. Conoce los nombres, tipos y jerarquía de cada botón, campo de texto, elemento de menú, checkbox y etiqueta en la aplicación. Puede hacer clic en elementos por nombre, leer sus valores, escribir en campos, navegar menús y pulsar atajos de teclado -- todo a través de la interfaz de accesibilidad estructurada que macOS proporciona a las tecnologías de asistencia.

Piensa en ello como **Playwright para apps de escritorio**: preciso y fiable porque opera sobre la estructura real de la interfaz, no sobre aproximación visual.

## Cómo se compara con Anthropic Computer Use

| | mac-use | Anthropic Computer Use |
|---|---|---|
| **Comprensión de la UI** | Árbol de elementos estructurado (nombres, roles, jerarquía) | Capturas de pantalla (análisis de píxeles) |
| **Selección de elementos** | Por nombre, rol o ruta (ej. "click button Save") | Por coordenadas de píxeles (ej. "click at 340, 520") |
| **Velocidad** | Llamadas directas a la API, sin procesamiento de imagen | Requiere captura de pantalla y modelo de visión por acción |
| **Precisión** | Exacta -- los elementos se identifican sin ambigüedad | Aproximada -- las coordenadas pueden fallar, especialmente tras cambios de diseño |
| **Coste** | Mínimo -- llamadas de herramientas solo texto | Caro -- cada acción requiere una llamada al modelo de visión |
| **Independencia de resolución** | Funciona a cualquier escala de pantalla | Sensible a la resolución y el escalado |
| **Plataforma** | Solo macOS | Multiplataforma |
| **Requisitos** | Permisos de accesibilidad | Permisos de grabación de pantalla |

## Pasas horas haciendo clic en apps que no se comunican entre sí

Ya conoces la historia. Copiar de esta app, pegar en aquella. Hacer clic en 14 pantallas para enviar un formulario. Exportar a CSV -- ah espera, no hay exportación. Y vuelta a empezar mañana.

Un oficinista [automatizó su trabajo administrativo y se hizo viral](https://reddit.com/r/BestofRedditorUpdates/comments/1s23k0o/facing_disciplinary_investigation_sack_for/) (2.300+ upvotes) -- no porque fuera técnicamente impresionante, sino porque *todo el mundo reconoció el dolor*. En sanidad, el problema es tan grave que tiene nombre: ["Death by 1,000 Clicks"](https://reddit.com/r/programming/comments/bcr3g5/bad_software_can_kill_death_by_1000_clicks_where/) (1.900+ upvotes) -- médicos que pasan más tiempo navegando software de historia clínica que atendiendo pacientes, con la fatiga de interfaz causando literalmente errores médicos.

Estas apps no tienen API. No tienen CLI. No tienen exportación. Solo una GUI frente a la que alguien tiene que sentarse y hacer clic. Hasta ahora.

mac-use permite que un agente de IA maneje cualquier aplicación de macOS de la misma forma que lo haría un humano -- sin errores y 24/7. Si puedes verlo en pantalla, mac-use puede leerlo, hacer clic en él y escribir en él.

### Qué está automatizando la gente

- **Software fiscal y gubernamental** -- rellenar declaraciones de impuestos en apps de escritorio como eTax o ELSTER que no ofrecen API, ni scripting, solo formularios
- **Contabilidad y apps empresariales** -- introducir datos en GnuCash, QuickBooks Desktop, SAP GUI o cualquier software empresarial heredado
- **Entrada de datos entre apps** -- mover datos entre aplicaciones sin copiar y pegar. Escanear un email de envío, extraer el número de seguimiento, rellenarlo en tu software de recepción. Hay todo un [mercado de freelancers pagando $0.50/tarea](https://reddit.com/r/freelance_forhire/comments/1kxjxgj/hiring_paypertask_050_100_for_2_minute_copypaste/) por este tipo de trabajo (856 candidatos)
- **Extracción de datos de apps cerradas** -- exportar tu [historial de iMessage](https://reddit.com/r/applesucks/comments/1s1avhv/you_cannot_export_your_own_imessage_history_in/) que Apple no te deja exportar, extraer transacciones de apps bancarias, leer dashboards en apps Java heredadas
- **Software de hardware y proveedores** -- configurar apps como Logitech G Hub que tienen [una UX terrible y ninguna alternativa](https://reddit.com/r/LogitechG/comments/1ll327d/why_logitech_g_hub_is_the_worst_software/)
- **QA y testing de accesibilidad** -- probar apps nativas de macOS, verificar estados de elementos, auditar si los botones tienen etiquetas correctas

### ¿Por qué no AppleScript o Shortcuts?

Apple [disolvió el equipo de AppleScript](https://reddit.com/r/Automator/comments/1fuwaby/automator_applescript_or_any_other_macos_ideas/). Automator está deprecado. Shortcuts en Mac está [a medio hacer](https://reddit.com/r/shortcuts/comments/1pxpbd2/finally_dynamic_homekit_control_in_siri_shortcuts/). Todo el stack de automatización de macOS está en decadencia.

mac-use usa la capa de la API de Accesibilidad que Apple mantiene activamente (es obligatoria para el cumplimiento de accesibilidad). No necesita que las apps expongan acciones de Shortcuts ni diccionarios AppleScript. Si la app tiene una ventana, mac-use puede controlarla.

## Inicio rápido

### Instalar con pip (recomendado)

```bash
pip install mac-use
mac-use
```

### O instalar con uvx

```bash
uvx mac-use
```

### Configurar en Claude Code

Añade a tu configuración MCP de Claude Code (`~/.claude.json`):

```json
{
  "mcpServers": {
    "mac-use": {
      "command": "mac-use"
    }
  }
}
```

Si usas uvx:

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

### Conceder permisos de Accesibilidad

mac-use requiere acceso de Accesibilidad para leer e interactuar con los elementos de interfaz de las aplicaciones.

1. Abre **Ajustes del Sistema** (o Preferencias del Sistema en versiones anteriores de macOS)
2. Ve a **Privacidad y seguridad > Accesibilidad**
3. Añade y activa tu aplicación de terminal (Terminal, iTerm2, Ghostty, etc.) o el proceso de Claude Code

Sin este permiso, todas las herramientas devolverán un error "assistive access denied".

## Herramientas

### list_windows

Lista todas las ventanas de aplicación abiertas con sus nombres de proceso, índices de ventana y títulos.

```
list_windows()
```

Esta es normalmente tu primera llamada -- te indica el nombre exacto del proceso para usar con las demás herramientas. Esto es especialmente importante para aplicaciones Java (como eTax) que pueden aparecer como "JavaApplicationStub" en lugar de su nombre visible.

### get_ui_elements

Obtiene el árbol completo de elementos de interfaz de una ventana de aplicación. Devuelve tipos de elementos, nombres, valores y sus rutas en la jerarquía.

```
get_ui_elements(app_name="Safari")
get_ui_elements(app_name="Finder", window_index=2, max_depth=3)
get_ui_elements(app_name="JavaApplicationStub", filter_roles="AXTextField,AXButton,AXCheckBox")
```

Usa `filter_roles` para devolver solo tipos de elementos específicos -- drásticamente más rápido en apps complejas como Java Swing, donde un volcado completo del árbol puede tardar 10-30 segundos.

### click_element

Hace clic en un botón, checkbox o cualquier otro elemento interactuable. Soporta dos modos:

**Modo ruta** -- usa una ruta de elemento AppleScript:
```
click_element(app_name="Safari", element_description="button 2 of group 1 of window 1")
```

**Modo búsqueda por nombre** -- busca y hace clic por nombre (con prefijo de tipo opcional):
```
click_element(app_name="Finder", element_description="New Folder")
click_element(app_name="Safari", element_description="button:Downloads")
click_element(app_name="TextEdit", element_description="checkbox:Wrap to Page")
```

### type_text

Escribe texto en un campo. Escribe en el campo actualmente enfocado, o apunta a un campo específico por nombre.

```
type_text(app_name="Safari", text="https://example.com", field_name="Address and Search")
type_text(app_name="TextEdit", text="Hello, world!")
```

### read_element

Lee el valor, nombre, rol y estado de cualquier elemento de interfaz.

```
read_element(app_name="Safari", element_description="text field 1 of window 1")
read_element(app_name="Calculator", element_description="Display")
```

### activate_app

Trae una aplicación al primer plano.

```
activate_app(app_name="Finder")
```

### press_key

Pulsa una tecla o atajo de teclado.

```
press_key(key="return")
press_key(key="s", modifiers="command")
press_key(key="f", modifiers="command,shift")
press_key(key="tab")
press_key(key="down arrow")
```

### menu_action

Hace clic en un elemento de la barra de menú por ruta.

```
menu_action(app_name="TextEdit", menu_path="File > Save")
menu_action(app_name="Safari", menu_path="File > New Window")
menu_action(app_name="Finder", menu_path="Edit > Select All")
```

### fill_form

Rellena múltiples campos de formulario en una sola llamada. En lugar de un viaje de ida y vuelta por campo, todos los campos se rellenan en una sola ejecución -- significativamente más rápido para tareas de entrada de datos como formularios fiscales o creación de cuentas.

```
fill_form(app_name="JavaApplicationStub", fields={
    "First Name": "John",
    "Last Name": "Doe",
    "Email": "john@example.com",
    "Phone": "+1 555 0123"
})
```

### screenshot

Captura una captura de pantalla de una ventana de app específica o de la pantalla completa. Guarda en `/tmp/` y devuelve la ruta del archivo.

```
screenshot(app_name="Safari")
screenshot(full_screen=True)
```

## Requisitos

- **macOS** (cualquier versión reciente -- Ventura, Sonoma, Sequoia)
- **Python 3.10+**
- **Permisos de accesibilidad** concedidos al proceso que realiza la llamada (ver Inicio rápido más arriba)

Sin dependencias externas más allá del paquete Python `mcp`. Toda la interacción con macOS se realiza a través del comando integrado `osascript`.

## Desarrollo

```bash
git clone https://github.com/entpnomad/mac-use.git
cd mac-use
pip install -e .
mac-use
```

## Licencia

MIT -- ver [LICENSE](LICENSE).

## Autor

[entpnomad](https://github.com/entpnomad)
