
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input

def LSTM_model(input_shape, 
               lstm_units=64, 
               dropout_rate=0.2, 
               optimizer='adam', 
               loss='mse'):
    """
    Cria e retorna um modelo LSTM sequencial com parâmetros ajustáveis.
    """
    model = Sequential()
    model.add(Input(shape=input_shape))
    model.add(LSTM(lstm_units))
    model.add(Dropout(dropout_rate))
    model.add(Dense(1))

    model.compile(loss=loss, optimizer=optimizer)
    return model

