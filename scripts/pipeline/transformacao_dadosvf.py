
#@title Transformação de dados

"""
Script de Transformação de Dados - Piloto Day Trade

Este script realiza o processo de transformação dos dados financeiros, incluindo o cálculo de indicadores técnicos,
adição de características temporais e diárias, além de filtrar novos dados a partir da última data registrada.
"""

import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv

load_dotenv()

def carregar_dados(arquivo):
    """
    Carrega dados de um arquivo CSV ou retorna o DataFrame se já for fornecido como argumento.

    Parâmetros:
    Caminho do arquivo ou DataFrame a ser carregado.

    Retorna:
    Dados carregados a partir do arquivo ou argumento.
    """
    if isinstance(arquivo, pd.DataFrame):
        return arquivo
    if not os.path.exists(arquivo):
        print(f"O arquivo {arquivo} não existe.")
        return pd.DataFrame()
    try:
        return pd.read_csv(arquivo, parse_dates=["data"])
    except Exception as e:
        print(f"Erro ao carregar {arquivo}: {e}")
        return pd.DataFrame()

def obter_ultima_data(df):
    """
    Retorna a última data registrada no DataFrame.

    Parâmetros:
    df (pd.DataFrame): O DataFrame a ser analisado.

    Retorna:
    datetime: Última data registrada no DataFrame ou None se não houver dados.
    """
    return df["data"].max() if "data" in df.columns and not df.empty else None

def filtrar_novos_dados(df, ultima_data):
    """
    Filtra os dados para obter apenas os registros com data posterior à última data fornecida.

    Parâmetros:
    O DataFrame a ser filtrado.
    A última data registrada nos dados transformados.

    Retorna:
    pd.DataFrame: Dados filtrados com data posterior à última data.
    """
    return df[df["data"] > ultima_data] if ultima_data else df

def calcular_indicadores(df):
    """
    Calcula indicadores técnicos financeiros e adiciona novas colunas ao DataFrame.

    Parâmetros:
    O DataFrame com dados financeiros que será transformado.

    Retorna:
    DataFrame com as colunas dos indicadores calculados.
    """
    # Verifica se o DataFrame possui as colunas necessárias para cálculo dos indicadores
    if df.empty or not all(c in df.columns for c in ['data', 'hora', 'abertura', 'minimo', 'maximo', 'fechamento', 'volume']):
        return df

    # Ordena os dados por data e hora
    df = df.sort_values(by=['data', 'hora'])

    # Calcula o retorno percentual
    df['retorno'] = df['fechamento'].pct_change()

    # Calcula volatilidade, médias móveis e outros indicadores
    df['volatilidade'] = df['retorno'].rolling(20).std()
    # Substituir os primeiros NaN por 0
    df['volatilidade'] = df['volatilidade'].fillna(0)
    df['SMA_10'] = df['fechamento'].rolling(10).mean()
    df['EMA_10'] = df['fechamento'].ewm(span=10).mean()
    df['MACD'] = df['fechamento'].ewm(span=12).mean() - df['fechamento'].ewm(span=26).mean()
    df['Signal_Line'] = df['MACD'].ewm(span=9).mean()

    # Cálculo do índice de força relativa (RSI)
    ganho = df['retorno'].clip(lower=0)
    perda = -df['retorno'].clip(upper=0)
    media_ganho = ganho.ewm(span=14).mean()
    media_perda = perda.ewm(span=14).mean() + 1e-10
    df['rsi'] = 100 - (100 / (1 + media_ganho / media_perda))

    # Cálculo do On-Balance Volume (OBV)
    df['OBV'] = (df['volume'] * np.sign(df['fechamento'].diff())).fillna(0).cumsum()

    # Cálculo do ADX e outros indicadores de tendência
    delta_high = df['maximo'].diff()
    delta_low = -df['minimo'].diff()
    plus_dm = np.where((delta_high > delta_low) & (delta_high > 0), delta_high, 0)
    minus_dm = np.where((delta_low > delta_high) & (delta_low > 0), delta_low, 0)
    tr1 = df['maximo'] - df['minimo']
    tr2 = abs(df['maximo'] - df['fechamento'].shift())
    tr3 = abs(df['minimo'] - df['fechamento'].shift())
    tr = np.max([tr1, tr2, tr3], axis=0)
    atr = pd.Series(tr).rolling(14).mean()
    df['ADX'] = 100 * abs((pd.Series(plus_dm).rolling(14).mean() - pd.Series(minus_dm).rolling(14).mean()) /
                          (pd.Series(plus_dm).rolling(14).mean() + pd.Series(minus_dm).rolling(14).mean() + 1e-10)).rolling(14).mean()

    # Calcula as Bandas de Bollinger
    df['BB_MA20'] = df['fechamento'].rolling(20).mean()
    df['BB_STD20'] = df['fechamento'].rolling(20).std()
    df['BB_upper'] = df['BB_MA20'] + (2 * df['BB_STD20'])
    df['BB_lower'] = df['BB_MA20'] - (2 * df['BB_STD20'])

    # Calcula o Stochastic Oscillator (%K e %D)
    low14 = df['minimo'].rolling(14).min()
    high14 = df['maximo'].rolling(14).max()
    df['%K'] = 100 * ((df['fechamento'] - low14) / (high14 - low14 + 1e-10))
    df['%D'] = df['%K'].rolling(3).mean()

    # Calcula o Commodity Channel Index (CCI)
    tp = (df['maximo'] + df['minimo'] + df['fechamento']) / 3
    cci_ma = tp.rolling(20).mean()
    cci_std = tp.rolling(20).std()
    df['CCI'] = (tp - cci_ma) / (0.015 * cci_std + 1e-10)

    # Inclui a volatilidade (ATR)
    df['ATR'] = atr

    # Cria colunas com lags de fechamento, retorno e volume
    for lag in range(1, 4):
        df[f'fechamento_lag{lag}'] = df['fechamento'].shift(lag)
        df[f'retorno_lag{lag}'] = df['retorno'].shift(lag)
        df[f'volume_lag{lag}'] = df['volume'].shift(lag)

    return df

