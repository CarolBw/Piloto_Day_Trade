#@title Definindo Script para criar o modelo LSTM

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, TimeDistributed

def LSTM_model(input_shape):
    """
    Cria um modelo LSTM com:
    - 2 camadas LSTM com Dropout
    - Uma camada TimeDistributed com 4 saídas por timestep (abertura, maximo, minimo, fechamento)
    - Compilado com otimizador Adam e perda MSE

    Args:
        input_shape (tuple): formato da entrada (timesteps, n_features)

    Returns:
        model (tf.keras.Model): modelo compilado pronto para treino
    """
    model = Sequential()

    # Primeira camada LSTM com 64 neurônios e retorno de sequência
    model.add(LSTM(units=64, return_sequences=True, input_shape=input_shape))
    model.add(Dropout(0.2))  # Dropout para evitar overfitting

    # Segunda camada LSTM com 32 neurônios
    model.add(LSTM(units=32, return_sequences=True))
    model.add(Dropout(0.2))

    # Camada final: 4 saídas (abertura, max, min, fechamento) por timestep
    model.add(TimeDistributed(Dense(4)))

    # Compilando o modelo
    model.compile(optimizer='adam', loss='mse')

    return model
