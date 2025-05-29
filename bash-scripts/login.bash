#!/bin/bash
echo "Logging in..."
response=$(curl -s -c cookies.txt -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "josh@test.com", "password": "password"}')

if echo "$response" | grep -q "access denied\|unauthorized"; then
  echo "❌ Login failed."
else
  echo "✅ Login successful."
fi
