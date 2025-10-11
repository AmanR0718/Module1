# 🚀 Quick Start Guide

## Step 1: Install Prerequisites (5 minutes)

### Install Docker Desktop
- Windows/Mac: Download from https://www.docker.com/products/docker-desktop
- Linux: `curl -fsSL https://get.docker.com | sh`

### Install Node.js (for mobile app)
- Download from https://nodejs.org (LTS version)

## Step 2: Download Project Files (2 minutes)

1. Create project folder:
```bash
mkdir zambian-farmer-system
cd zambian-farmer-system
```

2. Copy all files from the artifacts provided into this folder
   - Maintain the folder structure shown in the documentation

## Step 3: Start Backend (3 minutes)

```bash
# Copy environment template
cp .env.example .env

# Start all services with Docker
docker-compose up -d

# Wait 30 seconds for services to start

# Initialize database
docker-compose exec mongodb mongosh -u admin -p password123 \
  --authenticationDatabase admin zambian_farmers \
  /docker-entrypoint-initdb.d/init.js
```

## Step 4: Test Backend (1 minute)

Open browser: http://localhost:8000/docs

Default login:
- Email: admin@zambian-farmers.zm
- Password: admin123

## Step 5: Setup Mobile App (5 minutes)

```bash
cd mobile

# Install dependencies
npm install

# Install Expo CLI
npm install -g expo-cli

# Find your computer's IP
# Windows: ipconfig
# Mac/Linux: ifconfig

# Create .env file with your IP
echo "EXPO_PUBLIC_API_URL=http://YOUR_IP:8000" > .env

# Start app
npx expo start
```

## Step 6: Run on Phone

1. Install "Expo Go" from App Store/Play Store
2. Scan QR code from terminal
3. App will load on your phone
4. Login and start registering farmers!

## ✅ You're Done!

- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Mobile App: Running on your phone via Expo Go