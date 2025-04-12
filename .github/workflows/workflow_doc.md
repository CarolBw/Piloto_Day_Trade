
#@title Definindo Documentação do workflow completo para Execução do Pipeline 

## Objetivo

Este documento descreve o fluxo de trabalho para a execução automatizada do pipeline de dados, utilizando o GitHub Actions. O pipeline abrange desde a extração até a modelagem de dados, e foi estruturado para garantir a automação da execução do processo, facilitando atualizações contínuas e execuções programadas no repositório GitHub.

## Estrutura do Pipeline

O pipeline é composto por várias etapas que são executadas em sequência. Cada uma das etapas envolve um script específico para garantir a correta manipulação dos dados:

1. **Extração de Dados:** Obtém os dados brutos de uma fonte externa, como o Yahoo Finance ou qualquer outra fonte configurada.
2. **Limpeza de Dados:** Realiza a limpeza e formatação dos dados brutos.
3. **Transformação de Dados:** Aplica transformações necessárias para deixar os dados prontos para a modelagem.
4. **Criação de Banco Dimensional:** Estrutura os dados de maneira que sejam facilmente analisáveis.
5. **Carga de Dados:** Carrega os dados transformados para o banco de dados.
6. **Geração de Catálogo de Dados:** Cria um catálogo de metadados para facilitar o uso futuro dos dados.
7. **Preparação de Dados para Modelagem LSTM:** Prepara os dados específicos para alimentar o modelo de LSTM.
8. **Modelagem e Avaliação:** Treina e avalia o modelo LSTM.

### Scripts Responsáveis por Cada Etapa

1. **`extracao_dados.py`:** Extração dos dados brutos.
2. **`limpeza_dados.py`:** Limpeza e pré-processamento dos dados brutos.
3. **`transformacao_dados.py`:** Aplicação das transformações necessárias nos dados.
4. **`criar_banco_dimensional.py`:** Criação do banco dimensional para armazenar os dados.
5. **`carga_dados.py`:** Carga dos dados transformados no banco dimensional.
6. **`gerar_catalogo_dados.py`:** Geração do catálogo de dados.
7. **`preparar_dados_modelagem_LSTM.py`:** Preparação final dos dados para treinamento do modelo LSTM.

## GitHub Actions: Workflow

O objetivo é configurar um workflow automatizado no GitHub Actions para que ele execute todo o pipeline a cada novo push ou evento programado. Para isso, criamos um arquivo YAML no repositório do GitHub.

### Workflow: `pipeline.yml`

Este workflow será responsável por orquestrar todas as etapas de execução. Abaixo está o conteúdo do arquivo YAML:

```yaml
name: Pipeline Completo de Dados

on:
  push:
    branches:
      - main
  schedule:
    - cron: '0 0 * * 1'  # Executa toda segunda-feira às 00:00 (UTC)

jobs:
  run_pipeline:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout do repositório
      uses: actions/checkout@v2

    - name: Configurar Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'

    - name: Instalar dependências
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Executar Extração de Dados
      run: python scripts/pipeline/extracao_dados.py

    - name: Executar Limpeza de Dados
      run: python scripts/pipeline/limpeza_dados.py

    - name: Executar Transformação de Dados
      run: python scripts/pipeline/transformacao_dados.py

    - name: Criar Banco Dimensional
      run: python scripts/pipeline/criar_banco_dimensional.py

    - name: Carregar Dados
      run: python scripts/pipeline/carga_dados.py

    - name: Gerar Catálogo de Dados
      run: python scripts/pipeline/gerar_catalogo_dados.py

    - name: Preparar Dados para Modelagem LSTM
      run: python scripts/modelagem_machine_learning/preparar_dados_modelagem_LSTM.py

    - name: Avaliar Modelo LSTM
      run: python scripts/modelagem_machine_learning/calcular_metricas_avaliar_modelo_LSTM.py


  ### Explicação do Workflow:

    - Evento de Acionamento:

    O workflow é acionado por dois eventos principais:

    Push para a branch main: Sempre que um novo commit for enviado para a branch main, o pipeline será executado automaticamente.

    Agendamento Semanal: O pipeline é executado toda segunda-feira às 00:00 UTC, garantindo que os dados sejam atualizados regularmente.

    - Jobs:

    run_pipeline: Este job é o responsável por executar todas as etapas do pipeline.

    Ele é executado em uma máquina virtual Ubuntu, configurada com Python 3.8.

    - Etapas:

    Checkout do Repositório: Faz o checkout do código do repositório.

    Configuração do Python: Configura o ambiente Python necessário.

    Instalação de Dependências: Instala as dependências listadas no requirements.txt.

    Execução das Etapas do Pipeline: Cada etapa do pipeline é executada com o comando python apontando para o script correspondente.

    - Requisitos para o Workflow:
    requirements.txt: Um arquivo contendo todas as dependências necessárias para rodar o pipeline. Ele deve estar no repositório e ser mantido atualizado.

    Acesso ao Repositório: O repositório deve conter todos os scripts e arquivos de dados necessários para a execução do pipeline.
