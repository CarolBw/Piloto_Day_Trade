
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os
import dotenv

dotenv.load_dotenv()

def extrair_dados(ticker, intervalo, dias, dados_brutos):
    """Extrai e complementa dados históricos do Yahoo Finance considerando apenas dias úteis (10h-18h)."""
    df_total = pd.DataFrame()
    extracao_inicial = True
    
    if os.path.exists(dados_brutos):
        try:
            df_total = pd.read_csv(dados_brutos)
            df_total.columns = df_total.columns.str.strip()
            df_total = df_total.dropna()
            df_total.index = pd.to_datetime(df_total.iloc[:, 0], errors='coerce', utc=True)
            df_total = df_total[df_total.index.notna()]
            df_total = df_total.drop(df_total.columns[0], axis=1)
            
            ultima_data = df_total.index.max()
            if pd.isna(ultima_data):
                raise ValueError("Nenhuma data válida encontrada.")
            data_inicio = ultima_data + timedelta(minutes=5)
            extracao_inicial = False
        except Exception as e:
            print(f"Erro ao carregar CSV: {e}. Iniciando do zero.")
            data_inicio = datetime.today() - timedelta(days=dias)
    else:
        data_inicio = datetime.today() - timedelta(days=dias)
    
    data_fim = datetime.today()
    extracao_realizada = False
    
    while data_inicio < data_fim:
        data_fim_bloco = min(data_inicio + timedelta(days=7), data_fim)
        df_novo = yf.download(ticker, start=data_inicio.strftime("%Y-%m-%d"),
                              end=data_fim_bloco.strftime("%Y-%m-%d"), interval=intervalo, progress=True)
        if df_novo.empty:
            break
        df_novo.index = pd.to_datetime(df_novo.index, utc=True)
        df_total = pd.concat([df_total, df_novo])
        data_inicio = data_fim_bloco
        extracao_realizada = True
    
    if extracao_realizada:
        df_total.to_csv(dados_brutos)
        print("Dados atualizados.")
    
    df_total.index = pd.to_datetime(df_total.index, errors='coerce', utc=True)
    df_total = df_total[df_total.index.notna()]
    df_uteis = df_total[(df_total.index.weekday < 5) & (df_total.index.hour >= 10) & (df_total.index.hour < 18)]
    print(f"Dados úteis extraídos: {df_uteis.shape[0]} registros.")
    return df_uteis

if __name__ == "__main__":
    ticker = "BBDC4.SA"
    intervalo = "5m"
    dias = 45
    dados_brutos = "/content/Piloto_Day_Trade/data/dados_brutosv3.csv"
    df = extrair_dados(ticker, intervalo, dias, dados_brutos)
