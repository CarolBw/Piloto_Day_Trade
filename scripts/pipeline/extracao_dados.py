
#@title  Extração de dados

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os
import dotenv
import logging

logging.getLogger("yfinance").setLevel(logging.CRITICAL)
dotenv.load_dotenv()

"""
Essa função tem como objetivo extrair dados históricos de um ativo financeiro do Yahoo Finance
com controle de incremental, salvando tudo em um CSV que serve como base bruta do pipeline.
Etapas:
- Define intervalo de coleta:
- Início: hoje menos dias
- Fim: ontem às 18:10 (ajustado para o fechamento)
- Verifica se já existem dados anteriores salvos (dados_brutos.csv):
- Se sim, tenta encontrar a última data registrada válida e usa como novo início e(xtração incremental).
- Faz a requisição ao Yahoo Finance (yf.download), no intervalo necessário.
- Ajusta o fuso horário dos dados para "America/Sao_Paulo".
- Mescla os dados novos aos antigos (se houver), remove duplicatas e linhas com muitos nulos.
- Salva o conjunto atualizado no CSV.
- Retorna o conjunto de dados atualizado.

"""

def extrair_dados(ticker, dias, intervalo, dados_brutos):
    """Extrai e organiza dados do Yahoo Finance no intervalo correto."""
    df_total = pd.DataFrame()
    data_inicio = data_inicio = (datetime.today() - timedelta(days=dias)).date()
    data_fim = datetime.now().replace(hour=18, minute=10, second=0, microsecond=0) - timedelta(days=1)

    primeira_extracao = True

    if os.path.exists(dados_brutos) and os.path.getsize(dados_brutos) > 0:
        df_temp = pd.read_csv(
            dados_brutos,
            index_col=0,
            parse_dates=True,
            date_format="%Y-%m-%d %H:%M:%S"
        )
        if not df_temp.empty:
            df_temp = df_temp.iloc[2:].copy()
            df_temp.index.name = 'data'
            df_temp = df_temp.reset_index()
            df_temp['data'] = pd.to_datetime(df_temp['data']).dt.date
            ultima_data = pd.to_datetime(df_temp['data'], errors='coerce').max()
            print(f"Última data encontrada: {ultima_data}")

            if pd.notnull(ultima_data):
                data_inicio = ultima_data + timedelta(days=1)
                primeira_extracao = False

    if primeira_extracao:
        print(f"\nPrimeira extração de dados.")
        print(f"Data de início: {data_inicio.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Data de fim: {data_fim.strftime('%Y-%m-%d %H:%M:%S')}\n")
    else:
        print(f"\nExtração complementar a partir de {data_inicio.strftime('%Y-%m-%d %H:%M:%S')}.")
        print(f"Data de fim: {data_fim.strftime('%Y-%m-%d %H:%M:%S')}\n")

    df_novo = yf.download(
        ticker,
        start=data_inicio.strftime("%Y-%m-%d"),
        end=data_fim.strftime("%Y-%m-%d"),
        interval=intervalo,
        progress=False
    )


    if not df_novo.empty:
        df_novo.index = (
            df_novo.index.tz_convert("America/Sao_Paulo")
            if df_novo.index.tz is not None
            else df_novo.index.tz_localize("UTC").tz_convert("America/Sao_Paulo")
        )

        if os.path.exists(dados_brutos) and not primeira_extracao:
            df_antigo = pd.read_csv(dados_brutos, index_col=0, parse_dates=True)
            df_total = pd.concat([df_antigo, df_novo])
        else:
            df_total = df_novo

        df_total = (
            df_total.drop_duplicates()
            .dropna(thresh=df_total.shape[1] * 0.5)

        )

        df_total.to_csv(dados_brutos)
        print("Dados somados e salvos com sucesso.")
    else:
        print("Nenhum dado complementar foi adicionado.")

    return df_total

if __name__ == "__main__":
    ticker = "BBDC4.SA"
    intervalo = "5m"
    dias = 45
    dados_brutos = "/content/Piloto_Day_Trade/data/raw/dados_brutos.csv"
    df = extrair_dados(ticker, dias, intervalo, dados_brutos)
