import os
import re
import logging
from datetime import datetime
import requests
import typer
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_ORGANIZATION = os.getenv("GITHUB_ORGANIZATION")

URL_API = "https://api.github.com/graphql"
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

# Configuração automatizada da pasta e arquivo de logs
PASTA_LOGS = "logs"
os.makedirs(PASTA_LOGS, exist_ok=True)
arquivo_log = os.path.join(PASTA_LOGS, f"importacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(arquivo_log, encoding="utf-8")
    ]
)


def executar_query(query: str, variables: dict = None):
    """Auxiliar para disparar chamadas GraphQL ao GitHub."""
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
        
    resposta = requests.post(URL_API, json=payload, headers=HEADERS)
    if resposta.status_code != 200:
        erro_msg = f"Erro na API do GitHub: {resposta.status_code} - {resposta.text}"
        logging.error(erro_msg)
        raise Exception(erro_msg)
        
    dados = resposta.json()
    if "errors" in dados:
        erro_msg = f"Erro no GraphQL: {dados['errors']}"
        logging.error(erro_msg)
        raise Exception(erro_msg)
        
    return dados["data"]


def buscar_project_id(org: str, numero_projeto: int):
    """Busca o Node ID interno do projeto baseado no número visível na URL."""
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
        
    raise Exception("Não foi possível encontrar o ID do projeto. Verifique o utilizador/org e o número no GitHub.")


def adicionar_draft_item(project_id: str, titulo: str, descricao: str):
    """Executa a mutation correta para criar uma Draft Issue no projeto."""
    mutation = """
    mutation($projectId: ID!, $title: String!, $body: String!) {
      addProjectV2DraftIssue(input: {projectId: $projectId, title: $title, body: $body}) {
        projectItem {
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


def importar(
    arquivo: str = typer.Option(..., "--file", "-f", help="Caminho do ficheiro Markdown com as tarefas."),
    projeto: int = typer.Option(..., "--project", "-p", prompt="Qual é o número do projeto no GitHub? (Ex: 1, 2)", help="Número sequencial do GitHub Project V2.")
):
    """Lê tarefas de um ficheiro Markdown padronizado e importa no GitHub Projects V2."""
    logging.info(f"Iniciando execução: arquivo={arquivo}, projeto={projeto}")

    if not all([GITHUB_TOKEN, GITHUB_ORGANIZATION]):
        msg = "Erro: Verifique se GITHUB_TOKEN e GITHUB_ORGANIZATION estão no seu ficheiro .env"
        typer.secho(msg, fg=typer.colors.RED)
        logging.error(msg)
        raise typer.Exit(1)

    if not os.path.exists(arquivo):
        msg = f"Erro: Ficheiro '{arquivo}' não foi encontrado."
        typer.secho(msg, fg=typer.colors.RED)
        logging.error(msg)
        raise typer.Exit(1)

    typer.echo(f"A ler tarefas de {arquivo}...")
    with open(arquivo, "r", encoding="utf-8") as f:
        linhas = f.readlines()

    # Regex para capturar os padrões de checklist
    padrao = r"^\s*(?:-\s*)?\[[\s|x|X]?\]\s*([^|]+)\|\s*(.*)$"
    
    tarefas = []
    for linha in linhas:
        match = re.match(padrao, linha)
        if match:
            titulo = match.group(1).strip()
            descricao = match.group(2).strip()
            tarefas.append({"titulo": titulo, "descricao": descricao})

    if not tarefas:
        msg_vazio = "Nenhuma tarefa encontrada no formato correto ('- [ ] Titulo | Descricao')."
        typer.secho(msg_vazio, fg=typer.colors.YELLOW)
        logging.warning(msg_vazio)
        raise typer.Exit()

    typer.secho(f"Encontradas {len(tarefas)} tarefas prontas para importação.", fg=typer.colors.GREEN)
    logging.info(f"{len(tarefas)} tarefas estruturadas para processamento.")

    try:
        typer.echo(f"A ligar ao GitHub para procurar metadados do projeto {projeto}...")
        project_id = buscar_project_id(GITHUB_ORGANIZATION, projeto)
        typer.secho(f"Projeto localizado com sucesso! ID: {project_id}", fg=typer.colors.CYAN)
        logging.info(f"Conexão estabelecida. Project ID GraphQL: {project_id}")
    except Exception as e:
        msg_erro = f"Erro de autenticação ou localização: {e}"
        typer.secho(msg_erro, fg=typer.colors.RED)
        logging.error(msg_erro)
        raise typer.Exit(1)

    sucessos = 0
    falhas = 0

    with typer.progressbar(tarefas, label="A importar tarefas no board") as lista_tarefas:
        for tarefa in lista_tarefas:
            try:
                adicionar_draft_item(project_id, tarefa["titulo"], tarefa["descricao"])
                logging.info(f"Sucesso ao importar: '{tarefa['titulo']}'")
                sucessos += 1
            except Exception as e:
                # O terminal mostra o aviso curto, o log guarda o payload de erro completo da API
                typer.secho(f"\nFalha ao importar '{tarefa['titulo']}'. Verifique os logs para detalhes.", fg=typer.colors.RED)
                logging.error(f"Falha na tarefa '{tarefa['titulo']}': {e}")
                falhas += 1

    typer.secho(f"\n🚀 Importação concluída! Sucessos: {sucessos} | Falhas: {falhas}", fg=typer.colors.GREEN, bold=True)
    typer.echo(f"Histórico detalhado guardado em: {arquivo_log}")
    logging.info(f"Fim da execução. Sucessos: {sucessos}, Falhas: {falhas}")


if __name__ == "__main__":
    typer.run(importar)