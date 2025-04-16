
import os
from dotenv import load_dotenv

def git_update(commit="Atualização via Colab"):
   
    load_dotenv('/content/.env')

    usuario = os.getenv('GITHUB_USERNAME')
    email = os.getenv('EMAIL')
    token = os.getenv('GITHUB_TOKEN')
    projeto = os.getenv('PROJECT_NAME')

    if not all([usuario, email, token, projeto]):
        raise ValueError("Variáveis de ambiente ausentes. Verifique o .env.")

    if not os.path.isdir(projeto):
        print(f"Diretório '{projeto}' não encontrado.")
        return

    os.chdir(projeto)
    os.system("git add .")
    os.system(f'git commit -m "{commit}" || echo \"Nada a commitar.\"')
    os.system("git push origin main || echo \"Falha ao enviar alterações.\"")
    print("Repositório atualizado.")

if __name__ == "__main__":
    git_update("Commit inicial")
