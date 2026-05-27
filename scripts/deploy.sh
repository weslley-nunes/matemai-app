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

# Verificando caminhos de certificados existentes
echo "Checking cert paths..." >> "$PROJECT_DIR/static/robots.txt"
sudo ls -la /etc/letsencrypt/live/ >> "$PROJECT_DIR/static/robots.txt" 2>&1
sudo ls -la /etc/letsencrypt/live/matemai.com.br/ >> "$PROJECT_DIR/static/robots.txt" 2>&1

# Configurar HTTPS se ainda não estiver configurado
if [ ! -f "/etc/letsencrypt/live/matemai.com.br/fullchain.pem" ]; then
    echo "Certificado SSL não encontrado. Rodando script de configuração..." >> "$PROJECT_DIR/static/robots.txt"
    chmod +x scripts/setup_https.sh
    ./scripts/setup_https.sh >> "$PROJECT_DIR/static/robots.txt" 2>&1
    echo "Script de configuração finalizado." >> "$PROJECT_DIR/static/robots.txt"
else
    echo "Certificado SSL já existe. Verificando se precisa de renovação..." >> "$PROJECT_DIR/static/robots.txt"
    
    # Configurar hooks de renovação automática do Certbot para parar/iniciar o Nginx de forma persistente
    echo "Configurando hooks persistentes de renovação..." >> "$PROJECT_DIR/static/robots.txt"
    sudo mkdir -p /etc/letsencrypt/renewal-hooks/pre >> "$PROJECT_DIR/static/robots.txt" 2>&1
    sudo mkdir -p /etc/letsencrypt/renewal-hooks/post >> "$PROJECT_DIR/static/robots.txt" 2>&1
    
    sudo tee /etc/letsencrypt/renewal-hooks/pre/stop-nginx.sh > /dev/null <<'EOF'
#!/bin/bash
echo "Parando Nginx e limpando iptables para renovação do Certbot..."
systemctl stop nginx
iptables -t nat -F
EOF
    sudo chmod +x /etc/letsencrypt/renewal-hooks/pre/stop-nginx.sh >> "$PROJECT_DIR/static/robots.txt" 2>&1
    
    sudo tee /etc/letsencrypt/renewal-hooks/post/start-nginx.sh > /dev/null <<'EOF'
#!/bin/bash
echo "Iniciando Nginx após renovação do Certbot..."
systemctl start nginx
EOF
    sudo chmod +x /etc/letsencrypt/renewal-hooks/post/start-nginx.sh >> "$PROJECT_DIR/static/robots.txt" 2>&1

    # Limpar regras de iptables que possam estar redirecionando a porta 80 antes de renovar
    sudo iptables -t nat -F >> "$PROJECT_DIR/static/robots.txt" 2>&1

    # Tenta renovar o certificado. O certbot só renova se estiver próximo da expiração ou expirado.
    echo "Running certbot renew..." >> "$PROJECT_DIR/static/robots.txt"
    sudo certbot renew --pre-hook "systemctl stop nginx" --post-hook "systemctl start nginx" >> "$PROJECT_DIR/static/robots.txt" 2>&1
    echo "Certbot renew exit code: $?" >> "$PROJECT_DIR/static/robots.txt"
fi

echo -e "\n--- FINAL CERTIFICATE STATUS ---" >> "$PROJECT_DIR/static/robots.txt"
sudo certbot certificates >> "$PROJECT_DIR/static/robots.txt" 2>&1


# Copiar arquivos estáticos para o webroot (SEO)
echo "Copiando arquivos estáticos (sitemap, robots)..."
sudo cp -r static/* /var/www/html/

# Copiar log para a pasta estática do Streamlit (Permite acesso via URL)
STREAMLIT_STATIC=$(python -c "import streamlit; print(streamlit.__path__[0])")/static
echo "Copiando logs para a pasta estática do Streamlit: $STREAMLIT_STATIC"
cp "$PROJECT_DIR/static/robots.txt" "$STREAMLIT_STATIC/certbot_log.txt"

# Atualizar configuração do Nginx (Garante que as rotas estáticas existam)
chmod +x scripts/update_nginx.sh
./scripts/update_nginx.sh

# Reiniciar o serviço do Streamlit
echo "Reiniciando serviço..."
sudo systemctl restart $SERVICE_NAME

echo "Deploy concluído com sucesso!"
