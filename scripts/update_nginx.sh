#!/bin/bash

DOMAIN="matemai.com.br"

echo "Updating Nginx configuration for $DOMAIN..."

# Create Nginx Configuration with SSL and Static Files
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

    # SEO Static Files
    location /sitemap.xml {
        alias /var/www/html/sitemap.xml;
    }

    location /robots.txt {
        alias /var/www/html/robots.txt;
    }

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

# Enable Site
if [ ! -f /etc/nginx/sites-enabled/matemai ]; then
    sudo ln -s /etc/nginx/sites-available/matemai /etc/nginx/sites-enabled/
fi

# Restart Nginx
echo "Reloading Nginx..."
sudo systemctl reload nginx
echo "Nginx configuration updated!"
