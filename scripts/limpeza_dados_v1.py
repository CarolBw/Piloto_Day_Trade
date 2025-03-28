
import pandas as pd
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
dados_brutos = os.getenv('dados_brutos')
dados_limpos = os.getenv('dados_limpos')

def obter_ultima_data_registrada(dados_limpos):
    """Obtém a última data registrada no arquivo CSV de dados limpos."""
    try:
        ultimo_registro = pd.read_csv(csv_dados_limpos, usecols=["data"], parse_dates=["data"]).tail(1)
        if not ultimo_registro.empty:
            ultima_data = ultimo_registro.iloc[0]["data"].date()
            print(f"✅ Última data registrada no CSV: {ultima_data}")
            return ultima_data
    except FileNotFoundError:
        print("⚠️ Arquivo CSV não encontrado. Considerando início sem dados prévios.")
    except Exception as e:
        print(f"❌ Erro ao obter última data registrada: {e}")
    return None

def obter_dados_brutos(dados_brutos, ultima_data):
    """Lê apenas os novos dados do CSV e processa corretamente o índice de datas."""
    try:
        df = pd.read_csv(csv_dados_brutos, index_col=0, parse_dates=True, dayfirst=True)
        
        df.index = pd.to_datetime(df.index, errors='coerce').tz_localize(None)
        df = df[df.index.notna()]
        df.columns = df.columns.str.strip()
        
        if ultima_data:
            ontem = datetime.today().date()  # Agora inclui até ontem
            df = df[(df.index.date > ultima_data) & (df.index.date <= ontem)]
        
        return df if not df.empty else None
    except Exception as e:
        print(f"❌ Erro ao obter dados brutos: {e}")
        return None

def limpar_organizar_dados(df):
    """Realiza a limpeza e padronização dos dados."""
    mapeamento_colunas = {
        'Close': 'preco_fechamento',
        'High': 'preco_maximo',
        'Low': 'preco_minimo',
        'Open': 'preco_abertura',
        'Volume': 'volume'
    }
    
    df.rename(columns=mapeamento_colunas, inplace=True)
    df = df[~df.index.duplicated(keep="first")]
    df['data'] = df.index.date
    df['hora'] = df.index.time
    df.index.name = None
    df.reset_index(drop=True, inplace=True)
    
    df['preco_abertura'] = df['preco_abertura'].astype(float).round(2)
    df['preco_minimo'] = df['preco_minimo'].astype(float).round(2)
    df['preco_maximo'] = df['preco_maximo'].astype(float).round(2)
    df['preco_fechamento'] = df['preco_fechamento'].astype(float).round(2)
    df['volume'] = pd.to_numeric(df['volume'], errors='coerce', downcast='integer')
    df['data'] = pd.to_datetime(df['data'])
  
    df = df[['data', 'hora', 'preco_abertura', 'preco_minimo', 'preco_maximo', 'preco_fechamento', 'volume']]
    return df.sort_values(by='data', ascending=False)

def processar_limpeza(dados_brutos, dados_limpos):
    """Executa o processo de limpeza dos dados."""
    ultima_data = obter_ultima_data_registrada(dados_limpos)
    df = obter_dados_brutos(dados_brutos, ultima_data)
    
    if df is None:
        print("Nenhum novo dado para processar limpeza de dados.")
        return None
    
    df = limpar_organizar_dados(df)
    print(f"Processando limpeza para dados até {df['data'].max().date()}")
    print("\nAmostra dos dados limpos:\n", df.head())
    print("\nDados limpos e prontos para inserção no banco de dados.")
    return df

if __name__ == "__main__":
    df = processar_limpeza(dados_brutos, dados_limpos)
    if df is not None:
        df.to_csv('/content/Piloto_Day_trade_BBDC4/data/dados_limpos.csv', index=False)
