
import sqlite3
import os

# Caminho para o banco
db_path = "/content/Piloto_Day_Trade/modelagem/database/banco_dimensional.db"
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# Conecta ao banco (cria se não existir)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Tabelas dimensão
cursor.execute("""
CREATE TABLE IF NOT EXISTS dim_tempo (
    id_tempo INTEGER PRIMARY KEY,
    data DATE,
    hora TEXT,
    dia_da_semana INTEGER
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS dim_indicadores (
    id_tempo INTEGER PRIMARY KEY,
    SMA_10 REAL,
    EMA_10 REAL,
    MACD REAL,
    Signal_Line REAL,
    RSI REAL,
    OBV REAL,
    FOREIGN KEY (id_tempo) REFERENCES dim_tempo(id_tempo)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS dim_lags (
    id_tempo INTEGER PRIMARY KEY,
    fechamento_lag1 REAL,
    retorno_lag1 REAL,
    volume_lag1 REAL,
    FOREIGN KEY (id_tempo) REFERENCES dim_tempo(id_tempo)
);
""")

# Tabela fato
cursor.execute("""
CREATE TABLE IF NOT EXISTS fato_precos (
    id_tempo INTEGER PRIMARY KEY,
    preco_fechamento REAL,
    FOREIGN KEY (id_tempo) REFERENCES dim_tempo(id_tempo)
);
""")

# Confirma e fecha
conn.commit()
conn.close()
print("✅ Banco e tabelas criados com sucesso.")
