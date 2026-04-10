# ============================================================
# Stage 1: Pipeline de Dados (Python)
# ============================================================
FROM python:3.11-slim AS builder

WORKDIR /app

# Instalar dependencias Python
RUN pip install --no-cache-dir pandas numpy matplotlib seaborn plotly

# Copiar dataset e scripts
COPY energy_economics_curated.csv .
COPY limpeza_dados.py .
COPY graficos.py .
COPY gerar_dashboard.py .

# Executar pipeline de dados
RUN python limpeza_dados.py \
    && python graficos.py \
    && python gerar_dashboard.py

# ============================================================
# Stage 2: Servir Dashboard (Nginx)
# ============================================================
FROM nginx:alpine

# Copiar configuracao customizada do Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copiar dashboard e dados gerados
COPY dashboard.html /usr/share/nginx/html/index.html
COPY --from=builder /app/dados_dashboard.json /usr/share/nginx/html/
COPY --from=builder /app/graficos/ /usr/share/nginx/html/graficos/

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
