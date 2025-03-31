
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import os

# Carregar dados
df = pd.read_csv('/content/Piloto_Day_Trade/data/dados_transformados_finais.csv', parse_dates=['data'])
df = df[['data', 'hora', 'abertura', 'minimo', 'maximo', 'fechamento',
        'volume', 'volatilidade', 'mes', 'dia_da_semana', 'hora_num', 'minuto', 'mercado_aberto', 'retorno']]

# Filtrar os dados para considerar apenas os últimos 10 dias úteis
df = df.sort_values(by=['data', 'hora'], ascending=True)
df = df[df['data'] >= df['data'].max() - pd.Timedelta(days=10)]  

# Criar features e targets
df['target_abertura'] = df['abertura'].shift(-1)
df['target_min'] = df['minimo'].shift(-1)
df['target_max'] = df['maximo'].shift(-1)
df['target_fechamento'] = df['fechamento'].shift(-1)

df.dropna(inplace=True)  # Remover valores nulos

# Definir features e targets
features = ['abertura', 'minimo', 'maximo', 'fechamento',
            'volume', 'volatilidade', 'mes', 'dia_da_semana', 'hora_num', 'minuto', 'mercado_aberto', 'retorno']
X = df[features]

targets = ['target_abertura', 'target_min', 'target_max', 'target_fechamento']

def treinar_e_avaliar(target_name):
    y = df[target_name]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    # Criar e treinar modelo
    model = xgb.XGBRegressor(
        objective='reg:squarederror', 
        n_estimators=500,  # Aumentado para capturar mais padrões
        learning_rate=0.03,  # Reduzido para tornar o modelo mais preciso
        max_depth=6,  # Testando uma profundidade maior
        min_child_weight=3,  # Evita dividir nós com poucas amostras, reduz overfitting
        subsample=0.7,  # Reduzindo um pouco para melhorar generalização
        colsample_bytree=0.7,  # Menos colunas por árvore para evitar overfitting
        early_stopping_rounds=50  # Mantido para evitar overtraining
    )
    
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

    # Fazer previsões
    y_pred = model.predict(X_test)

    # Criar DataFrame de comparação
    comparison_df = pd.DataFrame({
        'Data': df.loc[X_test.index, 'data'],
        'Hora': df.loc[X_test.index, 'hora'],
        'Real': y_test,
        'Previsao': y_pred
    })
    
    print(f"\nAmostra de Comparação para {target_name}:")
    print(comparison_df.head(10))
    
    # Avaliação do modelo
    print(f"\nAvaliação para {target_name}:")
    print(f"MAE: {mean_absolute_error(y_test, y_pred):.4f}")
    print(f"RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.4f}")
    print(f"R²: {r2_score(y_test, y_pred):.4f}")

    return model

# Criar diretório de saída, se não existir
output_dir = "/content/Piloto_Day_Trade/models/"
os.makedirs(output_dir, exist_ok=True)

# Treinar, avaliar e salvar o modelo corretamente
for target in targets:
    modelo_treinado = treinar_e_avaliar(target)
    
    if modelo_treinado:
        modelo_treinado.save_model(f'{output_dir}xgboost_model_{target}.json')
        print(f"✅ Modelo XGBoost para {target} salvo com sucesso!")
    else:
        print(f"❌ Erro ao treinar modelo para {target}. Modelo não foi salvo.")
