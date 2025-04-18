

import pandas as pd
import os

def diagnosticar_qualidade_dados(df, path_output):
    """
    Gera diagnóstico de qualidade dos dados:
    duplicação, nulos, valores únicos, gaps e outliers.

    Parâmetros:
    df (pd.DataFrame): Conjunto de dados analisado.
    path_output (str): Caminho para salvar o relatório CSV.

    Retorna:
    None
    """
    os.makedirs(os.path.dirname(path_output), exist_ok=True)

    relatorio = []

    # Linhas duplicadas
    relatorio.append(["Duplicatas (linhas completas)", df.duplicated().sum()])

    # Gaps de tempo (se houver colunas data e hora)
    if {'data', 'hora'}.issubset(df.columns):
        try:
            df_ordenado = df.sort_values(['data', 'hora'])
            df_ordenado['timestamp'] = pd.to_datetime(df_ordenado['data'] + ' ' + df_ordenado['hora'])
            gaps = df_ordenado['timestamp'].diff().gt(pd.Timedelta(minutes=5)).sum()
            relatorio.append(["Gaps (>5min entre registros)", int(gaps)])
        except Exception as e:
            relatorio.append(["Erro ao verificar gaps", str(e)])
    else:
        relatorio.append(["Gaps", "Colunas 'data' e 'hora' não encontradas"])

    # Valores nulos
    for col in df.columns:
        pct_null = df[col].isnull().mean() * 100
        relatorio.append([f"Nulos (%) - {col}", round(pct_null, 2)])

    # Valores únicos
    for col in df.columns:
        unicos = df[col].nunique()
        relatorio.append([f"Valores únicos - {col}", unicos])

    # Outliers (IQR)
    for col in df.select_dtypes(include=['float64', 'int64']).columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        outliers = df[(df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)]
        relatorio.append([f"Outliers (IQR) - {col}", len(outliers)])

    # Converter para DataFrame e salvar
    relatorio_df = pd.DataFrame(relatorio, columns=["Verificação", "Resultado"])
    relatorio_df.to_csv(path_output, index=False)
    print(f"Relatório salvo em: {path_output}")
