
#@title Script para geração do catálogo de dados

import pandas as pd
from pathlib import Path

def gerar_catalogo_dados(df: pd.DataFrame, path_output: str) -> None:
    """
    Gera o catálogo de dados a partir do DataFrame df,
    salvando em path_output no formato CSV.
    """

    # Detecta tipos das colunas
    col_types = df.dtypes.apply(lambda x: 'float' if 'float' in str(x) else ('int' if 'int' in str(x) else 'object')).to_dict()

    # Define tabelas com base nas colunas
    tabelas = {
        "fato_precos": {},
        "dim_tempo": {},
        "dim_indicadores": {},
        "dim_lags": {},
        "dim_operacional": {}
    }

    for col, tipo in col_types.items():
        if col == "id_fato_precos":
            tabelas["fato_precos"][col] = tipo
        elif col == "id_tempo":
            for t in ["dim_tempo", "dim_indicadores", "dim_lags", "dim_operacional"]:
                tabelas[t][col] = tipo
        elif "abertura" in col or "fechamento" in col or "minimo" in col or "maximo" in col:
            tabelas["fato_precos"][col] = tipo
        elif any(ind in col for ind in ["SMA", "EMA", "MACD", "Signal", "rsi", "OBV", "volatilidade", "retorno"]):
            tabelas["dim_indicadores"][col] = tipo
        elif "lag" in col:
            tabelas["dim_lags"][col] = tipo
        elif col in ["data", "hora", "dia_da_semana_entrada"]:
            tabelas["dim_tempo"][col] = tipo
        elif col in ["data_previsao", "dia_da_semana_previsao", "hora_num", "minuto", "mercado_aberto",
                     "fechamento_dia", "volume_dia", "maximo_dia", "minimo_dia",
                     "fechamento_dia_anterior", "volume_dia_anterior", "maximo_dia_anterior", "minimo_dia_anterior"]:
            tabelas["dim_operacional"][col] = tipo

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
            "mercado_aberto": "Indica se o mercado está aberto no horário (1) ou não (0)",
            "fechamento_dia": "Preço de fechamento do ativo no dia corrente",
            "volume_dia": "Volume de negociações do ativo no dia corrente",
            "maximo_dia": "Maior preço do ativo no dia corrente",
            "minimo_dia": "Menor preço do ativo no dia corrente",
            "fechamento_dia_anterior": "Preço de fechamento do ativo no dia anterior",
            "volume_dia_anterior": "Volume de negociações do ativo no dia anterior",
            "maximo_dia_anterior": "Maior preço do ativo no dia anterior",
            "minimo_dia_anterior": "Menor preço do ativo no dia anterior"
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

    # Geração do catálogo
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
                "linhagem": "Fonte: Yahoo Finance via yfinance"
            })

    catalogo_df = pd.DataFrame(linhas)
    Path(path_output).parent.mkdir(parents=True, exist_ok=True)
    catalogo_df.to_csv(path_output, index=False)
    print(f"Catálogo de dados gerado em: {path_output}")
