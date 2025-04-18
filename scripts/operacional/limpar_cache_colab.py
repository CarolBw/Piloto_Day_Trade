
# Limpa variáveis
from IPython import get_ipython
get_ipython().magic('reset -f')

# Limpa arquivos temporários e libera memória
import gc
import os
import shutil

# Apaga diretórios temporários customizados (ajuste conforme necessário)
pastas_para_limpar = [
    '/content/__pycache__',
    '/content/sample_data',
    '/content/Piloto_Day_Trade/__pycache__'
]

for pasta in pastas_para_limpar:
    if os.path.exists(pasta):
        shutil.rmtree(pasta)

# Força coleta de lixo
gc.collect()

print("Cache limpo.")
