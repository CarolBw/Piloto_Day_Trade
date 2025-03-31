
import pandas as pd
import numpy as np
import joblib
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

# Carregar os dados históricos do mercado
df = pd.read_csv('/content/Piloto_Day_Trade/data/dados_transformados_recentes.csv', parse_dates=["data"])

# Remover datas específicas do dataset
datas_excluir = ['2025-03-28', '2025-03-27']
df = df[~df['data'].dt.strftime('%Y-%m-%d').isin(datas_excluir)]

# Ordenar os dados por data para garantir sequência temporal
df = df.sort_values(by=["data", "hora"])

# Definir os atributos (features) e os alvos (targets)
features = [
    "abertura", "minimo", "maximo", "fechamento", "SMA_10", "EMA_10",
    "rsi", "MACD", "Signal_Line", "OBV", "fechamento_lag1", "fechamento_lag2", "fechamento_lag3",
    "retorno_lag1", "retorno_lag2", "retorno_lag3", "volume_lag1", "volume_lag2", "volume_lag3"
]

# Definir os alvos (targets)
targets = ["abertura", "minimo", "maximo", "fechamento"]

# Criar um dicionário para armazenar modelos e previsões
modelos = {}
previsoes = {}

# Separar os dados em treino e teste garantindo que a última data de treino seja ontem e a primeira de teste seja hoje
ontem = df['data'].max() - pd.Timedelta(days=1)
X_train = df[df['data'] <= ontem][features]
y_train = df[df['data'] <= ontem][targets]
X_test = df[df['data'] > ontem][features]
y_test = df[df['data'] > ontem][targets]

# Treinar um modelo XGBoost para cada target
for target in targets:
    modelo = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
    modelo.fit(X_train, y_train[target])
    modelos[target] = modelo
    
    # Fazer previsões para o próximo dia
    previsoes[target] = modelo.predict(X_test)
    
    # Avaliar o modelo
    erro = mean_absolute_error(y_test[target], previsoes[target])
    r2 = r2_score(y_test[target], previsoes[target])
    print(f"Erro médio absoluto para {target}: {erro}")
    print(f"R² para {target}: {r2}")

# Converter previsões em DataFrame para análise
df_previsoes = pd.DataFrame(previsoes, index=X_test.index)

# Exibir valores reais e previstos para o último dia de teste
df_comparacao = X_test.copy()
for target in targets:
    df_comparacao[f"Real_{target}"] = y_test[target].values
    df_comparacao[f"Previsto_{target}"] = df_previsoes[target].values

# Exibir data de entrada e data prevista
data_entrada = ontem.strftime('%Y-%m-%d')
data_prevista = df["data"].max().strftime('%Y-%m-%d')
print(f"\n🔎 Data de entrada para previsão: {data_entrada}")
print(f"📅 Data prevista: {data_prevista}")

# Mostrar comparação dos valores reais e previstos para todas as variáveis (para o último dia de previsão)
print("\n📊 Valores reais e previstos:")
print(df_comparacao[[f"Real_{target}" for target in targets] + [f"Previsto_{target}" for target in targets]].tail())

# Exibir estatísticas de erro médio absoluto
print("\n📈 Estatísticas de Erro Médio Absoluto para cada target:")
for target in targets:
    erro = mean_absolute_error(y_test[target], previsoes[target])
    print(f"{target}: {erro}")

# Exibir o coeficiente de determinação (R²)
print("\n📊 Coeficiente de determinação (R²) para cada target:")
for target in targets:
    r2 = r2_score(y_test[target], previsoes[target])
    print(f"{target}: {r2}")

# Salvar os modelos treinados
for target, modelo in modelos.items():
    joblib.dump(modelo, f"modelo_{target}.pkl")
    print(f"Modelo para {target} salvo como modelo_XGBoot_{target}.pkl")
