
#@title Script para gerar o catálogo de dados em conformidade com o enunciado
"""
Catálogo de Dados contendo minimamente uma descrição detalhada dos dados e seus domínios,
contendo valores mínimos e máximos esperados para dados numéricos, e possíveis categorias para dados categóricos.

Este modelo deve também descrever a linhagem dos dados, de onde os mesmos foram baixados
e qual técnica foi utilizada para compor o conjunto de dados, caso haja.
"""

from pathlib import Path
import pandas as pd

# Define colunas de cada tabela com tipos
tabelas = {
    "fato_precos": {
        "id_fato_precos": "int",
        "id_tempo": "int",
        "abertura": "float",
        "minimo": "float",
        "maximo": "float",
        "fechamento": "float"
    },
    "dim_tempo": {
        "id_tempo": "int",
        "data": "object",
        "hora": "object",
        "dia_da_semana_entrada": "int"
    },
    "dim_indicadores": {
        "id_indicadores": "int",
        "id_tempo": "int",
        "SMA_10": "float",
        "EMA_10": "float",
        "MACD": "float",
        "Signal_Line": "float",
        "rsi": "float",
        "OBV": "float",
        "retorno": "float",
        "volatilidade": "float"
    },
    "dim_lags": {
        "id_lags": "int",
        "id_tempo": "int",
        "fechamento_lag1": "float",
        "retorno_lag1": "float",
        "volume_lag1": "float",
        "fechamento_lag2": "float",
        "retorno_lag2": "float",
        "volume_lag2": "float",
        "fechamento_lag3": "float",
        "retorno_lag3": "float",
        "volume_lag3": "float"
    },
    "dim_operacional": {
        "id_operacional": "int",
        "id_tempo": "int",
        "data_previsao": "object",
        "dia_da_semana_previsao": "int",
        "hora_num": "int",
        "minuto": "int",
        "mercado_aberto": "int"
    }
}

def dominio(col, tipo):
    if tipo in ["float", "int"]:
        if "retorno" in col:
            return "-0.05 a 0.05 (retorno percentual por intervalo de 5 min)"
        elif "volatilidade" in col:
            return "0 a 0.1 (desvio padrão do retorno por janela de tempo)"
        elif "abertura" in col or "fechamento" in col or "minimo" in col or "maximo" in col:
            return "10.0 a 50.0 (valores típicos para BBDC4)"
        elif "MACD" in col or "Signal" in col:
            return "-5 a 5"
        elif "rsi" in col:
            return "0 a 100"
        elif "OBV" in col:
            return "valor acumulativo, depende do ativo"
        elif "volume" in col:
            return "0 a 1.000.000 (valores inteiros positivos)"
        elif "dia_da_semana" in col:
            return "0=Segunda, ..., 6=Domingo"
        elif "mercado_aberto" in col:
            return "0=Fechado, 1=Aberto"
        else:
            return "valores numéricos contínuos"
    elif tipo == "object":
        if "data" in col:
            return "formato YYYY-MM-DD"
        elif "hora" in col:
            return "formato HH:MM:SS"
        else:
            return "texto livre"
    return "não especificado"

def descricao(col):
    descricoes = {
        "abertura": "Preço de abertura do ativo BBDC4 no intervalo de 5 minutos",
        "minimo": "Menor preço do ativo BBDC4 no intervalo de 5 minutos",
        "maximo": "Maior preço do ativo BBDC4 no intervalo de 5 minutos",
        "fechamento": "Preço de fechamento do ativo BBDC4 no intervalo de 5 minutos",
        "retorno": "Retorno percentual do ativo no intervalo de 5 minutos",
        "volatilidade": "Volatilidade dos retornos do ativo em janela deslizante",
        "SMA_10": "Média móvel simples de 10 períodos calculada sobre os preços",
        "EMA_10": "Média móvel exponencial de 10 períodos",
        "MACD": "Moving Average Convergence Divergence, indicador técnico",
        "Signal_Line": "Linha de sinal do MACD",
        "rsi": "Índice de força relativa (RSI), oscilador técnico",
        "OBV": "On Balance Volume, indicador técnico baseado em volume",
        "hora_num": "Hora expressa como número inteiro",
        "minuto": "Minuto do intervalo de tempo",
        "mercado_aberto": "Indica se o mercado está aberto no horário (1) ou não (0)"
    }
    for key in descricoes:
        if key in col:
            return descricoes[key]
    if "lag" in col:
        return f"Valor defasado de {col.replace('_lag', '')}"
    if "dia_da_semana" in col:
        return "Dia da semana correspondente à data"
    if "id_" in col:
        return "Identificador único para relacionar com outras tabelas"
    return ""

def tecnica(col):
    if any(ind in col for ind in ["SMA", "EMA", "MACD", "Signal", "rsi", "OBV"]):
        return "calculado internamente via engenharia de features técnicas"
    if "lag" in col:
        return "calculado como valor defasado (lag)"
    if col in ["data", "hora", "hora_num", "minuto", "dia_da_semana_entrada", "dia_da_semana_previsao"]:
        return "extraído de data/hora original"
    if col == "mercado_aberto":
        return "derivado da data/hora com base em calendário de mercado"
    return "cópia ou identificador"

linhagem = "Fonte: Yahoo Finance via yfinance"

linhas = []
for tabela, colunas in tabelas.items():
    for col, tipo in colunas.items():
        linhas.append({
            "tabela": tabela,
            "coluna": col,
            "tipo": tipo,
            "descricao": descricao(col),
            "dominio": dominio(col, tipo),
            "tecnica": tecnica(col),
            "linhagem": linhagem
        })

catalogo_df = pd.DataFrame(linhas)
catalogo_df.to_csv("/content/Piloto_Day_Trade/modelagem/catalogo_dados.csv", index=False)
