#!/bin/bash
# Install only missing packages on Azure ML compute instance

echo "🔍 Checking for missing packages..."

# Only install if not already available
python3 -c "import accelerate" 2>/dev/null || pip install accelerate
python3 -c "import flask" 2>/dev/null || pip install flask  
python3 -c "import psutil" 2>/dev/null || pip install psutil

echo "✅ Package check complete!"

# Make sure we have write permissions for results
mkdir -p results logs benchmarks

echo "📁 Ready for model testing!"
echo "💾 Available RAM: $(free -h | awk '/^Mem:/ {print $7}')"
echo "💿 Available Storage: $(df -h . | awk 'NR==2 {print $4}')"