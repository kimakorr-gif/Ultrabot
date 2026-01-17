#!/usr/bin/env python3
"""Environment checker for Ultrabot setup verification."""

import sys
import os
from pathlib import Path

def check_python_version():
    """Check Python version."""
    print("🐍 Python Version Check")
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major >= 3 and version.minor >= 11:
        print(f"  ✅ Python {version_str} (required: 3.11+)")
        return True
    else:
        print(f"  ❌ Python {version_str} (required: 3.11+)")
        return False

def check_dependencies():
    """Check if required packages are installed."""
    print("\n📦 Dependencies Check")
    
    required = [
        'fastapi',
        'sqlalchemy',
        'aiogram',
        'aiohttp',
        'redis',
        'pydantic',
        'prometheus_client',
        'dishka',
        'alembic',
    ]
    
    all_ok = True
    for pkg in required:
        try:
            __import__(pkg)
            print(f"  ✅ {pkg}")
        except ImportError:
            print(f"  ❌ {pkg} (not installed)")
            all_ok = False
    
    return all_ok

def check_env_file():
    """Check if .env file exists and has required variables."""
    print("\n⚙️  Configuration Check")
    
    if not Path(".env").exists():
        print("  ❌ .env file not found")
        print("     Run: cp .env.example .env")
        return False
    
    print("  ✅ .env file found")
    
    required_vars = [
        'TELEGRAM_TOKEN',
        'TELEGRAM_CHANNEL_ID',
        'YANDEX_API_KEY',
    ]
    
    with open(".env") as f:
        content = f.read()
    
    missing = []
    for var in required_vars:
        if f"{var}=" in content:
            # Check if it has a value (not just =)
            for line in content.split('\n'):
                if line.startswith(var + '='):
                    value = line.split('=', 1)[1].strip()
                    if value and not value.startswith('your_'):
                        print(f"  ✅ {var} configured")
                    else:
                        missing.append(var)
                    break
        else:
            missing.append(var)
    
    if missing:
        print(f"  ⚠️  Missing values for: {', '.join(missing)}")
        print("     Edit .env and set your credentials")
    
    return len(missing) == 0

def check_docker():
    """Check if Docker is installed and running."""
    print("\n🐳 Docker Check")
    
    import subprocess
    
    try:
        subprocess.run(['docker', '--version'], capture_output=True, check=True)
        print("  ✅ Docker installed")
        
        # Check if running
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✅ Docker daemon running")
            
            # Check services
            if 'postgres' in result.stdout:
                print("  ✅ PostgreSQL running")
            else:
                print("  ⚠️  PostgreSQL not running (start with: docker-compose up -d)")
            
            return True
        else:
            print("  ⚠️  Docker daemon not running")
            return False
    except FileNotFoundError:
        print("  ⚠️  Docker not installed (optional, but recommended)")
        return False

def check_files():
    """Check if required files exist."""
    print("\n📁 Project Files Check")
    
    required_files = [
        'requirements.txt',
        'setup.py',
        'pyproject.toml',
        'Makefile',
        '.env.example',
        'docker-compose.yml',
    ]
    
    required_dirs = [
        'src',
        'tests',
        'docs',
        'kubernetes',
    ]
    
    all_ok = True
    
    for file in required_files:
        if Path(file).exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file}")
            all_ok = False
    
    for dir in required_dirs:
        if Path(dir).exists():
            print(f"  ✅ {dir}/")
        else:
            print(f"  ❌ {dir}/")
            all_ok = False
    
    return all_ok

def main():
    """Run all checks."""
    print("🔍 Ultrabot Environment Verification\n")
    print("=" * 50)
    
    results = {
        "Python Version": check_python_version(),
        "Dependencies": check_dependencies(),
        "Configuration (.env)": check_env_file(),
        "Docker": check_docker(),
        "Project Files": check_files(),
    }
    
    print("\n" + "=" * 50)
    print("\n📊 Summary\n")
    
    critical_ok = results["Python Version"] and results["Dependencies"] and results["Project Files"]
    config_ok = results["Configuration (.env)"]
    docker_ok = results["Docker"]
    
    if critical_ok:
        print("✅ Critical checks PASSED")
    else:
        print("❌ Critical checks FAILED")
        print("\nYou need to:")
        if not results["Python Version"]:
            print("  - Install Python 3.11+")
        if not results["Dependencies"]:
            print("  - Run: pip install -r requirements.txt")
        if not results["Project Files"]:
            print("  - Clone the repository again")
        return 1
    
    if config_ok:
        print("✅ Configuration COMPLETE")
    else:
        print("⚠️  Configuration INCOMPLETE")
        print("   Run: cp .env.example .env")
        print("   Then edit .env with your credentials")
    
    if docker_ok:
        print("✅ Docker is READY")
    else:
        print("⚠️  Docker not available")
        print("   (optional - you can run without it)")
    
    print("\n📝 Next Steps:\n")
    
    if not config_ok:
        print("1. Configure .env file:")
        print("   cp .env.example .env")
        print("   nano .env")
        print("")
    
    print("2. Start services (if Docker available):")
    print("   docker-compose up -d")
    print("")
    
    print("3. Run the application:")
    print("   make run              (production)")
    print("   make run-dev          (development with auto-reload)")
    print("   ./run.sh              (quick start script)")
    print("")
    
    print("4. Run tests:")
    print("   make test             (all tests)")
    print("   make test-coverage    (with coverage report)")
    print("")
    
    print("📖 Documentation:")
    print("   - GETTING_STARTED.md  (5-minute quick start)")
    print("   - INSTALL.md          (detailed setup guide)")
    print("   - ARCHITECTURE.md     (system design)")
    print("   - docs/               (API, deployment, monitoring)")
    
    return 0 if critical_ok else 1

if __name__ == "__main__":
    sys.exit(main())
