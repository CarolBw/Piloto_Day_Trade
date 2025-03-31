
import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def carregar_dados(caminho):
    """Carrega um CSV e retorna um DataFrame ou None se não existir."""
    try:
        if os.path.exists(caminho):
            df = pd.read_csv(caminho, parse_dates=["data"])
            return df if not df.empty else pd.DataFrame()
        else:
            print(f"⚠️ Arquivo de dados não encontrado: {caminho}")
            return pd.DataFrame()
    except Exception as e:
        print(f"❌ Erro ao carregar {caminho}: {e}")
        return pd.DataFrame()

def obter_ultima_data(df):
    """Retorna a última data disponível nos dados."""
    return df["data"].max() if not df.empty and "data" in df.columns else None

def filtrar_novos_dados(df, ultima_data):
    """Filtra os dados para incluir apenas os novos registros."""
    if df.empty:
        print("⚠️ Nenhum dado limpo disponível.")
        return pd.DataFrame()
    return df[df["data"] > ultima_data] if ultima_data else df

def calcular_lags(df, colunas, lags=3):
    """Gera variáveis defasadas (lags) para as colunas especificadas."""
    for coluna in colunas:
        for lag in range(1, lags + 1):
            df[f"{coluna}_lag{lag}"] = df[coluna].shift(lag)
    return df

def calcular_indicadores(df):
    """Calcula indicadores técnicos para análise financeira."""
    if df.empty:
        print("⚠️ Nenhum dado para calcular indicadores.")
        return df

    df = df.sort_values("data", ascending=False)
    df['retorno'] = df['fechamento'].pct_change().fillna(0)
    df['volatilidade'] = df['retorno'].rolling(20).std().fillna(0)
    
    df['SMA_10'] = df['fechamento'].rolling(10).mean().fillna(0)
    df['EMA_10'] = df['fechamento'].ewm(span=10, adjust=False).mean()
    
    ganho = df['retorno'].clip(lower=0)
    perda = -df['retorno'].clip(upper=0)
    df['rsi'] = 100 - (100 / (1 + (ganho.ewm(span=14).mean() / (perda.ewm(span=14).mean() + 1e-10))))
    
    df['SMA_20'] = df['fechamento'].rolling(20).mean()
    df['std_dev'] = df['fechamento'].rolling(20).std()
    df['upper_band'] = df['SMA_20'] + 2 * df['std_dev']
    df['lower_band'] = df['SMA_20'] - 2 * df['std_dev']
    
    df['MACD'] = df['fechamento'].ewm(span=12).mean() - df['fechamento'].ewm(span=26).mean()
    df['Signal_Line'] = df['MACD'].ewm(span=9).mean()
    
    df['OBV'] = (df['volume'] * np.sign(df['fechamento'].diff())).fillna(0).cumsum()
    
    # Criar variáveis de defasagem (lags)
    df = calcular_lags(df, ['fechamento', 'retorno', 'volume'], lags=3)
    
    scaler = MinMaxScaler()
    df[['fechamento_normalizado', 'volume_normalizado']] = scaler.fit_transform(df[['fechamento', 'volume']])
    
    std_scaler = StandardScaler()
    df[['rsi_padronizado', 'macd_padronizado']] = std_scaler.fit_transform(df[['rsi', 'MACD']].fillna(0)) 
   
    # Criar colunas de data
    df['ano'] = df['data'].dt.year
    df['mes'] = df['data'].dt.month
    df['dia'] = df['data'].dt.day
    df['dia_da_semana'] = df['data'].dt.weekday  # 0 = segunda-feira, 6 = domingo

    # Corrigir a coluna 'hora'
    df['hora'] = df['hora'].astype(str).str.strip()
    df.loc[~df['hora'].str.contains(":"), 'hora'] += ":00:00"
    df['hora'] = pd.to_datetime(df['hora'], format='%H:%M:%S', errors='coerce').dt.time

    # Criar colunas de hora e minuto
    df['hora_num'] = df['hora'].apply(lambda x: x.hour if pd.notnull(x) else np.nan)
    df['minuto'] = df['hora'].apply(lambda x: x.minute if pd.notnull(x) else np.nan)

    # Criar coluna indicando se o mercado está aberto (entre 10h e 17h)
    df['mercado_aberto'] = ((df['hora_num'] >= 10) & (df['hora_num'] <= 17)).astype(int)
    
    df.dropna(inplace=True)

    return df

def processar_transformacao(dados_limpos, dados_transformados):
    """Executa o processo de transformação dos dados."""
    
    df_transformado = carregar_dados(dados_transformados)
    df_limpo = carregar_dados(dados_limpos)

    if df_transformado is None or df_transformado.empty:
        df_transformado = pd.DataFrame()

    ultima_data = obter_ultima_data(df_transformado)
    novos_dados = filtrar_novos_dados(df_limpo, ultima_data)

    if not novos_dados.empty:
        novos_dados = calcular_indicadores(novos_dados)
        df_final = pd.concat([df_transformado, novos_dados], ignore_index=True) if not df_transformado.empty else novos_dados
        return df_final
    else:
        print("⏭️ Nenhum novo dado para processar.")
        return df_transformado

if __name__ == "__main__":
    dados_limpos = '/content/Piloto_Day_Trade/data/dados_limpos_3003.csv'
    dados_transformados = '/content/Piloto_Day_Trade/data/dados_transformados_finais.csv'

    df_transformado = processar_transformacao(dados_limpos, dados_transformados)

    if not df_transformado.empty:
        print("✅ Os dados foram transformados com sucesso.")
        print("\nAmostra dos dados transformados:\n", df_transformado.head())
        df_transformado.to_csv(dados_transformados, index=False)
        print(f"✅ Dados transformados salvos em {dados_transformados}.")
    else:
        print("⚠️ Nenhum dado transformado para salvar.")
