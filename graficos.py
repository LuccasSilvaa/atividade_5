import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Backend sem GUI para salvar imagens
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ============================================================
# CONFIGURACOES
# ============================================================
sns.set_theme(style="darkgrid", palette="viridis", font_scale=1.1)
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.bbox'] = 'tight'

# Criar pasta para graficos
os.makedirs('graficos', exist_ok=True)

# Carregar dataset limpo
df = pd.read_csv('energy_economics_limpo.csv')
df['data_observacao'] = pd.to_datetime(df['data_observacao'])

print("=" * 60)
print("GERACAO DE GRAFICOS - ECONOMIA DE ENERGIA")
print("=" * 60)
print(f"Dataset: {df.shape[0]} linhas x {df.shape[1]} colunas\n")

# ============================================================
# GRAFICO 1 - SEABORN: Evolucao da Energia Renovavel Global
# ============================================================
print("[1/8] Evolucao da energia renovavel ao longo dos anos...")

media_renovavel = df.groupby('observation_year')['renewable_energy_consumption_pct_final_energy_use'].mean().reset_index()

fig, ax = plt.subplots(figsize=(14, 6))
sns.lineplot(
    data=media_renovavel,
    x='observation_year',
    y='renewable_energy_consumption_pct_final_energy_use',
    color='#2ecc71',
    linewidth=3,
    marker='o',
    markersize=8,
    ax=ax
)
ax.fill_between(
    media_renovavel['observation_year'],
    media_renovavel['renewable_energy_consumption_pct_final_energy_use'],
    alpha=0.2,
    color='#2ecc71'
)
ax.set_title('Evolucao do Consumo de Energia Renovavel (Media Global)', fontsize=16, fontweight='bold')
ax.set_xlabel('Ano', fontsize=13)
ax.set_ylabel('% do Consumo Final de Energia', fontsize=13)
ax.set_ylim(bottom=0)
plt.savefig('graficos/01_evolucao_energia_renovavel.png')
plt.close()
print("   -> Salvo: graficos/01_evolucao_energia_renovavel.png")

# ============================================================
# GRAFICO 2 - SEABORN: Heatmap de Correlacao
# ============================================================
print("[2/8] Heatmap de correlacao entre variaveis...")

colunas_corr = [
    'renewable_energy_consumption_pct_final_energy_use',
    'co2_emissions_metric_tonnes_per_capita',
    'real_gdp_constant_2015_usd',
    'forest_area_pct_land_area',
    'urban_population_pct_total_population',
    'ecological_footprint_index',
    'adaptive_capacity_index',
    'total_population',
    'average_temperature_celsius',
    'greenhouse_gas_emissions_metric_tonnes_per_capita'
]

# Nomes curtos para o heatmap
nomes_curtos = [
    'Energia Renovavel %',
    'CO2 per Capita',
    'PIB Real (USD)',
    'Area Florestal %',
    'Pop. Urbana %',
    'Pegada Ecologica',
    'Cap. Adaptativa',
    'Populacao Total',
    'Temp. Media (C)',
    'GEE per Capita'
]

corr_matrix = df[colunas_corr].corr()
corr_matrix.index = nomes_curtos
corr_matrix.columns = nomes_curtos

fig, ax = plt.subplots(figsize=(14, 11))
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
sns.heatmap(
    corr_matrix,
    mask=mask,
    annot=True,
    fmt='.2f',
    cmap='RdYlGn',
    center=0,
    square=True,
    linewidths=1,
    cbar_kws={'shrink': 0.8, 'label': 'Correlacao'},
    ax=ax,
    vmin=-1, vmax=1
)
ax.set_title('Matriz de Correlacao - Variaveis de Energia e Economia', fontsize=16, fontweight='bold')
plt.savefig('graficos/02_heatmap_correlacao.png')
plt.close()
print("   -> Salvo: graficos/02_heatmap_correlacao.png")

# ============================================================
# GRAFICO 3 - SEABORN: Top 15 Paises - Emissoes CO2
# ============================================================
print("[3/8] Top 15 paises com maiores emissoes de CO2 (2020)...")

df_2020 = df[df['observation_year'] == 2020].copy()
top15_co2 = df_2020.nlargest(15, 'co2_emissions_metric_tonnes_per_capita')

fig, ax = plt.subplots(figsize=(14, 8))
colors = sns.color_palette('YlOrRd_r', n_colors=15)
sns.barplot(
    data=top15_co2,
    y='country_name',
    x='co2_emissions_metric_tonnes_per_capita',
    palette=colors,
    ax=ax,
    edgecolor='white',
    linewidth=0.8
)
ax.set_title('Top 15 Paises - Emissoes de CO2 per Capita (2020)', fontsize=16, fontweight='bold')
ax.set_xlabel('Toneladas Metricas per Capita', fontsize=13)
ax.set_ylabel('')
# Adicionar valores nas barras
for i, v in enumerate(top15_co2['co2_emissions_metric_tonnes_per_capita']):
    ax.text(v + 0.3, i, f'{v:.1f}', va='center', fontsize=10, fontweight='bold')
