#!/bin/bash

API_URL="${1:-http://localhost:8000}"

echo "🧪 Testing API endpoints..."
echo "API URL: $API_URL"
echo ""

# Test health endpoint
echo "1. Testing health endpoint..."
response=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/health")
if [ "$response" == "200" ]; then
    echo "   ✅ Health check passed"
else
    echo "   ❌ Health check failed (HTTP $response)"
fi

# Test login
echo "2. Testing login..."
response=$(curl -s -X POST "$API_URL/api/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin@zambian-farmers.zm&password=admin123")

if echo "$response" | grep -q "access_token"; then
    echo "   ✅ Login successful"
    TOKEN=$(echo "$response" | grep -o '"access_token":"[^"]*' | sed 's/"access_token":"//')
else
    echo "   ❌ Login failed"
    TOKEN=""
fi

# Test authenticated endpoint
if [ -n "$TOKEN" ]; then
    echo "3. Testing authenticated endpoint..."
    response=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/api/auth/me" \
        -H "Authorization: Bearer $TOKEN")
    
    if [ "$response" == "200" ]; then
        echo "   ✅ Authentication working"
    else
        echo "   ❌ Authentication failed (HTTP $response)"
    fi
fi

# Test farmers endpoint
if [ -n "$TOKEN" ]; then
    echo "4. Testing farmers endpoint..."
    response=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/api/farmers/" \
        -H "Authorization: Bearer $TOKEN")
    
    if [ "$response" == "200" ]; then
        echo "   ✅ Farmers endpoint working"
    else
        echo "   ❌ Farmers endpoint failed (HTTP $response)"
    fi
fi

# Test chiefs endpoint
if [ -n "$TOKEN" ]; then
    echo "5. Testing chiefs endpoint..."
    response=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/api/chiefs/provinces" \
        -H "Authorization: Bearer $TOKEN")
    
    if [ "$response" == "200" ]; then
        echo "   ✅ Chiefs endpoint working"
    else
        echo "   ❌ Chiefs endpoint failed (HTTP $response)"
    fi
fi

echo ""
echo "Test complete!"