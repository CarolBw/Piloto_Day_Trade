
import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def avaliar_modelo_lstm(modelo, X_teste, y_teste, caminho_scaler='/content/Piloto_Day_Trade/models/LSTM/scalers/scaler_normalizacao_preco.pkl'):
    """
    Avalia um modelo LSTM fornecido, imprimindo as principais métricas e comparação entre previsões e valores reais.
    """
    print("🔍 Realizando previsões...")
    y_previsto = modelo.predict(X_teste)

    print("📦 Carregando scaler de preços para inversão...")
    scaler_precos = joblib.load(caminho_scaler)
    colunas_precos = ['abertura', 'maximo', 'minimo', 'fechamento']

    y_previsto_reshape = y_previsto.reshape(-1, 4)
    y_teste_reshape = y_teste.reshape(-1, 4)

    y_previsto_original = scaler_precos.inverse_transform(y_previsto_reshape)
    y_teste_original = scaler_precos.inverse_transform(y_teste_reshape)

    df_previsto = pd.DataFrame(y_previsto_original, columns=colunas_precos)
    df_real = pd.DataFrame(y_teste_original, columns=colunas_precos)

    comparacao = pd.DataFrame({
        'Abertura_Real': df_real['abertura'],
        'Abertura_Prevista': df_previsto['abertura'],
        'Maximo_Real': df_real['maximo'],
        'Maximo_Previsto': df_previsto['maximo'],
        'Minimo_Real': df_real['minimo'],
        'Minimo_Previsto': df_previsto['minimo'],
        'Fechamento_Real': df_real['fechamento'],
        'Fechamento_Previsto': df_previsto['fechamento']
    })

    print("\n📊 Comparação de previsões (valores reais):")
    print(comparacao.head(10))

    def calcular_metricas(y_real, y_previsto, nome):
        mae = mean_absolute_error(y_real, y_previsto)
        mse = mean_squared_error(y_real, y_previsto)
        r2 = r2_score(y_real, y_previsto)
        print(f"{nome} - MAE: {mae:.4f}, MSE: {mse:.4f}, R²: {r2:.4f}")

    print("\n📈 Métricas de desempenho por coluna:")
    calcular_metricas(df_real['abertura'], df_previsto['abertura'], "Abertura")
    calcular_metricas(df_real['maximo'], df_previsto['maximo'], "Máximo")
    calcular_metricas(df_real['minimo'], df_previsto['minimo'], "Mínimo")
    calcular_metricas(df_real['fechamento'], df_previsto['fechamento'], "Fechamento")

    return df_real, df_previsto, comparacao


if __name__ == "__main__":
    print("📥 Importando scripts de modelo e dados...")
    from tensorflow.keras.models import load_model
    from scripts.modelagem_machine_learning.preparar_dados_modelagem_LSTM import preparar_dados_lstm

    print("📊 Preparando dados para avaliação...")
    X_treino, X_teste, y_treino, y_teste = preparar_dados_lstm(
        path_dados='/content/Piloto_Day_Trade/data/transformed/dados_transformados.csv',
        tam_seq=96,
        tx_treino=0.8
    )

    print("📡 Carregando modelo salvo...")
    modelo_lstm_v1 = load_model('/content/Piloto_Day_Trade/models/LSTM/modelo_LSTM_v1.keras')

    print("✅ Avaliando modelo...")
    df_real, df_previsto, comparacao = avaliar_modelo_lstm(
        modelo=modelo_lstm_v1,
        X_teste=X_teste,
        y_teste=y_teste
    )
