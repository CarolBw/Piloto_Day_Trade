
# @title Carga de dados

import sqlite3
import pandas as pd
import os

def carregar_dados(df: pd.DataFrame, db_path: str):
    # Lista de colunas obrigatórias que devem existir no DataFrame
    colunas_obrigatorias = [
        'data', 'hora', 'dia_da_semana_entrada',
        'SMA_10', 'EMA_10', 'MACD', 'Signal_Line', 'rsi', 'OBV', 'retorno', 'volatilidade',
        'fechamento_lag1', 'retorno_lag1', 'volume_lag1',
        'fechamento_lag2', 'retorno_lag2', 'volume_lag2',
        'fechamento_lag3', 'retorno_lag3', 'volume_lag3',
        'hora_num', 'minuto', 'abertura', 'minimo', 'maximo', 'fechamento'
    ]

    # Verifica se todas as colunas obrigatórias estão presentes no DataFrame
    colunas_faltantes = [col for col in colunas_obrigatorias if col not in df.columns]
    if colunas_faltantes:
        raise ValueError(f"Colunas ausentes no DataFrame: {colunas_faltantes}")

    # Conexão com o banco de dados SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    registros_inseridos = 0

    # Loop para inserir os dados do DataFrame nas tabelas do banco
    for _, row in df.iterrows():
        # Verifica se já existe um registro com a mesma data e hora
        cursor.execute("SELECT id_tempo FROM dim_tempo WHERE data = ? AND hora = ?", (row['data'], row['hora']))
        resultado = cursor.fetchone()
        if resultado:
            continue  # Se o registro já existir, pula para o próximo

        # Obtém o ID da tabela dim_tempo
        cursor.execute("SELECT MAX(id_tempo) FROM dim_tempo")
        max_id = cursor.fetchone()[0]
        id_tempo = 1 if max_id is None else max_id + 1

        # 1. Inserção na tabela dim_tempo (data, hora, dia da semana)
        cursor.execute("""
            INSERT INTO dim_tempo (id_tempo, data, hora, dia_da_semana_entrada)
            VALUES (?, ?, ?, ?)
        """, (id_tempo, row['data'], row['hora'], row['dia_da_semana_entrada']))

        # 2. Inserção na tabela dim_indicadores (indicadores técnicos como SMA, EMA, etc.)
        cursor.execute("""
            INSERT INTO dim_indicadores (id_indicadores, id_tempo, SMA_10, EMA_10, MACD, Signal_Line, rsi, OBV, retorno, volatilidade, fechamento_dia, volume_dia, maximo_dia, minimo_dia)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            id_tempo, id_tempo, row['SMA_10'], row['EMA_10'], row['MACD'],
            row['Signal_Line'], row['rsi'], row['OBV'], row['retorno'], row['volatilidade'],
            row.get('fechamento_dia', None), row.get('volume_dia', None),
            row.get('maximo_dia', None), row.get('minimo_dia', None)
        ))

        # 3. Inserção na tabela dim_lags (valores defasados de fechamento, retorno e volume)
        cursor.execute("""
            INSERT INTO dim_lags (
                id_lags, id_tempo,
                fechamento_lag1, retorno_lag1, volume_lag1,
                fechamento_lag2, retorno_lag2, volume_lag2,
                fechamento_lag3, retorno_lag3, volume_lag3
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            id_tempo, id_tempo,
            row['fechamento_lag1'], row['retorno_lag1'], row['volume_lag1'],
            row['fechamento_lag2'], row['retorno_lag2'], row['volume_lag2'],
            row['fechamento_lag3'], row['retorno_lag3'], row['volume_lag3']
        ))

        # 4. Inserção na tabela dim_operacional (informações operacionais como hora e minuto)
        cursor.execute("""
            INSERT INTO dim_operacional (
                id_operacional, id_tempo,
                dia_da_semana_previsao, hora_num, minuto, mercado_aberto,
                fechamento_dia_anterior, volume_dia_anterior, maximo_dia_anterior, minimo_dia_anterior
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            id_tempo, id_tempo,
            row.get('dia_da_semana_previsao', row['dia_da_semana_entrada']),
            row['hora_num'], row['minuto'],
            row.get('mercado_aberto', 1),
            row.get('fechamento_dia_anterior', None), row.get('volume_dia_anterior', None),
            row.get('maximo_dia_anterior', None), row.get('minimo_dia_anterior', None)
        ))

        # 5. Inserção na tabela fato_precos (preços e volume)
        cursor.execute("""
            INSERT INTO fato_precos (id_fato_precos, id_tempo, abertura, minimo, maximo, fechamento, fechamento_dia, volume_dia, maximo_dia, minimo_dia)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            id_tempo, id_tempo, row['abertura'], row['minimo'], row['maximo'], row['fechamento'],
            row.get('fechamento_dia', None), row.get('volume_dia', None),
            row.get('maximo_dia', None), row.get('minimo_dia', None)
        ))

        registros_inseridos += 1  # Conta o número de registros inseridos

    # Commit das alterações no banco e fechamento da conexão
    conn.commit()
    conn.close()
    print(f"Carga incremental concluída. {registros_inseridos} novos registros inseridos.")

if __name__ == "__main__":
    # Caminho do banco de dados e arquivo CSV de dados transformados
    db_path = "/content/Piloto_Day_Trade/modelagem/database/banco_dimensional_vf.db"
    df_path = "/content/Piloto_Day_Trade/data/transformed/dados_transformados.csv"

    # Verifica se o arquivo CSV existe
    if not os.path.exists(df_path):
        raise FileNotFoundError(f"O arquivo {df_path} não existe.")

    # Carrega o DataFrame do arquivo CSV
    df = pd.read_csv(df_path)

    # Verifica se o DataFrame está vazio
    if df.empty:
        raise ValueError("O DataFrame carregado está vazio.")

    # Chama a função para carregar os dados no banco
    carregar_dados(df, db_path)

