#!/usr/bin/env python3
"""
DevOps Deploy Tool - GitHub Repository Deployment with COMPRESSED Monitoring
Usage: python deploy_tool.py [command] [options]
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from commands.init import InitCommand
from commands.deploy import DeployCommand
from commands.status import StatusCommand
from commands.rollback import RollbackCommand
from commands.config_cmd import ConfigCommand
from commands.monitoring import MonitoringCommand
from utils.prerequisites import check_prerequisites


def main():
    parser = argparse.ArgumentParser(description='GitHub Deploy Tool with GZIP Compressed Monitoring')
    parser.add_argument('command', choices=['init', 'deploy', 'status', 'rollback', 'config', 'check', 'monitoring'])
    parser.add_argument('subcommand', nargs='?', choices=['init', 'status', 'destroy', 'update'], help='Monitoring subcommand')
    parser.add_argument('--env', default='dev', help='Environment (dev/staging/prod)')
    parser.add_argument('--github-url', help='GitHub repository URL')
    parser.add_argument('--name', help='Project name')
    parser.add_argument('--env-file', help='Path to .env file')
    parser.add_argument('--no-docker', action='store_true', help='Skip Docker file creation')
    parser.add_argument('--no-health-check', action='store_true', help='Skip health check endpoint creation')
    parser.add_argument('--set', help='Set config (key=value)')
    parser.add_argument('--list', action='store_true', help='List config')
    parser.add_argument('--deployment', type=int, help='Deployment index for rollback (1-based)')
    
    args = parser.parse_args()
    
    try:
        if args.command == 'check':
            check_prerequisites()
            
        elif args.command == 'init':
            command = InitCommand()
            command.execute(args)
            
        elif args.command == 'deploy':
            command = DeployCommand()
            command.execute(args)
            
        elif args.command == 'status':
            command = StatusCommand()
            command.execute(args)
            
        elif args.command == 'rollback':
            command = RollbackCommand()
            command.execute(args)
            
        elif args.command == 'monitoring':
            command = MonitoringCommand()
            command.execute(args)
                
        elif args.command == 'config':
            command = ConfigCommand()
            command.execute(args)
                
    except KeyboardInterrupt:
        print("\nCancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
 
