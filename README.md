
# Objetivo do Projeto

## 1. Propósito do MVP

Este projeto tem como objetivo principal a criação de um pipeline para extração, transformação, carga, análise e previsão da movimentação intradiária dos preços de um ativo financeiro em intervalos de 5 minutos. O modelo preditivo central será baseado em redes neurais recorrentes (LSTM), mas outras abordagens serão exploradas. O MVP visa garantir previsões para embasar decisões estratégicas de day trade.

## 2. Problema a Ser Resolvido

A alta volatilidade dos mercados financeiros exige ferramentas robustas para antecipação de movimentos de preço. A dificuldade está em capturar padrões de curto prazo e projetá-los com precisão. Traders e investidores necessitam de um modelo que consiga interpretar os padrões históricos e transformá-los em previsões úteis.

## 3. Pipeline do Projeto

O pipeline está estruturado em sete etapas principais:

### 3.1. Extração e armazenamento dos dados brutos
- Coleta de dados históricos do ativo BBDC4 em intervalos de 5 minutos, via API do Yahoo Finance (yfinance).
- Armazenamento dos dados no GitHub sincronizado com Google Colab, com backup em nuvem.
- Salvo como `dados_brutos.csv`

### 3.2. Limpeza e organização dos dados
- Padronização dos tipos de dados
- Padronização dos nomes de colunas
- Remoção de valores nulos ou duplicados
- Remoção de colunas desnecessárias
- Ordenação cronológica
- Salvo como `dados_limpos.csv`

### 3.3. Transformação de dados e engenharia de features
- Cálculo de indicadores técnicos (SMA, EMA, MACD, RSI, OBV)
- Cálculo de retornos e variância (volatilidade)
- Criação de variáveis de lag de preço, volume e retorno
- Adição de variáveis temporais (hora, dia da semana, mercado aberto)
- Salvo como `dados_transformados.csv`

### 3.4. Modelagem e estruturação do banco dimensional
- **Fato**: `fato_precos` com preços e chave para `dim_tempo`
- **Dimensões**:
  - `dim_tempo`: data, hora, dia da semana
  - `dim_indicadores`: indicadores técnicos
  - `dim_lags`: lags de preço, volume, retorno
  - `dim_operacional`: hora, minuto, data da previsão, mercado aberto
- Banco gerado em SQLite via script automatizado (`banco_dimensional.db`)

### 3.5. Carga (ETL)
- **Extração:** via API (automatizada)
- **Limpeza:** padronização, remoção de nulos/duplicatas
- **Transformação:** features técnicas e derivadas
- **Carga:** população das tabelas do banco dimensional
- ETL organizado em scripts Python e automatizado

### 3.6. Treinamento e ajuste do modelo preditivo
- **Preparação dos dados**:
  - Padronização com StandardScaler para retornos e indicadores
  - Normalização com MinMaxScaler para preços e volumes
  - Separar features (X) e targets (y)
  - Divisão treino/teste com base em dias útis
- **Modelo base:** LSTM com duas camadas ocultas, camada densa e MSE como perda
- **Avaliação:** Métricas de MSE, R², comparação com targets reais

### 3.7. Análise dos resultados
- Comparativo entre preços previstos vs. reais
- Validação das previsões para abertura, máxima, mínima e fechamento
- Importância das variáveis
- Interpretação dos erros e possíveis melhorias

## 4. Perguntas a Serem Respondidas
- É possível prever com precisão a movimentação intradiária a cada 5 minutos?
- Os dados do dia anterior são suficientes para prever o comportamento do dia seguinte?
- O modelo LSTM é eficaz para padrões de curtíssimo prazo?
- É viável derivar os targets globais do dia a partir das previsões intradiárias?
- Quais indicadores mais contribuem para a previsão?
- Como lidar corretamente com fins de semana e feriados?
- A padronização/normalização das variáveis afeta o desempenho?

## 5. Critérios de Sucesso
- Pipeline funcional de extração → transformação → carga → previsão
- Modelo com bom desempenho em MSE e R²
- Targets globais coerentes com valores reais
- Correta gestão de datas (incluindo segundas-feiras)
- Previsões utilizáveis para tomada de decisão

