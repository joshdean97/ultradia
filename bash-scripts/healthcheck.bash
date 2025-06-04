#!/bin/bash

# Send health check request
response=$(curl -s -w "%{http_code}" -o /dev/null http://localhost:5000/api/health)
http_code="${response: -3}"
# Handle response
if [ "$http_code" -eq 200 ]; then
  echo "✅ Health check successful."
else
  echo "❌ Health check failed (HTTP $http_code)."
fi
