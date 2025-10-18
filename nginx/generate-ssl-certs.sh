#!/bin/bash

# Script to generate self-signed SSL certificates for development
# For production, use Let's Encrypt or proper CA-signed certificates

echo "Generating self-signed SSL certificates for development..."

# Create nginx/ssl directory if it doesn't exist
mkdir -p nginx/ssl

# Generate private key
openssl genrsa -out nginx/ssl/key.pem 2048

# Generate certificate signing request (CSR)
openssl req -new -key nginx/ssl/key.pem -out nginx/ssl/cert.csr \
  -subj "/C=ZM/ST=Lusaka/L=Lusaka/O=Zambian Farmer Support System/CN=localhost"

# Generate self-signed certificate (valid for 365 days)
openssl x509 -req -days 365 -in nginx/ssl/cert.csr -signkey nginx/ssl/key.pem -out nginx/ssl/cert.pem

# Remove CSR file
rm nginx/ssl/cert.csr

# Set appropriate permissions
chmod 600 nginx/ssl/key.pem
chmod 644 nginx/ssl/cert.pem

echo "✓ SSL certificates generated successfully!"
echo "  - Certificate: nginx/ssl/cert.pem"
echo "  - Private Key: nginx/ssl/key.pem"
echo ""
echo "Note: These are self-signed certificates for development only."
echo "For production, use proper CA-signed certificates or Let's Encrypt."