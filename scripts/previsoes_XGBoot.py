
import pandas as pd
import numpy as np
import joblib

# Função para carregar modelos salvos
def carregar_modelos():  
    # Caminhos para os modelos salvos
    modelo_paths = {
        'abertura': '/content/Piloto_Day_Trade/models/XGBoost_abertura.pkl',
        'minimo': '/content/Piloto_Day_Trade/models/XGBoost_minimo.pkl',
        'maximo': '/content/Piloto_Day_Trade/models/XGBoost_maximo.pkl',
        'fechamento': '/content/Piloto_Day_Trade/models/XGBoost_fechamento.pkl'
    }
    modelos_carregados = {}
    for target, path in modelo_paths.items():
        modelo_carregado = joblib.load(path)
        modelos_carregados[target] = modelo_carregado
    return modelos_carregados

# Função para realizar previsões
def previsoes_XGBoot(df_entrada, modelos_carregados, data_entrada, data_prevista):
    # Garantir que apenas as colunas de features sejam usadas
    features = [
        "abertura", "minimo", "maximo", "fechamento", "SMA_10", "EMA_10",
        "rsi", "MACD", "Signal_Line", "OBV", "fechamento_lag1", "fechamento_lag2", "fechamento_lag3",
        "retorno_lag1", "retorno_lag2", "retorno_lag3", "volume_lag1", "volume_lag2", "volume_lag3"
    ]
    X_novo = df_entrada[features]

    # Garantir que não haja NaN nos dados
    X_novo = X_novo.dropna()
    
    # Carregar os modelos treinados
    modelos_carregados = carregar_modelos()

    # Criar um dicionário para armazenar as previsões
    previsoes_futuras = {}

    # Fazer previsões para cada target
    for target, modelo in modelos_carregados.items():
        previsoes = modelo.predict(X_novo)
        previsoes_futuras[target] = previsoes[0]  # Pegando o primeiro valor de previsão

    # Exibir as previsões exatas
    print(f"\n📅 Previsões para {data_prevista}:")
    for target, previsao in previsoes_futuras.items():
        print(f"{target.capitalize()} Previsão: {previsao:.4f}")

    return previsoes_futuras

if __name__ == "__main__":
    # Carregar os dados históricos do mercado
    df = pd.read_csv('/content/Piloto_Day_Trade/data/dados_transformados_recentes.csv', parse_dates=["data"])

    # Definir datas
    data_entrada = '2025-03-26'
    data_prevista = '2025-03-27'

    # Filtrar os dados de entrada
    df_entrada = df[df["data"] == pd.to_datetime(data_entrada)]

    # Fazer previsões para o dia 27
    previsoes_resultado = previsoes_XGBoot(df_entrada, data_entrada, data_prevista)
