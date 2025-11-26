#!/bin/bash

# Define Domain
DOMAIN="matemai.com.br"

echo "Configuring HTTPS for $DOMAIN..."

# 1. Install Nginx and Certbot
echo "Installing Nginx and Certbot..."
sudo apt-get update
sudo apt-get install -y nginx certbot python3-certbot-nginx

# 2. Create Nginx Configuration
echo "Creating Nginx configuration..."
sudo tee /etc/nginx/sites-available/matemai > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    # Priority rule for ACME challenge to prevent proxying to Streamlit
    location ^~ /.well-known/acme-challenge/ {
        default_type "text/plain";
        root /var/www/html;
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

# Ensure webroot exists
sudo mkdir -p /var/www/html

# 3. Enable Site
echo "Enabling site..."
if [ -f /etc/nginx/sites-enabled/default ]; then
    sudo rm /etc/nginx/sites-enabled/default
fi

if [ ! -f /etc/nginx/sites-enabled/matemai ]; then
    sudo ln -s /etc/nginx/sites-available/matemai /etc/nginx/sites-enabled/
fi

# 4. Test and Restart Nginx
echo "Restarting Nginx..."
sudo nginx -t
sudo systemctl restart nginx

# 5. Run Certbot
echo "Starting Certbot to obtain SSL certificate..."
echo "Please follow the instructions on the screen (enter email, agree to terms)."
# Use webroot authenticator (uses our manual location block) and nginx installer (configures SSL)
sudo certbot -a webroot -i nginx -w /var/www/html -d $DOMAIN -d www.$DOMAIN
