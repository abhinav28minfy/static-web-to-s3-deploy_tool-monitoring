# DevOps Deploy Tool - Command Reference


GitHub-to-S3 deployment tool with GZIP compressed monitoring.

## Prerequisites
- Node.js, npm, Git, AWS CLI with SSO, Python 3.7+
- Run: pip install boto3


## Quick Start
- python deploy_tool.py check
- python deploy_tool.py init --github-url https://github.com/username/repo
- python deploy_tool.py deploy
- python deploy_tool.py monitoring init


## All Commands


## Prerequisites & Setup
- python deploy_tool.py check
- python deploy_tool.py init --github-url https://github.com/user/repo
- python deploy_tool.py init --github-url https://github.com/user/repo --name my-project

## Deployment Commands
- python deploy_tool.py deploy
- python deploy_tool.py deploy --env dev
- python deploy_tool.py deploy --env staging
- python deploy_tool.py deploy --env prod
- python deploy_tool.py deploy --env prod --env-file /path/to/.env
- python deploy_tool.py deploy --no-docker --no-health-check
- python deploy_tool.py deploy --github-url https://github.com/user/repo --env-file /path/to/.env

## Status & Information
- python deploy_tool.py status

## Rollback Commands
- python deploy_tool.py rollback
- python deploy_tool.py rollback --env dev
- python deploy_tool.py rollback --env staging
- python deploy_tool.py rollback --env prod
- python deploy_tool.py rollback --env dev --deployment 2
- python deploy_tool.py rollback --deployment 3

## GZIP Compressed Monitoring Commands
- python deploy_tool.py monitoring init # Setup with MANDATORY email alerts
- python deploy_tool.py monitoring status # Check monitoring status
- python deploy_tool.py monitoring update # Update monitored websites
- python deploy_tool.py monitoring destroy # Remove monitoring (~$8/month)

## Configuration Management
- python deploy_tool.py config --set key=value
- python deploy_tool.py config --set environments.dev.bucket=my-dev-bucket
- python deploy_tool.py config --set aws_region=us-east-1
- python deploy_tool.py config --set create_health_check=true
- python deploy_tool.py config --list

## Multi-Environment Deploy
- python deploy_tool.py deploy --env dev
- python deploy_tool.py deploy --env staging
- python deploy_tool.py deploy --env prod

## Advanced Deploy with Environment File
- python deploy_tool.py deploy --env prod --env-file /home/user/production.env



## Key Features
- Auto S3 bucket creation with static hosting

- Health check endpoints (/health)

- GZIP compressed monitoring (bypasses 16KB AWS limit)

- Email alerts via Gmail SMTP

- Prometheus + Grafana dashboard

- Multi-environment support (dev/staging/prod)

- Point-in-time rollbacks with backup

- React/Vite project auto-detection

- Docker file generation


PS: Remember to move to the deploy_tool directory and configuring aws sso, before running the commands. Also make sure the code to be deployed is in the master branch of your github repository. If you intend to monitor the deployment of multiple applications, make sure to use minitoring init after deploying all, or use monitoing destroy, each time after a new application is deployed, then initialize the unified monitoring(auto).
 
