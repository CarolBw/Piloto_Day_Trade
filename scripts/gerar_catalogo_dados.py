
"""
Catálogo de Dados detalhado para o modelo dimensional em Esquema Estrela
Projeto: Piloto_Day_Trade
Formato: CSV e JSON
Objetivo: Atender aos requisitos de documentação com descrição, domínio, tipo, fonte, técnica e status.
"""

import pandas as pd
import json

# Lista detalhada das variáveis do modelo estrela
catalogo = [
    # Tabela Fato
    {"tabela": "fato_precos", "variavel": "id_tempo", "tipo": "int", "descricao": "Chave estrangeira que referencia a dimensão de tempo", "dominio": "inteiros positivos", "fonte": "dim_tempo", "tecnica": "chave relacional", "status": "ativo"},
    {"tabela": "fato_precos", "variavel": "abertura", "tipo": "float", "descricao": "Preço de abertura do ativo", "dominio": "valores reais positivos", "fonte": "dados_transformados.csv", "tecnica": "extração direta", "status": "ativo"},
    {"tabela": "fato_precos", "variavel": "minimo", "tipo": "float", "descricao": "Preço mínimo do ativo", "dominio": "valores reais positivos", "fonte": "dados_transformados.csv", "tecnica": "extração direta", "status": "ativo"},
    {"tabela": "fato_precos", "variavel": "maximo", "tipo": "float", "descricao": "Preço máximo do ativo", "dominio": "valores reais positivos", "fonte": "dados_transformados.csv", "tecnica": "extração direta", "status": "ativo"},
    {"tabela": "fato_precos", "variavel": "fechamento", "tipo": "float", "descricao": "Preço de fechamento do ativo (variável alvo)", "dominio": "valores reais positivos", "fonte": "dados_transformados.csv", "tecnica": "extração direta", "status": "ativo"},

    # Dimensão Tempo
    {"tabela": "dim_tempo", "variavel": "id_tempo", "tipo": "int", "descricao": "Identificador único da dimensão tempo", "dominio": "inteiros positivos", "fonte": "gerado", "tecnica": "indexação temporal", "status": "ativo"},
    {"tabela": "dim_tempo", "variavel": "data", "tipo": "object", "descricao": "Data da observação (YYYY-MM-DD)", "dominio": "datas do dataset", "fonte": "dados_transformados.csv", "tecnica": "extração direta", "status": "ativo"},
    {"tabela": "dim_tempo", "variavel": "hora", "tipo": "object", "descricao": "Hora da observação (HH:MM)", "dominio": "intervalos de 15 minutos", "fonte": "dados_transformados.csv", "tecnica": "extração direta", "status": "ativo"},
    {"tabela": "dim_tempo", "variavel": "dia_da_semana_entrada", "tipo": "int", "descricao": "Dia da semana da entrada (0=Seg, 6=Dom)", "dominio": "0 a 6", "fonte": "dados_transformados.csv", "tecnica": "extraído da data", "status": "ativo"},

    # Dimensão Indicadores Técnicos
    {"tabela": "dim_indicadores", "variavel": "id_tempo", "tipo": "int", "descricao": "Chave estrangeira para a dimensão tempo", "dominio": "inteiros positivos", "fonte": "dim_tempo", "tecnica": "relacional", "status": "ativo"},
    {"tabela": "dim_indicadores", "variavel": "SMA_10", "tipo": "float", "descricao": "Média móvel simples de 10 períodos", "dominio": "valores reais", "fonte": "dados_transformados.csv", "tecnica": "rolling mean", "status": "ativo"},
    {"tabela": "dim_indicadores", "variavel": "EMA_10", "tipo": "float", "descricao": "Média móvel exponencial de 10 períodos", "dominio": "valores reais", "fonte": "dados_transformados.csv", "tecnica": "EMA", "status": "ativo"},
    {"tabela": "dim_indicadores", "variavel": "MACD", "tipo": "float", "descricao": "MACD - Média móvel de convergência/divergência", "dominio": "valores reais", "fonte": "dados_transformados.csv", "tecnica": "diferença entre EMAs", "status": "ativo"},
    {"tabela": "dim_indicadores", "variavel": "Signal_Line", "tipo": "float", "descricao": "Linha de sinal do MACD", "dominio": "valores reais", "fonte": "dados_transformados.csv", "tecnica": "média do MACD", "status": "ativo"},
    {"tabela": "dim_indicadores", "variavel": "rsi", "tipo": "float", "descricao": "Índice de Força Relativa", "dominio": "0 a 100", "fonte": "dados_transformados.csv", "tecnica": "RSI clássico", "status": "ativo"},
    {"tabela": "dim_indicadores", "variavel": "OBV", "tipo": "float", "descricao": "On Balance Volume", "dominio": "valores reais", "fonte": "dados_transformados.csv", "tecnica": "volume cumulativo", "status": "ativo"},
    {"tabela": "dim_indicadores", "variavel": "retorno", "tipo": "float", "descricao": "Retorno percentual do período", "dominio": "valores reais", "fonte": "dados_transformados.csv", "tecnica": "fechamento relativo", "status": "ativo"},
    {"tabela": "dim_indicadores", "variavel": "volatilidade", "tipo": "float", "descricao": "Volatilidade do preço no período", "dominio": "valores reais positivos", "fonte": "dados_transformados.csv", "tecnica": "desvio padrão móvel", "status": "ativo"},

    # Dimensão Lags
    {"tabela": "dim_lags", "variavel": "id_tempo", "tipo": "int", "descricao": "Chave estrangeira para a dimensão tempo", "dominio": "inteiros positivos", "fonte": "dim_tempo", "tecnica": "relacional", "status": "ativo"},
    {"tabela": "dim_lags", "variavel": "fechamento_lag1", "tipo": "float", "descricao": "Fechamento 1 candle anterior", "dominio": "valores reais", "fonte": "dados_transformados.csv", "tecnica": "shift(-1)", "status": "ativo"},
    {"tabela": "dim_lags", "variavel": "retorno_lag1", "tipo": "float", "descricao": "Retorno 1 candle anterior", "dominio": "valores reais", "fonte": "dados_transformados.csv", "tecnica": "shift(-1)", "status": "ativo"},
    {"tabela": "dim_lags", "variavel": "volume_lag1", "tipo": "float", "descricao": "Volume 1 candle anterior", "dominio": "valores reais positivos", "fonte": "dados_transformados.csv", "tecnica": "shift(-1)", "status": "ativo"},
    {"tabela": "dim_lags", "variavel": "fechamento_lag2", "tipo": "float", "descricao": "Fechamento 2 candles atrás", "dominio": "valores reais", "fonte": "dados_transformados.csv", "tecnica": "shift(-2)", "status": "ativo"},
    {"tabela": "dim_lags", "variavel": "retorno_lag2", "tipo": "float", "descricao": "Retorno 2 candles atrás", "dominio": "valores reais", "fonte": "dados_transformados.csv", "tecnica": "shift(-2)", "status": "ativo"},
    {"tabela": "dim_lags", "variavel": "volume_lag2", "tipo": "float", "descricao": "Volume 2 candles atrás", "dominio": "valores reais positivos", "fonte": "dados_transformados.csv", "tecnica": "shift(-2)", "status": "ativo"},
    {"tabela": "dim_lags", "variavel": "fechamento_lag3", "tipo": "float", "descricao": "Fechamento 3 candles atrás", "dominio": "valores reais", "fonte": "dados_transformados.csv", "tecnica": "shift(-3)", "status": "ativo"},
    {"tabela": "dim_lags", "variavel": "retorno_lag3", "tipo": "float", "descricao": "Retorno 3 candles atrás", "dominio": "valores reais", "fonte": "dados_transformados.csv", "tecnica": "shift(-3)", "status": "ativo"},
    {"tabela": "dim_lags", "variavel": "volume_lag3", "tipo": "float", "descricao": "Volume 3 candles atrás", "dominio": "valores reais positivos", "fonte": "dados_transformados.csv", "tecnica": "shift(-3)", "status": "ativo"},

    # Dimensão Operacional
    {"tabela": "dim_operacional", "variavel": "id_tempo", "tipo": "int", "descricao": "Chave estrangeira para a dimensão tempo", "dominio": "inteiros positivos", "fonte": "dim_tempo", "tecnica": "relacional", "status": "ativo"},
    {"tabela": "dim_operacional", "variavel": "data_previsao", "tipo": "object", "descricao": "Data de previsão do modelo", "dominio": "datas futuras ou atuais", "fonte": "dados_transformados.csv", "tecnica": "extração direta", "status": "ativo"},
    {"tabela": "dim_operacional", "variavel": "dia_da_semana_previsao", "tipo": "int", "descricao": "Dia da semana da previsão", "dominio": "0 a 6", "fonte": "dados_transformados.csv", "tecnica": "extraído da data", "status": "ativo"},
    {"tabela": "dim_operacional", "variavel": "hora_num", "tipo": "int", "descricao": "Hora convertida em número inteiro", "dominio": "0 a 23", "fonte": "dados_transformados.csv", "tecnica": "conversão", "status": "ativo"},
    {"tabela": "dim_operacional", "variavel": "minuto", "tipo": "int", "descricao": "Minuto da observação", "dominio": "0 a 59", "fonte": "dados_transformados.csv", "tecnica": "extração direta", "status": "ativo"},
    {"tabela": "dim_operacional", "variavel": "mercado_aberto", "tipo": "int", "descricao": "Indicador se o mercado está aberto (1=sim, 0=não)", "dominio": "0 ou 1", "fonte": "dados_transformados.csv", "tecnica": "regras de horário", "status": "ativo"},
]

# Salvar como CSV
df = pd.DataFrame(catalogo)
df.to_csv("/content/Piloto_Day_Trade/modelagem/catalog/catalogo_dados.csv", index=False)
print("✅ Catálogo CSV salvo.")

# Salvar como JSON
with open("/content/Piloto_Day_Trade/modelagem/catalog/catalogo_dados.json", "w") as f:
    json.dump(catalogo, f, indent=4, ensure_ascii=False)
print("✅ Catálogo JSON salvo.")
