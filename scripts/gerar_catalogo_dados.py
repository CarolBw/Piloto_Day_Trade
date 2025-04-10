
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

def gerar_catalogo(caminhos_csv, caminho_saida_csv, caminho_saida_json):
    catalogo = []

    for caminho in caminhos_csv:
        if not os.path.exists(caminho):
            print(f"⚠️ Arquivo não encontrado: {caminho}")
            continue

        try:
            df = pd.read_csv(caminho)
            nome_arquivo = os.path.basename(caminho)
            stat = os.stat(caminho)

            entry = {
                "arquivo": nome_arquivo,
                "caminho": caminho,
                "linhas": int(len(df)),
                "colunas": int(len(df.columns)),
                "nomes_colunas": df.columns.tolist(),
                "tipos_colunas": df.dtypes.astype(str).to_dict(),
                "data_min": str(df['data'].min()) if 'data' in df.columns else None,
                "data_max": str(df['data'].max()) if 'data' in df.columns else None,
                "tamanho_em_bytes": int(stat.st_size),
                "ultima_modificacao": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "descricao": "",
                "fonte": "",
                "responsavel": "",
                "status": "ativo"
            }
            catalogo.append(entry)
        except Exception as e:
            print(f"❌ Erro ao processar {caminho}: {e}")

    df_catalogo = pd.DataFrame(catalogo)

    # Salvar CSV
    df_catalogo.to_csv(caminho_saida_csv, index=False)
    print(f"✅ Catálogo salvo em: {caminho_saida_csv}")

    # Salvar JSON
    with open(caminho_saida_json, 'w') as f:
        json.dump(catalogo, f, indent=4, ensure_ascii=False)
    print(f"✅ Catálogo JSON salvo em: {caminho_saida_json}")

    return df_catalogo
