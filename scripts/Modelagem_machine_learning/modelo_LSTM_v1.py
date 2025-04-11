
# Tentativa inicial - Modelo base LSTM para previsão intradiária de preços

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

# 🔧 Construção do modelo
LSTM_model = Sequential([
    
    # Camada LSTM 1:
    # - 100 unidades (aumentado para maior capacidade de captura de padrões temporais)
    # - return_sequences=True para passar a sequência completa para a próxima camada
    # - input_shape: (32, número de features) - sequência de 32 timesteps com n features
    LSTM(100, return_sequences=True, input_shape=(X_treino.shape[1], X_treino.shape[2])),
    
    # Dropout leve para reduzir overfitting sem perder muito sinal
    Dropout(0.1),

    # Camada LSTM 2:
    # - Outra LSTM com 100 unidades
    # - Também retorna sequência, pois a saída é uma sequência (32 timestamps com 4 preços)
    LSTM(100, return_sequences=True),
    
    # Outro Dropout leve
    Dropout(0.1),

    # Camada densa intermediária:
    # - 64 neurônios com ativação ReLU
    # - Introduz não-linearidade e ajuda a refinar a saída da LSTM antes da previsão final
    Dense(64, activation='relu'),

    # Camada de saída:
    # - 4 unidades: prevendo abertura, máxima, mínima e fechamento por timestamp
    # - Sem ativação, saída contínua (valores de preços normalizados)
    Dense(4)
])

# 🧠 Compilação do modelo
# - Otimizador Adam, bom para problemas não estacionários como séries temporais
# - Função de perda MSE (erro quadrático médio), apropriado para regressão
LSTM_model.compile(optimizer='adam', loss='mse')

# 🚂 Treinamento do modelo
# - 20 épocas: número inicial para observar o desempenho
# - batch_size=16: menor para atualizar pesos com frequência e lidar com variação dos dados
historico = LSTM_model.fit(
    X_treino, y_treino,
    validation_data=(X_teste, y_teste),
    epochs=20,
    batch_size=16
)


