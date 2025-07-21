"""Rollback command implementation."""

from datetime import datetime
from commands.base import BaseCommand
from utils.build import build_project, create_health_check_endpoint
from utils.docker_utils import create_dockerfile_and_dockerignore


class RollbackCommand(BaseCommand):
    def execute(self, args):
        """Rollback deployment."""
        print(f"Rolling back {args.env} environment...")
        
        if not self.aws_client.check_sso_login():
            return False
        
        deployments = self.config_manager.get('deployments', [])
        env_deployments = [d for d in deployments if d['environment'] == args.env and d['status'] == 'success']
        
        if len(env_deployments) < 2:
            print(f"No previous {args.env} deployment to rollback to")
            return False
        
        deployment_index = args.deployment
        if deployment_index is None:
            print(f"\nAvailable deployments for {args.env}:")
            for i, deployment in enumerate(env_deployments[1:], 1):
                print(f"  {i}. {deployment['timestamp'][:19]} - Commit: {deployment.get('commit_short', 'N/A')}")
            
            try:
                choice = input(f"\nSelect deployment to rollback to (1-{len(env_deployments)-1}): ").strip()
                deployment_index = int(choice)
                if deployment_index < 1 or deployment_index >= len(env_deployments):
                    print("Invalid selection")
                    return False
            except ValueError:
                print("Invalid input")
                return False
        
        target_deployment = env_deployments[deployment_index]
        current_deployment = env_deployments[0]
        
        print(f"\nRollback Plan:")
        print(f"  Current:  {current_deployment['timestamp'][:19]} - {current_deployment.get('commit_short', 'N/A')}")
        print(f"  Target:   {target_deployment['timestamp'][:19]} - {target_deployment.get('commit_short', 'N/A')}")
        
        confirm = input("\nProceed with rollback? (yes/no): ").lower().strip()
        if confirm != 'yes':
            print("Rollback cancelled")
            return False
        
        try:
            github_url = target_deployment.get('github_url', self.config_manager.get('github_url'))
            commit_hash = target_deployment.get('commit_hash')
            bucket_name = target_deployment.get('bucket')
            env_file_path = self.config_manager.get('env_file_path') if target_deployment.get('env_file_used') else None
            
            if not github_url or not commit_hash:
                print("Missing repository URL or commit hash")
                return False
            
            # Create backup and clear current deployment
            backup_prefix = f"rollback_backups/{args.env}"
            self.aws_client.backup_current_deployment(bucket_name, backup_prefix)
            self.aws_client.clear_s3_bucket(bucket_name)
            
            print(f"\nDeploying commit {commit_hash[:8]}...")
            project_path, actual_commit = self.git_ops.clone_repository(github_url, None, commit_hash)
            build_path = build_project(project_path, env_file_path, self.config_manager.config)
            
            if self.config_manager.get('create_health_check', True):
                create_health_check_endpoint(build_path)
            
            if self.config_manager.get('create_dockerfile', True):
                create_dockerfile_and_dockerignore(build_path, project_path, 
                                                 self.config_manager.get('project_type', 'react'))
            
            website_url = self.aws_client.create_s3_bucket(bucket_name)
            self.aws_client.upload_to_s3(build_path, bucket_name)
            
            # Save rollback record
            rollback_deployment = {
                'timestamp': datetime.now().isoformat(),
                'environment': args.env,
                'bucket': bucket_name,
                'url': website_url,
                'region': self.aws_client.aws_region,
                'profile': self.aws_client.aws_profile,
                'github_url': github_url,
                'github_branch': target_deployment.get('github_branch', 'master'),
                'commit_hash': actual_commit,
                'commit_short': actual_commit[:8] if actual_commit else None,
                'env_file_used': env_file_path is not None,
                'docker_files_created': self.config_manager.get('create_dockerfile', True),
                'health_check_created': self.config_manager.get('create_health_check', True),
                'status': 'success',
                'rollback_from': current_deployment['timestamp'],
                'rollback_to': target_deployment['timestamp']
            }
            
            deployments = self.config_manager.get('deployments', [])
            deployments.insert(0, rollback_deployment)
            self.config_manager.set('deployments', deployments[:10])
            
            print("Rollback successful!")
            print("=" * 50)
            print(f"URL: {website_url}")
            print(f"Health: {website_url}/health")
            print(f"Rolled back to: {actual_commit[:8] if actual_commit else 'N/A'}")
            print(f"Backup: s3://{bucket_name}/{backup_prefix}")
            
            monitoring_config = self.config_manager.get('monitoring', {})
            if monitoring_config.get('enabled'):
                compression = monitoring_config.get('compression', '').upper()
                print("=" * 50)
                print(f"{compression} MONITORING IS TRACKING ROLLBACK!")
                if monitoring_config.get('grafana_url'):
                    print(f"Dashboard: {monitoring_config['grafana_url']}")
                
                alerting_config = monitoring_config.get('alerting', {})
                if alerting_config.get('enabled'):
                    print(f"Alerts active: {alerting_config.get('email')}")
                    print("You'll get notified if rollback causes issues!")
            
            return True
            
        except Exception as e:
            print(f"Rollback failed: {e}")
            return False
        finally:
            self.cleanup()
 
