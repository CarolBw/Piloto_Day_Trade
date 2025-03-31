
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

df = pd.read_csv('/content/Piloto_Day_Trade/data/dados_transformados_finais', parse_dates=['data'])
df = df[['data', 'hora', 'abertura', 'minimo', 'maximo', 'fechamento',
            'volume', 'volatilidade', 'mes', 'dia_da_semana', 'hora_num', 'minuto','mercado_aberto']]

# Filtrar os dados para considerar apenas os últimos 10 dias úteis
df = df.sort_values(by=['data', 'hora'], ascending=True)
df = df[df['data'] >= df['data'].max() - pd.Timedelta(days=10)]  

# Criar features e targets
df.loc[:, 'target_abertura'] = df['abertura'].shift(-1)  # Previsão da abertura do próximo período
df.loc[:, 'target_min'] = df['minimo'].shift(-1)  # Previsão do mínimo do próximo período
df.loc[:, 'target_max'] = df['maximo'].shift(-1)  # Previsão da máxima do próximo período
df.loc[:, 'target_fechamento'] = df['fechamento'].shift(-1)  # Previsão do fechamento do próximo período

df.dropna(inplace=True)  # Remover valores nulos

# Definindo as features
features = ['abertura', 'minimo', 'maximo', 'fechamento',
            'volume', 'volatilidade', 'mes', 'dia_da_semana', 'hora_num', 'minuto','mercado_aberto']
X = df[features]

# Lista de targets para prever
targets = ['target_abertura', 'target_min', 'target_max', 'target_fechamento']

# Função para treinar, avaliar e mostrar a comparação de previsões
def treinar_e_avaliar(target_name):
    y = df[target_name]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)  # shuffle=False para manter a ordem cronológica
    
    # Criar modelo XGBoost com ajustes de parâmetros
    model = xgb.XGBRegressor(
        objective='reg:squarederror', 
        n_estimators=200,  # Número de árvores
        learning_rate=0.05,  # Taxa de aprendizado
        max_depth=5,         # Profundidade das árvores
        min_child_weight=1,  # Peso mínimo das folhas
        subsample=0.8,       # Subamostragem
        colsample_bytree=0.8,  # Subamostragem das colunas
        early_stopping_rounds=50  # Early stopping
    )
    
    # Treinar o modelo
    model.fit(X_train, y_train, 
              eval_set=[(X_test, y_test)], 
              verbose=False)  # Usar early stopping

    # Realizar previsões
    y_pred = model.predict(X_test)
    
    # Corrigir a associação de data e hora com as previsões
    comparison_df = pd.DataFrame({
        'Data': df.loc[X_test.index, 'data'],
        'Hora': df.loc[X_test.index, 'hora'],  # Incluir hora
        'Real': y_test, 
        'Previsao': y_pred
    })
    
    print(f"\nAmostra de Comparação para {target_name}:")
    print(comparison_df.head(10))  # Exibir as primeiras 10 linhas para visualização
    
    # Avaliação
    print(f"\nAvaliação para {target_name}:")
    print(f"MAE: {mean_absolute_error(y_test, y_pred):.4f}")
    print(f"RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.4f}")
    print(f"R²: {r2_score(y_test, y_pred):.4f}")
    
    # Salvar o modelo treinado
    model.save_model(f'/content/Piloto_Day_Trade/models/xgboost_model_{target_name}.json')
    print(f"✅ Modelo XGBoost para {target_name} salvo com sucesso!")

# Treinar e avaliar para cada target
for target in targets:
    treinar_e_avaliar(target)

