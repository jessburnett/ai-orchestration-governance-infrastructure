#!/bin/bash

# Start the Governance Hub in the background
echo "🚀 Starting Governance Hub..."
uvicorn ecosystem_hub:app --host 0.0.0.0 --port 8000 &

# Wait for the Hub using a more universal check
echo "⏳ Waiting for Hub to start on port 8000..."
MAX_RETRIES=30
COUNT=0
while ! python3 -c "import socket; s = socket.socket(); s.connect(('127.0.0.1', 8000))" >/dev/null 2>&1; do
    if [ $COUNT -ge $MAX_RETRIES ]; then
        echo "❌ Hub failed to start. Check terminal output above."
        exit 1
    fi
    sleep 1
    COUNT=$((COUNT+1))
done

echo "✅ Hub is READY!"

# Start the Dashboard
echo "📊 Starting Dashboard..."
streamlit run dashboard.py --server.address 0.0.0.0 --server.enableCORS=false --server.enableXsrfProtection=false
