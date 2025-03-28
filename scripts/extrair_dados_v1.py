
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os
import dotenv

dotenv.load_dotenv()

def extrair_dados(ticker, intervalo, dias, dados_brutos):
    """ Realiza a extração dos primeiros 40 dias de dados e mantém os dados recentes a cada iteração """
    extracao_inicial = False
    
    # Verifica se o arquivo de dados brutos já existe
    if os.path.exists(dados_brutos):
        df = pd.read_csv(dados_brutos, index_col=0, parse_dates=True)
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)  # Remove a informação de fuso horário
        df = df.dropna() # Deleta os valores NaN
        df = df.sort_index(ascending=False)  # Ordena da data atual para trás
        ultimo_registro = pd.to_datetime(df.index.max()) # Pega a data do ultimo registro
        print(f"\U0001F4C5 Último registro encontrado: {ultimo_registro}")
        data_inicio = ultimo_registro + timedelta(minutes=5) if not pd.isnull(ultimo_registro) else datetime.today() - timedelta(days=dias)
        extracao_inicial = pd.isnull(ultimo_registro)
    else:
        # Caso os dados brutos ainda não existam, cria um dataframe vazio
        df = pd.DataFrame()
        # Estipula a data de início e quantidade de dias
        data_inicio = datetime.today() - timedelta(days=dias)
        extracao_inicial = True
    
    # Determina a data atual como fim
    data_fim = datetime.today()
    extracao_realizada = False
    print("\U0001F504 Iniciando extração de dados...")
    
    while data_inicio < data_fim:
        data_fim_bloco = min(data_inicio + timedelta(days=7), data_fim)
        print(f"\U0001F4CA Extraindo de {data_inicio} até {data_fim_bloco}")
        df_atual = yf.download(ticker, start=data_inicio.strftime("%Y-%m-%d"),
                               end=data_fim_bloco.strftime("%Y-%m-%d"), interval=intervalo, progress=True)
        
        if df_atual.empty:
            print("⚠️ Nenhum dado novo encontrado.")
            break
        
        df = pd.concat([df, df_atual])
        data_inicio = data_fim_bloco
        extracao_realizada = True
    
    if extracao_realizada:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(0)
            df.index.name = None
        df.to_csv(dados_brutos)
        print("✅ Extração concluída e dados salvos.")
    else:
        print("⏭️ Nenhuma atualização realizada.")
    
    df.index = pd.to_datetime(df.index, errors="coerce", utc=True)
    df_uteis = df[(df.index.weekday < 5) & (df.index.hour >= 10) & 
                  (df.index.hour < 18) & ((df.index.hour != 17) | (df.index.minute <= 10))]
    
    print(f"\U0001F4C8 Total de {df_uteis.index.normalize().nunique()} dias úteis no período das 10h às 17:10h.")
    return df_uteis

if __name__ == "__main__":
    ticker = "BBDC4.SA"
    intervalo = "5m"
    dias = 45
    dados_brutos = "/content/Piloto_Day_trade_BBDC4/data/dados_brutos.csv"
    df = extrair_dados(ticker, intervalo, dias, dados_brutos)
