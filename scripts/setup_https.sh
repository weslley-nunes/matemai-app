#!/bin/bash

# Define Domain
DOMAIN="matemai.com.br"
EMAIL="contato@matemai.com.br"

echo "Configuring HTTPS for $DOMAIN..."

# 1. Install Nginx and Certbot (if not already installed)
echo "Ensuring Nginx and Certbot are installed..."
sudo apt-get update
sudo apt-get install -y nginx certbot python3-certbot-nginx

# 2. Stop Nginx to free up port 80 for Certbot Standalone
echo "Stopping Nginx..."
sudo systemctl stop nginx

# 3. Clear iptables redirects that might hijack port 80 (CRITICAL FIX)
echo "Clearing iptables NAT rules..."
sudo iptables -t nat -F

# 4. Obtain Certificate (Standalone Mode)
echo "Obtaining SSL Certificate..."
sudo certbot certonly --standalone -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email $EMAIL

# 4. Create Nginx Configuration with SSL
echo "Creating Nginx configuration..."
sudo tee /etc/nginx/sites-available/matemai > /dev/null <<EOF
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
    sudo rm /etc/nginx/sites-enabled/default
fi

if [ ! -f /etc/nginx/sites-enabled/matemai ]; then
    sudo ln -s /etc/nginx/sites-available/matemai /etc/nginx/sites-enabled/
fi

# 6. Restart Nginx
echo "Starting Nginx..."
sudo systemctl start nginx

echo "HTTPS Configuration Complete!"
