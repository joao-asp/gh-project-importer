# gh-projects-importer
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

[English](#english) | [Português (Brasil)](#português-brasil)

---

## English

A command-line interface (CLI) to parse tasks from Markdown files and bulk import them as Draft Issues into GitHub Projects V2 via GraphQL.

### Motivation
I wrote this tool to solve a personal bottleneck: manual data entry. Managing multiple scopes and projects meant I was wasting too much time copying and pasting individual tasks into GitHub boards. This script automates the process, letting you write or generate your tasks locally and push them all at once.

### Prerequisites

- Python 3.8+
- A GitHub Personal Access Token (PAT) with `repo`, `read:org`, `write:org`, and `project` scopes.

### Installation & Setup

1. Clone the repository:
```bash
git clone [https://github.com/YOUR_USER/gh-projects-importer.git](https://github.com/YOUR_USER/gh-projects-importer.git)
cd gh-projects-importer

```

2. Install the dependencies:

```bash
pip install -r requirements.txt

```

3. Create a `.env` file in the root directory:

```env
GITHUB_TOKEN=your_personal_access_token
GITHUB_ORGANIZATION=your_username_or_organization_name
PROJECT_NUMBER=1

```

*(The `PROJECT_NUMBER` is the integer found in your GitHub Project URL).*

### Usage

Your Markdown file must follow a strict syntax to be parsed correctly. Each task must be a checklist item, using a pipe (`|`) to separate the title from the description.

**Syntax:**
`- [ ] Task Title | Brief description of the task.`

**Run the CLI:**

```bash
python importador.py --file path/to/your/tasks.md

```

### AI Prompt Template (Optional)

If you use LLMs to break down your project scopes, use the following strict prompt to ensure the output matches the required parser syntax:

> Act as a Tech Lead. I will provide a project scope, and you must break it down into atomic, actionable technical tasks.
> **MANDATORY Formatting Rules:**
> 1. Do not write any introductions, warnings, or conclusions.
> 2. Do not group tasks by sections.
> 3. Return ONLY the task list.
> 4. You must use EXACTLY the following Markdown format on each line, separating the title from the description with the `|` character:
> `- [ ] Short title | One-sentence description of what needs to be done.`
> 
> 
> **Context:**
> [INSERT YOUR PROJECT CONTEXT/SCOPE HERE]

### License

This project is licensed under the [GNU AGPLv3](https://www.google.com/search?q=LICENSE).

---

## Português (Brasil)

Uma interface de linha de comando (CLI) para extrair tarefas de arquivos Markdown e importá-las em lote como Draft Issues no GitHub Projects V2 via GraphQL.

### Motivação

Escrevi esta ferramenta para resolver um gargalo pessoal: a entrada manual de dados. Gerenciar vários escopos e projetos significava perder muito tempo copiando e colando tarefas individuais nos boards do GitHub. Este script automatiza o processo, permitindo que você escreva ou gere suas tarefas localmente e as envie de uma só vez.

### Pré-requisitos

* Python 3.8+
* Um GitHub Personal Access Token (PAT) com os escopos `repo`, `read:org`, `write:org` e `project`.

### Instalação e Configuração

1. Clone o repositório:

```bash
git clone [https://github.com/SEU_USUARIO/gh-projects-importer.git](https://github.com/SEU_USUARIO/gh-projects-importer.git)
cd gh-projects-importer

```

2. Instale as dependências:

```bash
pip install -r requirements.txt

```

3. Crie um arquivo `.env` no diretório raiz:

```env
GITHUB_TOKEN=seu_personal_access_token
GITHUB_ORGANIZATION=seu_usuario_ou_nome_da_organizacao
PROJECT_NUMBER=1

```

*(O `PROJECT_NUMBER` é o número inteiro encontrado na URL do seu GitHub Project).*

### Como usar

Seu arquivo Markdown deve seguir uma sintaxe estrita para ser processado corretamente. Cada tarefa deve ser um item de checklist, usando um pipe (`|`) para separar o título da descrição.

**Sintaxe:**
`- [ ] Título da Tarefa | Breve descrição da tarefa.`

**Execute o CLI:**

```bash
python importador.py --file caminho/para/suas/tarefas.md

```

### Modelo de Prompt para IA (Opcional)

Se você usa LLMs para quebrar o escopo dos seus projetos, utilize o prompt restrito abaixo para garantir que a saída seja compatível com o parser da ferramenta:

> Atue como um Tech Lead. Vou fornecer o escopo de um projeto e você deve quebrá-lo em tarefas técnicas atômicas e acionáveis.
> **Regras OBRIGATÓRIAS de formatação:**
> 1. Não escreva introduções, avisos ou conclusões.
> 2. Não agrupe as tarefas por seções.
> 3. Retorne APENAS a lista de tarefas.
> 4. Você deve usar EXATAMENTE o seguinte formato Markdown em cada linha, separando o título da descrição com o caractere `|`:
> `- [ ] Título curto | Descrição de uma frase sobre o que deve ser feito.`
> 
> 
> **Contexto:**
> [INSIRA O CONTEXTO/ESCOPO DO SEU PROJETO AQUI]

### Licença

Este projeto é licenciado sob a [GNU AGPLv3](https://www.google.com/search?q=LICENSE).
