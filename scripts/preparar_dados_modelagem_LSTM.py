
"""
Função que prepara os dados transformados para modelagem com LSTM:
- Aplica normalização e padronização
- Cria sequências de entrada e saída
- Divide em treino e teste
- Salva o scaler de preço para uso posterior nas previsões

Retorna:
    X_treino, X_teste, y_treino, y_teste: arrays prontos para modelagem LSTM
"""

import os
import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler, MinMaxScaler

def preparar_dados_lstm(
    path_dados,       # Caminho do CSV com os dados
    tam_seq=32,       # Tamanho da sequência para entrada na LSTM
    tx_treino=0.8     # Proporção dos dados para treino
):
    # Caminho do scaler
    caminho_scaler_preco = '/content/Piloto_Day_Trade/models/scalers/scaler_normalizacao_preco.pkl'

    # Criar diretório do scaler se não existir
    os.makedirs(os.path.dirname(caminho_scaler_preco), exist_ok=True)

    # Carregar dados transformados
    df = pd.read_csv(path_dados)

    # Garantir colunas de data como datetime
    df['data'] = pd.to_datetime(df['data'], errors='coerce')
    df['data_previsao'] = pd.to_datetime(df['data_previsao'], errors='coerce')

    # Definir colunas de preço
    preco_cols = ['abertura', 'maximo', 'minimo', 'fechamento']

    # Garantir que não há valores ausentes nos preços
    df = df.dropna(subset=preco_cols)

    # Salvar scaler de preço com base nos valores reais (antes da normalização)
    scaler_preco = MinMaxScaler()
    scaler_preco.fit(df[preco_cols])
    joblib.dump(scaler_preco, caminho_scaler_preco)

    print("Scaler de preço salvo com sucesso.")

    # Definir colunas para padronização e normalização
    padronizar_cols = ['retorno', 'volatilidade', 'MACD', 'Signal_Line', 'rsi']
    normalizar_cols = ['abertura', 'minimo', 'maximo', 'fechamento', 'volume', 'SMA_10', 'EMA_10', 'OBV',
                       'fechamento_lag1', 'retorno_lag1', 'volume_lag1',
                       'fechamento_lag2', 'retorno_lag2', 'volume_lag2',
                       'fechamento_lag3', 'retorno_lag3', 'volume_lag3']

    # Inicializar scalers
    scaler_standard = StandardScaler()
    scaler_minmax = MinMaxScaler()

    # Aplicar transformações
    df[padronizar_cols] = scaler_standard.fit_transform(df[padronizar_cols])
    df[normalizar_cols] = scaler_minmax.fit_transform(df[normalizar_cols])

    # Converter colunas categóricas para int
    categorias = ['dia_da_semana_entrada', 'dia_da_semana_previsao', 'hora_num', 'minuto', 'mercado_aberto']
    df[categorias] = df[categorias].astype(int)

    # Manter apenas colunas numéricas
    df = df.select_dtypes(include=['number'])

    # Função para criar sequências
    def criar_sequencias(dados, tam_seq):
        entradas, saidas = [], []
        for i in range(len(dados) - tam_seq - 1):
            entradas.append(dados.iloc[i:i+tam_seq].values)
            saidas.append(dados.iloc[i+1:i+1+tam_seq][['abertura', 'maximo', 'minimo', 'fechamento']].values)
        return np.array(entradas), np.array(saidas)

    # Gerar X e y
    X, y = criar_sequencias(df, tam_seq)

    # Dividir entre treino e teste
    tamanho_treino = int(tx_treino * len(X))
    X_treino, X_teste = X[:tamanho_treino], X[tamanho_treino:]
    y_treino, y_teste = y[:tamanho_treino], y[tamanho_treino:]

    return X_treino, X_teste, y_treino, y_teste


# Execução direta 
if __name__ == "__main__":
    path_dados = '/content/Piloto_Day_Trade/data/dados_transformados.csv'
    X_treino, X_teste, y_treino, y_teste = preparar_dados_lstm(
        path_dados=path_dados,
        tam_seq=96,
        tx_treino=0.8
    )