plt.savefig('graficos/03_top15_co2_2020.png')
plt.close()
print("   -> Salvo: graficos/03_top15_co2_2020.png")

# ============================================================
# GRAFICO 4 - SEABORN: Distribuicao da Energia Renovavel
# ============================================================
print("[4/8] Distribuicao da energia renovavel por decada...")

df['decada'] = (df['observation_year'] // 5) * 5
df['decada_label'] = df['decada'].astype(str) + '-' + (df['decada'] + 4).astype(str)

fig, ax = plt.subplots(figsize=(14, 7))
sns.violinplot(
    data=df,
    x='decada_label',
    y='renewable_energy_consumption_pct_final_energy_use',
    palette='mako',
    inner='box',
    ax=ax,
    cut=0
)
ax.set_title('Distribuicao do Consumo de Energia Renovavel por Periodo', fontsize=16, fontweight='bold')
ax.set_xlabel('Periodo', fontsize=13)
ax.set_ylabel('% do Consumo Final de Energia', fontsize=13)
plt.savefig('graficos/04_distribuicao_renovavel_periodo.png')
plt.close()
print("   -> Salvo: graficos/04_distribuicao_renovavel_periodo.png")

# ============================================================
# GRAFICO 5 - PLOTLY: Mapa Mundial Interativo - CO2
# ============================================================
print("[5/8] Mapa mundial interativo - Emissoes CO2 (2020)...")

fig = px.choropleth(
    df_2020,
    locations='country_name',
    locationmode='country names',
    color='co2_emissions_metric_tonnes_per_capita',
    hover_name='country_name',
    hover_data={
        'co2_emissions_metric_tonnes_per_capita': ':.2f',
        'renewable_energy_consumption_pct_final_energy_use': ':.1f',
        'total_population': ':,.0f'
    },
    color_continuous_scale='RdYlGn_r',
    title='Emissoes de CO2 per Capita por Pais (2020)',
    labels={
        'co2_emissions_metric_tonnes_per_capita': 'CO2 (ton/capita)',
        'renewable_energy_consumption_pct_final_energy_use': 'Energia Renovavel %',
        'total_population': 'Populacao'
    }
)
fig.update_layout(
    geo=dict(showframe=False, showcoastlines=True, projection_type='natural earth'),
    title_font_size=20,
    height=600,
    margin=dict(l=0, r=0, t=60, b=0)
)
fig.write_html('graficos/05_mapa_co2_2020.html')
print("   -> Salvo: graficos/05_mapa_co2_2020.html")

# ============================================================
# GRAFICO 6 - PLOTLY: Scatter Animado - PIB vs CO2 ao Longo do Tempo
# ============================================================
print("[6/8] Scatter animado - PIB vs CO2 ao longo dos anos...")

fig = px.scatter(
    df,
    x='real_gdp_constant_2015_usd',
    y='co2_emissions_metric_tonnes_per_capita',
    animation_frame='observation_year',
    animation_group='country_name',
    size='total_population',
    color='renewable_energy_consumption_pct_final_energy_use',
    hover_name='country_name',
    log_x=True,
    size_max=60,
    color_continuous_scale='Viridis',
    title='Relacao PIB vs Emissoes de CO2 (Animacao por Ano)',
    labels={
        'real_gdp_constant_2015_usd': 'PIB Real (USD 2015, Log)',
        'co2_emissions_metric_tonnes_per_capita': 'CO2 per Capita (ton)',
        'renewable_energy_consumption_pct_final_energy_use': 'Energia Renovavel %',
        'total_population': 'Populacao'
    },
    range_y=[0, df['co2_emissions_metric_tonnes_per_capita'].quantile(0.98)]
)
fig.update_layout(
    title_font_size=20,
    height=650,
    xaxis_title='PIB Real (USD 2015, Escala Log)',
    yaxis_title='CO2 per Capita (Toneladas Metricas)'
)
fig.write_html('graficos/06_scatter_pib_co2_animado.html')
print("   -> Salvo: graficos/06_scatter_pib_co2_animado.html")

# ============================================================
# GRAFICO 7 - PLOTLY: Comparativo de Paises - Linhas Interativas
# ============================================================
print("[7/8] Evolucao comparativa de paises selecionados...")

paises_destaque = ['Brazil', 'China', 'United States', 'India', 'Germany',
                   'Nigeria', 'Japan', 'South Africa', 'Norway', 'Australia']
df_destaque = df[df['country_name'].isin(paises_destaque)]

fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        'Emissoes CO2 per Capita',
        'Consumo de Energia Renovavel (%)',
        'PIB Real (USD 2015)',
        'Pegada Ecologica'
    ),
    vertical_spacing=0.12,
    horizontal_spacing=0.08
)

