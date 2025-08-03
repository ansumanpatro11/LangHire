#!/usr/bin/env python3
"""
Setup script for LangHire - JD-Aware Resume Analyzer
Run with: python setup.py
"""
import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a shell command with error handling."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_requirements():
    """Check if required tools are installed."""
    print("🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Check for conda
    try:
        subprocess.run(["conda", "--version"], check=True, capture_output=True)
        print("✅ Conda detected")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ Conda not found, will use pip instead")
        return True

def setup_environment():
    """Setup the conda environment or pip install."""
    print("\n🏗️ Setting up environment...")
    
    # Try conda first
    try:
        if Path("environment.yml").exists():
            print("📦 Creating conda environment from environment.yml...")
            if run_command("conda env create -f environment.yml", "Conda environment creation"):
                print("✅ Conda environment 'langhire' created successfully")
                print("🔄 To activate: conda activate langhire")
                return True
    except Exception:
        pass
    
    # Fallback to pip
    print("📦 Installing dependencies with pip...")
    return run_command("pip install -r requirements.txt", "Pip installation")

def setup_env_file():
    """Setup environment variables file."""
    print("\n🔧 Setting up environment configuration...")
    
    env_file = Path(".env")
    env_template = Path(".env.template")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if env_template.exists():
        # Copy template to .env
        with open(env_template, 'r') as template:
            content = template.read()
        
        with open(env_file, 'w') as env:
            env.write(content)
        
        print("✅ .env file created from template")
        print("⚠️ Please edit .env file and add your Google API key")
        return True
    else:
        # Create basic .env file
        with open(env_file, 'w') as env:
            env.write("# LangHire Environment Configuration\n")
            env.write("# Get your API key from: https://makersuite.google.com/app/apikey\n")
            env.write("GOOGLE_API_KEY=your_gemini_api_key_here\n")
        
        print("✅ Basic .env file created")
        print("⚠️ Please edit .env file and add your Google API key")
        return True

def create_directories():
    """Create necessary directories."""
    print("\n📁 Creating project directories...")
    
    directories = [
        "tests",
        "logs",
        "data/samples",
        "docs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True

def run_tests():
    """Run basic tests to verify installation."""
    print("\n🧪 Running basic tests...")
    
    if not Path("tests").exists():
        print("⚠️ Tests directory not found, skipping tests")
        return True
    
    try:
        # Try to import main modules
        sys.path.insert(0, str(Path("src").absolute()))
        
        from parsers.resume_parser import ResumeParser
        from parsers.jd_parser import JobDescriptionParser
        from analyzer.skill_matcher import SkillMatcher
        from analyzer.scoring_engine import ScoringEngine
        
        print("✅ All modules imported successfully")
        
        # Run a basic functionality test
        parser = ResumeParser()
        test_text = "Test resume with Python skills"
        result = parser.clean_text(test_text)
        
        if result:
            print("✅ Basic functionality test passed")
            return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "="*60)
    print("🎉 LangHire setup completed successfully!")
    print("="*60)
    print("\n📋 Next Steps:")
    print("1. Activate your environment:")
    print("   conda activate langhire")
    print("\n2. Configure your API key:")
    print("   Edit .env file and add your Google Gemini API key")
    print("   Get key from: https://makersuite.google.com/app/apikey")
    print("\n3. Run the application:")
    print("   streamlit run app.py")
    print("\n4. Open in browser:")
    print("   http://localhost:8501")
    print("\n🔗 Useful commands:")
    print("   • Run tests: pytest tests/")
    print("   • Format code: black src/")
    print("   • Check types: mypy src/")
    print("\n📚 Documentation:")
    print("   • README.md - Complete project documentation")
    print("   • config.py - Configuration options")
    print("   • src/ - Source code with detailed comments")
    print("\n💡 Need help? Check the README.md file!")

def main():
    """Main setup function."""
    print("🎯 LangHire - JD-Aware Resume Analyzer Setup")
    print("=" * 50)
    
    success_steps = []
    
    # Check requirements
    if check_requirements():
        success_steps.append("Requirements check")
    
    # Setup environment
    if setup_environment():
        success_steps.append("Environment setup")
    
    # Setup env file
    if setup_env_file():
        success_steps.append("Environment configuration")
    
    # Create directories
    if create_directories():
        success_steps.append("Directory creation")
    
    # Run tests
    if run_tests():
        success_steps.append("Basic tests")
    
    # Summary
    print(f"\n📊 Setup Summary: {len(success_steps)}/5 steps completed")
    
    if len(success_steps) >= 4:
        print_next_steps()
        return 0
    else:
        print("\n❌ Setup encountered issues. Please check the errors above.")
        print("💡 Try running individual steps manually or check the README.md")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)