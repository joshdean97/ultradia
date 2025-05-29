#!/bin/bash

# Send logout request with saved session cookie
response=$(curl -s -w "%{http_code}" -b cookies.txt -X POST http://localhost:5000/api/auth/logout)
http_code="${response: -3}"

# Handle response
if [ "$http_code" -eq 200 ]; then
  echo "✅ Logout successful."
else
  echo "❌ Logout failed (HTTP $http_code)."
fi

# Clean up cookies
rm -f cookies.txt
