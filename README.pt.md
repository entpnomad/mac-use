# mac-use

🌐 [English](README.md) | [Español](README.es.md) | [Français](README.fr.md) | [Italiano](README.it.md) | [Português](README.pt.md) | [Deutsch](README.de.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**Automatize o seu trabalho no computador. Deixe a IA clicar, digitar e ler qualquer app do macOS.**

---

## O que e o mac-use?

mac-use e um servidor [MCP (Model Context Protocol)](https://modelcontextprotocol.io) que da aos assistentes de IA controlo direto sobre qualquer aplicacao macOS atraves da API nativa de Acessibilidade.

Em vez de tirar capturas de ecra e adivinhar onde clicar com base em coordenadas de pixels (como o [Anthropic's computer use](https://docs.anthropic.com/en/docs/agents-and-tools/computer-use)), o mac-use le a arvore real de elementos de interface de qualquer aplicacao usando macOS System Events e AppleScript. Conhece os nomes, tipos e hierarquia de cada botao, campo de texto, item de menu, checkbox e etiqueta na aplicacao. Pode clicar em elementos por nome, ler os seus valores, digitar em campos, navegar menus e pressionar atalhos de teclado -- tudo atraves da interface de acessibilidade estruturada que o macOS fornece as tecnologias de assistencia.

Pense nele como **Playwright para apps desktop**: preciso e fiavel porque opera na estrutura real da interface em vez de aproximacao visual.

## Como se compara ao Anthropic Computer Use

| | mac-use | Anthropic Computer Use |
|---|---|---|
| **Compreensao da UI** | Arvore de elementos estruturada (nomes, funcoes, hierarquia) | Capturas de ecra (analise de pixels) |
| **Selecao de elementos** | Por nome, funcao ou caminho (ex. "click button Save") | Por coordenadas de pixels (ex. "click at 340, 520") |
| **Velocidade** | Chamadas diretas a API, sem processamento de imagem | Requer captura de ecra e modelo de visao por acao |
| **Precisao** | Exata -- os elementos sao identificados sem ambiguidade | Aproximada -- as coordenadas podem falhar, especialmente apos alteracoes de layout |
| **Custo** | Minimo -- chamadas de ferramentas apenas texto | Caro -- cada acao requer uma chamada ao modelo de visao |
| **Independencia de resolucao** | Funciona em qualquer escala de ecrã | Sensivel a resolucao e ao redimensionamento |
| **Plataforma** | Apenas macOS | Multiplataforma |
| **Requisitos** | Permissoes de acessibilidade | Permissoes de gravacao de ecra |

## Passas horas a clicar em apps que nao comunicam entre si

Conheces a historia. Copiar desta app, colar naquela. Clicar em 14 ecras para submeter um formulario. Exportar para CSV -- ah espera, nao ha exportacao. E voltar a fazer tudo amanha.

Um trabalhador de escritorio [automatizou o seu trabalho administrativo e tornou-se viral](https://reddit.com/r/BestofRedditorUpdates/comments/1s23k0o/facing_disciplinary_investigation_sack_for/) (2.300+ upvotes) -- nao porque fosse tecnicamente impressionante, mas porque *toda a gente reconheceu a dor*. Na saude, o problema e tao grave que tem nome: ["Death by 1,000 Clicks"](https://reddit.com/r/programming/comments/bcr3g5/bad_software_can_kill_death_by_1000_clicks_where/) (1.900+ upvotes) -- medicos que passam mais tempo a navegar software de registos clinicos do que a tratar pacientes, com a fadiga de interface a causar literalmente erros medicos.

Estas apps nao tem API. Nao tem CLI. Nao tem exportacao. Apenas uma interface grafica em frente a qual alguem tem de se sentar e clicar. Ate agora.

O mac-use permite que um agente de IA conduza qualquer aplicacao macOS da mesma forma que um humano faria -- sem erros e 24/7. Se consegues ve-lo no ecra, o mac-use consegue le-lo, clicar nele e digitar nele.

### O que as pessoas estao a automatizar

- **Software fiscal e governamental** -- preencher declaracoes de impostos em apps desktop como eTax ou ELSTER que nao oferecem API, nem scripting, apenas formularios
- **Contabilidade e apps empresariais** -- introduzir dados no GnuCash, QuickBooks Desktop, SAP GUI ou qualquer software empresarial legado
- **Introducao de dados entre apps** -- mover dados entre aplicacoes sem copiar e colar. Ler um email de envio, extrair o numero de rastreamento, preenche-lo no teu software de rececao. Ha todo um [mercado de freelancers a pagar $0.50/tarefa](https://reddit.com/r/freelance_forhire/comments/1kxjxgj/hiring_paypertask_050_100_for_2_minute_copypaste/) por este tipo de trabalho (856 candidatos)
- **Extracao de dados de apps bloqueadas** -- exportar o teu [historico do iMessage](https://reddit.com/r/applesucks/comments/1s1avhv/you_cannot_export_your_own_imessage_history_in/) que a Apple nao te deixa exportar, extrair transacoes de apps bancarias, ler dashboards em apps Java legadas
- **Software de hardware e fornecedores** -- configurar apps como Logitech G Hub que tem [uma UX terrivel e nenhuma alternativa](https://reddit.com/r/LogitechG/comments/1ll327d/why_logitech_g_hub_is_the_worst_software/)
- **QA e testes de acessibilidade** -- testar apps macOS nativas, verificar estados de elementos, auditar se os botoes tem etiquetas adequadas

### Porque nao AppleScript ou Shortcuts?

A Apple [dissolveu a equipa de AppleScript](https://reddit.com/r/Automator/comments/1fuwaby/automator_applescript_or_any_other_macos_ideas/). O Automator esta descontinuado. Os Shortcuts no Mac estao [pela metade](https://reddit.com/r/shortcuts/comments/1pxpbd2/finally_dynamic_homekit_control_in_siri_shortcuts/). Toda a stack de automacao do macOS esta em declinio.

O mac-use usa a camada da API de Acessibilidade que a Apple mantem ativamente (e obrigatoria para conformidade com acessibilidade). Nao precisa que as apps exponham acoes de Shortcuts ou dicionarios AppleScript. Se a app tem uma janela, o mac-use pode controla-la.

## Inicio rapido

### Instalar com pip (recomendado)

```bash
pip install mac-use
mac-use
```

### Ou instalar com uvx

```bash
uvx mac-use
```

### Configurar no Claude Code

Adiciona a tua configuracao MCP do Claude Code (`~/.claude.json`):

```json
{
  "mcpServers": {
    "mac-use": {
      "command": "mac-use"
    }
  }
}
```

Se usas uvx:

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

### Conceder permissoes de Acessibilidade

O mac-use requer acesso de Acessibilidade para ler e interagir com os elementos de interface das aplicacoes.

1. Abre **Definicoes do Sistema** (ou Preferencias do Sistema em versoes anteriores do macOS)
2. Vai a **Privacidade e Seguranca > Acessibilidade**
3. Adiciona e ativa a tua aplicacao de terminal (Terminal, iTerm2, Ghostty, etc.) ou o processo do Claude Code

Sem esta permissao, todas as ferramentas devolverao um erro "assistive access denied".

## Ferramentas

### list_windows

Lista todas as janelas de aplicacao abertas com os nomes dos processos, indices de janela e titulos.

```
list_windows()
```

Esta e tipicamente a tua primeira chamada -- indica-te o nome exato do processo para usar com as outras ferramentas. Isto e especialmente importante para aplicacoes Java (como eTax) que podem aparecer como "JavaApplicationStub" em vez do seu nome de exibicao.

### get_ui_elements

Obtem a arvore completa de elementos de interface de uma janela de aplicacao. Devolve tipos de elementos, nomes, valores e os seus caminhos na hierarquia.

```
get_ui_elements(app_name="Safari")
get_ui_elements(app_name="Finder", window_index=2, max_depth=3)
get_ui_elements(app_name="JavaApplicationStub", filter_roles="AXTextField,AXButton,AXCheckBox")
```

Usa `filter_roles` para devolver apenas tipos de elementos especificos -- drasticamente mais rapido em apps complexas como Java Swing, onde um dump completo da arvore pode demorar 10-30 segundos.

### click_element

Clica num botao, checkbox ou qualquer outro elemento interativo. Suporta dois modos:

**Modo caminho** -- usa um caminho de elemento AppleScript:
```
click_element(app_name="Safari", element_description="button 2 of group 1 of window 1")
```

**Modo pesquisa por nome** -- encontra e clica por nome (com prefixo de tipo opcional):
```
click_element(app_name="Finder", element_description="New Folder")
click_element(app_name="Safari", element_description="button:Downloads")
click_element(app_name="TextEdit", element_description="checkbox:Wrap to Page")
```

### type_text

Digita texto num campo. Digita no campo atualmente focado, ou direciona para um campo especifico por nome.

```
type_text(app_name="Safari", text="https://example.com", field_name="Address and Search")
type_text(app_name="TextEdit", text="Hello, world!")
```

### read_element

Le o valor, nome, funcao e estado de qualquer elemento de interface.

```
read_element(app_name="Safari", element_description="text field 1 of window 1")
read_element(app_name="Calculator", element_description="Display")
```

### activate_app

Traz uma aplicacao para o primeiro plano.

```
activate_app(app_name="Finder")
```

### press_key

Pressiona uma tecla ou atalho de teclado.

```
press_key(key="return")
press_key(key="s", modifiers="command")
press_key(key="f", modifiers="command,shift")
press_key(key="tab")
press_key(key="down arrow")
```

### menu_action

Clica num item da barra de menu por caminho.

```
menu_action(app_name="TextEdit", menu_path="File > Save")
menu_action(app_name="Safari", menu_path="File > New Window")
menu_action(app_name="Finder", menu_path="Edit > Select All")
```

### fill_form

Preenche multiplos campos de formulario numa unica chamada. Em vez de uma ida e volta por campo, todos os campos sao preenchidos numa unica execucao -- significativamente mais rapido para tarefas de introducao de dados como formularios fiscais ou criacao de contas.

```
fill_form(app_name="JavaApplicationStub", fields={
    "First Name": "John",
    "Last Name": "Doe",
    "Email": "john@example.com",
    "Phone": "+1 555 0123"
})
```

### screenshot

Captura uma captura de ecra de uma janela de app especifica ou do ecra inteiro. Guarda em `/tmp/` e devolve o caminho do ficheiro.

```
screenshot(app_name="Safari")
screenshot(full_screen=True)
```

## Requisitos

- **macOS** (qualquer versao recente -- Ventura, Sonoma, Sequoia)
- **Python 3.10+**
- **Permissoes de acessibilidade** concedidas ao processo que faz a chamada (ver Inicio rapido acima)

Sem dependencias externas para alem do pacote Python `mcp`. Toda a interacao com o macOS e feita atraves do comando integrado `osascript`.

## Desenvolvimento

```bash
git clone https://github.com/entpnomad/mac-use.git
cd mac-use
pip install -e .
mac-use
```

## Licenca

MIT -- ver [LICENSE](LICENSE).

## Autor

[entpnomad](https://github.com/entpnomad)
