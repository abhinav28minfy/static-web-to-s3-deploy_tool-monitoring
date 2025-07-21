"""Build utilities."""

import os
import json
import subprocess
import shutil
from datetime import datetime


def detect_project_type(project_path):
    """Detect project type from package.json."""
    package_json_path = os.path.join(project_path, 'package.json')
    
    if os.path.exists(package_json_path):
        try:
            with open(package_json_path, 'r') as f:
                pkg = json.load(f)
                if 'vite' in pkg.get('devDependencies', {}):
                    return 'vite'
                elif 'react-scripts' in pkg.get('dependencies', {}):
                    return 'react'
        except json.JSONDecodeError:
            print("Warning: Could not parse package.json")
    return 'react'


def get_build_command(project_type):
    """Get build command for project type."""
    commands = {
        'react': 'npm run build',
        'vite': 'npm run build'
    }
    return commands.get(project_type, 'npm run build')


def handle_env_file(project_path, env_file_path):
    """Handle environment file copying."""
    if not env_file_path:
        return
    
    if not os.path.exists(env_file_path):
        print(f"Warning: .env file not found at {env_file_path}")
        return
    
    try:
        dest_path = os.path.join(project_path, '.env')
        shutil.copy2(env_file_path, dest_path)
        print(f"Copied .env file from {env_file_path} to project directory")
    except Exception as e:
        print(f"Warning: Could not copy .env file: {e}")


def create_health_check_endpoint(build_dir):
    """Create health check endpoint."""
    health_check_content = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "service": "static-website",
        "checks": {
            "database": "not_applicable",
            "external_services": "not_applicable",
            "disk_space": "ok",
            "memory": "ok"
        }
    }
    
    health_check_path = os.path.join(build_dir, 'health')
    
    try:
        with open(health_check_path, 'w') as f:
            json.dump(health_check_content, f, indent=2)
        print(f"Created health check endpoint")
        return health_check_path
    except Exception as e:
        print(f"Warning: Could not create health check endpoint: {e}")
        return None


def build_project(project_path, env_file_path, config):
    """Build the project."""
    print("Building project...")
    
    original_cwd = os.getcwd()
    os.chdir(project_path)
    
    try:
        if not os.path.exists('package.json'):
            raise Exception("package.json not found. This doesn't appear to be a Node.js project.")
        
        if env_file_path:
            handle_env_file(project_path, env_file_path)
        
        print("Installing dependencies...")
        result = subprocess.run(['npm', 'install'], shell=True, check=True, capture_output=True, text=True)
        print("Dependencies installed successfully")
        
        print("Building...")
        build_command = config.get('build_command', 'npm run build')
        result = subprocess.run(build_command, shell=True, check=True, capture_output=True, text=True)
        print("Build completed successfully")
        
        build_dir = config.get('build_dir', 'build')
        build_path = os.path.join(project_path, build_dir)
        
        if not os.path.exists(build_path):
            raise Exception(f"Build directory {build_dir} not found after build")
        
        print(f"Build completed - {build_path}")
        return build_path
        
    except FileNotFoundError:
        raise Exception("npm command not found. Please install Node.js from https://nodejs.org/")
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e.stderr}")
        raise Exception("Build process failed")
    finally:
        os.chdir(original_cwd)
 
