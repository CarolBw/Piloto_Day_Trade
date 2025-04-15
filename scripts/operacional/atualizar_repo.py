
#@title Função operacional para atualizar repositório remoto

import subprocess
import os
import dotenv

dotenv.load_dotenv()

def atualizar_repo(commit_message="Atualizando arquivos"):
    try:
        # Verifica se está dentro de um repositório Git
        subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], check=True, capture_output=True)
        print("Repositório Git detectado.")

        # Verifica a branch atual
        current_branch = subprocess.run(['git', 'branch', '--show-current'], capture_output=True, text=True).stdout.strip()
        if current_branch != "main":
            print("Alterando para a branch 'main'...")
            subprocess.run(['git', 'checkout', 'main'], check=True)
        else:
            print("Já está na branch 'main'.")

        # Verifica se há alterações
        print("Verificando alterações pendentes...")
        status = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        changes = status.stdout.strip()

        if changes == "":
            print("Nenhuma alteração detectada. Nada para commit.")
            return

        print("Arquivos com alterações detectadas:")
        for line in changes.splitlines():
            status_code = line[:2].strip()
            file_path = line[3:]
            status_label = {
                'M': 'Modificado',
                'A': 'Adicionado',
                'D': 'Deletado',
                'R': 'Renomeado',
                '??': 'Não rastreado'
            }.get(status_code, f"Outro ({status_code})")
            print(f"  - {status_label}: {file_path}")

        print("Adicionando arquivos alterados...")
        subprocess.run(['git', 'add', '.'], check=True)

        print(f"Realizando commit com a mensagem: '{commit_message}'")
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)

        print("Enviando alterações para o repositório remoto...")
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)

        print("Arquivos atualizados com sucesso na branch 'main'.")

    except subprocess.CalledProcessError as e:
        print("Erro ao executar comandos Git.")
        print(f"Detalhes: {e}")
    except Exception as e:
        print("Ocorreu um erro inesperado.")
        print(f"Detalhes: {e}")

if __name__ == "__main__":
    atualizar_repo("Garantir que o repositório esteja atualizado")
