"""Init command implementation."""

import sys
from commands.base import BaseCommand
from utils.prerequisites import check_prerequisites_bool
from utils.build import detect_project_type, get_build_command


class InitCommand(BaseCommand):
    def execute(self, args):
        """Initialize project from GitHub."""
        if not args.github_url:
            print("GitHub URL required")
            print("Usage: python deploy_tool.py init --github-url https://github.com/user/repo")
            sys.exit(1)
        
        print("Initializing project from GitHub...")
        
        if not check_prerequisites_bool():
            return False
        
        try:
            owner, repo, branch = self.git_ops.parse_github_url(args.github_url)
            
            project_name = args.name or repo
            
            temp_path, _ = self.git_ops.clone_repository(args.github_url, branch)
            project_type = detect_project_type(temp_path)
            
            config_updates = {
                'project_name': project_name,
                'project_type': project_type,
                'github_url': args.github_url,
                'github_owner': owner,
                'github_repo': repo,
                'github_branch': branch,
                'aws_region': self.aws_client.aws_region,
                'aws_profile': self.aws_client.aws_profile,
                'environments': {
                    'dev': {'bucket': f'{project_name}-dev'},
                    'staging': {'bucket': f'{project_name}-staging'}, 
                    'prod': {'bucket': f'{project_name}-prod'}
                },
                'build_command': get_build_command(project_type),
                'build_dir': 'build' if project_type == 'react' else 'dist',
                'create_dockerfile': True,
                'create_health_check': True,
                'env_file_path': None,
                'monitoring': {
                    'enabled': False,
                    'instance_id': None,
                    'grafana_url': None,
                    'prometheus_url': None,
                    'alerting': {
                        'enabled': False,
                        'email': None,
                        'gmail_app_password': None
                    }
                }
            }
            
            self.config_manager.update(config_updates)
            
            print(f"Project '{project_name}' initialized successfully")
            print(f"Repository: {owner}/{repo}")
            print(f"Branch: {branch}")
            print(f"Project type: {project_type}")
            print(f"Build directory: {config_updates['build_dir']}")
            print(f"Build command: {config_updates['build_command']}")
            print(f"AWS Region: {self.aws_client.aws_region}")
            print(f"AWS Profile: {self.aws_client.aws_profile}")
            
        except Exception as e:
            print(f"Failed to initialize project: {e}")
            return False
        finally:
            self.cleanup()
