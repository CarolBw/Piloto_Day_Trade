
# @title Executar pipeline completo de dados com importações diretas

import os
import pandas as pd

from scripts.pipeline.extracao_dados import extrair_dados
from scripts.pipeline.limpeza_dados import limpeza_dados
from scripts.pipeline.transformacao_dados import transformar_dados
from scripts.pipeline.carga_dados import carregar_dados
from scripts.pipeline.criar_banco_dimensional import criar_banco
from scripts.pipeline.gerar_catalogo_dados import gerar_catalogo
from scripts.modelagem_machine_learning.preparar_dados_modelagem_LSTM import preparar_dados_lstm

def executar_pipeline():
    print("\nIniciando execução completa do pipeline...")

    # Etapa 1: Extração
    print("Executando: Extração de dados")
    ticker = "BBDC4.SA"
    intervalo = "5m"
    dias = 45
    caminho_bruto = "/content/Piloto_Day_Trade/data/raw/dados_brutos.csv"
    extrair_dados(ticker, dias, intervalo, caminho_bruto)

    # Etapa 2: Limpeza
    print("Executando: Limpeza de dados")
    df_bruto = pd.read_csv(caminho_bruto, index_col=0, parse_dates=True, dayfirst=True)
    caminho_limpo = "/content/Piloto_Day_Trade/data/cleaned/dados_limpos.csv"
    limpeza_dados(df_bruto, caminho_limpo)

    # Etapa 3: Transformação
    print("Executando: Transformação de dados")
    caminho_transformado = "/content/Piloto_Day_Trade/data/transformed/dados_transformados.csv"
    transformar_dados(caminho_limpo, caminho_transformado)

    # Etapa 4: Criar banco dimensional
    print("Executando: Criação do banco dimensional")
    criar_banco()

    # Etapa 5: Carga de dados
    print("Executando: Carga de dados")
    df_transformado = pd.read_csv(caminho_transformado)
    carregar_dados(df_transformado)

    # Etapa 6: Geração de catálogo
    print("Executando: Geração de catálogo de dados")
    gerar_catalogo()

    # Etapa 7: Preparação dos dados para modelagem
    print("Executando: Preparação de dados para LSTM")
    preparar_dados_lstm(
        path_dados=caminho_transformado,
        tam_seq=96,
        tx_treino=0.8
    )

    print("\nPipeline finalizado com sucesso.")

if __name__ == "__main__":
    executar_pipeline()
