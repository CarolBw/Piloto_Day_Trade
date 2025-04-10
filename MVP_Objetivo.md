

**Objetivo do Projeto**

### 1. Propósito do MVP

Este projeto tem como objetivo principal a criação de um pipeline para extração, transformação, carga, análise e previsão da movimentação intradiária dos preços de um ativo financeiro em intervalos de 5 minutos. O modelo preditivo central será baseado em redes neurais recorrentes (LSTM), mas outras abordagens serão exploradas. O MVP visa garantir previsões  para embasar decisões estratégicas de day trade.

### 2. Problema a Ser Resolvido

A alta volatilidade dos mercados financeiros exige ferramentas robustas para antecipação de movimentos de preço. A dificuldade está em capturar padrões de curto prazo e projetá-los com precisão. Traders e investidores necessitam de um modelo que consiga interpretar os padrões históricos e transformá-los em previsões úteis.

### 3. Pipeline do Projeto

O projeto será estruturado em cinco  etapas:

1. **Extração e armazenamento dos dados:** Coleta de dados históricos de ativos financeiros em intervalos de 15 minutos utilizando a API do Yahoo Finance (yfinance). Os dados serão armazenados em um repositório GitHub sincronizado com Google Colab, garantindo acesso remoto e backup na nuvem.
2. **Transformação e engenharia de features:** Aplicação normalização, padronização e criação de indicadores técnicos  para melhorar a entrada do modelo.
3. **Modelagem e estruturação do banco de dados:** Implementação de um modelo de dados estruturado no formato de Data Lake, onde os dados brutos, transformados e prontos para modelagem serão armazenados separadamente. Um catálogo de dados será desenvolvido, contendo descrições detalhadas.
4. **Treinamento e ajuste do modelo:** Implementação da rede LSTM para capturar padrões temporais, além da avaliação e otimização do modelo.
5. **Análise e aplicação dos resultados:** Interpretação das previsões, comparação com os valores reais e validação da eficácia na tomada de decisões.

### 4. Modelagem dos Dados

Para organizar os dados e facilitar o processamento pelo modelo, será utilizado um modelo **flat no conceito de Data Lake**. As tabelas seguirão o seguinte esquema:

- **Tabela Bruta:** Contém os dados extraídos do Yahoo Finance, sem modificações.
- **Tabela Transformada:** Inclui a limpeza geral,  e as novas features derivadas.
- Tabela Normalizada: Inclui as variáveis normalizadas, padronizadas para diferentes testes na acurácia do modelo.
- **Tabela Final:** Contém os dados que indicaram melhor acurácia no modelo preditivo.

Será criado um **Catálogo de Dados** contendo:

- Definição de cada variável utilizada no modelo.
- Valores mínimos e máximos esperados para dados numéricos.
- Categorias possíveis para variáveis categóricas.
- Linhagem dos dados (origem, processamento e destino).

### 5. Carga e Pipeline ETL

O fluxo de dados será implementado utilizando **pipelines de ETL (Extração, Transformação e Carga)**. O processo será automatizado para garantir a integridade dos dados armazenados. A carga dos dados ocorrerá de forma sequencial:

1. **Extração:** Dados coletados do Yahoo Finance via API.
2. **Transformação:** Processamento dos dados, incluindo limpeza, normalização, engenharia de features e tratamento de valores ausentes.
3. **Carga:** Armazenamento dos dados transformados no Data Lake, segmentados em diferentes camadas (bruto, transformado, normalizado e final).

A implementação será realizada no Google Colab com Github, para garantir controle de versões e reprodutibilidade do código.

### 6. Perguntas a Serem Respondidas

Este MVP visa responder às seguintes questões:

- É possível prever com precisão a movimentação intradiária de um ativo a cada 15 minutos?
- Os dados do dia anterior fornecem informações suficientes para a previsão do dia seguinte?
- A modelagem com LSTM captura corretamente as tendências de curto prazo?
- A previsão da movimentação intradiária também permite derivar com precisão as targets globais do dia (abertura, mínima, máxima e fechamento)?
- Quais indicadores técnicos e features são mais relevantes para melhorar a acurácia do modelo?
- Como considerar corretamente as quebras de fim de semana (exemplo: prever a segunda-feira usando os dados de sexta-feira)?
- A normalização e padronização das variáveis melhora a precisão do modelo?

### 7. Critérios de Sucesso

Para que o MVP seja considerado bem-sucedido o esperado é que:

1. O pipeline de extração, transformação e previsão funcione de forma eficiente.
2. O modelo consiga prever a movimentação dos preços com um erro médio aceitável (avaliado por MSE ou R2).
3. A previsão de targets globais (abertura, máxima, mínima, fechamento) seja consistente com os valores reais.
4. O modelo consiga lidar corretamente com fins de semana e feriados.
5. As previsões sejam suficientes para auxiliar na tomada de decisão de trading.



