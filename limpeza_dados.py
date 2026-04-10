import pandas as pd
import numpy as np

# ============================================================
# 1. CARREGAR DATASET
# ============================================================
df = pd.read_csv('energy_economics_curated.csv')
print("=" * 60)
print("LIMPEZA DO DATASET - ECONOMIA DE ENERGIA")
print("=" * 60)
print(f"\n[INFO] Dataset original: {df.shape[0]} linhas x {df.shape[1]} colunas")

# ============================================================
# 1b. CONVERTER COLUNAS NUMERICAS QUE ESTAO COMO STRING
# ============================================================
colunas_para_numerico = [
    'foreign_direct_investment_net_inflows_pct_gdp',
    'real_gdp_constant_2015_usd',
    'natural_capital_dependency_index',
]
for col in colunas_para_numerico:
    df[col] = pd.to_numeric(df[col], errors='coerce')
print(f"\n[CONVERSAO] Colunas convertidas para numerico: {len(colunas_para_numerico)}")

# ============================================================
# 2. REMOVER DUPLICADOS
# ============================================================
duplicados_antes = df.duplicated().sum()
df = df.drop_duplicates()
duplicados_exatos = duplicados_antes

# Duplicados por país + ano (registros que não deveriam existir)
duplicados_chave = df.duplicated(subset=['country_name', 'observation_year']).sum()
df = df.drop_duplicates(subset=['country_name', 'observation_year'], keep='last')

print(f"\n[DUPLICADOS] REMOVIDOS:")
print(f"   - Linhas exatamente duplicadas: {duplicados_exatos}")
print(f"   - Duplicados por (país, ano):   {duplicados_chave}")
print(f"   - Linhas após remoção:          {df.shape[0]}")

# ============================================================
# 3. CONVERTER DATAS
# ============================================================
# Converter observation_year para datetime (início do ano)
df['observation_year'] = df['observation_year'].astype(int)
df['data_observacao'] = pd.to_datetime(df['observation_year'], format='%Y')

# Garantir que country_identifier é inteiro
df['country_identifier'] = df['country_identifier'].astype(int)

print(f"\n[DATAS] CONVERSAO DE DATAS:")
print(f"   - 'observation_year' mantido como int")
print(f"   - 'data_observacao' criada como datetime")
print(f"   - Período: {df['observation_year'].min()} a {df['observation_year'].max()}")

# ============================================================
# 4. REMOVER DADOS INVÁLIDOS
# ============================================================
linhas_antes = df.shape[0]
invalid_log = []

# 4a. Percentuais devem estar entre 0 e 100
colunas_pct = [
    'forest_area_pct_land_area',
    'renewable_energy_consumption_pct_final_energy_use',
    'urban_population_pct_total_population',
]

for col in colunas_pct:
    invalidos = ((df[col] < 0) | (df[col] > 100)).sum()
    if invalidos > 0:
        invalid_log.append(f"   - {col}: {invalidos} valores fora de [0, 100]")
        df.loc[(df[col] < 0) | (df[col] > 100), col] = np.nan

# 4b. Emissões de CO2 não podem ser negativas
colunas_nao_negativas = [
    'co2_emissions_metric_tonnes_per_capita',
    'total_greenhouse_gas_emissions_kt_co2e',
    'greenhouse_gas_emissions_metric_tonnes_per_capita',
    'ecological_footprint_index',
    'total_population',
    'land_area_sq_km',
    'surface_area_sq_km',
]

for col in colunas_nao_negativas:
    invalidos = (df[col] < 0).sum()
    if invalidos > 0:
        invalid_log.append(f"   - {col}: {invalidos} valores negativos")
        df.loc[df[col] < 0, col] = np.nan

# 4c. Índices entre 0 e 1
colunas_indice = [
    'adaptive_capacity_index',
    'readiness_index',
]

for col in colunas_indice:
    invalidos = ((df[col] < 0) | (df[col] > 1)).sum()
    if invalidos > 0:
        invalid_log.append(f"   - {col}: {invalidos} valores fora de [0, 1]")
        df.loc[(df[col] < 0) | (df[col] > 1), col] = np.nan

# 4d. Anos fora do intervalo razoável
invalidos_ano = ((df['observation_year'] < 1990) | (df['observation_year'] > 2025)).sum()
if invalidos_ano > 0:
    invalid_log.append(f"   - observation_year: {invalidos_ano} anos fora de [1990, 2025]")
    df = df[(df['observation_year'] >= 1990) & (df['observation_year'] <= 2025)]

print(f"\n[VALIDACAO] DADOS INVALIDOS CORRIGIDOS:")
if invalid_log:
    for msg in invalid_log:
        print(msg)
else:
    print("   - Nenhum dado inválido encontrado!")

linhas_removidas = linhas_antes - df.shape[0]
print(f"   - Linhas removidas por ano inválido: {linhas_removidas}")

# ============================================================
# 5. PREENCHER VALORES NULOS
# ============================================================
nulos_antes = df.isnull().sum()
nulos_total_antes = nulos_antes.sum()

print(f"\n[NULOS] PREENCHIMENTO DE NULOS (total antes: {nulos_total_antes}):")

# 5a. Colunas numéricas - preencher com mediana por país (interpolação por grupo)
colunas_numericas = df.select_dtypes(include=[np.number]).columns.tolist()
colunas_numericas = [c for c in colunas_numericas if c not in ['country_identifier', 'observation_year']]

for col in colunas_numericas:
    nulos_col = df[col].isnull().sum()
    if nulos_col > 0:
        # Primeiro: interpolar dentro de cada país (tendência temporal)
        df[col] = df.groupby('country_name')[col].transform(
            lambda x: x.interpolate(method='linear', limit_direction='both')
        )
        # Segundo: preencher restantes com mediana global
        restantes = df[col].isnull().sum()
        if restantes > 0:
            df[col] = df[col].fillna(df[col].median())
        
        preenchidos = nulos_col - df[col].isnull().sum()
        if preenchidos > 0:
            print(f"   - {col}: {preenchidos} nulos preenchidos")

nulos_total_depois = df.isnull().sum().sum()
print(f"   - Total de nulos restantes: {nulos_total_depois}")

# ============================================================
# 6. AJUSTAR TIPOS DE DADOS
# ============================================================
# Garantir tipos corretos após preenchimento
df['country_name'] = df['country_name'].astype(str).str.strip()
df['total_population'] = df['total_population'].astype(int)

print(f"\n[TIPOS] DADOS AJUSTADOS:")
print(f"   - country_name: string (sem espaços extras)")
print(f"   - total_population: int")

# ============================================================
# 7. ORDENAR DATASET
# ============================================================
df = df.sort_values(['country_name', 'observation_year']).reset_index(drop=True)

# ============================================================
# 8. SALVAR DATASET LIMPO
# ============================================================
arquivo_limpo = 'energy_economics_limpo.csv'
df.to_csv(arquivo_limpo, index=False)

print(f"\n{'=' * 60}")
print(f"[OK] RESUMO FINAL")
print(f"{'=' * 60}")
print(f"   Linhas finais:  {df.shape[0]}")
print(f"   Colunas finais: {df.shape[1]}")
print(f"   Nulos restantes: {df.isnull().sum().sum()}")
print(f"   Arquivo salvo:  {arquivo_limpo}")
print(f"\n[COLUNAS] Dataset limpo:")
for i, col in enumerate(df.columns, 1):
    print(f"   {i:2d}. {col} ({df[col].dtype})")

print(f"\n[AMOSTRA] Primeiras 3 linhas:")
print(df.head(3).to_string())
