#@title Preparar dados modelagem LSTM

"""
Script de preparação de dados para modelagem com LSTM:
- Aplica normalização e padronização
- Salva scaler de preço
- Salva versão tratada em CSV
- Cria sequências de entrada e saída
- Divide em treino e teste
"""

import os
import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler, MinMaxScaler

def preparar_dados(path_dados):
    caminho_scaler_preco = '/content/Piloto_Day_Trade/models/LSTM/scalers/scaler_normalizacao_preco.pkl'
    os.makedirs(os.path.dirname(caminho_scaler_preco), exist_ok=True)
    df = pd.read_csv(path_dados)

    df['data'] = pd.to_datetime(df['data'], errors='coerce')
    df['data_previsao'] = pd.to_datetime(df['data_previsao'], errors='coerce')

    preco_cols = ['abertura', 'maximo', 'minimo', 'fechamento']
    df = df.dropna(subset=preco_cols)

    scaler_preco = MinMaxScaler()
    scaler_preco.fit(df[preco_cols])
    joblib.dump(scaler_preco, caminho_scaler_preco)

    padronizar_cols = ['retorno', 'volatilidade', 'MACD', 'Signal_Line', 'rsi']
    normalizar_cols = [
        'abertura', 'minimo', 'maximo', 'fechamento', 'volume', 'SMA_10', 'EMA_10', 'OBV',
        'fechamento_lag1', 'retorno_lag1', 'volume_lag1',
        'fechamento_lag2', 'retorno_lag2', 'volume_lag2',
        'fechamento_lag3', 'retorno_lag3', 'volume_lag3'
    ]

    df[padronizar_cols] = StandardScaler().fit_transform(df[padronizar_cols])
    df[normalizar_cols] = MinMaxScaler().fit_transform(df[normalizar_cols])

    categorias = ['dia_da_semana_entrada', 'dia_da_semana_previsao', 'hora_num', 'minuto', 'mercado_aberto']
    df[categorias] = df[categorias].astype(int)

    df = df.select_dtypes(include='number').dropna()

    caminho_preparado = '/content/Piloto_Day_Trade/data/transformed/dados_preparados_para_modelagem.csv'
    os.makedirs(os.path.dirname(caminho_preparado), exist_ok=True)
    df.to_csv(caminho_preparado, index=False)
    print(f"✅ Dados preparados salvos em: {caminho_preparado}")

    return df

def criar_sequencias(df, tam_seq=96):
    entradas, saidas = [], []
    for i in range(len(df) - 2*tam_seq):
        entrada = df.iloc[i : i + tam_seq].values
        saida = df.iloc[i + tam_seq : i + 2*tam_seq][['abertura', 'maximo', 'minimo', 'fechamento']].values
        entradas.append(entrada)
        saidas.append(saida)
    return np.array(entradas), np.array(saidas)

def dividir_treino_teste(X, y, tx_treino=0.8):
    tamanho_treino = int(tx_treino * len(X))
    return X[:tamanho_treino], X[tamanho_treino:], y[:tamanho_treino], y[tamanho_treino:]

def preparar_dados_lstm(path_dados, tam_seq=96, tx_treino=0.8):
    df_preparado = preparar_dados(path_dados)
    X, y = criar_sequencias(df_preparado, tam_seq)
    X_treino, X_teste, y_treino, y_teste = dividir_treino_teste(X, y, tx_treino)
    return X_treino, X_teste, y_treino, y_teste

if __name__ == "__main__":
    path_dados = '/content/Piloto_Day_Trade/data/transformed/dados_transformados.csv'
    X_treino, X_teste, y_treino, y_teste = preparar_dados_lstm(path_dados, tam_seq=96, tx_treino=0.8)

    print("✅ Dados de treino e teste prontos:")
    print(f"X_treino: {X_treino.shape}, y_treino: {y_treino.shape}")
    print(f"X_teste: {X_teste.shape}, y_teste: {y_teste.shape}")
