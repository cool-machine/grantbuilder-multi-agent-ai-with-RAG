#!/bin/bash
set -e

echo "🚀 Starting Ollama Test Container..."

# Start Ollama in background
ollama serve &
OLLAMA_PID=$!

echo "⏳ Waiting for Ollama to start..."
sleep 10

# Pull a small, fast model for testing (tinyllama is ~0.6GB, very fast)
echo "📥 Pulling tinyllama model for testing..."
ollama pull tinyllama

echo "✅ Ollama Test Container ready!"
echo "📊 Available models:"
ollama list

echo "🔍 Testing model..."
echo '{"model": "tinyllama", "prompt": "Test prompt", "stream": false}' | \
    curl -s -X POST http://localhost:11434/api/generate \
    -H "Content-Type: application/json" \
    -d @- | head -c 200

echo ""
echo "🎉 Ollama Test Container is working!"

# Keep Ollama running
wait $OLLAMA_PID