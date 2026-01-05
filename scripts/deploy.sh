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

# Configurar HTTPS se ainda não estiver configurado
if [ ! -f "/etc/letsencrypt/live/matemai.com.br/fullchain.pem" ]; then
    echo "Certificado SSL não encontrado. Rodando script de configuração..."
    chmod +x scripts/setup_https.sh
    ./scripts/setup_https.sh
else
    echo "Certificado SSL já existe. Pulando configuração."
fi

# Reiniciar o serviço do Streamlit
echo "Reiniciando serviço..."
sudo systemctl restart $SERVICE_NAME

echo "Deploy concluído com sucesso!"
