echo "📱 Setting up mobile app..."

cd mobile

# Install dependencies
echo "Installing dependencies..."
npm install

# Get computer IP address
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n1)
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    IP=$(hostname -I | awk '{print $1}')
else
    # Windows
    IP=$(ipconfig | grep "IPv4" | awk '{print $NF}' | head -n1)
fi

# Create .env file
echo "Creating .env file..."
echo "EXPO_PUBLIC_API_URL=http://${IP}:8000" > .env

echo ""
echo "✅ Mobile app setup complete!"
echo ""
echo "Your API URL: http://${IP}:8000"
echo ""
echo "To start the app, run:"
echo "  cd mobile"
echo "  npx expo start"
echo ""
echo "Then scan the QR code with Expo Go app on your phone"
