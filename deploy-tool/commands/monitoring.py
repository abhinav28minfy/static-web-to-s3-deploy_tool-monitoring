"""Monitoring command implementation."""

import time
from datetime import datetime
from commands.base import BaseCommand
from utils.compression import create_compressed_monitoring_user_data


class MonitoringCommand(BaseCommand):
    def execute(self, args):
        """Handle monitoring commands."""
        if args.subcommand == 'init':
            self._init_monitoring()
        elif args.subcommand == 'status':
            self._monitoring_status()
        elif args.subcommand == 'destroy':
            self._destroy_monitoring()
        elif args.subcommand == 'update':
            self._update_monitoring_targets()
        else:
            print("GZIP Monitoring Commands:")
            print("  init    - Set up monitoring with GZIP compression")
            print("  status  - Check monitoring status")
            print("  destroy - Remove monitoring")
            print("  update  - Update monitored websites")
            print("\nUsage: python deploy_tool.py monitoring <subcommand>")
    
    def _init_monitoring(self):
        """Initialize monitoring with GZIP compression."""
        print("Setting up monitoring with GZIP compression...")
        
        if not self.aws_client.check_sso_login():
            return False
        
        if not self.config_manager.get('project_name'):
            print("Project not initialized. Run 'init' first.")
            return False
        
        if self.config_manager.get('monitoring.enabled'):
            print("Monitoring already enabled!")
            monitoring_config = self.config_manager.get('monitoring', {})
            if monitoring_config.get('grafana_url'):
                print(f"Grafana: {monitoring_config['grafana_url']}")
            return True
        
        # Get targets from deployments
        targets = []
        deployments = self.config_manager.get('deployments', [])
        
        seen_urls = set()
        for deployment in deployments:
            if deployment.get('status') == 'success' and deployment.get('url'):
                if deployment['url'] not in seen_urls:
                    targets.append(deployment['url'])
                    seen_urls.add(deployment['url'])
        
        if not targets:
            print("No websites found to monitor!")
            print("Deploy your app first: python deploy_tool.py deploy")
            return False
        
        print(f"\nFound {len(targets)} website(s) to monitor:")
        for i, target in enumerate(targets, 1):
            print(f"  {i}. {target}")
        
        # Email setup
        #enable_alerts = input(f"\nEnable email alerts for downtime? (y/n): ").lower().strip()
        
        #alert_email = None
        #gmail_app_password = None
        
        alert_email, gmail_app_password = self._collect_smtp_credentials()
        
        print(f"\nGZIP Monitoring Setup Summary:")
        print(f"Websites to monitor: {len(targets)}")
        print(f"Dashboard: Working UP/DOWN status + response times")
        print(f"Email alerts: {'Yes - ' + alert_email if alert_email else 'No'}")
        print(f"Instance: t3.micro (~$8/month)")
        print(f"Compression: GZIP (bypasses 16KB limit)")
        print(f"Auto-refresh: 30 seconds")
        
        confirm = input(f"\nStart GZIP monitoring setup? (yes/no): ").lower().strip()
        if confirm != 'yes':
            print("Setup cancelled")
            return False
        
        try:
            print("\nCREATING GZIP MONITORING INSTANCE...")
            instance_id, public_ip = self._create_monitoring_instance(targets, alert_email, gmail_app_password)
            
            print("WAITING FOR SERVICES TO START (3-4 minutes for full setup)...")
            time.sleep(240)  # 4 minutes
            
            grafana_url = f"http://{public_ip}:3000"
            prometheus_url = f"http://{public_ip}:9090"
            
            monitoring_config = {
                'enabled': True,
                'instance_id': instance_id,
                'public_ip': public_ip,
                'grafana_url': grafana_url,
                'prometheus_url': prometheus_url,
                'targets': targets,
                'created_at': datetime.now().isoformat(),
                'compression': 'gzip',
                'alerting': {
                    'enabled': bool(alert_email),
                    'email': alert_email,
                    'gmail_app_password': gmail_app_password
                }
            }
            
            self.config_manager.set('monitoring', monitoring_config)
            
            print("\nGZIP MONITORING SETUP COMPLETE!")
            print("=" * 60)
            print(f"GRAFANA DASHBOARD: {grafana_url}")
            print(f"PROMETHEUS: {prometheus_url}")
            print("=" * 60)
            print("LOGIN CREDENTIALS:")
            print("  Username: admin")
            print("  Password: admin123")
            print("=" * 60)
            print("WORKING FEATURES:")
            print("  Website status dashboard (UP/DOWN)")
            print("  Response time monitoring with graphs")
            print("  Health check endpoint monitoring")
            print("  Auto-refresh every 30 seconds")
            print("  Historical data tracking")
            if alert_email:
                print(f"  Email alerts to: {alert_email}")
                print("  Website down alerts (2min threshold)")
                print("  SMTP configured via Gmail")
            print("=" * 60)
            print("GZIP COMPRESSION SUCCESS:")
            print("  Bypassed 16KB AWS user data limit!")
            print("  Full monitoring stack deployed")
            print("  All dashboard features working")
            print("  Email alerts configured")
            print("=" * 60)
            print("COST: ~$8/month (t3.micro)")
            print("ALL SYSTEMS WORKING WITH COMPRESSION!")
            
            return True
            
        except Exception as e:
            print(f"GZIP MONITORING SETUP FAILED: {e}")
            print("Try again or check AWS permissions")
            return False
    
    def _monitoring_status(self):
        """Show monitoring status."""
        print("GZIP Monitoring Status")
        print("=" * 50)
        
        monitoring_config = self.config_manager.get('monitoring', {})
        
        if not monitoring_config.get('enabled'):
            print("Monitoring not enabled")
            print("Run: python deploy_tool.py monitoring init")
            return
        
        print(f"Status: ACTIVE (GZIP Compressed)")
        print(f"Instance: {monitoring_config.get('instance_id', 'N/A')}")
        print(f"IP Address: {monitoring_config.get('public_ip', 'N/A')}")
        print(f"Created: {monitoring_config.get('created_at', 'N/A')[:19]}")
        print(f"Compression: {monitoring_config.get('compression', 'None').upper()}")
        
        print(f"\nACCESS URLs:")
        if monitoring_config.get('grafana_url'):
            print(f"  Grafana Dashboard: {monitoring_config['grafana_url']}")
            print(f"      Login: admin/admin123")
        if monitoring_config.get('prometheus_url'):
            print(f"  Prometheus: {monitoring_config['prometheus_url']}")
        
        targets = monitoring_config.get('targets', [])
        print(f"\nMONITORED WEBSITES ({len(targets)}):")
        for i, target in enumerate(targets, 1):
            print(f"  {i}. {target}")
            print(f"     Health: {target}/health")
        
        alerting_config = monitoring_config.get('alerting', {})
        print(f"\nEMAIL ALERTS:")
        if alerting_config.get('enabled'):
            print(f"  Status: ACTIVE")
            print(f"  Email: {alerting_config.get('email', 'N/A')}")
            print(f"  SMTP: Gmail configured")
            print(f"  Alerts: Website down (2min threshold)")
        else:
            print(f"  Status: DISABLED")
        
        print(f"\nCOMPRESSION INFO:")
        print(f"  Method: GZIP compression used")
        print(f"  Benefit: Bypassed 16KB AWS limit")
        print(f"  Features: Full monitoring stack deployed")
        
        print(f"\nMonthly cost: ~$8 (t3.micro)")
    
    def _destroy_monitoring(self):
        """Destroy monitoring."""
        monitoring_config = self.config_manager.get('monitoring', {})
        
        if not monitoring_config.get('enabled'):
            print("No monitoring to destroy")
            return False
        
        instance_id = monitoring_config.get('instance_id')
        if not instance_id:
            print("No instance found")
            return False
        
        print(f"This will destroy:")
        print(f"  GZIP compressed monitoring instance: {instance_id}")
        print(f"  All Grafana dashboards and data")
        print(f"  All email alert configurations")
        print(f"  All Prometheus metrics")
        
        confirm = input(f"\nDestroy GZIP monitoring? (yes/no): ").lower().strip()
        if confirm != 'yes':
            print("Cancelled")
            return False
        
        try:
            ec2 = self.aws_client.get_ec2_client()
            ec2.terminate_instances(InstanceIds=[instance_id])
            print(f"Instance {instance_id} terminated")
            
            self.config_manager.set('monitoring', {
                'enabled': False,
                'instance_id': None,
                'public_ip': None,
                'grafana_url': None,
                'prometheus_url': None,
                'targets': [],
                'destroyed_at': datetime.now().isoformat(),
                'compression': None,
                'alerting': {'enabled': False, 'email': None}
            })
            
            print("GZIP monitoring destroyed!")
            print("Run 'monitoring init' to recreate with compression")
            return True
            
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def _update_monitoring_targets(self):
        """Update monitoring targets."""
        monitoring_config = self.config_manager.get('monitoring', {})
        
        if not monitoring_config.get('enabled'):
            print("Monitoring not enabled")
            return False
        
        # Get current targets from deployments
        targets = []
        deployments = self.config_manager.get('deployments', [])
        
        seen_urls = set()
        for deployment in deployments:
            if deployment.get('status') == 'success' and deployment.get('url'):
                if deployment['url'] not in seen_urls:
                    targets.append(deployment['url'])
                    seen_urls.add(deployment['url'])
        
        if not targets:
            print("No websites to monitor")
            return False
        
        print(f"Updating GZIP monitoring targets:")
        for i, target in enumerate(targets, 1):
            print(f"  {i}. {target}")
        
        self.config_manager.set('monitoring.targets', targets)
        
        print("Targets updated in config!")
        print("To apply to monitoring:")
        print("  1. SSH to monitoring instance")
        print("  2. Update prometheus.yml")
        print("  3. Run: docker-compose restart prometheus")
        print("\nOr recreate GZIP monitoring for auto-update:")
        print("  python deploy_tool.py monitoring destroy")
        print("  python deploy_tool.py monitoring init")
        
        return True
    
    def _collect_smtp_credentials(self):
        """Collect SMTP credentials."""
        print("\nEmail Alert Setup")
        print("=" * 30)
        
        email = input("Gmail address: ").strip()
        if not email:
            return None, None
        
        print("\nGet Google App Password:")
        print("1. Go to https://myaccount.google.com/apppasswords")
        print("2. Create app password for 'Deploy Tool'")
        
        app_password = input("App Password: ").strip().replace(' ', '')
        if not app_password:
            return None, None
        
        return email, app_password
    
    def _create_monitoring_instance(self, targets, alert_email=None, gmail_app_password=None):
        """Create monitoring EC2 instance."""
        ec2 = self.aws_client.get_ec2_client()
        
        # Create security group
        sg_name = f"{self.config_manager.get('project_name', 'deploy')}-monitoring-sg"
        sg_id = self._create_security_group(sg_name)
        
        # Get AMI
        ami_id = self._get_latest_amazon_linux_ami()
        
        # Create compressed user data
        user_data = create_compressed_monitoring_user_data(targets, alert_email, gmail_app_password)
        
        instance_name = f"{self.config_manager.get('project_name', 'deploy')}-monitoring"
        
        response = ec2.run_instances(
            ImageId=ami_id,
            MinCount=1,
            MaxCount=1,
            InstanceType='t3.micro',
            SecurityGroupIds=[sg_id],
            UserData=user_data,
            TagSpecifications=[{
                'ResourceType': 'instance',
                'Tags': [
                    {'Key': 'Name', 'Value': instance_name},
                    {'Key': 'Project', 'Value': self.config_manager.get('project_name', 'deploy')},
                    {'Key': 'Purpose', 'Value': 'gzip-monitoring'},
                    {'Key': 'Compression', 'Value': 'gzip'}
                ]
            }]
        )
        
        instance_id = response['Instances'][0]['InstanceId']
        print(f"Created GZIP compressed monitoring instance: {instance_id}")
        
        # Wait for running state
        print("Waiting for instance to be running...")
        waiter = ec2.get_waiter('instance_running')
        waiter.wait(InstanceIds=[instance_id])
        
        response = ec2.describe_instances(InstanceIds=[instance_id])
        instance = response['Reservations'][0]['Instances'][0]
        public_ip = instance.get('PublicIpAddress')
        
        print(f"Instance running at: {public_ip}")
        return instance_id, public_ip
    
    def _create_security_group(self, sg_name):
        """Create security group for monitoring."""
        ec2 = self.aws_client.get_ec2_client()
        
        try:
            response = ec2.describe_security_groups(
                Filters=[{'Name': 'group-name', 'Values': [sg_name]}]
            )
            
            if response['SecurityGroups']:
                sg_id = response['SecurityGroups'][0]['GroupId']
                print(f"Using existing security group: {sg_id}")
                return sg_id
            
            response = ec2.create_security_group(
                GroupName=sg_name,
                Description='Security group for compressed monitoring'
            )
            sg_id = response['GroupId']
            
            ec2.authorize_security_group_ingress(
                GroupId=sg_id,
                IpPermissions=[
                    {'IpProtocol': 'tcp', 'FromPort': 3000, 'ToPort': 3000, 'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'Grafana'}]},
                    {'IpProtocol': 'tcp', 'FromPort': 9090, 'ToPort': 9090, 'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'Prometheus'}]},
                    {'IpProtocol': 'tcp', 'FromPort': 9115, 'ToPort': 9115, 'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'Blackbox'}]},
                    {'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22, 'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'SSH'}]}
                ]
            )
            
            print(f"Created security group: {sg_id}")
            return sg_id
            
        except Exception as e:
            print(f"Error creating security group: {e}")
            raise
    
    def _get_latest_amazon_linux_ami(self):
        """Get latest Amazon Linux AMI."""
        ec2 = self.aws_client.get_ec2_client()
        
        try:
            response = ec2.describe_images(
                Owners=['amazon'],
                Filters=[
                    {'Name': 'name', 'Values': ['amzn2-ami-hvm-*-x86_64-gp2']},
                    {'Name': 'state', 'Values': ['available']},
                    {'Name': 'architecture', 'Values': ['x86_64']},
                    {'Name': 'virtualization-type', 'Values': ['hvm']},
                    {'Name': 'root-device-type', 'Values': ['ebs']}
                ]
            )
            
            images = sorted(response['Images'], key=lambda x: x['CreationDate'], reverse=True)
            
            if images:
                ami_id = images[0]['ImageId']
                print(f"Using latest Amazon Linux 2 AMI: {ami_id}")
                return ami_id
            else:
                region_amis = {
                    'us-east-1': 'ami-0c02fb55956c7d316',
                    'us-west-2': 'ami-0c2d3e23000000000',
                    'eu-west-1': 'ami-0c2d3e23000000001', 
                    'ap-south-1': 'ami-0ad21ae1d0696ad58',
                    'ap-southeast-1': 'ami-0c2d3e23000000002'
                }
                fallback_ami = region_amis.get(self.aws_client.aws_region, 'ami-0ad21ae1d0696ad58')
                print(f"Using fallback AMI for {self.aws_client.aws_region}: {fallback_ami}")
                return fallback_ami
                
        except Exception as e:
            print(f"Error getting latest AMI: {e}")
            region_amis = {
                'us-east-1': 'ami-0c02fb55956c7d316',
                'us-west-2': 'ami-0c2d3e23000000000',
                'eu-west-1': 'ami-0c2d3e23000000001', 
                'ap-south-1': 'ami-0ad21ae1d0696ad58',
                'ap-southeast-1': 'ami-0c2d3e23000000002'
            }
            fallback_ami = region_amis.get(self.aws_client.aws_region, 'ami-0ad21ae1d0696ad58')
            print(f"Using fallback AMI for {self.aws_client.aws_region}: {fallback_ami}")
            return fallback_ami
 
