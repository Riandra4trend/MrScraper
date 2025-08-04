import os
import sys
import subprocess
import platform
from pathlib import Path

def install_requirements():
    """Install Python requirements"""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        print("📝 Creating .env configuration file...")
        env_content = """# Google AI API Key for natural language processing
# Get your key from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your_google_ai_api_key_here

# Optional: Set log level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO
"""
        env_file.write_text(env_content)
        print("✅ .env file created. Please edit it with your Google AI API key.")
        return True
    else:
        print("ℹ️  .env file already exists")
        return True

def check_system_requirements():
    """Check system requirements"""
    print("🔍 Checking system requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Check internet connection by attempting to reach a test URL
    try:
        import requests
        response = requests.get("https://httpbin.org/status/200", timeout=5)
        if response.status_code == 200:
            print("✅ Internet connection verified")
        else:
            print("⚠️  Internet connection may be unstable")
    except Exception:
        print("⚠️  Could not verify internet connection (required for API calls)")
    
    return True

def run_test_installation():
    """Run a quick test to verify installation"""
    print("🧪 Running installation test...")
    try:
        # Test core imports
        import requests
        import pandas as pd
        from io import StringIO
        
        print("✅ Core modules (requests, pandas) import successfully")
        
        # Test optional AI import
        try:
            import google.generativeai as genai
            print("✅ Google AI module available")
        except ImportError:
            print("⚠️  Google AI module not available (install with: pip install google-generativeai)")
        
        # Test HTML parsing dependencies
        try:
            import html5lib
            print("✅ html5lib parser available")
        except ImportError:
            print("⚠️  html5lib not available (some HTML parsing may fail)")
        
        try:
            import bs4
            print("✅ BeautifulSoup4 parser available")
        except ImportError:
            print("⚠️  BeautifulSoup4 not available (fallback parser missing)")
        
        # Test basic pandas HTML parsing
        test_html = "<table><tr><th>Test</th></tr><tr><td>Data</td></tr></table>"
        df_list = pd.read_html(StringIO(test_html))
        if len(df_list) > 0:
            print("✅ HTML table parsing functional")
        
        print("✅ Installation test completed successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def display_usage_examples():
    """Display usage examples"""
    print("\n🎯 USAGE EXAMPLES")
    print("="*50)
    print("1. Basic Location Search:")
    print("   python intelligent_scraper.py -c 'Find all ranches in Texas'")
    
    print("\n2. International Search:")
    print("   python intelligent_scraper.py -c 'Show me breeders from Alberta, Canada'")
    
    print("\n3. Name-Based Search:")
    print("   python intelligent_scraper.py -c \"Search for ranches named 'Creek' in Iowa\"")
    
    print("\n4. Informal Queries:")
    print("   python intelligent_scraper.py -c 'argentina any?'")
    
    print("\n5. Run Comprehensive Tests:")
    print("   python test_scraper_validation.py")
    
    print("\n6. Programmatic Usage:")
    print("   from intelligent_scraper import ShorthornApiScraper")
    print("   scraper = ShorthornApiScraper()")
    print("   result = scraper.search('Find ranches in California')")
    
    print("\n📚 For detailed documentation, see README.md")

def validate_environment():
    """Validate the setup environment"""
    print("🔧 Validating environment setup...")
    
    # Check if .env file has been configured
    env_file = Path(".env")
    if env_file.exists():
        env_content = env_file.read_text()
        if "your_google_ai_api_key_here" in env_content:
            print("⚠️  Please update .env file with your actual Google AI API key")
            print("   The scraper will work without it but with limited functionality")
        else:
            print("✅ .env file appears to be configured")
    
    # Check if project files exist
    required_files = [
        "intelligent_scraper.py",
        "test_scraper_validation.py",
        "requirements.txt"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All required project files present")
    
    return True

def main():
    """Main setup function"""
    print("🚀 Intelligent Cattle Ranch Scraper Setup")
    print("="*45)
    
    success = True
    
    # Check system requirements
    if not check_system_requirements():
        success = False
    
    # Validate environment
    if not validate_environment():
        success = False
    
    # Install requirements
    if not install_requirements():
        success = False
    
    # Create .env file
    if not create_env_file():
        success = False
    
    # Run test installation
    if not run_test_installation():
        success = False
    
    print("\n" + "="*50)
    if success:
        print("🎉 Setup completed successfully!")
        print("\n⚠️  NEXT STEPS:")
        print("1. Edit .env file with your Google AI API key for full functionality")
        print("2. The scraper works without API key using basic parsing")
        print("3. Run tests to verify everything works: python test_scraper_validation.py")
        display_usage_examples()
    else:
        print("❌ Setup completed with errors")
        print("Please resolve the issues above before using the scraper")
    
    print(f"\n📧 For support: Create an issue on the project repository")
    print("🌟 Star the project if you find it useful!")

if __name__ == "__main__":
    main()