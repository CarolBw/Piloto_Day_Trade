#@title Analise de qualidade dos dados

**Relatório de Qualidade e Preparação dos Dados do Ativo BBDC4**

Este relatório documenta todas as etapas do processo de preparação dos dados,  extração, limpeza, transformação e análise de qualidade considerando preparação final para o modelo.


### **1. Extração dos Dados**

Os dados brutos foram extraídos do Yahoo (Yfinance) trazendo informações financeiras do ativo BBDC4 em intervalos regulares de 5 minutos. A base original incluía colunas como `data`, `hora`, `abertura`, `fechamento`, `máximo`, `mínimo` e `volume`. A extração garantiu a correta interpretação dos formatos de data e hora e a integração completa dos registros sem perdas.


### **2. Limpeza dos Dados**

A limpeza assegurou a integridade e consistência dos dados, por meio das seguintes etapas:

- Remoção de valores nulos (`NaN`) e registros duplicados;
- Conversão de tipos incorretos, como datas representadas como string para o tipo `datetime`;
- Padronização dos nomes e tipos das colunas principais;
- Validação de intervalos temporais e de valores numéricos coerentes (sem valores negativos indevidos ou zeros onde não aplicáveis).

Ao final desta etapa, os dados estavam prontos para transformação, sem anomalias estruturais.


### **3. Transformação dos Dados**

A transformação incluiu o enriquecimento da base com indicadores técnicos, variáveis derivadas, ajustes temporais e integração incremental com a base consolidada.

#### **3.1 Indicadores Técnicos**

- **Retorno e Volatilidade** (curto prazo);
- **SMA e EMA** (médias móveis);
- **MACD e Linha de Sinal** (tendência);
- **ADX** (força da tendência);
- **RSI, CCI, Estocástico** (momentum);
- **OBV** (volume e direção);
- **Bandas de Bollinger** (volatilidade);
- **ATR** (amplitude de variação).

#### **3.2 Variáveis de Lag**

Foram criadas defasagens de 1, 2 e 3 períodos para `fechamento`, `retorno` e `volume`, permitindo a captura de padrões temporais.

#### **3.3 Variáveis Temporais**

- Conversão de `hora:minuto` para formato numérico;
- Extração do **dia da semana** para fins de sazonalidade;
- Criação de flags para fins de semana e feriados (se aplicável).

#### **3.4 Variáveis Diárias e de Contexto**

- Cálculo da **abertura, fechamento, máxima, mínima e volume diários**;
- Inclusão dos valores do **dia anterior** como contexto para o modelo.

#### **3.5 Filtro Temporal e Integração**

- Processamento restrito a datas posteriores à última data já presente no histórico transformado, evitando retrabalho;
- Integração incremental da nova base com o histórico existente e salva em diretório apropriado do pipeline.


### **4. Diagnóstico de Qualidade dos Dados Transformados**

Foram aplicadas validações para garantir a robustez da base:

- **Integridade:** Nenhum valor nulo remanescente; campos essenciais completos;
- **Consistência Temporal:** Candles com intervalos regulares entre 10h e 17h em dias úteis; datas e horas ordenadas;
- **Estatísticas:** Retornos e volatilidades distribuídos conforme esperado; sem outliers estruturais significativos;
- **Completude de Features:** Todos os indicadores e variáveis derivadas presentes após burn-in inicial.

### **5. Conclusão Geral**

O dataset final apresenta elevada qualidade, estruturado para modelagem preditiva de movimentação intradiária. A riqueza de variáveis, associada à coerência temporal e informacional, permite a utilização segura em modelos baseados em séries temporais, como LSTM ou Transformer. A base está pronta para uso em análises avançadas de mercado.

Além disso, os dados finais preparados para o modelo incluem as seguintes peculiaridades:

- As features e os targets são normalizados separadamente usando `MinMaxScaler`;
- Os dados são organizados em sequências baseadas nos **3 dias úteis anteriores** ao dia de previsão;
- Apenas dias com **sequência completa de candles** (84 candles por dia entre 10h e 17h) são utilizados;
- As datas válidas para previsão são registradas e associadas às amostras geradas;
- Os dados normalizados e os scalers são persistidos em disco, prontos para uso nos experimentos com LSTM intradiária.

