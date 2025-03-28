
import pandas as pd
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def obter_ultima_data_registrada(dados_limpos):
    """Obtém a última data registrada no arquivo CSV de dados limpos."""
    try:
        if not os.path.exists(dados_limpos):
            print("Arquivo CSV não encontrado. Considerando processar limpeza em todos os dados existentes.")
            return None

        df = pd.read_csv(dados_limpos, usecols=["data"], parse_dates=["data"])
        
        if df.empty or df["data"].isna().all():
            print("CSV está vazio ou sem datas válidas. Considerando processar todos os dados.")
            return None

        ultima_data = df["data"].dropna().max().date()  # Garante que a data é válida
        print(f"✅ Última data registrada no CSV: {ultima_data}")
        return ultima_data

    except Exception as e:
        print(f"❌ Erro ao obter última data registrada: {e}")
        return None


def obter_dados_brutos(dados_brutos, ultima_data):
    """Lê apenas os novos dados do CSV e processa corretamente o índice de datas."""
    try:
        df = pd.read_csv(dados_brutos, index_col=0, parse_dates=True, dayfirst=True)
        
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
    """Realiza a limpeza e padronização dos dados de mercado."""

    # Mapeia os nomes das colunas do Yahoo Finance para nomes mais intuitivos
    mapeamento_colunas = {
        'Close': 'preco_fechamento',
        'High': 'preco_maximo',
        'Low': 'preco_minimo',
        'Open': 'preco_abertura',
        'Volume': 'volume'
    }

    # Renomeia as colunas conforme o mapeamento definido
    df.rename(columns=mapeamento_colunas, inplace=True)

    # Remove entradas duplicadas no índice faz uma cópia 
    df = df[~df.index.duplicated(keep="first")].copy()

    # Cria colunas data e hora, extraídas do índice
    df['data'] = df.index.date
    df['hora'] = df.index.time

    # Remove o nome do índice para evitar conflitos ao resetá-lo
    df.index.name = None

    # Reseta o índice, pois a data já foi extraída para uma coluna separada
    df.reset_index(drop=True, inplace=True)

    # Converte e arredonda colunas numéricas para evitar erros e manter consistência nos valores
    for col in ['preco_abertura', 'preco_minimo', 'preco_maximo', 'preco_fechamento']:
        df[col] = pd.to_numeric(df[col], errors='coerce').round(2)

    # Converte a coluna 'volume' para número inteiro, tratando erros e valores inválidos
    df['volume'] = pd.to_numeric(df['volume'], errors='coerce', downcast='integer')

    # Converte a coluna 'data' para formato datetime para facilitar operações futuras
    df['data'] = pd.to_datetime(df['data'])

    # Remove as linhas onde TODAS as colunas numéricas são NaN
    df.dropna(subset=['preco_abertura', 'preco_minimo', 'preco_maximo', 'preco_fechamento', 'volume'], how='all', inplace=True)

    # Reorganiza as colunas
    df = df[['data', 'hora', 'preco_abertura', 'preco_minimo', 'preco_maximo', 'preco_fechamento', 'volume']]

    # Ordena os dados da data mais recente para a mais antiga
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
    dados_brutos = '/content/Piloto_Day_Trade/data/dados_brutosv2.csv' 
    dados_limpos = '/content/Piloto_Day_Trade/data/dados_limposv2.csv'
    df = processar_limpeza(dados_brutos, dados_limpos)
    if df is not None:
        df.to_csv(dados_limpos, index=False)
