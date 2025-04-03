
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def normalizar_dados(arquivo):
    """
    Carrega os dados de um arquivo CSV, aplica normalização e padronização.
    """
    # Carregar dados
    if isinstance(arquivo, pd.DataFrame):
        df = arquivo  # Se já for um DataFrame, usa diretamente
    elif not os.path.exists(arquivo):
        print(f"⚠️ O arquivo {arquivo} não existe. Criando um novo DataFrame vazio.")
        return pd.DataFrame()
    else:
        try:
            df = pd.read_csv(arquivo, parse_dates=["data"])
            print(f"✅ Arquivo {arquivo} carregado com {len(df)} linhas.")
        except Exception as e:
            print(f"❌ Erro ao carregar {arquivo}: {e}")
            return pd.DataFrame()
    
    if df.empty:
        print("⚠️ DataFrame vazio. Nenhuma normalização aplicada.")
        return df
    
    # Inicializar scalers
    scaler_padronizacao = StandardScaler()
    scaler_normalizacao = MinMaxScaler()
    
    # Colunas a serem padronizadas (média 0, desvio padrão 1)
    padronizar_cols = ['retorno', 'volatilidade', 'MACD', 'Signal_Line', 'rsi']
    df[padronizar_cols] = scaler_padronizacao.fit_transform(df[padronizar_cols])
    
    # Colunas a serem normalizadas (escala entre 0 e 1)
    normalizar_cols = ['abertura', 'minimo', 'maximo', 'fechamento', 'volume', 'SMA_10', 'EMA_10', 'OBV',
                       'fechamento_lag1', 'retorno_lag1', 'volume_lag1', 'fechamento_lag2', 'retorno_lag2', 'volume_lag2',
                       'fechamento_lag3', 'retorno_lag3', 'volume_lag3']
    df[normalizar_cols] = scaler_normalizacao.fit_transform(df[normalizar_cols])
    
    # Variáveis categóricas (convertidas para inteiro)
    categoricas = ['dia_da_semana_entrada', 'dia_da_semana_previsao', 'hora_num', 'minuto', 'mercado_aberto']
    df[categoricas] = df[categoricas].astype(int)
    
    # Converter datas para formato adequado
    df['data_previsao'] = pd.to_datetime(df['data_previsao'])
    df['data'] = pd.to_datetime(df['data'])
    
    return df

if __name__ == "__main__":    
    # Definir caminho do arquivo de entrada
    caminho_arquivo = "/content/Piloto_Day_Trade/data/dados_transformados15.csv"
    
    # Normalizar e padronizar os dados
    df_normalizado = normalizar_dados(caminho_arquivo)  
    
    # Salvar os dados normalizados
    caminho_saida = "/content/Piloto_Day_Trade/data/dados_normalizados15.csv"
    df_normalizado.to_csv(caminho_saida, index=False)    
    
    print(f"✅ Dataset normalizado e padronizado salvo com sucesso.")
    print(df_normalizado.head(5))
