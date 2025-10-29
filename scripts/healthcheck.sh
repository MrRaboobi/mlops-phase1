#!/bin/sh
# Simple health check script for Docker
curl -f http://localhost:8000/health || exit 1
