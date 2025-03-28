
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
            print("Arquivo .csv de dados limpos não encontrado.") 
            print("Considerando processar limpeza em todos os dados existentes no .csv de dados brutos.")
            return None

        df = pd.read_csv(dados_limpos, usecols=["data"], parse_dates=["data"])
        
        if df.empty or df["data"].isna().all():
            print(".csv está vazio ou sem datas válidas. Considerando processar todos os dados.")
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

import pandas as pd

def limpar_organizar_dados(df):
    """Realiza a limpeza e padronização dos dados de mercado sem alterar a hora original,
    garantindo que apenas registros entre 10h e 18h em dias úteis sejam mantidos."""

    # Mapeamento das colunas para nomes padronizados
    mapeamento_colunas = {
        'Close': 'preco_fechamento',
        'High': 'preco_maximo',
        'Low': 'preco_minimo',
        'Open': 'preco_abertura',
        'Volume': 'volume'
    }

    # Renomeia as colunas
    df.rename(columns=mapeamento_colunas, inplace=True)

    # Remove entradas duplicadas no índice
    df = df[~df.index.duplicated(keep="first")].copy()

    # Garante que o índice está em formato datetime correto e sem fuso horário
    df.index = pd.to_datetime(df.index, utc=True).tz_convert(None)

    # Cria colunas separadas para data e hora, mantendo o horário exato da série
    df['data'] = df.index.date  # Mantém apenas a data
    df['hora'] = df.index.strftime('%H:%M:%S')  # Preserva a hora exata no formato correto

    # Remove o nome do índice e reseta para evitar conflitos
    df.index.name = None
    df.reset_index(drop=True, inplace=True)

    # Converte e arredonda colunas numéricas
    for col in ['preco_abertura', 'preco_minimo', 'preco_maximo', 'preco_fechamento']:
        df[col] = pd.to_numeric(df[col], errors='coerce').round(2)

    # Converte volume para número inteiro
    df['volume'] = pd.to_numeric(df['volume'], errors='coerce', downcast='integer')

    # Converte a coluna 'data' para datetime
    df['data'] = pd.to_datetime(df['data'])

    # Filtra apenas dias úteis (segunda a sexta)
    df = df[df['data'].dt.weekday < 5]

    # Filtra apenas horários entre 10:00 e 18:00
    df = df[(df['hora'] >= '10:00:00') & (df['hora'] <= '18:00:00')]

    # Remove apenas linhas onde TODAS as colunas numéricas são NaN
    df.dropna(subset=['preco_abertura', 'preco_minimo', 'preco_maximo', 'preco_fechamento', 'volume'], how='all', inplace=True)

    # Reorganiza as colunas na ordem desejada
    df = df[['data', 'hora', 'preco_abertura', 'preco_minimo', 'preco_maximo', 'preco_fechamento', 'volume']]

    # Ordena os dados da data mais recente para a mais antiga
    return df.sort_values(by=['data', 'hora'], ascending=False)

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
    dados_brutos = '/content/Piloto_Day_Trade/data/dados_brutos.csv' 
    dados_limpos = '/content/Piloto_Day_Trade/data/dados_limposv2.csv'
    df = processar_limpeza(dados_brutos, dados_limpos)
    if df is not None:
        df.to_csv(dados_limpos, index=False)
