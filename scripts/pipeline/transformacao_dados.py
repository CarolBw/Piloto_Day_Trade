
"""
Função de Transformação de Dados para Modelagem Preditiva
Processa e transforma os dados para análise e previsão, gerando um conjunto
de características para serem utilizadas no treinamento dos modelos.

Objetivos:
- Criar um dataset com variáveis relevantes para o modelo.
- Incluir indicadores técnicos, estatísticas de volatilidade, médias móveis e outras features.
- Permitir a experimentação com diferentes combinações de features.

Estratégia:
- Durante os testes de parametrização e treinamento, serão geradas diferentes versões do dataset,
refinando a seleção de features a medida que geramos acurácia.

"""

import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def carregar_dados(arquivo):
    """Carrega um CSV e retorna um DataFrame, ou um DataFrame vazio se o arquivo não existir."""
    if isinstance(arquivo, pd.DataFrame):
        return arquivo  # Se já for um DataFrame, retorna diretamente

    if not os.path.exists(arquivo):
        print(f"O arquivo {arquivo} não existe. Criando um novo DataFrame vazio.")
        return pd.DataFrame()

    try:
        df = pd.read_csv(arquivo, parse_dates=["data"])
        print(f"Arquivo {arquivo} carregado com {len(df)} linhas.")
        return df if not df.empty else pd.DataFrame()
    except Exception as e:
        print(f"Erro ao carregar {arquivo}: {e}")
        return pd.DataFrame()

def obter_ultima_data(df):
    """Retorna a última data disponível nos dados."""
    if "data" in df.columns and not df.empty:
        ultima_data = df["data"].max()
        print(f"Última data encontrada nos dados: {ultima_data}")
        return ultima_data
    return None

def filtrar_novos_dados(df, ultima_data):
    """Filtra os dados para incluir apenas os novos registros."""
    if df.empty:
        print("Nenhum dado limpo disponível.")
        return pd.DataFrame()

    if ultima_data:
        df_novo = df[df["data"] > ultima_data]
        print(f"Dados novos filtrados: {len(df_novo)} registros encontrados.")
        return df_novo
    return df

def calcular_indicadores(df):
    """Calcula indicadores técnicos e gera novas features para análise de dados financeiros."""

    if df.empty:
        print("Nenhum dado disponível para calcular indicadores.")
        return df

    colunas_necessarias = ["data", "hora", "abertura", "minimo", "maximo", "fechamento", "volume"]

    if not all(col in df.columns for col in colunas_necessarias):
        print("Dados insuficientes para cálculo de indicadores.")
        return df

    # Ordenação correta dos dados
    df = df.sort_values(by=['data', 'hora'], ascending=[True, True])

    # Cálculo do retorno percentual e volatilidade
    df['retorno'] = df['fechamento'].pct_change()
    df['volatilidade'] = df['retorno'].rolling(20).std()

    # Médias móveis
    df['SMA_10'] = df['fechamento'].rolling(10).mean()
    df['EMA_10'] = df['fechamento'].ewm(span=10, adjust=False).mean()

    # MACD e linha de sinal
    df['MACD'] = df['fechamento'].ewm(span=12).mean() - df['fechamento'].ewm(span=26).mean()
    df['Signal_Line'] = df['MACD'].ewm(span=9).mean()

    # RSI (Índice de Força Relativa)
    ganho = df['retorno'].clip(lower=0)
    perda = -df['retorno'].clip(upper=0)
    media_ganho = ganho.ewm(span=14).mean()
    media_perda = perda.ewm(span=14).mean() + 1e-10
    df['rsi'] = 100 - (100 / (1 + (media_ganho / media_perda)))

    # OBV (On Balance Volume)
    df['OBV'] = (df['volume'] * np.sign(df['fechamento'].diff())).fillna(0).cumsum()

    # Criar lags para fechamento, retorno e volume
    for lag in range(1, 4):
        df[f'fechamento_lag{lag}'] = df['fechamento'].shift(lag)
        df[f'retorno_lag{lag}'] = df['retorno'].shift(lag)
        df[f'volume_lag{lag}'] = df['volume'].shift(lag)

    # Substituir NaN por zero onde necessário
    df.fillna(0, inplace=True)

    # Ordenação final
    df = df.sort_values(by=['data', 'hora'], ascending=[False, True])

    print(f"Indicadores calculados. Tamanho final do DataFrame: {len(df)} linhas.")
    return df

