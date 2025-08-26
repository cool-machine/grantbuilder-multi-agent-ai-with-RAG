"""
Setup script for DeepSeek R1 Multi-Agent Grant Writing System
Automated installation and configuration
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run shell command with error handling"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return None

def check_prerequisites():
    """Check system prerequisites"""
    print("🔍 Checking prerequisites...")
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ required")
        return False
    print("✅ Python version OK")
    
    # Check Azure CLI
    azure_cli = shutil.which("az")
    if not azure_cli:
        print("❌ Azure CLI not found. Install from https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
        return False
    print("✅ Azure CLI found")
    
    return True

def setup_environment():
    """Set up Python environment"""
    print("📦 Setting up Python environment...")
    
    # Install requirements
    if os.path.exists("system_requirements.txt"):
        run_command("pip install -r system_requirements.txt", "Installing Python dependencies")
    else:
        print("⚠️ system_requirements.txt not found")

def configure_azure_services():
    """Configure Azure services"""
    print("☁️ Configuring Azure services...")
    
    if os.path.exists("deploy_azure_services.sh"):
        # Make script executable
        run_command("chmod +x deploy_azure_services.sh", "Making deployment script executable")
        
        print("🚀 Ready to deploy Azure services!")
        print("   Run: ./deploy_azure_services.sh")
    else:
        print("⚠️ deploy_azure_services.sh not found")

def setup_configuration():
    """Set up configuration files"""
    print("⚙️ Setting up configuration...")
    
    # Check if config template exists
    if os.path.exists("config.template.env"):
        if not os.path.exists("azure_services_config.env"):
            print("📋 Configuration template available at config.template.env")
            print("   Copy to azure_services_config.env and fill in your values after Azure deployment")
        else:
            print("✅ Configuration file already exists")
    
def verify_installation():
    """Verify installation"""
    print("🧪 Verifying installation...")
    
    try:
        # Test imports
        import langgraph
        import azure.storage.blob
        import azure.cosmos
        print("✅ Core dependencies imported successfully")
        
        # Test system files
        required_files = [
            "integrated_deepseek_mcp_system.py",
            "deepseek_r1_config.py", 
            "deepseek_r1_agent_prompts.py",
            "azure_mcp_research_tools.py",
            "azure_mcp_collaboration_tools.py",
            "azure_mcp_validation_tools.py"
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        if missing_files:
            print(f"❌ Missing files: {', '.join(missing_files)}")
            return False
        else:
            print("✅ All required files present")
            
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 DeepSeek R1 Multi-Agent System Setup")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        print("❌ Prerequisites check failed. Please install missing requirements.")
        return False
    
    # Setup environment
    setup_environment()
    
    # Configure Azure services
    configure_azure_services()
    
    # Setup configuration
    setup_configuration()
    
    # Verify installation
    if verify_installation():
        print("\n🎉 SETUP COMPLETE!")
        print("=" * 50)
        print("Next steps:")
        print("1. Run: ./deploy_azure_services.sh")
        print("2. Copy config.template.env to azure_services_config.env and fill in values")  
        print("3. Run: python test_system.py")
        print("4. Run: python integrated_deepseek_mcp_system.py")
        print("\n💰 Expected cost: $0.25-0.70 per grant application")
        return True
    else:
        print("❌ Setup verification failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)