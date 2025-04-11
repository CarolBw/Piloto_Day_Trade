
#@title Definição do esquema - Modelo Estrela 

O modelo estrela foi escolhido por sua simplicidade e clareza na organização dos dados para análise. Ele é ideal para consultas rápidas e análise preditiva. No nosso projeto, temos um único fato (preços OHLC) e múltiplas variáveis explicativas que os influenciam.

A estrutura facilita agregações temporais e análises do comportamento dos preços, sendo também eficiente para alimentar o pipeline de machine learning. Ao organizar as variáveis preditoras ao redor das medidas de preço, conseguimos isolar responsabilidades e tornar as análises mais precisas e escaláveis.

## Tabela Fato: `fato_precos`
| Coluna         | Tipo   | Descrição                                   |
|----------------|--------|---------------------------------------------|
| id_fato_precos | int    | PK, identificador único da linha            |
| id_tempo       | int    | FK para a dimensão tempo                    |
| abertura       | float  | Preço de abertura                           |
| minimo         | float  | Preço mínimo                                |
| maximo         | float  | Preço máximo                                |
| fechamento     | float  | Preço de fechamento (variável alvo)         |

## Dimensão: `dim_tempo`
| Coluna                | Tipo   | Descrição                                 |
|------------------------|--------|-------------------------------------------|
| id_tempo              | int    | PK                                        |
| data                  | object | Data da observação                        |
| hora                  | object | Hora da observação                        |
| dia_da_semana_entrada | int    | Dia da semana da entrada (0=Seg, 6=Dom)   |

## Dimensão: `dim_indicadores`
| Coluna       | Tipo   | Descrição                                       |
|--------------|--------|--------------------------------------------------|
| id_indicadores | int  | PK                                               |
| id_tempo     | int    | FK para a dimensão tempo                        |
| SMA_10       | float  | Média móvel simples de 10 períodos              |
| EMA_10       | float  | Média móvel exponencial de 10 períodos          |
| MACD         | float  | Moving Average Convergence Divergence           |
| Signal_Line  | float  | Linha de sinal do MACD                          |
| rsi          | float  | Índice de força relativa                        |
| OBV          | float  | On-Balance Volume                               |
| retorno      | float  | Retorno do período                              |
| volatilidade | float  | Volatilidade do período                         |

## Dimensão: `dim_lags`
| Coluna          | Tipo   | Descrição                                       |
|-----------------|--------|--------------------------------------------------|
| id_lags         | int    | PK                                              |
| id_tempo        | int    | FK para a dimensão tempo                        |
| fechamento_lag1 | float  | Fechamento no candle anterior (1 lag)          |
| retorno_lag1    | float  | Retorno do candle anterior (1 lag)             |
| volume_lag1     | float  | Volume do candle anterior (1 lag)              |
| fechamento_lag2 | float  | Fechamento dois candles atrás (2 lags)         |
| retorno_lag2    | float  | Retorno dois candles atrás (2 lags)            |
| volume_lag2     | float  | Volume dois candles atrás (2 lags)             |
| fechamento_lag3 | float  | Fechamento três candles atrás (3 lags)         |
| retorno_lag3    | float  | Retorno três candles atrás (3 lags)            |
| volume_lag3     | float  | Volume três candles atrás (3 lags)             |

## Dimensão: `dim_operacional`
| Coluna                 | Tipo   | Descrição                                      |
|------------------------|--------|------------------------------------------------|
| id_operacional         | int    | PK                                             |
| id_tempo               | int    | FK para a dimensão tempo                       |
| data_previsao          | object | Data prevista para o modelo                    |
| dia_da_semana_previsao | int    | Dia da semana da previsão                      |
| hora_num               | int    | Hora como número inteiro                       |
| minuto                 | int    | Minuto da observação                           |
| mercado_aberto         | int    | Indicador binário (1=aberto, 0=fechado)        |
