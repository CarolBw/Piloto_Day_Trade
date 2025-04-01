
import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def carregar_dados(arquivo):
    """Carrega um CSV e retorna um DataFrame, ou um DataFrame vazio se o arquivo não existir."""
    if isinstance(arquivo, pd.DataFrame):
        return arquivo  # Se já for um DataFrame, retorna diretamente
    
    if not os.path.exists(arquivo):
        print(f"⚠️ Arquivo não encontrado: {arquivo}")
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(arquivo, parse_dates=["data"])
        return df if not df.empty else pd.DataFrame()
    except Exception as e:
        print(f"❌ Erro ao carregar {arquivo}: {e}")
        return pd.DataFrame()

def obter_ultima_data(df):
    """Retorna a última data disponível nos dados."""
    return df["data"].max() if "data" in df.columns and not df.empty else None

def filtrar_novos_dados(df, ultima_data):
    """Filtra os dados para incluir apenas os novos registros."""
    if df.empty:
        print("⚠️ Nenhum dado limpo disponível.")
        return pd.DataFrame()
    return df[df["data"] > ultima_data] if ultima_data else df

def calcular_indicadores(df):
    """Calcula indicadores técnicos."""
    if df.empty:
        print("⚠️ Nenhum dado para calcular indicadores.")
        return df
    
    colunas_necessarias = ["data", "fechamento", "volume"]
    if not all(col in df.columns for col in colunas_necessarias):
        print("❌ Dados insuficientes para cálculo de indicadores.")
        return df
    
    df = df.sort_values("data")
    df['retorno'] = df['fechamento'].pct_change().fillna(0)
    df['volatilidade'] = df['retorno'].rolling(20).std().fillna(0)
    df['SMA_10'] = df['fechamento'].rolling(10).mean().fillna(0)
    df['EMA_10'] = df['fechamento'].ewm(span=10, adjust=False).mean()
    
    df['MACD'] = df['fechamento'].ewm(span=12).mean() - df['fechamento'].ewm(span=26).mean()
    df['Signal_Line'] = df['MACD'].ewm(span=9).mean()
    
    scaler = MinMaxScaler()
    df[['fechamento_normalizado', 'volume_normalizado']] = scaler.fit_transform(df[['fechamento', 'volume']])
    
    df = df.sort_values['data', 'hora'], ascending=[False, True]
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
        
        pasta = os.path.dirname(dados_transformados)
        if not os.path.exists(pasta):
            os.makedirs(pasta)
            print(f"📂 Criando diretório: {pasta}")
        
        df_final.to_csv(dados_transformados, index=False)
        print(f"✅ Dados transformados salvos em {dados_transformados}")
        return df_final
    else:
        print("⏭️ Nenhum novo dado para processar.")
        return df_transformado

if __name__ == "__main__":
    dados_limpos = '/content/Piloto_Day_Trade/data/dados_limpos_3103.csv'
    dados_transformados = '/content/Piloto_Day_Trade/data/dados_transformados_3103.csv'
    
    df_transformado = processar_transformacao(dados_limpos, dados_transformados)
    
    if df_transformado.empty:
        print("⚠️ Nenhum dado transformado para salvar.")
