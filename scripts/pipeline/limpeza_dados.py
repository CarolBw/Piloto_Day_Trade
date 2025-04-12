
import pandas as pd

def limpeza_dados(df, path_dados_limpos):
    # Verificar se os dados estão corretos
    print("Dados originais:")
    print(df.head())
    print(df.info())

    # Remover as primeiras duas linhas (com 'Ticker' e 'Datetime')
    df = df.iloc[2:].copy()

    # Verificar após a remoção 
    print("Após remoção das duas primeiras linhas:")
    print(df.head())

    # Garantir que o índice esteja no formato de data e hora (timezone UTC)
    df.index = pd.to_datetime(df.index, utc=True)

    # Definir o fuso horário como "America/Sao_Paulo"
    df.index = df.index.tz_convert("America/Sao_Paulo")

    # Remover a referência de fuso horário 
    df.index = df.index.tz_localize(None)

    # Criar a coluna 'hora' com base no índice
    df['hora'] = df.index.strftime('%H:%M:%S')

    # Renomear o índice para 'data'
    df.index.name = 'data'

    # Resetar o índice para transformar o Datetime em uma coluna normal
    df = df.reset_index()

    # Verificar após a transformação do índice
    print("\nApós conversão de índice:")
    print(df.head())

    # Remover o horário da coluna 'data', mantendo apenas a data
    df['data'] = df['data'].dt.date

    # Mapeamento das colunas para nomes padronizados
    mapeamento_colunas = {
        'Close': 'fechamento',
        'High': 'maximo',
        'Low': 'minimo',
        'Open': 'abertura',
        'Volume': 'volume'
    }

    # Renomear as colunas
    df.rename(columns=mapeamento_colunas, inplace=True)

    # Converte e arredonda as colunas numéricas
    for col in ['abertura', 'minimo', 'maximo', 'fechamento']:
        df[col] = pd.to_numeric(df[col], errors='coerce').round(2)

    # Converte a coluna 'volume' para número inteiro
    df['volume'] = pd.to_numeric(df['volume'], errors='coerce', downcast='integer')

    # Reorganiza as colunas na ordem desejada
    df = df[['data', 'hora', 'abertura', 'minimo', 'maximo', 'fechamento', 'volume']]

    # Verificar após reorganizar as colunas
    print("\nApós reorganizar as colunas:")
    print(df.head())

    # Verificar e remover duplicatas mantendo a primeira ocorrência
    df = df.drop_duplicates(keep='first')

    # Remover as linhas com 50% ou mais de valores nulos
    df = df.dropna(thresh=df.shape[1] * 0.5)

    # Verificar após remoção de duplicatas e nulos
    print("\nApós remover duplicatas e nulos:")
    print(df.head())

    # Garantir que 'data' e 'hora' estejam no formato datetime
    df['data'] = pd.to_datetime(df['data'], format='%Y-%m-%d')
    df['hora'] = pd.to_datetime(df['hora'], format='%H:%M:%S').dt.time

    # Filtra apenas os dias úteis (segunda a sexta)
    df = df[df['data'].dt.weekday < 5]

    # Verificar após filtrar dias úteis
    print("\nApós filtrar apenas os dias úteis:")
    print(df.head())

    # Filtra apenas horários entre 09:55 e 18:05
    df = df[(df['hora'] >= pd.to_datetime('09:55:00').time()) &
            (df['hora'] <= pd.to_datetime('18:05:00').time())]

    # Verificar após filtrar o intervalo de horário
    print("\nApós filtrar o intervalo de horário (09:55-18:05):")
    print(df.head())

    # Caso o DataFrame fique vazio, informar o motivo
    if df.empty:
        print("O DataFrame ficou vazio após o filtro de horário. Verifique se os dados estão dentro do intervalo de 09:55-18:05.")
    else:
        print("\nLimpeza de dados concluída com sucesso.")

    # Ordenar os dados
    df = df.sort_values(["data", "hora"], ascending=[False, True])
    print("\nDados limpos e ordenados:")
    print(df.head(10))

    # Salva os dados limpos em CSV
    df.to_csv(path_dados_limpos, index=False)
    print(f"\nOs dados foram limpos e salvos em csv.")

    return df


if __name__ == "__main__":
    # Ler os dados brutos
    dados_brutos = pd.read_csv(f"/content/Piloto_Day_Trade/data/raw/dados_brutos.csv", index_col=0, parse_dates=True, dayfirst=True)
    path_dados_limpos = '/content/Piloto_Day_Trade/data/cleaned/dados_limpos.csv'
    # Aplicar limpeza nos dados
    df_limpo = limpeza_dados(dados_brutos, path_dados_limpos)


