
import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Fazer previsões
y_previsto = LSTM_model.predict(X_teste)

# Carregar o scaler específico para as colunas de preço
scaler_precos = joblib.load('/content/Piloto_Day_Trade/models/scalers/scaler_normalizacao_preco.pkl')

# Colunas de preço
colunas_precos = ['abertura', 'maximo', 'minimo', 'fechamento']

# Redimensionar para (amostras, 4)
y_previsto_reshape = y_previsto.reshape(-1, 4)
y_teste_reshape = y_teste.reshape(-1, 4)

# Inverter normalização
y_previsto_original = scaler_precos.inverse_transform(y_previsto_reshape)
y_teste_original = scaler_precos.inverse_transform(y_teste_reshape)

# DataFrames com nomes das colunas
df_previsto = pd.DataFrame(y_previsto_original, columns=colunas_precos)
df_real = pd.DataFrame(y_teste_original, columns=colunas_precos)

# Comparação
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

print("📊 Comparação de previsões (valores reais):")
print(comparacao.head(10))

# Função de métricas
def calcular_metricas(y_real, y_previsto, nome):
    mae = mean_absolute_error(y_real, y_previsto)
    mse = mean_squared_error(y_real, y_previsto)
    r2 = r2_score(y_real, y_previsto)
    print(f"{nome} - MAE: {mae:.4f}, MSE: {mse:.4f}, R²: {r2:.4f}")

# Métricas por coluna
calcular_metricas(df_real['abertura'], df_previsto['abertura'], "Abertura")
calcular_metricas(df_real['maximo'], df_previsto['maximo'], "Máximo")
calcular_metricas(df_real['minimo'], df_previsto['minimo'], "Mínimo")
calcular_metricas(df_real['fechamento'], df_previsto['fechamento'], "Fechamento")
