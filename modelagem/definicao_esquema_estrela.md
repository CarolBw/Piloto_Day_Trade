
# Esquema Estrela - Projeto Piloto_Day_Trade

## Justificativa do Modelo
O modelo estrela foi escolhido por sua simplicidade e clareza na organização dos dados para análise. Ele é ideal para consultas rápidas e análise preditiva. E nosso projeto temos um fato, preçoe variáveis explicativas. 
A estrutura facilita agregações temporais e análises do comportamento.

O modelo será a base para alimentar o pipeline. Ele organiza as variáveis preditoras ao redor da variável alvo, oque permite separar as responsábilidade e facilitar a análise.

## Tabela Fato: `fato_precos`
| Coluna        | Tipo     | Descrição                         |
|---------------|----------|-----------------------------------|
| data          | date     | Data da observação                |
| hora          | string   | Hora da observação                |
| fechamento    | float    | Preço de fechamento (target)     |
| id_dim_tempo  | int      | FK para a dimensão tempo         |
| id_dim_tecnica| int      | FK para indicadores técnicos     |
| id_dim_lags   | int      | FK para lags                     |
| id_dim_volume | int      | FK para volume                   |

## Dimensão: `dim_tempo`
| Coluna                | Tipo   | Descrição                       |
|------------------------|--------|---------------------------------|
| id_dim_tempo          | int    | PK                              |
| dia_da_semana_entrada | int    | Dia da semana da entrada        |
| data_previsao         | date   | Data prevista para análise      |
| dia_da_semana_previsao| int    | Dia da semana da previsão       |
| hora_num              | int    | Hora como número                |
| minuto                | int    | Minuto da hora                  |
| mercado_aberto        | int    | Flag se o mercado estava aberto |

## Dimensão: `dim_tecnica`
| Coluna        | Tipo     | Descrição                        |
|---------------|----------|----------------------------------|
| id_dim_tecnica| int      | PK                               |
| SMA_10        | float    | Média móvel simples (10)         |
| EMA_10        | float    | Média móvel exponencial (10)     |
| MACD          | float    | Convergência/Divergência         |
| Signal_Line   | float    | Linha de sinal do MACD           |
| rsi           | float    | Índice de força relativa         |
| OBV           | float    | On-Balance Volume                |
| retorno       | float    | Retorno diário                   |
| volatilidade  | float    | Volatilidade calculada           |

## Dimensão: `dim_lags`
| Coluna            | Tipo   | Descrição                     |
|-------------------|--------|-------------------------------|
| id_dim_lags       | int    | PK                            |
| fechamento_lag1   | float  | Fechamento D-1                |
| retorno_lag1      | float  | Retorno D-1                   |
| volume_lag1       | float  | Volume D-1                    |
| fechamento_lag2   | float  | Fechamento D-2                |
| retorno_lag2      | float  | Retorno D-2                   |
| volume_lag2       | float  | Volume D-2                    |
| fechamento_lag3   | float  | Fechamento D-3                |
| retorno_lag3      | float  | Retorno D-3                   |
| volume_lag3       | float  | Volume D-3                    |

## Dimensão: `dim_volume`
| Coluna         | Tipo   | Descrição              |
|----------------|--------|------------------------|
| id_dim_volume  | int    | PK                     |
| volume         | int    | Volume negociado       |
| abertura       | float  | Preço de abertura      |
| minimo         | float  | Preço mínimo           |
| maximo         | float  | Preço máximo           |

