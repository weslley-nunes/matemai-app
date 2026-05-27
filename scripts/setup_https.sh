#!/bin/bash

# Define Domain
DOMAIN="matemai.com.br"
EMAIL="contato@matemai.com.br"

echo "Configuring HTTPS for $DOMAIN..."

# 1. Install Nginx and Certbot (if not already installed)
echo "Ensuring Nginx and Certbot are installed..."
sudo -n apt-get update
sudo -n apt-get install -y nginx certbot python3-certbot-nginx

# 2. Stop Nginx to free up port 80 for Certbot Standalone
echo "Stopping Nginx..."
sudo -n systemctl stop nginx

# 3. Clear iptables redirects that might hijack port 80 (CRITICAL FIX)
echo "Clearing iptables NAT rules..."
sudo -n iptables -t nat -F

# Configurar hooks de renovação automática do Certbot para parar/iniciar o Nginx de forma persistente
echo "Configurando hooks persistentes de renovação..."
sudo -n mkdir -p /etc/letsencrypt/renewal-hooks/pre
sudo -n mkdir -p /etc/letsencrypt/renewal-hooks/post

sudo -n tee /etc/letsencrypt/renewal-hooks/pre/stop-nginx.sh > /dev/null <<'EOF'
#!/bin/bash
echo "Parando Nginx e limpando iptables para renovação do Certbot..."
systemctl stop nginx
iptables -t nat -F
EOF
sudo -n chmod +x /etc/letsencrypt/renewal-hooks/pre/stop-nginx.sh

sudo -n tee /etc/letsencrypt/renewal-hooks/post/start-nginx.sh > /dev/null <<'EOF'
#!/bin/bash
echo "Iniciando Nginx após renovação do Certbot..."
systemctl start nginx
EOF
sudo -n chmod +x /etc/letsencrypt/renewal-hooks/post/start-nginx.sh

# 4. Obtain Certificate (Standalone Mode)
echo "Obtaining SSL Certificate..."
sudo -n certbot certonly --standalone -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email $EMAIL

# 4. Create Nginx Configuration with SSL
echo "Creating Nginx configuration..."
sudo -n tee /etc/nginx/sites-available/matemai > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl;
    server_name $DOMAIN www.$DOMAIN;

    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header Host \$host;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
EOF

# 5. Enable Site
echo "Enabling site..."
if [ -f /etc/nginx/sites-enabled/default ]; then
    sudo -n rm /etc/nginx/sites-enabled/default
fi

if [ ! -f /etc/nginx/sites-enabled/matemai ]; then
    sudo -n ln -s /etc/nginx/sites-available/matemai /etc/nginx/sites-enabled/
fi

# 6. Restart Nginx
echo "Starting Nginx..."
sudo -n systemctl start nginx

echo "HTTPS Configuration Complete!"
