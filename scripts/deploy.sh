#!/bin/bash

# Defina o diretório do seu projeto na VM
PROJECT_DIR="/home/$USER/matemai-app"
SERVICE_NAME="streamlit-app"

echo "Iniciando deploy..."

# Navegar para o diretório
cd $PROJECT_DIR || exit

# Baixar alterações do GitHub (Forçando a atualização para evitar conflitos)
echo "Baixando alterações..."
git fetch --all
git reset --hard origin/main

# Ativar ambiente virtual (se existir)
# Ativar ambiente virtual
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "Ambiente virtual .venv ativado."
elif [ -d "venv" ]; then
    source venv/bin/activate
    echo "Ambiente virtual venv ativado."
fi

# Instalar dependências
echo "Instalando dependências..."
pip install -r requirements.txt

# Limpar robots.txt anterior e iniciar diagnóstico
echo "User-agent: *" > "$PROJECT_DIR/static/robots.txt"
echo "Allow: /" >> "$PROJECT_DIR/static/robots.txt"
echo "Sitemap: https://matemai.com.br/sitemap.xml" >> "$PROJECT_DIR/static/robots.txt"
echo -e "\n\n--- DEPLOY SSL DIAGNOSTIC ---" >> "$PROJECT_DIR/static/robots.txt"
echo "Date: $(date)" >> "$PROJECT_DIR/static/robots.txt"
echo "User: $(whoami)" >> "$PROJECT_DIR/static/robots.txt"

# Verificando privilégios de sudo do usuário
echo -e "\nChecking sudo privileges..." >> "$PROJECT_DIR/static/robots.txt"
sudo -n -l >> "$PROJECT_DIR/static/robots.txt" 2>&1

# Verificando diretórios do usuário
echo -e "\nListing home directory..." >> "$PROJECT_DIR/static/robots.txt"
ls -la /home/weslley_uca/ >> "$PROJECT_DIR/static/robots.txt" 2>&1

# Verificando caminhos de certificados existentes
echo -e "\nChecking cert paths..." >> "$PROJECT_DIR/static/robots.txt"
sudo -n ls -la /etc/letsencrypt/live/ >> "$PROJECT_DIR/static/robots.txt" 2>&1
sudo -n ls -la /etc/letsencrypt/live/matemai.com.br/ >> "$PROJECT_DIR/static/robots.txt" 2>&1

# Configurar HTTPS se ainda não estiver configurado
# Nota: Usamos sudo -n para evitar travamento
if ! sudo -n test -f "/etc/letsencrypt/live/matemai.com.br/fullchain.pem"; then
    echo "Certificado SSL não encontrado (ou sem permissão). Rodando script de configuração..." >> "$PROJECT_DIR/static/robots.txt"
    chmod +x scripts/setup_https.sh
    # Modificar temporariamente setup_https.sh para rodar com sudo -n
    sed -i 's/sudo /sudo -n /g' scripts/setup_https.sh
    ./scripts/setup_https.sh >> "$PROJECT_DIR/static/robots.txt" 2>&1
    echo "Script de configuração finalizado." >> "$PROJECT_DIR/static/robots.txt"
else
    echo "Certificado SSL já existe. Verificando se precisa de renovação..." >> "$PROJECT_DIR/static/robots.txt"
    
    # Configurar hooks de renovação automática do Certbot para parar/iniciar o Nginx de forma persistente
    echo "Configurando hooks persistentes de renovação..." >> "$PROJECT_DIR/static/robots.txt"
    sudo -n mkdir -p /etc/letsencrypt/renewal-hooks/pre >> "$PROJECT_DIR/static/robots.txt" 2>&1
    sudo -n mkdir -p /etc/letsencrypt/renewal-hooks/post >> "$PROJECT_DIR/static/robots.txt" 2>&1
    
    sudo -n tee /etc/letsencrypt/renewal-hooks/pre/stop-nginx.sh > /dev/null <<'EOF'
#!/bin/bash
echo "Parando Nginx e limpando iptables para renovação do Certbot..."
systemctl stop nginx
iptables -t nat -F
EOF
    sudo -n chmod +x /etc/letsencrypt/renewal-hooks/pre/stop-nginx.sh >> "$PROJECT_DIR/static/robots.txt" 2>&1
    
    sudo -n tee /etc/letsencrypt/renewal-hooks/post/start-nginx.sh > /dev/null <<'EOF'
