
# @title Executar pipeline completo de dados

import os

# Caminho base
BASE = "/content/Piloto_Day_Trade/scripts"

# Etapas do pipeline
etapas = [
    f"{BASE}/pipeline/extracao_dados.py",
    f"{BASE}/pipeline/limpeza_dados.py",
    f"{BASE}/pipeline/transformacao_dados.py",
    f"{BASE}/pipeline/criar_banco_dimensional.py",
    f"{BASE}/pipeline/carga_dados.py",
    f"{BASE}/pipeline/gerar_catalogo_dados.py",
    f"{BASE}/modelagem_machine_learning/preparar_dados_modelagem_LSTM.py",
]

def executar_pipeline():
    print("\nIniciando execução completa do pipeline...\n")
    for etapa in etapas:
        print(f"\nExecutando: {etapa}")
        os.system(f"python3 {etapa}")
    print("\nPipeline finalizado com sucesso.")

if __name__ == "__main__":
    executar_pipeline()
