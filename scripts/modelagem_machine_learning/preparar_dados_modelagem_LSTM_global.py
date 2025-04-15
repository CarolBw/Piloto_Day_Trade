
# @title Preparação dos dados para o modelo LSTM Global

import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

def preparar_dados_lstm_global(df, janela=16, test_size=0.2, val_size=0.1):
    """
    Prepara os dados para um modelo LSTM prever os alvos globais do próximo dia (mínimo, máximo, fechamento, volume),
    usando sequências de candles intradiários (ex: 5 em 5 minutos) do(s) dia(s) anterior(es).
    """

    # Ordenar temporalmente
    df = df.sort_values(['data', 'hora']).reset_index(drop=True)

    # Definir colunas
    features = [
        'abertura', 'minimo', 'maximo', 'fechamento', 'volume',
        'SMA_10', 'EMA_10', 'OBV', 'retorno', 'volatilidade',
        'MACD', 'Signal_Line', 'rsi', 'ADX', 'BB_MA20', 'BB_STD20',
        'BB_upper', 'BB_lower', '%K', '%D', 'CCI', 'ATR',
        'fechamento_lag1', 'retorno_lag1', 'volume_lag1',
        'fechamento_lag2', 'retorno_lag2', 'volume_lag2',
        'fechamento_lag3', 'retorno_lag3', 'volume_lag3',
        'hora_num', 'minuto'
    ]
    targets = ['minimo_dia', 'maximo_dia', 'fechamento_dia', 'volume_dia']

    # Normalização
    scaler_features = MinMaxScaler()
    scaler_targets = MinMaxScaler()
    X_scaled = scaler_features.fit_transform(df[features])
    y_scaled = scaler_targets.fit_transform(df[targets])

    # Construir DataFrames auxiliares
    df_seq = pd.DataFrame(X_scaled, columns=features)
    df_seq['data'] = df['data'].values
    df_targets = pd.DataFrame(y_scaled, columns=targets)
    df_targets['data'] = df['data'].values

    # Geração de sequências por dia
    X, y = [], []
    dias_unicos = df_seq['data'].unique()
    for i in range(len(dias_unicos) - 1):
        dia = dias_unicos[i]
        proximo = dias_unicos[i + 1]

        dados_dia = df_seq[df_seq['data'] == dia].drop(columns='data')
        alvo_proximo = df_targets[df_targets['data'] == proximo][targets]

        if len(dados_dia) >= janela and not alvo_proximo.empty:
            X.append(dados_dia.iloc[-janela:].values)
            y.append(alvo_proximo.iloc[0].values)

    X = np.array(X)
    y = np.array(y)

    # Salvar dados completos antes do split
    np.savez_compressed(
        '/content/Piloto_Day_Trade/models/LSTM/lstm_global_dataset_completo.npz',
        X=X, y=y
    )

    # Split sem embaralhar
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, shuffle=False)
    X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=val_size, shuffle=False)

    # Salvar splits
    np.savez_compressed(
        '/content/Piloto_Day_Trade/models/LSTM/lstm_global_datasets.npz',
        X_train=X_train, X_val=X_val, X_test=X_test,
        y_train=y_train, y_val=y_val, y_test=y_test
    )

    # Salvar scalers
    joblib.dump(scaler_features, '/content/Piloto_Day_Trade/models/LSTM/scaler_features_lstm_global.save')
    joblib.dump(scaler_targets, '/content/Piloto_Day_Trade/models/LSTM/scaler_targets_lstm_global.save')

    return X_train, X_val, X_test, y_train, y_val, y_test, {
        'scaler_features': scaler_features,
        'scaler_targets': scaler_targets
    }

# Bloco de teste local (não roda se importado)
if __name__ == "__main__":
    df_transformado = pd.read_csv('/content/Piloto_Day_Trade/data/transformed/dados_transformados.csv')
    X_train, X_val, X_test, y_train, y_val, y_test, scalers = preparar_dados_lstm_global(df_transformado)

    print("Pré-visualização de uma sequência de entrada normalizada:")
    print(X_train[0])

    print("\nTarget correspondente (normalizado):")
    print(y_train[0])
