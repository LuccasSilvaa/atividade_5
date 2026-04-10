#!/bin/sh

echo "============================================"
echo "  Energy Economics Dashboard"
echo "============================================"

# Iniciar Nginx em background
nginx

echo "[OK] Nginx rodando na porta 80"

# Iniciar Cloudflare Tunnel
echo "[...] Iniciando Cloudflare Tunnel..."
echo ""

cloudflared tunnel --url http://localhost:80 --no-autoupdate
