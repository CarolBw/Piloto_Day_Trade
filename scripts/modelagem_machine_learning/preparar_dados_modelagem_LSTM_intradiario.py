
import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from collections import Counter
import joblib
import datetime

def preparar_dados_lstm_intradiario(
    df: pd.DataFrame,
    colunas_features: list,
    colunas_targets: list,
    dias_entrada: int = 3,
    n_pontos_dia: int = None,
    verbose: bool = True
):
  
    df = df.copy()

    if "data" not in df.columns:
        raise ValueError("A coluna 'data' é obrigatória.")

    for col in colunas_features + colunas_targets:
        if col not in df.columns:
            raise ValueError(f"Coluna '{col}' ausente no DataFrame.")

    if df[colunas_features + colunas_targets].isnull().any().any():
        raise ValueError("[Erro] Existem valores nulos nas colunas de features ou targets.")

    df["data"] = df["data"].astype(str)

    contagem_por_dia = df.groupby("data").size()
    valor_mais_comum = Counter(contagem_por_dia).most_common(1)[0][0]
    n_pontos_dia = n_pontos_dia or valor_mais_comum

    if verbose:
        print(f"[Info] Detectado {n_pontos_dia} candles por dia.")

    scaler_features = MinMaxScaler()
    scaler_targets = MinMaxScaler()

    if not np.allclose(df[colunas_features].max(), 1.0, atol=1e-2):
        df[colunas_features] = scaler_features.fit_transform(df[colunas_features])
    else:
        if verbose:
            print("[Info] As colunas de features parecem já estar normalizadas.")

    if not np.allclose(df[colunas_targets].max(), 1.0, atol=1e-2):
        df[colunas_targets] = scaler_targets.fit_transform(df[colunas_targets])
    else:
        if verbose:
            print("[Info] As colunas de targets parecem já estar normalizadas.")

    path_norm = '/content/Piloto_Day_Trade/data/prepared/dados_normalizados.csv'
    os.makedirs(os.path.dirname(path_norm), exist_ok=True)
    df.to_csv(path_norm, index=False)
    if verbose:
        print(f"[Info] Dados normalizados salvos em: {path_norm}")

    scaler_path = '/content/Piloto_Day_Trade/models/LSTM'
    os.makedirs(scaler_path, exist_ok=True)
    joblib.dump(scaler_features, os.path.join(scaler_path, 'scaler_features.pkl'))
    joblib.dump(scaler_targets, os.path.join(scaler_path, 'scaler_targets.pkl'))
    if verbose:
        print(f"[Info] Scalers salvos em: {scaler_path}")

    dias_unicos = sorted(df["data"].unique())
    X, y, datas_validas = [], [], []

    for i in range(dias_entrada, len(dias_unicos)):
        dias_passados = dias_unicos[i - dias_entrada:i]
        dia_target = dias_unicos[i]

        entradas = []
        sequencia_valida = True

        for dia in dias_passados:
            dados_dia = df[df["data"] == dia][colunas_features].values
            if len(dados_dia) != n_pontos_dia:
                sequencia_valida = False
                break
            entradas.append(dados_dia)

        saida = df[df["data"] == dia_target][colunas_targets].values
        if len(saida) != n_pontos_dia:
            sequencia_valida = False

        if sequencia_valida:
            X.append(np.vstack(entradas))
            y.append(saida)
            datas_validas.append(dia_target)
        elif verbose:
            print(f"[Aviso] Ignorado: {dia_target} com sequência incompleta.")

    X = np.array(X)
    y = np.array(y)

    if verbose:
        print(f"[Info] X shape: {X.shape}, y shape: {y.shape}, Amostras válidas: {len(datas_validas)}")
        print("[Info] Preparação finalizada com sucesso.")

    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M')
    np.save(os.path.join(scaler_path, f'X_{timestamp}.npy'), X)
    np.save(os.path.join(scaler_path, f'y_{timestamp}.npy'), y)

    with open(os.path.join(scaler_path, f'datas_validas_{timestamp}.txt'), 'w') as f:
        for d in datas_validas:
            f.write(f"{d}\n")

    return X, y, datas_validas


if __name__ == "__main__":
    caminho_dados = '/content/Piloto_Day_Trade/data/transformed/dados_transformados.csv'
    caminho_scaler_features = '/content/Piloto_Day_Trade/models/LSTM/scaler_features.pkl'
    caminho_scaler_targets = '/content/Piloto_Day_Trade/models/LSTM/scaler_targets.pkl'

    df_transformado = pd.read_csv(caminho_dados)

    colunas_features = [
        'abertura', 'minimo', 'maximo', 'fechamento', 'volume',
        'SMA_10', 'EMA_10', 'OBV', 'retorno', 'volatilidade',
        'MACD', 'Signal_Line', 'rsi', 'ADX', 'BB_MA20', 'BB_STD20',
        'BB_upper', 'BB_lower', '%K', '%D', 'CCI', 'ATR'
    ]
    colunas_targets = ['minimo_dia', 'maximo_dia', 'fechamento_dia', 'volume_dia']

    X, y, datas = preparar_dados_lstm_intradiario(
        df=df_transformado,
        colunas_features=colunas_features,
        colunas_targets=colunas_targets,
        dias_entrada=3,
        verbose=True
    )

    print("\n[Resumo Final]")
    print(f"X shape: {X.shape}")
    print(f"y shape: {y.shape}")
    print(f"Amostras válidas: {len(datas)}")
    print(f"Primeira data válida: {datas[0] if datas else 'Nenhuma'}")

    scaler_features = joblib.load(caminho_scaler_features)
    scaler_targets = joblib.load(caminho_scaler_targets)
    print("\n[Info] Scalers carregados com sucesso.")