colors_map = px.colors.qualitative.D3

for i, pais in enumerate(paises_destaque):
    dp = df_destaque[df_destaque['country_name'] == pais]
    color = colors_map[i % len(colors_map)]
    show_legend = True

    fig.add_trace(go.Scatter(
        x=dp['observation_year'], y=dp['co2_emissions_metric_tonnes_per_capita'],
        name=pais, line=dict(color=color, width=2),
        legendgroup=pais, showlegend=show_legend
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=dp['observation_year'], y=dp['renewable_energy_consumption_pct_final_energy_use'],
        name=pais, line=dict(color=color, width=2),
        legendgroup=pais, showlegend=False
    ), row=1, col=2)

    fig.add_trace(go.Scatter(
        x=dp['observation_year'], y=dp['real_gdp_constant_2015_usd'],
        name=pais, line=dict(color=color, width=2),
        legendgroup=pais, showlegend=False
    ), row=2, col=1)

    fig.add_trace(go.Scatter(
        x=dp['observation_year'], y=dp['ecological_footprint_index'],
        name=pais, line=dict(color=color, width=2),
        legendgroup=pais, showlegend=False
    ), row=2, col=2)

fig.update_layout(
    title_text='Comparativo de Indicadores - Paises Selecionados (1995-2020)',
    title_font_size=20,
    height=800,
    hovermode='x unified',
    legend=dict(orientation='h', yanchor='bottom', y=-0.12, xanchor='center', x=0.5)
)
fig.update_yaxes(title_text='ton/capita', row=1, col=1)
fig.update_yaxes(title_text='%', row=1, col=2)
fig.update_yaxes(title_text='USD', row=2, col=1)
fig.update_yaxes(title_text='Indice', row=2, col=2)

fig.write_html('graficos/07_comparativo_paises.html')
print("   -> Salvo: graficos/07_comparativo_paises.html")

# ============================================================
# GRAFICO 8 - PLOTLY: Sunburst - Emissoes por Regiao
# ============================================================
print("[8/8] Treemap de emissoes totais de GEE por pais (2020)...")

df_2020_top = df_2020.nlargest(30, 'total_greenhouse_gas_emissions_kt_co2e').copy()
df_2020_top['gee_label'] = df_2020_top['total_greenhouse_gas_emissions_kt_co2e'].apply(
    lambda x: f'{x/1000:.0f} Mt'
)

fig = px.treemap(
    df_2020_top,
    path=['country_name'],
    values='total_greenhouse_gas_emissions_kt_co2e',
    color='co2_emissions_metric_tonnes_per_capita',
    color_continuous_scale='RdYlGn_r',
    title='Top 30 Paises - Emissoes Totais de GEE (2020)',
    hover_data={
        'total_greenhouse_gas_emissions_kt_co2e': ':,.0f',
        'co2_emissions_metric_tonnes_per_capita': ':.2f'
    },
    labels={
        'total_greenhouse_gas_emissions_kt_co2e': 'Emissoes GEE (kt CO2e)',
        'co2_emissions_metric_tonnes_per_capita': 'CO2 per Capita'
    }
)
fig.update_layout(
    title_font_size=20,
    height=650,
    margin=dict(l=10, r=10, t=60, b=10)
)
fig.write_html('graficos/08_treemap_emissoes_2020.html')
print("   -> Salvo: graficos/08_treemap_emissoes_2020.html")

# ============================================================
# RESUMO FINAL
# ============================================================
print(f"\n{'=' * 60}")
print("[OK] TODOS OS GRAFICOS GERADOS COM SUCESSO!")
print(f"{'=' * 60}")
print(f"\nPasta: graficos/")
print(f"\n--- SEABORN (imagens PNG) ---")
print(f"  1. 01_evolucao_energia_renovavel.png   - Linha temporal")
print(f"  2. 02_heatmap_correlacao.png            - Matriz de correlacao")
print(f"  3. 03_top15_co2_2020.png                - Barras horizontais")
print(f"  4. 04_distribuicao_renovavel_periodo.png - Violin plot")
print(f"\n--- PLOTLY (HTML interativos) ---")
print(f"  5. 05_mapa_co2_2020.html                - Mapa mundial")
print(f"  6. 06_scatter_pib_co2_animado.html       - Scatter animado")
print(f"  7. 07_comparativo_paises.html            - Painel comparativo")
print(f"  8. 08_treemap_emissoes_2020.html         - Treemap de emissoes")
print(f"\nAbra os arquivos .html no navegador para interatividade!")
