
# @title Script para criar banco de dados e tabelas

import sqlite3
import os

# Caminho para o banco
db_path = "/content/Piloto_Day_Trade/modelagem/database/banco_dimensional.db"
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# Conecta ao banco (cria se não existir)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Comandos SQL para criar as tabelas
sql_script = """
-- Criação da Tabela Fato
CREATE TABLE IF NOT EXISTS fato_precos (
    id_fato_precos INTEGER PRIMARY KEY,
    id_tempo INTEGER,
    abertura REAL,
    minimo REAL,
    maximo REAL,
    fechamento REAL,
    FOREIGN KEY (id_tempo) REFERENCES dim_tempo(id_tempo)
);

-- Criação da Dimensão Tempo
CREATE TABLE IF NOT EXISTS dim_tempo (
    id_tempo INTEGER PRIMARY KEY,
    data TEXT,
    hora TEXT,
    dia_da_semana_entrada INTEGER
);

-- Criação da Dimensão Indicadores Técnicos
CREATE TABLE IF NOT EXISTS dim_indicadores (
    id_indicadores INTEGER PRIMARY KEY,
    id_tempo INTEGER,
    SMA_10 REAL,
    EMA_10 REAL,
    MACD REAL,
    Signal_Line REAL,
    rsi REAL,
    OBV REAL,
    retorno REAL,
    volatilidade REAL,
    FOREIGN KEY (id_tempo) REFERENCES dim_tempo(id_tempo)
);

-- Criação da Dimensão Lags
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

-- Criação da Dimensão Operacional
CREATE TABLE IF NOT EXISTS dim_operacional (
    id_operacional INTEGER PRIMARY KEY,
    id_tempo INTEGER,
    data_previsao TEXT,
    dia_da_semana_previsao INTEGER,
    hora_num INTEGER,
    minuto INTEGER,
    mercado_aberto INTEGER,
    FOREIGN KEY (id_tempo) REFERENCES dim_tempo(id_tempo)
);
"""

# Executa o script SQL
cursor.executescript(sql_script)

# Confirma e fecha
conn.commit()
conn.close()
print("✅ Banco e tabelas criados com sucesso.")
