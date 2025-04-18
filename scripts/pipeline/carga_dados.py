
import sqlite3
import pandas as pd

def carregar_dados(df, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for _, row in df.iterrows():
        # Inserção em dim_tempo
        cursor.execute("""
            INSERT INTO dim_tempo (data, hora, dia_da_semana_entrada, hora_num, minuto)
            VALUES (?, ?, ?, ?, ?)
        """, (row['data'], row['hora'], row['dia_da_semana_entrada'], row['hora_num'], row['minuto']))

        id_tempo = cursor.lastrowid

        # Inserção em dim_indicadores
        cursor.execute("""
            INSERT INTO dim_indicadores (
                id_tempo, SMA_10, EMA_10, MACD, Signal_Line,
                rsi, OBV, CCI, ATR, retorno, volatilidade
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            id_tempo, row['SMA_10'], row['EMA_10'], row['MACD'], row['Signal_Line'],
            row['rsi'], row['OBV'], row['CCI'], row['ATR'], row['retorno'], row['volatilidade']
        ))

        # Inserção em dim_lags
        cursor.execute("""
            INSERT INTO dim_lags (
                id_tempo, fechamento_lag1, retorno_lag1, volume_lag1,
                fechamento_lag2, retorno_lag2, volume_lag2,
                fechamento_lag3, retorno_lag3, volume_lag3
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            id_tempo, row['fechamento_lag1'], row['retorno_lag1'], row['volume_lag1'],
            row['fechamento_lag2'], row['retorno_lag2'], row['volume_lag2'],
            row['fechamento_lag3'], row['retorno_lag3'], row['volume_lag3']
        ))

        # Inserção em dim_operacional
        cursor.execute("""
            INSERT INTO dim_operacional (
                id_tempo, data_previsao, dia_da_semana_previsao, hora_num, minuto,
                mercado_aberto, fechamento_dia, volume_dia, maximo_dia, minimo_dia,
                fechamento_dia_anterior, volume_dia_anterior, maximo_dia_anterior, minimo_dia_anterior
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            id_tempo, row['data_previsao'], row['dia_da_semana_previsao'], row['hora_num'], row['minuto'],
            row.get('mercado_aberto', 1),  # valor padrão
            row['fechamento_dia'], row['volume_dia'], row['maximo_dia'], row['minimo_dia'],
            row['fechamento_dia_anterior'], row['volume_dia_anterior'],
            row['maximo_dia_anterior'], row['minimo_dia_anterior']
        ))

        # Inserção na fato_precos
        cursor.execute("""
            INSERT INTO fato_precos (
                id_tempo, abertura, minimo, maximo, fechamento
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            id_tempo, row['abertura'], row['minimo'], row['maximo'], row['fechamento']
        ))

    conn.commit()
    conn.close()
    print("Dados carregados com sucesso.")

if __name__ == "__main__":
    df = pd.read_csv('/content/Piloto_Day_Trade/data/transformed/dados_transformados.csv')
    db_path = "/content/Piloto_Day_Trade/modelagem/database/banco_dimensional.db"
    carregar_dados(df, db_path)
