#!/bin/bash
# Run this script ONCE on your server to obtain the first SSL certificate.
# Make sure your DNS A records are pointing to this server before running.
#
# Usage: chmod +x init-certbot.sh && ./init-certbot.sh

set -e

DOMAIN="ship-ai.app"
EMAIL="your-email@example.com"   # ← change this to your real email

echo ">>> Downloading recommended SSL params from Certbot..."
mkdir -p ./certbot/conf

curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf \
  -o ./certbot/conf/options-ssl-nginx.conf

curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/_internal/cli/cli_defaults.py \
  | grep -q 'ssl_dhparams' || true   # just a check

# Generate a strong DH param if it doesn't exist yet
if [ ! -f ./certbot/conf/ssl-dhparams.pem ]; then
  echo ">>> Generating DH params (this may take a minute)..."
  openssl dhparam -out ./certbot/conf/ssl-dhparams.pem 2048
fi

echo ">>> Starting nginx in HTTP-only mode for ACME challenge..."
# Temporarily use a minimal config that only serves port 80
docker compose up -d nginx

echo ">>> Requesting certificate from Let's Encrypt..."
docker compose run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email "$EMAIL" \
  --agree-tos \
  --no-eff-email \
  -d "$DOMAIN" \
  -d "www.$DOMAIN"

echo ">>> Reloading nginx to load the new certificate..."
docker compose exec nginx nginx -s reload

echo ""
echo "✅  Done! Certificate issued for $DOMAIN and www.$DOMAIN"
echo "    Auto-renewal is handled by the certbot service in docker-compose.yml"