def adicionar_features_temporais(df):
    """Adiciona colunas temporais para análise de séries temporais."""

    if df.empty:
        print("Nenhum dado disponível para processamento.")
        return df

    # Converter 'data' para datetime se necessário
    df['data'] = pd.to_datetime(df['data'], errors='coerce')

    # Criar coluna do dia da semana para entrada e previsão
    df['dia_da_semana_entrada'] = df['data'].dt.weekday  # 0 = Segunda, 6 = Domingo
    df['data_previsao'] = df['data'] + pd.DateOffset(days=1)
    df['dia_da_semana_previsao'] = df['data_previsao'].dt.weekday

    # Ajustar casos de sexta-feira para segunda-feira
    df.loc[df['dia_da_semana_entrada'] == 4, 'data_previsao'] += pd.DateOffset(days=2)
    df['dia_da_semana_previsao'] = df['data_previsao'].dt.weekday

    # Verificar se 'hora' está presente e converter corretamente
    if 'hora' in df.columns:
        df['hora'] = pd.to_datetime(df['hora'].astype(str), format='%H:%M:%S', errors='coerce').dt.time

        # Criar colunas de hora e minuto
        df['hora_num'] = df['hora'].apply(lambda x: x.hour if pd.notnull(x) else np.nan)
        df['minuto'] = df['hora'].apply(lambda x: x.minute if pd.notnull(x) else np.nan)

        # Criar coluna indicando se o mercado está aberto (entre 10h e 17h)
        df['mercado_aberto'] = ((df['hora_num'] >= 10) & (df['hora_num'] <= 17)).astype(int)
    else:
        df['hora_num'] = np.nan
        df['minuto'] = np.nan
        df['mercado_aberto'] = 0

    return df

def transformar_dados(dados_limpos, dados_transformados):
    """Executa o processo de transformação dos dados."""

    df_transformado = carregar_dados(dados_transformados)
    df_limpo = carregar_dados(dados_limpos)


    if df_transformado.empty:
        print("Nenhum dado transformado encontrado. Criando novo DataFrame.")

    ultima_data = obter_ultima_data(df_transformado)
    novos_dados = filtrar_novos_dados(df_limpo, ultima_data)

    if not novos_dados.empty:
        novos_dados = calcular_indicadores(novos_dados)
        novos_dados = adicionar_features_temporais(novos_dados)
        df_final = pd.concat([df_transformado, novos_dados], ignore_index=True) if not df_transformado.empty else novos_dados

        pasta = os.path.dirname(dados_transformados)
        if not os.path.exists(pasta):
            os.makedirs(pasta)
            print(f"Criando diretório: {pasta}")

        df_final.to_csv(dados_transformados, index=False)
        print(f"Dados transformados salvos em {dados_transformados} ({len(df_final)} registros)")
        print(f"Última data disponível nos dados: {df_final['data'].max()}")
        print(f"df_final: {df_final.head(5)}")
        return df_final
    else:
        print("⏭Nenhum novo dado para processar.")
        print(f"Última data disponível nos dados: {df_transformado['data'].max()}")
        print(f"df_transformado: {df_transformado.head(5)}")
        return df_transformado

if __name__ == "__main__":
    path_dados_limpos = '/content/Piloto_Day_Trade/data/dados_limpos.csv'
    path_dados_transformados = '/content/Piloto_Day_Trade/data/dados_transformados_3103.csv'
    df_transformado =transformar_dados(path_dados_limpos, path_dados_transformados)

