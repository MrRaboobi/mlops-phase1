#!/bin/sh
echo "Running canary acceptance tests..."
sleep 3
curl -f http://localhost:8000/health && echo "Healthcheck passed!" || exit 1
