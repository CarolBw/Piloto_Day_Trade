
import sqlite3
import pandas as pd
import os

# Caminho para o banco de dados
db_path = "/content/Piloto_Day_Trade/modelagem/database/banco_dimensional.db"
assert os.path.exists(db_path), f"Banco de dados não encontrado em {db_path}"
# Leitura dos dados a serem carregados
df = pd.read_csv("/content/Piloto_Day_Trade/data/transformed/dados_transformados.csv")

# Função para carregar dados
def carregar_dados(df: pd.DataFrame):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for idx, row in df.iterrows():
        id_tempo = idx + 1  

        # 1. Inserir na dim_tempo
        cursor.execute("""
            INSERT INTO dim_tempo (id_tempo, data, hora, dia_da_semana_entrada)
            VALUES (?, ?, ?, ?)
        """, (id_tempo, row['data'], row['hora'], row['dia_da_semana_entrada']))

        # 2. Inserir na dim_indicadores
        cursor.execute("""
            INSERT INTO dim_indicadores (id_indicadores, id_tempo, SMA_10, EMA_10, MACD, Signal_Line, rsi, OBV, retorno, volatilidade)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (id_tempo, id_tempo, row['SMA_10'], row['EMA_10'], row['MACD'], row['Signal_Line'], row['rsi'],
              row['OBV'], row['retorno'], row['volatilidade']))

        # 3. Inserir na dim_lags
        cursor.execute("""
            INSERT INTO dim_lags (id_lags, id_tempo, fechamento_lag1, retorno_lag1, volume_lag1,
                                  fechamento_lag2, retorno_lag2, volume_lag2,
                                  fechamento_lag3, retorno_lag3, volume_lag3)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (id_tempo, id_tempo,
              row['fechamento_lag1'], row['retorno_lag1'], row['volume_lag1'],
              row['fechamento_lag2'], row['retorno_lag2'], row['volume_lag2'],
              row['fechamento_lag3'], row['retorno_lag3'], row['volume_lag3']))

        # 4. Inserir na dim_operacional
        cursor.execute("""
            INSERT INTO dim_operacional (id_operacional, id_tempo, data_previsao, dia_da_semana_previsao, hora_num, minuto, mercado_aberto)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (id_tempo, id_tempo, row['data_previsao'], row['dia_da_semana_previsao'],
              row['hora_num'], row['minuto'], row['mercado_aberto']))

        # 5. Inserir na fato_precos
        cursor.execute("""
            INSERT INTO fato_precos (id_fato_precos, id_tempo, abertura, minimo, maximo, fechamento)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (id_tempo, id_tempo, row['abertura'], row['minimo'], row['maximo'], row['fechamento']))

    conn.commit()
    conn.close()
    print(f"✅ Carga concluída com {len(df)} registros.")

if __name__ == "__main__":
    carregar_dados(df)

