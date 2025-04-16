
"""
Relatório do Processo de Transformação de Dados

O processo de transformação de dados segue as seguintes etapas:

Entrada de Dados
- Fonte: `/data/cleaned/dados_limpos.csv`
- Formato: CSV com colunas padrão (`data`, `hora`, `abertura`, `minimo`, `maximo`, `fechamento`, `volume`).

Identificação de Novos Dados
- Os dados transformados previamente são carregados de `/data/transformed/dados_transformados.csv`.
- A última data registrada nos dados transformados é usada como referência.
- Somente os registros com `data` posterior são considerados novos e seguem para transformação, com excessão da excecução do primeiro bloco.

Cálculo de Indicadores Técnicos
- Volatilidade (Desvio Padrão 20 períodos)
- Médias móveis:  
  - Simples (SMA_10)  
  - Exponencial (EMA_10)  
- MACD e Linha de Sinal
- RSI (Índice de Força Relativa)
- OBV (On-Balance Volume)
- ADX (Índice Direcional Médio)
- Bandas de Bollinger
- Estocástico (%K e %D)
- CCI (Commodity Channel Index)
- ATR (Average True Range)
- Lags (1 a 3 períodos)
  - Fechamento  
  - Retorno  
  - Volume

Geração de Features Temporais
- Dia da semana da entrada e da previsão
- Hora do dia e minuto convertidos para numérico

Geração de Features Diárias
- Fechamento do dia
- Volume diário
- Máximo e mínimo do dia
- Mesmas variáveis do **dia anterior

União dos Dados
- Os novos registros transformados são concatenados com os dados antigos (se existirem).
- São eliminadas linhas com `NaN` em variáveis críticas (`fechamento`, `retorno`, SMA, EMA, MACD, RSI).

Exportação
- O resultado final é salvo no caminho especificado:  
  `/data/transformed/dados_transformados.csv`
- Log de quantas linhas foram perdidas com `dropna` e quantos registros finais foram salvos.

Esperado:
- Dados prontos para modelagem preditiva
- Script otimizdo para processar uma primeira entrada e tambem dados novos de forma incrmental.

"""

import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# Carrega variáveis de ambiente a partir de um arquivo .env
load_dotenv()

# Função para carregar os dados limpos
def carregar_dados(arquivo):
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

# Retorna a data mais recente da coluna 'data' 
def obter_ultima_data(df):
    return df["data"].max() if "data" in df.columns and not df.empty else None

# Filtra dados com datas posteriores à última data existente
def filtrar_novos_dados(df, ultima_data):
    return df[df["data"] > ultima_data] if ultima_data else df

# Calcula indicadores técnicos clássicos e adiciona novas colunas
def calcular_indicadores(df):
    if df.empty or not all(c in df.columns for c in ['data', 'hora', 'abertura', 'minimo', 'maximo', 'fechamento', 'volume']):
        return df

    df = df.sort_values(by=['data', 'hora'])

    # Retorno intradiário
    df['retorno'] = df['fechamento'].pct_change()

    # Médias móveis
    df['SMA_10'] = df['fechamento'].rolling(10).mean()
    df['EMA_10'] = df['fechamento'].ewm(span=10).mean()

    # MACD e linha de sinal
    df['MACD'] = df['fechamento'].ewm(span=12).mean() - df['fechamento'].ewm(span=26).mean()
    df['Signal_Line'] = df['MACD'].ewm(span=9).mean()

    # RSI
    ganho = df['retorno'].clip(lower=0)
    perda = -df['retorno'].clip(upper=0)
    media_ganho = ganho.ewm(span=14).mean()
    media_perda = perda.ewm(span=14).mean() + 1e-10
    df['rsi'] = 100 - (100 / (1 + media_ganho / media_perda))

    # OBV (On-Balance Volume)
    df['OBV'] = (df['volume'] * np.sign(df['fechamento'].diff())).fillna(0).cumsum()

    # ADX
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

    # Bandas de Bollinger
    df['BB_MA20'] = df['fechamento'].rolling(20).mean()
    df['BB_STD20'] = df['fechamento'].rolling(20).std()
    df['BB_upper'] = df['BB_MA20'] + (2 * df['BB_STD20'])
    df['BB_lower'] = df['BB_MA20'] - (2 * df['BB_STD20'])

    # Estocástico %K e %D
    low14 = df['minimo'].rolling(14).min()
    high14 = df['maximo'].rolling(14).max()
    df['%K'] = 100 * ((df['fechamento'] - low14) / (high14 - low14 + 1e-10))
    df['%D'] = df['%K'].rolling(3).mean()

    # CCI (Commodity Channel Index)
    tp = (df['maximo'] + df['minimo'] + df['fechamento']) / 3
    cci_ma = tp.rolling(20).mean()
    cci_std = tp.rolling(20).std()
    df['CCI'] = (tp - cci_ma) / (0.015 * cci_std + 1e-10)

    # ATR
    df['ATR'] = atr

    # Lags de fechamento, retorno e volume
    for lag in range(1, 4):
        df[f'fechamento_lag{lag}'] = df['fechamento'].shift(lag)
        df[f'retorno_lag{lag}'] = df['retorno'].shift(lag)
        df[f'volume_lag{lag}'] = df['volume'].shift(lag)

    return df

