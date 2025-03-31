
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os
import dotenv

dotenv.load_dotenv()

def extrair_dados(ticker,  dias, intervalo, dados_brutos):
    """Extrai e organiza dados do Yahoo Finance no intervalo correto."""
    
    df_total = pd.DataFrame()  # DataFrame para armazenar os dados
    data_inicio = datetime.today() - timedelta(days=dias)  # Data inicial
    data_fim = datetime.today()  # Data final (hoje)

    # Verifica se o arquivo de dados brutos existe
    if os.path.exists(dados_brutos):
        df = pd.read_csv(dados_brutos, index_col=0, parse_dates=True, )
        
        # Garante que a data é válida

        if not df.empty:
            # Atualiza a data de início para a última data disponível nos dados brutos
            data_inicio = pd.to_datetime(df.index.max()) + timedelta(minutes=5)

    print(f"🔄 Extraindo dados de {data_inicio} até {data_fim}")

    # Extrai os dados do Yahoo Finance
    df_novo = yf.download(ticker, start=data_inicio.strftime("%Y-%m-%d"),
                          end=data_fim.strftime("%Y-%m-%d"), interval=intervalo, progress=True)

    if not df_novo.empty:
        # Ajusta o fuso horário dos dados para "America/Sao_Paulo"
        df_novo.index = df_novo.index.tz_convert("America/Sao_Paulo")

        # Concatena os novos dados com os existentes e remove duplicatas
        df_total = pd.concat([df_total, df_novo])
        df_total = df_total[~df_total.index.duplicated(keep='last')].sort_index()

        # Remove linhas com mais de 50% de valores nulos
        df_total = df_total.dropna(thresh=df_total.shape[1] * 0.5)

        # Salva os dados atualizados no arquivo CSV
        df_total.to_csv(dados_brutos)
        print("✅ Dados salvos com sucesso.")

    # Filtra os dados para o horário entre 10:00 e 18:00
    df_filtrado = df_total.between_time("10:00", "18:00")

    # Exibe os 10 primeiros e os 10 últimos registros
    print("Últimos 10 dados filtrados:")
    print(df_filtrado.tail(10))
    print("Primeiros 10 dados filtrados:")
    print(df_filtrado.head(10))

    return df_filtrado

if __name__ == "__main__":
    ticker = "BBDC4.SA"  # Ticker da ação
    intervalo = "5m"  # Intervalo de tempo (5 minutos)
    dias = 45  # Número de dias a partir de hoje para buscar os dados
    dados_brutos = "/content/Piloto_Day_Trade/data/dados_brutos2.csv"  # Caminho do arquivo de dados brutos
    df = extrair_dados(ticker, intervalo, dias, dados_brutos)
