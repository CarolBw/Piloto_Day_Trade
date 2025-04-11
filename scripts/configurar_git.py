
import os
from dotenv import load_dotenv

def git_config():
    """Configura o Git localmente e sincroniza com o repositório remoto no GitHub."""

    # Carregar variáveis de ambiente do arquivo .env
    load_dotenv(dotenv_path='/content/.env')

    # Obter as variáveis de ambiente do .env para o GitHub
    GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')
    EMAIL = os.getenv('EMAIL')
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    PROJECT_NAME = os.getenv('PROJECT_NAME')
    REPO_URL = f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{PROJECT_NAME}.git"

    # Configurar o Git localmente com as credenciais
    os.system(f'git config --global user.name "{GITHUB_USERNAME}"')
    os.system(f'git config --global user.email "{EMAIL}"')

    # Verificar se o diretório do projeto já existe e se é um repositório Git válido
    if os.path.isdir(PROJECT_NAME):
        print(f"O diretório '{PROJECT_NAME}' já existe. Entrando no diretório e sincronizando...")

        os.chdir(PROJECT_NAME)  # Entrar na pasta do projeto

        # Garantir que estamos na branch main
        os.system("git branch -M main")

        # Remover qualquer configuração errada do repositório remoto e adicionar novamente
        os.system("git remote remove origin")
        os.system("git remote add origin " + REPO_URL)

        # Puxar as últimas atualizações do GitHub, tratando históricos não relacionados
        os.system("git pull origin main --allow-unrelated-histories --no-rebase")
    else:
        print(f"Clonando o repositório '{PROJECT_NAME}'...")

        # Clonar o repositório remoto
        os.system(f"git clone {REPO_URL}")
        os.chdir(PROJECT_NAME)  # Entrar no diretório após o clone

        # Inicializar o repositório Git local (se necessário) e configurar remoto
        os.system("git branch -M main")
        os.system("git remote add origin " + REPO_URL)

        # Realizar o pull inicial para garantir que a branch main está sincronizada
        os.system("git pull origin main --allow-unrelated-histories --no-rebase")

    print(f"✅ Configuração do Git concluída e sincronizada com a branch main do repositório{REPO_URL}")


if __name__ == "__main__":
    git_config()


