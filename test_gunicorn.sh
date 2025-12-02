#!/bin/bash
# Test script to verify gunicorn can start the app

echo "Testing gunicorn startup..."
echo ""

# Check if gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    echo "ERROR: gunicorn not found. Install with: pip install gunicorn"
    exit 1
fi

echo "✓ Gunicorn is installed"
echo ""

# Test app import
echo "Testing app import..."
python -c "from backend_rag_api import app; print('✓ App imports successfully')" || {
    echo "ERROR: App import failed"
    exit 1
}

echo ""
echo "Starting gunicorn on port 5000..."
echo "Press Ctrl+C to stop"
echo ""

# Start gunicorn
gunicorn backend_rag_api:app --bind 0.0.0.0:5000 --timeout 120 --log-level debug

