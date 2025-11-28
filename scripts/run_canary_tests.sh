#!/bin/sh
echo "Running canary acceptance tests (5+ golden queries)..."

# Wait for service to be ready
sleep 5

# Test 1: Health check
echo "Test 1: Health check"
curl -f http://localhost:8000/health || exit 1
echo " ✓ Health check passed"

# Test 2: Root endpoint
echo "Test 2: Root endpoint"
curl -f http://localhost:8000/ || exit 1
echo " ✓ Root endpoint passed"

# Test 3: Simple prediction endpoint (backward compatibility)
echo "Test 3: Simple prediction endpoint"
curl -f -X POST http://localhost:8000/predict/simple \
  -H "Content-Type: application/json" \
  -d '{"signal_value": 0.3}' || exit 1
echo " ✓ Simple prediction passed"

# Test 4: Full prediction endpoint with sample ECG signal
echo "Test 4: Full prediction endpoint"
SAMPLE_SIGNAL='{"signal": [[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2],[0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3]], "ecg_id": 123}'
curl -f -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d "$SAMPLE_SIGNAL" || exit 1
echo " ✓ Full prediction passed"

# Test 5: API documentation endpoint
echo "Test 5: API documentation endpoint"
curl -f http://localhost:8000/docs || exit 1
echo " ✓ API docs accessible"

# Test 6: Storage endpoint (if available)
echo "Test 6: Storage endpoint"
curl -f http://localhost:8000/storage/ping || echo " ⚠ Storage endpoint not available (optional)"

echo ""
echo "✅ All acceptance tests passed!"
