"""Git and GitHub operations."""

import os
import subprocess
import tempfile
import shutil
from urllib.parse import urlparse
from typing import Tuple, Optional


class GitOperations:
    def __init__(self):
        self.temp_dir = None
    
    def parse_github_url(self, github_url: str) -> Tuple[str, str, str]:
        """Parse GitHub URL to extract owner, repo, and branch."""
        if github_url.endswith('.git'):
            github_url = github_url[:-4]
        
        parsed = urlparse(github_url)
        
        if parsed.netloc != 'github.com':
            raise ValueError("Only GitHub repositories are supported")
        
        path_parts = parsed.path.strip('/').split('/')
        if len(path_parts) < 2:
            raise ValueError("Invalid GitHub URL format")
        
        owner = path_parts[0]
        repo = path_parts[1]
        
        return owner, repo, 'master'
    
    def clone_repository(self, github_url: str, branch: str = 'master', commit_hash: Optional[str] = None) -> Tuple[str, str]:
        """Clone repository and return path and commit hash."""
        if commit_hash:
            print(f"Cloning repository from {github_url} at commit {commit_hash[:8]}...")
        else:
            print(f"Cloning repository from {github_url}...")
        
        self.temp_dir = tempfile.mkdtemp(prefix='deploy_')
        
        try:
            result = subprocess.run([
                'git', 'clone', 
                github_url, 
                self.temp_dir
            ], shell=True, check=True, capture_output=True, text=True)
            
            original_cwd = os.getcwd()
            os.chdir(self.temp_dir)
            
            try:
                if commit_hash:
                    result = subprocess.run([
                        'git', 'checkout', commit_hash
                    ], shell=True, check=True, capture_output=True, text=True)
                    print(f"Checked out commit {commit_hash[:8]}")
                else:
                    result = subprocess.run([
                        'git', 'checkout', branch
                    ], shell=True, check=True, capture_output=True, text=True)
                    print(f"Checked out branch {branch}")
                
                result = subprocess.run([
                    'git', 'rev-parse', 'HEAD'
                ], shell=True, check=True, capture_output=True, text=True)
                current_commit = result.stdout.strip()
                
                git_dir = os.path.join(self.temp_dir, '.git')
                if os.path.exists(git_dir):
                    try:
                        def handle_remove_readonly(func, path, exc):
                            os.chmod(path, 0o777)
                            func(path)
                        
                        shutil.rmtree(git_dir, onerror=handle_remove_readonly)
                    except Exception as e:
                        print(f"Warning: Could not remove .git directory: {e}")
                
                print(f"Repository cloned to {self.temp_dir}")
                return self.temp_dir, current_commit
                
            finally:
                os.chdir(original_cwd)
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            print(f"Failed to clone repository: {error_msg}")
            self.cleanup_temp_dir()
            raise Exception(f"Git clone failed: {error_msg}")
        except FileNotFoundError:
            print("Git command not found!")
            print("Please install Git from https://git-scm.com/")
            self.cleanup_temp_dir()
            raise Exception("Git is not installed or not in PATH")
    
    def cleanup_temp_dir(self):
        """Clean up temporary directory."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                def handle_remove_readonly(func, path, exc):
                    os.chmod(path, 0o777)
                    func(path)
                
                shutil.rmtree(self.temp_dir, onerror=handle_remove_readonly)
                print("Cleaned up temporary directory")
            except Exception as e:
                print(f"Warning: Could not clean up temporary directory: {e}")
                print(f"You may need to manually delete: {self.temp_dir}")
 
