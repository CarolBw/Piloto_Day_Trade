
import sqlite3
import os

def criar_banco(db_path):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    sql_script = """
    -- Tabela Fato: fato_precos
    CREATE TABLE IF NOT EXISTS fato_precos (
        id_fato_precos INTEGER PRIMARY KEY,
        id_tempo INTEGER,
        abertura REAL,
        minimo REAL,
        maximo REAL,
        fechamento REAL,
        FOREIGN KEY (id_tempo) REFERENCES dim_tempo(id_tempo)
    );

    -- Dimensão: dim_tempo
    CREATE TABLE IF NOT EXISTS dim_tempo (
        id_tempo INTEGER PRIMARY KEY,
        data TEXT,
        hora TEXT,
        dia_da_semana_entrada INTEGER,
        hora_num INTEGER,
        minuto INTEGER
    );

    -- Dimensão: dim_indicadores
    CREATE TABLE IF NOT EXISTS dim_indicadores (
        id_indicadores INTEGER PRIMARY KEY,
        id_tempo INTEGER,
        SMA_10 REAL,
        EMA_10 REAL,
        MACD REAL,
        Signal_Line REAL,
        rsi REAL,
        OBV REAL,
        CCI REAL,
        ATR REAL,
        retorno REAL,
        volatilidade REAL,
        fechamento_dia REAL,          -- Coluna adicionada
        FOREIGN KEY (id_tempo) REFERENCES dim_tempo(id_tempo)
    );

    -- Dimensão: dim_lags
    CREATE TABLE IF NOT EXISTS dim_lags (
        id_lags INTEGER PRIMARY KEY,
        id_tempo INTEGER,
        fechamento_lag1 REAL,
        retorno_lag1 REAL,
        volume_lag1 REAL,
        fechamento_lag2 REAL,
        retorno_lag2 REAL,
        volume_lag2 REAL,
        fechamento_lag3 REAL,
        retorno_lag3 REAL,
        volume_lag3 REAL,
        FOREIGN KEY (id_tempo) REFERENCES dim_tempo(id_tempo)
    );

    -- Dimensão: dim_operacional
    CREATE TABLE IF NOT EXISTS dim_operacional (
        id_operacional INTEGER PRIMARY KEY,
        id_tempo INTEGER,
        data_previsao TEXT,
        dia_da_semana_previsao INTEGER,
        hora_num INTEGER,
        minuto INTEGER,
        mercado_aberto INTEGER,
        fechamento_dia REAL,
        volume_dia REAL,
        maximo_dia REAL,
        minimo_dia REAL,
        fechamento_dia_anterior REAL,
        volume_dia_anterior REAL,
        maximo_dia_anterior REAL,
        minimo_dia_anterior REAL,
        FOREIGN KEY (id_tempo) REFERENCES dim_tempo(id_tempo)
    );
    """

    cursor.executescript(sql_script)
    conn.commit()
    conn.close()
    print("Banco e tabelas criados com sucesso conforme o esquema dimensional.")

if __name__ == "__main__":
    db_path = "/content/Piloto_Day_Trade/modelagem/database/banco_dimensional.db"
    criar_banco(db_path)