# Adiciona colunas temporais com base na data e hora dos registros
def adicionar_features_temporais(df):
    if df.empty:
        return df

    df['data'] = pd.to_datetime(df['data'], errors='coerce')
    df['dia_da_semana_entrada'] = df['data'].dt.weekday
    df.loc[df['dia_da_semana_entrada'] == 4, 'dia_da_semana_previsao'] = (df['data'] + pd.DateOffset(days=3)).dt.weekday

    if 'hora' in df.columns:
        df['hora'] = pd.to_datetime(df['hora'].astype(str), format='%H:%M:%S', errors='coerce').dt.time
        df['hora_num'] = df['hora'].apply(lambda x: x.hour if pd.notnull(x) else np.nan)
        df['minuto'] = df['hora'].apply(lambda x: x.minute if pd.notnull(x) else np.nan)
    else:
        df['hora_num'] = np.nan
        df['minuto'] = np.nan

    return df

# Adiciona agregações diárias como fechamento, volume, máximos e mínimos
def adicionar_features_diarias(df):
    if df.empty:
        return df

    df['volume'] = df['volume'].astype(int)
    df['fechamento_dia'] = df.groupby('data')['fechamento'].transform('last')
    df['volume_dia'] = df.groupby('data')['volume'].transform('sum').fillna(0).astype(int)
    df['maximo_dia'] = df.groupby('data')['maximo'].transform('max')
    df['minimo_dia'] = df.groupby('data')['minimo'].transform('min')

    # Lags dos dados diários
    df['fechamento_dia_anterior'] = df['fechamento_dia'].shift(1)
    df['volume_dia_anterior'] = df['volume_dia'].shift(1).fillna(0).astype(int)
    df['maximo_dia_anterior'] = df['maximo_dia'].shift(1)
    df['minimo_dia_anterior'] = df['minimo_dia'].shift(1)

    return df

def calcular_volatilidade(df, janela=20):
    df = df_transformado.copy()    
    # Garantir ordenação correta
    df = df.sort_values(['data', 'hora']).reset_index(drop=True)    
    # Calcular retorno logarítmico
    df['retorno_log'] = np.log(df['fechamento'] / df['fechamento'].shift(1))    
    # Calcular volatilidade como desvio padrão dos retornos log
    df['volatilidade'] = df['retorno_log'].rolling(window=janela, min_periods=1).std()    
    return df

# Função principal de transformação de dados: carrega, calcula, junta e salva
def transformar_dados(dados_limpos, dados_transformados):
    df_transformado = carregar_dados(dados_transformados)
    df_limpo = carregar_dados(dados_limpos)
    ultima_data = obter_ultima_data(df_transformado)
    novos_dados = filtrar_novos_dados(df_limpo, ultima_data)

    if not novos_dados.empty:
        novos_dados = calcular_indicadores(novos_dados)
        novos_dados = adicionar_features_temporais(novos_dados)
        novos_dados = adicionar_features_diarias(novos_dados)
        novos_dados = calcular_volatilidade(novos_dados)

        df_final = pd.concat([df_transformado, novos_dados], ignore_index=True) if not df_transformado.empty else novos_dados

        # Remove linhas com dados essenciais faltando
        linhas_antes = len(df_final)
        df_final = df_final.dropna(subset=['fechamento', 'retorno', 'SMA_10', 'EMA_10', 'MACD', 'rsi'])
        linhas_depois = len(df_final)
        print(f"Linhas perdidas no dropna: {linhas_antes - linhas_depois}")

        # Garante que o diretório exista e salva o csv de dados transformados
        os.makedirs(os.path.dirname(dados_transformados), exist_ok=True)
        df_final.to_csv(dados_transformados, index=False)
        print(f"Dados transformados salvos em {dados_transformados} ({len(df_final)} registros)")
        return df_final

    print("Nenhum novo dado para processar.")
    return df_transformado

# Execução
if __name__ == "__main__":
    path_dados_limpos = '/content/Piloto_Day_Trade/data/cleaned/dados_limpos.csv'
    path_dados_transformados = '/content/Piloto_Day_Trade/data/transformed/dados_transformados.csv'
    df_transformado = transformar_dados(path_dados_limpos, path_dados_transformados)
    print(df_transformado.head(22))
