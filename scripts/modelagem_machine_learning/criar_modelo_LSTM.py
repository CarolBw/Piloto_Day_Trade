
# Tentativa inicial - Modelo base LSTM para previsão intradiária de preços

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam, RMSprop

def LSTM_model(input_shape, 
               lstm_units=64, 
               dropout_rate=0.2, 
               optimizer='adam', 
               loss='mse'):
    
    model = Sequential()
    model.add(LSTM(lstm_units, input_shape=input_shape))
    model.add(Dropout(dropout_rate))
    model.add(Dense(1))
    
    if isinstance(optimizer, str):
        model.compile(loss=loss, optimizer=optimizer)
    else:
        model.compile(loss=loss, optimizer=optimizer)
        
    return model
