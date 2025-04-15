
## Escolha das Features na Transformação dos Dados

O conjunto de dados transformado para o modelo de previsão intradiária de preços do ativo BBDC4 foi projetado para capturar diferentes aspectos do comportamento do mercado financeiro. Abaixo estão listadas as features selecionadas e as respectivas razões para sua inclusão:

### 1. **Retorno e Volatilidade**
- **retorno**: Variação percentual do preço de fechamento entre candles consecutivos.
- **volatilidade**: Desvio padrão do retorno em uma janela móvel, mede a instabilidade e o risco.

### 2. **Médias Móveis**
- **SMA_10**: Média móvel simples de 10 períodos do fechamento.
- **EMA_10**: Média móvel exponencial de 10 períodos, mais sensível a variações recentes.

### 3. **Indicadores de Tendência**
- **MACD**: Diferença entre a média móvel exponencial de 12 e 26 períodos.
- **Signal_Line**: Média móvel exponencial de 9 períodos do MACD.
- **ADX**: Índice direcional médio que quantifica a força da tendência.

### 4. **Indicadores de Momento**
- **RSI (Relative Strength Index)**: Índice de força relativa, indica sobrecompra ou sobrevenda.
- **CCI (Commodity Channel Index)**: Mede variações do preço em relação à média, útil para detectar desvios extremos.

### 5. **Indicadores de Volume**
- **volume**: Volume negociado no candle.
- **OBV (On-Balance Volume)**: Indicador cumulativo que relaciona variação de preço com volume.

### 6. **Bandas de Bollinger**
- **BB_upper**: Banda superior (média + 2 desvios).
- **BB_lower**: Banda inferior (média - 2 desvios).
- **BB_MA20**: Média móvel central de 20 períodos.
- **BB_STD20**: Desvio padrão usado no cálculo das bandas.

### 7. **Estocástico**
- **%K**: Oscilador estocástico baseado em máximas e mínimas.
- **%D**: Média móvel de 3 períodos de %K.

### 8. **ATR (Average True Range)**
- **ATR**: Média da faixa verdadeira, mede a amplitude de oscilação de preços.

### 9. **Lags Temporais**
- **fechamento_lag1, fechamento_lag2, fechamento_lag3**: Preços de fechamento anteriores.
- **retorno_lag1, retorno_lag2, retorno_lag3**: Retornos anteriores.
- **volume_lag1, volume_lag2, volume_lag3**: Volumes negociados anteriores.

### 10. **Variáveis Temporais**
- **dia_da_semana_entrada**: Dia da semana correspondente ao candle atual.
- **dia_da_semana_previsao**: Dia da semana do candle de previsão.
- **hora_num**: Representação numérica da hora do candle.
- **minuto**: Minuto do candle.

### 11. **Resumo Diário do Dia Anterior**
- **fechamento_dia_anterior**: Preço de fechamento do último candle do dia anterior.
- **volume_dia_anterior**: Volume total negociado no dia anterior.
- **maximo_dia_anterior**: Maior preço registrado no dia anterior.
- **minimo_dia_anterior**: Menor preço registrado no dia anterior.
