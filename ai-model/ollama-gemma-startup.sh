#!/bin/bash
set -e

echo "🚀 Starting Ollama Gemma 3 270M Container..."

# Start Ollama in background
ollama serve &
OLLAMA_PID=$!

echo "⏳ Waiting for Ollama to start..."
sleep 15

# Pull Gemma 3 270M model
echo "📥 Pulling Gemma 3 270M-IT model (this may take 5-10 minutes)..."
echo "📊 Model size: ~270MB download, ~550MB loaded"
ollama pull gemma3:270m

echo "✅ Gemma 3 270M loaded successfully!"
echo "📊 Available models:"
ollama list

echo "🔍 Testing Gemma 3 270M generation..."
RESPONSE=$(echo '{"model": "gemma3:270m", "prompt": "Write a brief grant proposal for environmental research:", "stream": false}' | \
    curl -s -X POST http://localhost:11434/api/generate \
    -H "Content-Type: application/json" \
    -d @-)

echo "🎯 Test response:"
echo "$RESPONSE" | head -c 300
echo ""

echo "🎉 Ollama Gemma 3 270M Container is ready for production!"
echo "🔗 API Endpoint: http://localhost:11434/api/generate"
echo "📋 Usage: POST JSON with 'model' and 'prompt' fields"

# Keep Ollama running
wait $OLLAMA_PID