def adicionar_features_temporais(df):
    """
    Adiciona características temporais ao DataFrame, como o dia da semana e hora numérica.

    Parâmetros:
    df (pd.DataFrame): O DataFrame com dados financeiros.

    Retorna:
    pd.DataFrame: DataFrame com as características temporais adicionadas.
    """
    if df.empty:
        return df

    # Adiciona o dia da semana e a previsão do dia da semana
    df['data'] = pd.to_datetime(df['data'], errors='coerce')
    df['dia_da_semana_entrada'] = df['data'].dt.weekday
    df.loc[df['dia_da_semana_entrada'] == 4, 'dia_da_semana_previsao'] = (df['data'] + pd.DateOffset(days=3)).dt.weekday

    # Adiciona hora e minuto
    if 'hora' in df.columns:
        df['hora'] = pd.to_datetime(df['hora'].astype(str), format='%H:%M:%S', errors='coerce').dt.time
        df['hora_num'] = df['hora'].apply(lambda x: x.hour if pd.notnull(x) else np.nan)
        df['minuto'] = df['hora'].apply(lambda x: x.minute if pd.notnull(x) else np.nan)
    else:
        df['hora_num'] = np.nan
        df['minuto'] = np.nan

    return df

def adicionar_features_diarias(df):
    """
    Adiciona características diárias, como fechamento, volume e máximos/mínimos diários.

    Parâmetros:
    df (pd.DataFrame): O DataFrame com dados financeiros.

    Retorna:
    pd.DataFrame: DataFrame com as características diárias adicionadas.
    """
    if df.empty:
        return df

    # Adiciona características diárias, agrupadas por data
    df['fechamento_dia'] = df.groupby('data')['fechamento'].transform('last')
    df['volume_dia'] = df.groupby('data')['volume'].transform('sum')
    df['maximo_dia'] = df.groupby('data')['maximo'].transform('max')
    df['minimo_dia'] = df.groupby('data')['minimo'].transform('min')

    # Adiciona as características do dia anterior
    df['fechamento_dia_anterior'] = df['fechamento_dia'].shift(1)
    df['volume_dia_anterior'] = df['volume_dia'].shift(1).fillna(0).astype(int)
    df['maximo_dia_anterior'] = df['maximo_dia'].shift(1)
    df['minimo_dia_anterior'] = df['minimo_dia'].shift(1)

    return df

def transformar_dados(dados_limpos, dados_transformados):
    """
    Função principal para carregar, filtrar, calcular indicadores e transformar os dados financeiros.

    Parâmetros:
    dados_limpos: Caminho para os dados limpos a serem processados.
    dados_transformados: Caminho onde os dados transformados serão salvos.

    Retorna:
    DataFrame com os dados transformados.
    """
    # Carrega os dados limpos e transformados
    df_transformado = carregar_dados(dados_transformados)
    df_limpo = carregar_dados(dados_limpos)

    # Obtem a última data dos dados transformados
    ultima_data = obter_ultima_data(df_transformado)

    # Filtra os dados limpos para obter apenas os novos dados
    novos_dados = filtrar_novos_dados(df_limpo, ultima_data)

    if not novos_dados.empty:
        # Calcula os indicadores e adiciona as features temporais e diárias
        novos_dados = calcular_indicadores(novos_dados)
        novos_dados = adicionar_features_temporais(novos_dados)
        novos_dados = adicionar_features_diarias(novos_dados)

        # Concatena os novos dados com os dados transformados existentes
        df_final = pd.concat([df_transformado, novos_dados], ignore_index=True) if not df_transformado.empty else novos_dados

        # Remove registros com valores ausentes
        linhas_antes = len(df_final)
        df_final = df_final.dropna(subset=['fechamento', 'retorno', 'SMA_10', 'EMA_10', 'MACD', 'rsi'])
        linhas_depois = len(df_final)
        print(f"Linhas perdidas no dropna: {linhas_antes - linhas_depois}")

        # Salva os dados transformados
        os.makedirs(os.path.dirname(dados_transformados), exist_ok=True)
        df_final.to_csv(dados_transformados, index=False)
        print(f"Dados transformados salvos em {dados_transformados} ({len(df_final)} registros)")
        return df_final

    else:
        print("Nenhum novo dado para processar.")
        return df_transformado

if __name__ == "__main__":
    # Define os caminhos dos arquivos de dados
    path_dados_limpos = '/content/Piloto_Day_Trade/data/cleaned/dados_limpos.csv'
    path_dados_transformados = '/content/Piloto_Day_Trade/data/transformed/dados_transformados.csv'

    # Executa a transformação de dados
    df_transformado = transformar_dados(path_dados_limpos, path_dados_transformados)
