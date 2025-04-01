
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
        print(f"O arquivo de dados transformados ainda não existe no path.")
        print('Considerando transformar todo o conjunto de dados e criar o arquivo.')
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
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler

def calcular_indicadores(df):
    """Calcula indicadores técnicos e gera novas features para análise de dados financeiros."""
    
    if df.empty:
        print("⚠️ Nenhum dado disponível para calcular indicadores.")
        return df
    
    colunas_necessarias = ["data", "hora", "abertura", "minimo", "maximo", "fechamento", "volume"]
    
    if not all(col in df.columns for col in colunas_necessarias):
        print("❌ Dados insuficientes para cálculo de indicadores.")
        return df
    
    # Ordenação correta dos dados
    df = df.sort_values(by=['data', 'hora'], ascending=[True, True])

    # Cálculo do retorno percentual e volatilidade
    df['retorno'] = df['fechamento'].pct_change().fillna(0)
    df['volatilidade'] = df['retorno'].rolling(20).std().fillna(0)

    # Médias móveis
    df['SMA_10'] = df['fechamento'].rolling(10).mean()
    df['EMA_10'] = df['fechamento'].ewm(span=10, adjust=False).mean()

    # Bandas de Bollinger
    df['SMA_20'] = df['fechamento'].rolling(20).mean()
    df['std_dev'] = df['fechamento'].rolling(20).std()
    df['upper_band'] = df['SMA_20'] + (2 * df['std_dev'])
    df['lower_band'] = df['SMA_20'] - (2 * df['std_dev'])

    # MACD e linha de sinal
    df['MACD'] = df['fechamento'].ewm(span=12).mean() - df['fechamento'].ewm(span=26).mean()
    df['Signal_Line'] = df['MACD'].ewm(span=9).mean()

    # RSI (Índice de Força Relativa)
    ganho = df['retorno'].clip(lower=0)
    perda = -df['retorno'].clip(upper=0)
    media_ganho = ganho.ewm(span=14).mean()
    media_perda = perda.ewm(span=14).mean() + 1e-10  # Evita divisão por zero
    df['rsi'] = 100 - (100 / (1 + (media_ganho / media_perda)))

    # OBV (On Balance Volume)
    df['OBV'] = (df['volume'] * np.sign(df['fechamento'].diff())).fillna(0).cumsum()

    # Criar lags para fechamento, retorno e volume
    for lag in range(1, 4):
        df[f'fechamento_lag{lag}'] = df['fechamento'].shift(lag)
        df[f'retorno_lag{lag}'] = df['retorno'].shift(lag)
        df[f'volume_lag{lag}'] = df['volume'].shift(lag)

    # Normalização e padronização de algumas variáveis
    scaler = MinMaxScaler()
    df[['fechamento_normalizado', 'volume_normalizado']] = scaler.fit_transform(df[['fechamento', 'volume']])

    std_scaler = StandardScaler()
    df[['rsi_padronizado', 'macd_padronizado']] = std_scaler.fit_transform(df[['rsi', 'MACD']].fillna(0))

    # Criar colunas de tempo
    df['ano'] = df['data'].dt.year
    df['mes'] = df['data'].dt.month
    df['dia'] = df['data'].dt.day
    df['dia_da_semana'] = df['data'].dt.weekday  # 0 = segunda-feira, 6 = domingo

    # Ajuste na coluna 'hora'
    df['hora'] = df['hora'].astype(str).str.strip()
    df.loc[~df['hora'].str.contains(":"), 'hora'] += ":00:00"
    df['hora'] = pd.to_datetime(df['hora'], format='%H:%M', errors='coerce').dt.time

    # Criar colunas de hora e minuto
    df['hora_num'] = df['hora'].apply(lambda x: x.hour if pd.notnull(x) else np.nan)
    df['minuto'] = df['hora'].apply(lambda x: x.minute if pd.notnull(x) else np.nan)

    # Criar coluna indicando se o mercado está aberto (entre 10h e 17h)
    df['mercado_aberto'] = ((df['hora_num'] >= 10) & (df['hora_num'] <= 17)).astype(int)

    # Remover valores NaN criados no processo de cálculos
    df.dropna(inplace=True)

    # Ordenação final
    df = df.sort_values(by=['data', 'hora'], ascending=[False, True])

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
