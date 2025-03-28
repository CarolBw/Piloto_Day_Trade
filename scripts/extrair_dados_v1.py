
# Importação das bibliotecas necessárias
import yfinance as yf  # Biblioteca para baixar dados financeiros do Yahoo Finance
import pandas as pd  # Biblioteca para manipulação de dados em tabelas (DataFrame)
from datetime import datetime, timedelta  # Para manipular datas e intervalos de tempo
import os  # Biblioteca para interação com o sistema operacional (como verificar a existência de arquivos)
import dotenv  # Biblioteca para carregar variáveis de ambiente de um arquivo .env

# Carregar variáveis de ambiente do arquivo .env
dotenv.load_dotenv()

def extrair_dados(ticker, intervalo, dias, dados_brutos):
    """Extrai dados históricos do Yahoo Finance e complementa com dados novos até ontem."""
    
    extracao_inicial = False  # Flag para indicar se estamos realizando a primeira extração de dados
    
    # Verifica se o arquivo de dados existe
    if os.path.exists(dados_brutos):
        try:
            # Tenta carregar os dados já existentes no arquivo CSV
            df_total = pd.read_csv(dados_brutos, index_col=0)

            # Converte o índice para datetime, forçando coerção de erros
            df_total.index = pd.to_datetime(df_total.index, errors="coerce", utc=True)

            # Remove linhas com índice inválido (NaT)
            df_total = df_total[df_total.index.notna()]

            # Obtém a última data registrada nos dados
            if df_total.empty:
                raise ValueError("Arquivo CSV está vazio após limpeza.")

            ultima_data = df_total.index.max()
            print(f"📅 Última data registrada no arquivo: {ultima_data}")

            if pd.isna(ultima_data):  # Se a última data for inválida
                raise ValueError("Nenhuma data válida encontrada no arquivo existente.")

            # Remove o fuso horário se houver
            if ultima_data.tzinfo is not None:
                ultima_data = ultima_data.tz_convert(None)

            # Define o início da extração (5 minutos após o último dado)
            data_inicio = ultima_data + timedelta(minutes=5)
            extracao_inicial = False  # Indica que não é a primeira extração

        except Exception as e:
            # Caso haja erro ao carregar ou processar o arquivo, inicia uma nova extração
            print(f"⚠️ Erro ao carregar o arquivo CSV: {e}. Iniciando extração do zero.")
            df_total = pd.DataFrame()  # Cria um DataFrame vazio
            data_inicio = datetime.today() - timedelta(days=dias)  # Define a data de início como "dias" atrás
            extracao_inicial = True  # Marca que é a primeira extração

    else:
        # Se o arquivo não existe, inicia a extração do zero
        df_total = pd.DataFrame()  # Cria um DataFrame vazio
        data_inicio = datetime.today() - timedelta(days=dias)  # Define a data de início como "dias" atrás
        extracao_inicial = True  # Marca que é a primeira extração

    data_fim = datetime.today()  # Define o fim da extração como a data e hora atuais
    extracao_realizada = False  # Flag para verificar se houve extração de dados

    print("🔄 Iniciando extração de dados...")  # Mensagem indicando o início da extração
    
    # Laço que realiza a extração dos dados enquanto data_inicio for menor que data_fim
    while data_inicio < data_fim:
        data_fim_bloco = min(data_inicio + timedelta(days=7), data_fim)  # Define o bloco de dados a ser extraído (7 dias)
        print(f"📊 Extraindo de {data_inicio.strftime('%Y-%m-%d %H:%M')} até {data_fim_bloco.strftime('%Y-%m-%d %H:%M')}")

        # Baixa os dados do Yahoo Finance para o intervalo de tempo definido
        df_novo = yf.download(ticker, start=data_inicio.strftime("%Y-%m-%d"),
                              end=data_fim_bloco.strftime("%Y-%m-%d"), interval=intervalo, progress=True)

        if df_novo.empty:
            print("⚠️ Nenhum dado novo encontrado para este período.")  # Caso não haja dados, interrompe o processo
            break

        # Concatena os dados novos com os existentes
        df_total = pd.concat([df_total, df_novo])
        data_inicio = data_fim_bloco  # Atualiza a data de início para o próximo bloco de dados
        extracao_realizada = True  # Marca que a extração foi realizada

    # Após a extração, se os dados foram obtidos com sucesso
    if extracao_realizada:
        df_total.to_csv(dados_brutos)  # Salva os dados extraídos no arquivo CSV
        print("✅ Extração concluída e dados salvos no arquivo.")

        # Exibe informações sobre a extração realizada
        if extracao_inicial:
            print(f"🆕 Extração inicial realizada com {dias} dias de dados.")  # Se for a primeira extração
        else:
            # Caso contrário, exibe o período dos dados extraídos
            primeira_data_extraida = df_total.index.min()  # Primeira data extraída
            ultima_data_extraida = df_total.index.max()  # Última data extraída
            print(f"➕ Complemento realizado: {primeira_data_extraida} até {ultima_data_extraida}.")
    else:
        print("⏭️ Nenhum dado novo para extrair. Nenhuma atualização realizada.")  # Caso não haja dados novos

    print("📊 Últimos dados extraídos:")  # Exibe os últimos dados extraídos
    print(df_total.tail())  # Mostra as últimas 5 linhas dos dados extraídos

    # Filtra os dados úteis, removendo finais de semana e horários fora do horário de negociação (10h-17:10h)
    df_total.index = pd.to_datetime(df_total.index, errors="coerce", utc=True)  # Converte novamente as datas
    df_uteis = df_total[(df_total.index.weekday < 5) & (df_total.index.hour >= 10) & 
                         (df_total.index.hour < 18) & ((df_total.index.hour != 17) | (df_total.index.minute <= 10))]

    dias_uteis = df_uteis.index.normalize().nunique()  # Conta os dias úteis no período
    print(f"📈 Captamos {dias_uteis} dias úteis no período das 10h às 17:10h.")  # Exibe a quantidade de dias úteis

    return df_uteis  # Retorna os dados úteis filtrados

# Se este script for executado diretamente
if __name__ == "__main__":
    ticker = "BBDC4.SA"  # Define o ticker da ação a ser consultada
    intervalo = "5m"  # Define o intervalo dos dados (5 minutos)
    dias = 45  # Define o número de dias de dados a ser extraído inicialmente
    dados_brutos= "/content/Piloto_Day_Trade/data/dados_brutosv2.csv"  # Caminho do arquivo para salvar os dados
    df = extrair_dados(ticker, intervalo, dias, dados_brutos)  # Chama a função para extrair os dados
