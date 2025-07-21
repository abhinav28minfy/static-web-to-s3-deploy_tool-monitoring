"""Status command implementation."""

from commands.base import BaseCommand


class StatusCommand(BaseCommand):
    def execute(self, args):
        """Show deployment status."""
        print("Deployment Status")
        print("=" * 50)
        
        config = self.config_manager.config
        if not config:
            print("No configuration found")
            return
        
        print(f"AWS Profile: {config.get('aws_profile', self.aws_client.aws_profile)}")
        print(f"AWS Region: {config.get('aws_region', self.aws_client.aws_region)}")
        print(f"Create Dockerfile: {config.get('create_dockerfile', True)}")
        print(f"Create Health Check: {config.get('create_health_check', True)}")
        
        if config.get('env_file_path'):
            print(f"Environment file: {config['env_file_path']}")
        
        if config.get('github_url'):
            print(f"Repository: {config['github_url']}")
            print(f"Branch: {config.get('github_branch', 'master')}")
        
        monitoring_config = config.get('monitoring', {})
        if monitoring_config.get('enabled'):
            compression = monitoring_config.get('compression', '').upper()
            print(f"Monitoring: ACTIVE ({compression})")
            if monitoring_config.get('grafana_url'):
                print(f"  Dashboard: {monitoring_config['grafana_url']}")
            
            alerting_config = monitoring_config.get('alerting', {})
            if alerting_config.get('enabled'):
                print(f"  Email Alerts: ENABLED - {alerting_config.get('email')}")
            else:
                print(f"  Email Alerts: DISABLED")
        else:
            print(f"Monitoring: DISABLED")
        
        print()
        
        deployments = config.get('deployments', [])
        
        if not deployments:
            print("No deployments found")
            return
        
        print("Recent Deployments:")
        for i, deployment in enumerate(deployments[:5]):
            status_icon = 'SUCCESS' if deployment['status'] == 'success' else 'FAILED'
            print(f"{i+1}. {deployment['timestamp'][:19]} {status_icon}")
            print(f"   Environment: {deployment['environment']}")
            print(f"   URL: {deployment['url']}")
            if deployment.get('health_check_created'):
                print(f"   Health: {deployment['url']}/health")
            print(f"   Branch: {deployment.get('github_branch', 'N/A')}")
            print(f"   Commit: {deployment.get('commit_short', 'N/A')}")
            print(f"   Region: {deployment.get('region', 'N/A')}")
            print()
 
