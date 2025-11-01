#!/bin/bash
# Script to kill all processes on backend ports

PORTS=(8001 8002 8003 8004 8005 8006 8007 8008 8080)

echo "🔍 Checking for processes on backend ports..."
for port in "${PORTS[@]}"; do
    PID=$(lsof -ti :$port 2>/dev/null)
    if [ -n "$PID" ]; then
        echo "🛑 Killing process on port $port (PID: $PID)"
        kill -9 $PID 2>/dev/null
        sleep 0.5
    else
        echo "✅ Port $port is free"
    fi
done

echo "✨ Port cleanup complete!"
sleep 1

# Verify all ports are free
echo ""
echo "🔍 Verifying all ports are free..."
for port in "${PORTS[@]}"; do
    PID=$(lsof -ti :$port 2>/dev/null)
    if [ -n "$PID" ]; then
        echo "⚠️  Port $port still has process $PID"
    else
        echo "✅ Port $port is free"
    fi
done

