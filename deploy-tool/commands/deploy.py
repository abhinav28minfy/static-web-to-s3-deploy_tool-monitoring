"""Deploy command implementation."""

from datetime import datetime
from commands.base import BaseCommand
from utils.prerequisites import check_prerequisites_bool
from utils.build import build_project, create_health_check_endpoint
from utils.docker_utils import create_dockerfile_and_dockerignore


class DeployCommand(BaseCommand):
    def execute(self, args):
        """Deploy from GitHub."""
        print(f"Deploying from GitHub to {args.env}...")
        
        if not check_prerequisites_bool():
            return False
        
        github_url = args.github_url or self.config_manager.get('github_url')
        if not github_url:
            print("No GitHub URL found. Please run 'init' first or provide --github-url")
            return False
        
        if not self.aws_client.check_sso_login():
            return False
        
        # Handle flags
        if hasattr(args, 'no_docker') and args.no_docker:
            self.config_manager.set('create_dockerfile', False)
        if hasattr(args, 'no_health_check') and args.no_health_check:
            self.config_manager.set('create_health_check', False)
        
        # Handle env file
        env_file_path = args.env_file
        if not env_file_path and not self.config_manager.get('env_file_path'):
            response = input("Do you want to use a .env file? (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                env_file_path = input("Enter the full path to your .env file: ").strip()
                if env_file_path:
                    self.config_manager.set('env_file_path', env_file_path)
        elif not env_file_path:
            env_file_path = self.config_manager.get('env_file_path')
        
        env_config = self.config_manager.get(f'environments.{args.env}')
        if not env_config:
            print(f"Environment '{args.env}' not configured")
            return False
        
        bucket_name = env_config['bucket']
        branch = self.config_manager.get('github_branch', 'master')
        
        try:
            project_path, actual_commit = self.git_ops.clone_repository(github_url, branch)
            build_path = build_project(project_path, env_file_path, self.config_manager.config)
            
            # Create health check if enabled
            if self.config_manager.get('create_health_check', True):
                create_health_check_endpoint(build_path)
            
            # Create Docker files if enabled
            if self.config_manager.get('create_dockerfile', True):
                create_dockerfile_and_dockerignore(build_path, project_path, 
                                                 self.config_manager.get('project_type', 'react'))
            
            website_url = self.aws_client.create_s3_bucket(bucket_name)
            self.aws_client.upload_to_s3(build_path, bucket_name)
            
            # Upload Docker files if they exist
            self._upload_docker_files(build_path, project_path, bucket_name)
            
            # Save deployment record
            deployment = {
                'timestamp': datetime.now().isoformat(),
                'environment': args.env,
                'bucket': bucket_name,
                'url': website_url,
                'region': self.aws_client.aws_region,
                'profile': self.aws_client.aws_profile,
                'github_url': github_url,
                'github_branch': branch,
                'commit_hash': actual_commit,
                'commit_short': actual_commit[:8] if actual_commit else None,
                'env_file_used': env_file_path is not None,
                'docker_files_created': self.config_manager.get('create_dockerfile', True),
                'health_check_created': self.config_manager.get('create_health_check', True),
                'status': 'success'
            }
            
            deployments = self.config_manager.get('deployments', [])
            deployments.insert(0, deployment)
            self.config_manager.set('deployments', deployments[:10])
            
            print("Deployment successful!")
            print("=" * 50)
            print(f"Website URL: {website_url}")
            print(f"Health Check: {website_url}/health")
            print(f"Repository: {github_url}")
            print(f"Branch: {branch}")
            print(f"Commit: {actual_commit[:8] if actual_commit else 'N/A'}")
            print(f"Region: {self.aws_client.aws_region}")
            print(f"Profile: {self.aws_client.aws_profile}")
            
            if env_file_path:
                print(f"Environment file: {env_file_path}")
            if self.config_manager.get('create_dockerfile', True):
                print("Docker files created and uploaded")
            if self.config_manager.get('create_health_check', True):
                print("Health check endpoint created")
            
            # Check monitoring status
            monitoring_config = self.config_manager.get('monitoring', {})
            if monitoring_config.get('enabled'):
                print("=" * 50)
                print("GZIP MONITORING IS ACTIVE!")
                if monitoring_config.get('grafana_url'):
                    print(f"Grafana Dashboard: {monitoring_config['grafana_url']}")
            else:
                print("=" * 50)
                print("SET UP GZIP MONITORING:")
                print("   python deploy_tool.py monitoring init")
                print("   Get dashboard + email alerts with compression")
                print("   GZIP bypasses AWS 16KB limit!")
            
            return True
            
        except Exception as e:
            print(f"Deployment failed: {e}")
            return False
        finally:
            self.cleanup()
    
    def _upload_docker_files(self, build_path, project_path, bucket_name):
        """Upload Docker files to S3."""
        import os
        
        s3 = self.aws_client.get_s3_client()
        
        dockerfile_path = os.path.join(project_path, 'Dockerfile')
        dockerignore_path = os.path.join(project_path, '.dockerignore')
        
        if os.path.exists(dockerfile_path):
            try:
                s3.upload_file(
                    dockerfile_path,
                    bucket_name,
                    'Dockerfile',
                    ExtraArgs={'ContentType': 'text/plain'}
                )
                print("  Uploaded: Dockerfile")
            except Exception as e:
                print(f"Warning: Could not upload Dockerfile: {e}")
        
        if os.path.exists(dockerignore_path):
            try:
                s3.upload_file(
                    dockerignore_path,
                    bucket_name,
                    '.dockerignore',
                    ExtraArgs={'ContentType': 'text/plain'}
                )
                print("  Uploaded: .dockerignore")
            except Exception as e:
                print(f"Warning: Could not upload .dockerignore: {e}")
 
