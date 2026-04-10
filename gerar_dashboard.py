import pandas as pd
import json

df = pd.read_csv('energy_economics_limpo.csv')
df = df.drop(columns=['data_observacao'], errors='ignore')

# Converter para JSON compacto
data_json = df.to_json(orient='records', double_precision=4)

print(f"Dados: {len(df)} registros, tamanho JSON: {len(data_json)//1024} KB")

# Salvar JSON separado para o dashboard carregar
with open('dados_dashboard.json', 'w', encoding='utf-8') as f:
    f.write(data_json)

print("Arquivo dados_dashboard.json gerado com sucesso!")
