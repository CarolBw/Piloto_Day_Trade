
import pandas as pd
import numpy as np
import xgboost as xgb

'''Função para realizar a previsao do proximo dia'''

def prever_proximo_dia(df, data=None):
    # Garantir que a coluna 'data' esteja no formato correto
    df['data'] = pd.to_datetime(df['data'])
    
    # Se nenhuma data for fornecida, usar a última data disponível
    if data is None:
        data = df['data'].max()
    else:
        data = pd.to_datetime(data)
    
    # Filtrar o dataset pela data escolhida
    df_filtro = df[df['data'] == data]
    
    if df_filtro.empty:
        print(f"Nenhum dado encontrado para a data {data.date()}")
        return None
    
    # Selecionar as features para a previsão
    features = ['abertura', 'minimo', 'maximo', 'fechamento',
                'volume', 'volatilidade', 'dia_da_semana', 'hora_num', 'minuto', 'mercado_aberto', 
                'retorno', 'SMA_10', 'retorno_lag1', 'EMA_10', 'OBV', 'rsi', 'Signal_Line', 'std_dev', 'fechamento_lag1']
    
    X_pred = df_filtro[features]
    
    # Carregar os modelos treinados
    modelos = {}
    targets = ['target_abertura', 'target_min', 'target_max', 'target_fechamento']
    for target in targets:
        modelo = xgb.XGBRegressor()
        modelo.load_model(f'/content/Piloto_Day_Trade/models/xgboost_model_{target}.json')
        modelos[target] = modelo
    
    # Fazer previsões
    previsoes = {}
    for target, modelo in modelos.items():
        previsoes[target] = modelo.predict(X_pred)
    
    # Criar DataFrame com os resultados
    df_previsao = df_filtro[['data', 'hora']].copy()
    df_previsao['abertura'] = previsoes['target_abertura']
    df_previsao['minimo'] = previsoes['target_min']
    df_previsao['maximo'] = previsoes['target_max']
    df_previsao['fechamento'] = previsoes['target_fechamento']
    df_previsao = df_previsao.sort_values(by='hora', ascending=True)

    if df_previsao.empty:
        print(f"Nenhuma previsão disponível para a data {data.date()}")
        return None
    else:
        print(f'Previsões para a data {data + pd.Timedelta(days=1)}')          
        print(df_previsao.head(10))
        print(df_previsao.tail(10))

        print(f'Máxima do dia: {df["maximo"].max()})')
        print(f'Mínima do dia: {df["minimo"].min()}')



        return df_previsao

if __name__ == "__main__":
    # Carregar dados
    df = pd.read_csv('/content/Piloto_Day_Trade/data/dados_transformados_finais.csv', parse_dates=['data'])
    # Definir data
    data = '2025-03-28'
    # REalizar as previsões
    prever_proximo_dia(df, data)
    print("Previsões realizadas com sucesso!")
    
  