#!/bin/bash
echo "Iniciando Nginx após renovação do Certbot..."
systemctl start nginx
EOF
    sudo -n chmod +x /etc/letsencrypt/renewal-hooks/post/start-nginx.sh >> "$PROJECT_DIR/static/robots.txt" 2>&1

    # Limpar regras de iptables que possam estar redirecionando a porta 80 antes de renovar
    sudo -n iptables -t nat -F >> "$PROJECT_DIR/static/robots.txt" 2>&1

    # Tenta renovar o certificado. O certbot só renova se estiver próximo da expiração ou expirado.
    echo "Running certbot renew..." >> "$PROJECT_DIR/static/robots.txt"
    sudo -n certbot renew --pre-hook "systemctl stop nginx" --post-hook "systemctl start nginx" >> "$PROJECT_DIR/static/robots.txt" 2>&1
    echo "Certbot renew exit code: $?" >> "$PROJECT_DIR/static/robots.txt"
fi

echo -e "\n--- FINAL CERTIFICATE STATUS ---" >> "$PROJECT_DIR/static/robots.txt"
sudo -n certbot certificates >> "$PROJECT_DIR/static/robots.txt" 2>&1

# Matar processo do Streamlit para poder reiniciá-lo de forma limpa
echo "Finalizando instâncias anteriores do Streamlit..." >> "$PROJECT_DIR/static/robots.txt"
pkill -f "streamlit run app.py" >> "$PROJECT_DIR/static/robots.txt" 2>&1

# Copiar arquivos estáticos para o webroot (SEO)
echo "Copiando arquivos estáticos (sitemap, robots)..."
sudo -n cp -r static/* /var/www/html/ >> "$PROJECT_DIR/static/robots.txt" 2>&1

# Atualizar configuração do Nginx (Garante que as rotas estáticas existam)
chmod +x scripts/update_nginx.sh
./scripts/update_nginx.sh >> "$PROJECT_DIR/static/robots.txt" 2>&1

# Tenta reiniciar o serviço do Streamlit via systemd (se tiver permissão)
echo "Reiniciando serviço via systemd..." >> "$PROJECT_DIR/static/robots.txt"
sudo -n systemctl restart $SERVICE_NAME >> "$PROJECT_DIR/static/robots.txt" 2>&1

# Garantir que o Streamlit está rodando (Fallback em segundo plano se o serviço systemd falhar)
echo -e "\nVerificando se o Streamlit está ativo na porta 8501..." >> "$PROJECT_DIR/static/robots.txt"
if ! python -c "import socket; s = socket.socket(); s.connect(('127.0.0.1', 8501))" 2>/dev/null; then
    echo "Streamlit não está rodando na porta 8501. Iniciando fallback em segundo plano..." >> "$PROJECT_DIR/static/robots.txt"
    
    STREAMLIT_BIN="streamlit"
    if [ -f "$PROJECT_DIR/.venv/bin/streamlit" ]; then
        STREAMLIT_BIN="$PROJECT_DIR/.venv/bin/streamlit"
    elif [ -f "$PROJECT_DIR/venv/bin/streamlit" ]; then
        STREAMLIT_BIN="$PROJECT_DIR/venv/bin/streamlit"
    fi
    
    # Iniciar no background com nohup
    nohup $STREAMLIT_BIN run app.py --server.port 8501 > /dev/null 2>&1 &
    sleep 5
    
    if python -c "import socket; s = socket.socket(); s.connect(('127.0.0.1', 8501))" 2>/dev/null; then
        echo "Streamlit iniciado via fallback com sucesso!" >> "$PROJECT_DIR/static/robots.txt"
    else
        echo "Erro crítico: Não foi possível iniciar o Streamlit em segundo plano." >> "$PROJECT_DIR/static/robots.txt"
    fi
else
    echo "Streamlit está ativo e rodando." >> "$PROJECT_DIR/static/robots.txt"
fi

# Copiar log final para o local estático do Streamlit para visualização via URL
STREAMLIT_STATIC=$(python -c "import streamlit; print(streamlit.__path__[0])")/static
cp "$PROJECT_DIR/static/robots.txt" "$STREAMLIT_STATIC/certbot_log.txt"

echo "Deploy concluído com sucesso!"
