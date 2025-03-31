
import pandas as pd
import numpy as np
import xgboost as xgb
import matplotlib.pyplot as plt  # Importando o matplotlib para criar o gráfico
import matplotlib.dates as mdates
from matplotlib.ticker import FormatStrFormatter

'''Função para realizar a previsao do proximo dia'''

def prever_proximo_dia(df, data=None, ticker=None):
    # Garantir que a coluna 'data' esteja no formato correto
    df['data'] = pd.to_datetime(df['data'])
    
    # Se nenhuma data for fornecida, usar a última data disponível
    if data is None:
        data = df['data'].max()
    else:
        data = pd.to_datetime(data)
    
    # Função para verificar o próximo dia útil
    def proximo_dia_util(dia):
        while dia.weekday() >= 5:  # Se for sábado (5) ou domingo (6)
            dia += pd.Timedelta(days=1)  # Avança para o próximo dia
        return dia
    
    # Obter o próximo dia útil após a última data do dataset
    data_proxima = proximo_dia_util(data + pd.Timedelta(days=1))  # Calcula o próximo dia útil
    
    # Agora, vamos usar o último dia de dados disponível para fazer as previsões
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
        print(f"Nenhuma previsão disponível para a data {data_proxima.date()}")
        return None
    else:
        print(f'Previsões para a data {data_proxima.date()}')          
        print(df_previsao.head(40))

        # Calcular máxima e mínima do dia
        maxima_do_dia = df_filtro['maximo'].max()
        minima_do_dia = df_filtro['minimo'].min()

        print(f'Máxima do dia: {maxima_do_dia}')
        print(f'Mínima do dia: {minima_do_dia}')
        
        # Plotando o gráfico das previsões
        plt.figure(figsize=(16,6))
        plt.plot(df_previsao['hora'], df_previsao['abertura'], label='Abertura', marker='o')
        plt.plot(df_previsao['hora'], df_previsao['minimo'], label='Mínimo', marker='o')
        plt.plot(df_previsao['hora'], df_previsao['maximo'], label='Máximo', marker='o')
        plt.plot(df_previsao['hora'], df_previsao['fechamento'], label='Fechamento', marker='o')
        
        plt.title(f'Previsões para o dia {data_proxima.date()} - {ticker}')
        plt.xlabel('Hora')
        plt.ylabel('Preço')
        
        # Rotaciona as horas para melhor visualização
        plt.xticks(rotation=45)  
        plt.tight_layout()
        
        # Ajustando as legendas
        plt.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize=10)

if __name__ == "__main__":
    # Carregar dados
    df = pd.read_csv('/content/Piloto_Day_Trade/data/dados_transformados_finais.csv', parse_dates=['data']) 
    # Definir data de treino
    data = '2025-03-28' 
    ticker = 'BBDC4.SA'  # Defina o ticker para o gráfico
    # Realizar as previsões
    prever_proximo_dia(df, data, ticker)
    print("Previsões realizadas com sucesso!")
