#!/usr/bin/env python3
"""
Check Azure ML Compute Instance Environment
"""

import subprocess
import sys
import importlib.util

def check_package(package_name):
    """Check if package is installed and get version"""
    try:
        spec = importlib.util.find_spec(package_name)
        if spec is not None:
            module = importlib.import_module(package_name)
            version = getattr(module, '__version__', 'unknown')
            return f"✅ {package_name}: {version}"
        else:
            return f"❌ {package_name}: Not installed"
    except Exception as e:
        return f"⚠️  {package_name}: Error - {str(e)}"

def main():
    """Check environment status"""
    
    print("🔍 Checking Azure ML Environment...")
    print("=" * 50)
    
    # Check Python version
    print(f"🐍 Python: {sys.version}")
    print()
    
    # Check essential packages
    packages = [
        "torch",
        "transformers", 
        "accelerate",
        "flask",
        "requests",
        "psutil",
        "matplotlib",
        "pandas",
        "numpy"
    ]
    
    print("📦 Package Status:")
    for pkg in packages:
        print(check_package(pkg))
    
    print()
    
    # Check conda environments
    try:
        result = subprocess.run("conda env list", shell=True, capture_output=True, text=True)
        print("🌍 Available Conda Environments:")
        print(result.stdout)
    except:
        print("❌ Could not list conda environments")
    
    # Check system resources
    try:
        import psutil
        print(f"💾 RAM: {psutil.virtual_memory().total // (1024**3)} GB")
        print(f"💿 Storage: {psutil.disk_usage('.').free // (1024**3)} GB free")
    except:
        print("❌ Could not get system info")

if __name__ == "__main__":
    main()