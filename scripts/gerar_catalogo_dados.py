
#@title Geração de Catálogo de Dados

"""
Geração de Catálogo de Dados para rastreabilidade e governança no projeto Piloto_Day_Trade.
Gera um inventário estruturado de arquivos CSV, com metainformações úteis para controle de dados.

Salva o catálogo em CSV e JSON.
"""

import os
import pandas as pd
import json
from datetime import datetime
import numpy as np

def gerar_catalogo(path_dados, path_saida_csv, path_saida_json):
    catalogo = []

    # Anotações por arquivo
    anotacoes = {
        "dados_brutos.csv": {
            "descricao": "Extraídos do Yahoo Finance via yfinance. Dados originais, sem tratamento ou modificações.",
            "fonte": "yfinance",
            "responsavel": "Carolina B.",
            "status": "ativo"
        },
        "dados_limpos.csv": {
            "descricao": "Aplicada limpeza básica: tratamento de datas, remoção de nulos, padronização de colunas. Sem transformação de variáveis.",
            "fonte": "dados_brutos.csv",
            "responsavel": "Carolina B.",
            "status": "ativo"
        },
        "dados_transformados.csv": {
            "descricao": "Transformações aplicadas: criação de novas features com indicadores técnicos para análise preditiva. Sem normalização.",
            "fonte": "dados_limpos.csv",
            "responsavel": "Carolina B.",
            "status": "ativo"
        }
    }

    for caminho in path_dados:
        if not os.path.exists(caminho):
            print(f"⚠️ Arquivo não encontrado: {caminho}")
            continue

        try:
            df = pd.read_csv(caminho)
            nome_arquivo = os.path.basename(caminho)
            stat = os.stat(caminho)

            tipos_colunas = df.dtypes.astype(str).to_dict()
            dominios_colunas = {}

            for col in df.columns:
                if df[col].dtype in [np.float64, np.int64]:
                    dominios_colunas[col] = {
                        "min": float(df[col].min()),
                        "max": float(df[col].max()),
                        "media": float(df[col].mean()),
                        "desvio_padrao": float(df[col].std())
                    }
                elif df[col].dtype == object:
                    dominios_colunas[col] = {
                        "categorias_unicas": df[col].dropna().unique().tolist()
                    }

            anot = anotacoes.get(nome_arquivo, {})

            entry = {
                "arquivo": nome_arquivo,
                "caminho": caminho,
                "linhas": int(len(df)),
                "colunas": int(len(df.columns)),
                "nomes_colunas": df.columns.tolist(),
                "tipos_colunas": tipos_colunas,
                "dominios_colunas": dominios_colunas,
                "data_min": str(df['data'].min()) if 'data' in df.columns else None,
                "data_max": str(df['data'].max()) if 'data' in df.columns else None,
                "tamanho_em_bytes": int(stat.st_size),
                "ultima_modificacao": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "descricao": anot.get("descricao", ""),
                "fonte": anot.get("fonte", ""),
                "responsavel": anot.get("responsavel", ""),
                "status": anot.get("status", "ativo")
            }
            catalogo.append(entry)
        except Exception as e:
            print(f"❌ Erro ao processar {caminho}: {e}")

    df_catalogo = pd.DataFrame(catalogo)

    # Salvar CSV
    df_catalogo.to_csv(path_saida_csv, index=False)
    print(f"✅ Catálogo salvo em: {path_saida_csv}")

    # Salvar JSON
    with open(path_saida_json, 'w') as f:
        json.dump(catalogo, f, indent=4, ensure_ascii=False)
    print(f"✅ Catálogo JSON salvo em: {path_saida_json}")

    return df_catalogo
