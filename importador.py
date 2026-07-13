import os
import re
import requests
import typer
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

app = typer.Typer()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_ORG = os.getenv("GITHUB_ORGANIZATION")
PROJECT_NUMBER = os.getenv("PROJECT_NUMBER")

URL_API = "https://api.github.com/graphql"
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"}


def executar_query(query: str, variables: dict = None):
    """Auxiliar para disparar chamadas GraphQL ao GitHub."""
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
        
    resposta = requests.post(URL_API, json=payload, headers=HEADERS)
    if resposta.status_code != 200:
        raise Exception(f"Erro na API do GitHub: {resposta.status_code} - {resposta.text}")
        
    dados = resposta.json()
    if "errors" in dados:
        raise Exception(f"Erro no GraphQL: {dados['errors']}")
        
    return dados["data"]


def buscar_project_id(org: str, numero_projeto: int):
    """Busca o Node ID interno do projeto baseado no número visível na URL."""
    # Tenta buscar assumindo que o escopo seja um usuário individual primeiro
    query_user = """
    query($login: String!, $number: Int!) {
      user(login: $login) {
        projectV2(number: $number) {
          id
        }
      }
    }
    """
    try:
        dados = executar_query(query_user, {"login": org, "number": int(numero_projeto)})
        if dados.get("user") and dados["user"].get("projectV2"):
            return dados["user"]["projectV2"]["id"]
    except Exception:
        pass

    # Se falhar, tenta buscar assumindo que é uma Organização
    query_org = """
    query($login: String!, $number: Int!) {
      organization(login: $login) {
        projectV2(number: $number) {
          id
        }
      }
    }
    """
    dados = executar_query(query_org, {"login": org, "number": int(numero_projeto)})
    if dados.get("organization") and dados["organization"].get("projectV2"):
        return dados["organization"]["projectV2"]["id"]
        
    raise Exception("Não foi possível encontrar o ID do projeto. Verifique o usuário/org e o número.")


def adicionar_draft_item(project_id: str, titulo: str, descricao: str):
    """Executa a mutation para inserir uma Draft Issue no board do projeto."""
    mutation = """
    mutation($projectId: ID!, $title: String!, $body: String!) {
      addProjectV2ItemById(input: {projectId: $projectId, contentId: null, title: $title, body: $body}) {
        item {
          id
        }
      }
    }
    """
    variaveis = {
        "projectId": project_id,
        "title": titulo,
        "body": descricao
    }
    executar_query(mutation, variaveis)


@app.command()
def importar(
    arquivo: str = typer.Option(..., "--file", "-f", help="Caminho do arquivo Markdown com as tarefas."),
    projeto: int = typer.Option(..., "--project", "-p", prompt="Qual é o número do projeto no GitHub? (Ex: 1, 2)", help="Número sequencial do GitHub Project V2.")
):
    """Lê tarefas de um arquivo Markdown padronizado e as importa no GitHub Projects V2."""
    if not all([GITHUB_TOKEN, GITHUB_ORG]):
        typer.secho("Erro: Verifique se GITHUB_TOKEN e GITHUB_ORGANIZATION estão no seu .env", fg=typer.colors.RED)
        raise typer.Exit(1)

    if not os.path.exists(arquivo):
        typer.secho(f"Erro: Arquivo '{arquivo}' não encontrado.", fg=typer.colors.RED)
        raise typer.Exit(1)

    # 1. Parsing do arquivo Markdown
    typer.echo(f"Lendo tarefas de {arquivo}...")
    with open(arquivo, "r", encoding="utf-8") as f:
        linhas = f.readlines()

    # Regex captura o conteúdo dentro de [ ] ou [x] e divide pelo caractere pipeline |
    padrao = r"^\s*(?:-\s*)?\[[\s|x|X]?\]\s*([^|]+)\|\s*(.*)$"
    
    tarefas = []
    for linha in linhas:
        match = re.match(padrao, linha)
        if match:
            titulo = match.group(1).strip()
            descricao = match.group(2).strip()
            tarefas.append({"titulo": titulo, "descricao": descricao})

    if not tarefas:
        typer.secho("Nenhuma tarefa encontrada no formato correto ('- [ ] Titulo | Descricao').", fg=typer.colors.YELLOW)
        raise typer.Exit()

    typer.secho(f"Encontradas {len(tarefas)} tarefas prontas para importação.", fg=typer.colors.GREEN)

    # 2. Resgatar o Project ID do GitHub via GraphQL (usando a variável 'projeto' passada no terminal)
    try:
        typer.echo(f"Conectando ao GitHub para buscar metadados do projeto {projeto}...")
        project_id = buscar_project_id(GITHUB_ORG, projeto)
        typer.secho(f"Projeto localizado com sucesso! ID: {project_id}", fg=typer.colors.CYAN)
    except Exception as e:
        typer.secho(f"Erro de autenticação ou localização: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)

    # 3. Iterar e enviar as tarefas
    with typer.progressbar(tarefas, label="Importando tarefas no board") as lista_tarefas:
        for tarefa in lista_tarefas:
            try:
                adicionar_draft_item(project_id, tarefa["titulo"], tarefa["descricao"])
            except Exception as e:
                typer.secho(f"\nFalha ao importar '{tarefa['titulo']}': {e}", fg=typer.colors.RED)

    typer.secho("\n🚀 Importação concluída com sucesso!", fg=typer.colors.GREEN, bold=True)