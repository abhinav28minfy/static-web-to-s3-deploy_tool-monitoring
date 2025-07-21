"""Prerequisites checking utilities."""

import subprocess


def check_prerequisites():
    """Check and print prerequisites."""
    print("Checking prerequisites...")
    prerequisites = []
    
    try:
        result = subprocess.run(['node', '--version'], shell=True, capture_output=True, text=True)
        prerequisites.append(f"Node.js: {result.stdout.strip()}" if result.returncode == 0 else "Node.js: Not found")
    except:
        prerequisites.append("Node.js: Not found")
    
    try:
        result = subprocess.run(['npm', '--version'], shell=True, capture_output=True, text=True)
        prerequisites.append(f"npm: {result.stdout.strip()}" if result.returncode == 0 else "npm: Not found")
    except:
        prerequisites.append("npm: Not found")
    
    try:
        result = subprocess.run(['git', '--version'], shell=True, capture_output=True, text=True)
        prerequisites.append(f"Git: {result.stdout.strip()}" if result.returncode == 0 else "Git: Not found")
    except:
        prerequisites.append("Git: Not found")
    
    for prereq in prerequisites:
        print(f"  {prereq}")
    
    missing = [p for p in prerequisites if "Not found" in p]
    if missing:
        print("\nMissing prerequisites detected!")
        print("\nTo fix this:")
        if any("Node.js" in p for p in missing):
            print("  1. Install Node.js from https://nodejs.org/")
        if any("npm" in p for p in missing):
            print("  2. npm comes with Node.js installation")
        if any("Git" in p for p in missing):
            print("  3. Install Git from https://git-scm.com/")
        print("  4. Restart your terminal after installation")
        return False
    
    print("All prerequisites are installed!")
    return True


def check_prerequisites_bool():
    """Check prerequisites and return boolean."""
    return check_prerequisites()
 
