
import os
from dotenv import load_dotenv

def git_update():
    """Adiciona, commit e envia as mudanças para o repositório remoto no GitHub."""
    
    # Carregar variáveis do ambiente
    load_dotenv(dotenv_path='/content/.env')

    GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')
    EMAIL = os.getenv('EMAIL')
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    PROJECT_NAME = os.getenv('PROJECT_NAME')

    if not all([GITHUB_USERNAME, EMAIL, GITHUB_TOKEN, PROJECT_NAME]):
        raise ValueError("Variáveis de ambiente faltando. Verifique o arquivo .env.")

    REPO_URL = f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{PROJECT_NAME}.git"

    if not os.path.isdir(PROJECT_NAME):
        print(f"[ERROR] Diretório '{PROJECT_NAME}' não encontrado. Execute o script de configuração primeiro.")
        return

    os.chdir(PROJECT_NAME)

    # Verificando o status do repositório
    print("[INFO] Adicionando arquivos modificados...")
    os.system("git add .")

    print("[INFO] Commitando mudanças...")
    os.system('git commit -m "Sincronização automática via Colab" || echo "Nada a commitar."')

    print("[INFO] Enviando alterações para o repositório remoto...")
    os.system(f"git push origin main || echo 'Push falhou.'")

    print("[SUCESSO] Mudanças enviadas para o repositório remoto.")

if __name__ == "__main__":
    git_update()
