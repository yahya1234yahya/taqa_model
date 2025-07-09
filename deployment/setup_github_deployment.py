#!/usr/bin/env python3
"""
Setup script for DigitalOcean App Platform deployment
This script helps prepare your code for GitHub and App Platform deployment
"""

import os
import subprocess
import sys

def check_git_setup():
    """Check if git is initialized and configured"""
    print("🔍 Checking Git setup...")
    
    # Check if git is installed
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        print(f"✅ Git installed: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ Git is not installed. Please install Git first.")
        return False
    
    # Check if git repo is initialized
    if not os.path.exists('.git'):
        print("📦 Initializing Git repository...")
        subprocess.run(['git', 'init'])
        print("✅ Git repository initialized")
    else:
        print("✅ Git repository already exists")
    
    # Check git config
    try:
        name = subprocess.run(['git', 'config', 'user.name'], capture_output=True, text=True)
        email = subprocess.run(['git', 'config', 'user.email'], capture_output=True, text=True)
        
        if not name.stdout.strip():
            user_name = input("Enter your name for Git: ")
            subprocess.run(['git', 'config', 'user.name', user_name])
        else:
            print(f"✅ Git user: {name.stdout.strip()}")
            
        if not email.stdout.strip():
            user_email = input("Enter your email for Git: ")
            subprocess.run(['git', 'config', 'user.email', user_email])
        else:
            print(f"✅ Git email: {email.stdout.strip()}")
            
    except Exception as e:
        print(f"⚠️  Git config check failed: {e}")
    
    return True

def check_required_files():
    """Check if all required files exist for App Platform deployment"""
    print("\n🔍 Checking required files for App Platform...")
    
    required_files = [
        '.do/app.yaml',
        'runtime.txt', 
        'requirements_api.txt',
        'gunicorn_appplatform.conf.py',
        'wsgi.py',
        'api_server.py',
        'comprehensive_prediction_system.py'
    ]
    
    required_models = [
        'availability_model.pkl',
        'fiability_model.pkl', 
        'process_safety_model.pkl'
    ]
    
    required_data = [
        'equipment_simple.csv',
        'severe_words_simple.csv',
        'equipment_fiability_simple.csv',
        'severe_words_fiability_simple.csv',
        'equipment_process_safety_simple.csv',
        'severe_words_process_safety_simple.csv'
    ]
    
    all_files = required_files + required_models + required_data
    missing_files = []
    
    for file in all_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            if file.endswith('.pkl'):
                print(f"✅ {file} ({size/1024/1024:.1f}MB)")
            elif file.endswith('.csv'):
                print(f"✅ {file} ({size/1024:.0f}KB)")
            else:
                print(f"✅ {file}")
        else:
            missing_files.append(file)
            print(f"❌ Missing: {file}")
    
    if missing_files:
        print(f"\n⚠️  Missing {len(missing_files)} required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print(f"\n✅ All {len(all_files)} required files found!")
    return True

def check_file_sizes():
    """Check if files are within App Platform limits"""
    print("\n📏 Checking file sizes for App Platform limits...")
    
    large_files = []
    total_size = 0
    
    for root, dirs, files in os.walk('.'):
        # Skip .git directory
        if '.git' in dirs:
            dirs.remove('.git')
            
        for file in files:
            file_path = os.path.join(root, file)
            size = os.path.getsize(file_path)
            total_size += size
            
            # Check for files over 100MB (App Platform limit)
            if size > 100 * 1024 * 1024:
                large_files.append((file_path, size))
    
    if large_files:
        print("⚠️  Large files detected (over 100MB):")
        for file_path, size in large_files:
            print(f"   - {file_path}: {size/1024/1024:.1f}MB")
        print("   These may cause deployment issues on App Platform")
    else:
        print("✅ No files over 100MB limit")
    
    print(f"📊 Total repository size: {total_size/1024/1024:.1f}MB")
    
    return len(large_files) == 0

def setup_gitignore():
    """Create .gitignore file if it doesn't exist"""
    print("\n📝 Setting up .gitignore...")
    
    gitignore_content = """# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
api_env/
.venv
pip-log.txt
pip-delete-this-directory.txt

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Temporary files
*.tmp
*.temp
.cache/

# App Platform
.do/deploy.template.yaml
"""
    
    if not os.path.exists('.gitignore'):
        with open('.gitignore', 'w') as f:
            f.write(gitignore_content)
        print("✅ Created .gitignore file")
    else:
        print("✅ .gitignore already exists")

def commit_changes():
    """Add and commit all changes"""
    print("\n📦 Committing changes...")
    
    try:
        # Add all files
        subprocess.run(['git', 'add', '.'], check=True)
        
        # Check if there are changes to commit
        result = subprocess.run(['git', 'diff', '--cached', '--quiet'], capture_output=True)
        if result.returncode == 0:
            print("ℹ️  No changes to commit")
            return True
        
        # Commit changes
        commit_message = "Prepare for DigitalOcean App Platform deployment"
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        print("✅ Changes committed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git commit failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 DigitalOcean App Platform Deployment Setup")
    print("=" * 50)
    
    # Check current directory
    if not os.path.exists('api_server.py'):
        print("❌ Please run this script from your ML project directory")
        print("   (the directory containing api_server.py)")
        sys.exit(1)
    
    # Run all checks
    checks = [
        check_git_setup,
        check_required_files,
        check_file_sizes,
        setup_gitignore,
        commit_changes
    ]
    
    for check in checks:
        if not check():
            print(f"\n❌ Setup incomplete. Please fix the issues above.")
            sys.exit(1)
    
    print("\n🎉 Setup Complete!")
    print("=" * 50)
    print("✅ Your code is ready for DigitalOcean App Platform deployment!")
    print()
    print("📋 Next Steps:")
    print("1. Create a GitHub repository")
    print("2. Push your code: git remote add origin <your-repo-url>")
    print("3. git push -u origin main")
    print("4. Follow DIGITALOCEAN_APP_PLATFORM_GUIDE.md")
    print()
    print("🔗 Helpful Links:")
    print("   - GitHub: https://github.com/new")
    print("   - App Platform: https://cloud.digitalocean.com/apps")
    print("   - Guide: ./DIGITALOCEAN_APP_PLATFORM_GUIDE.md")

if __name__ == "__main__":
    main() 