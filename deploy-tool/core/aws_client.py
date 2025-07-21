"""AWS client management and operations."""

import boto3
import json
import time
from botocore.exceptions import ProfileNotFound, NoCredentialsError
from datetime import datetime
from typing import Optional


class AWSClient:
    def __init__(self, profile: str = 'abhinav', region: str = 'ap-south-1'):
        self.aws_profile = profile
        self.aws_region = region
        self._session = None
        self._s3_client = None
        self._ec2_client = None
    
    def get_boto3_session(self):
        """Get AWS session with error handling."""
        if self._session is None:
            try:
                self._session = boto3.Session(profile_name=self.aws_profile)
            except ProfileNotFound:
                print(f"AWS profile '{self.aws_profile}' not found.")
                print(f"Please run: aws configure sso --profile {self.aws_profile}")
                raise
            except NoCredentialsError:
                print(f"No credentials found for profile '{self.aws_profile}'.")
                print(f"Please run: aws sso login --profile {self.aws_profile}")
                raise
        return self._session
    
    def get_s3_client(self):
        """Get S3 client."""
        if self._s3_client is None:
            session = self.get_boto3_session()
            self._s3_client = session.client('s3', region_name=self.aws_region)
        return self._s3_client
    
    def get_ec2_client(self):
        """Get EC2 client."""
        if self._ec2_client is None:
            session = self.get_boto3_session()
            self._ec2_client = session.client('ec2', region_name=self.aws_region)
        return self._ec2_client
    
    def check_sso_login(self) -> bool:
        """Check if SSO login is valid."""
        try:
            session = self.get_boto3_session()
            sts = session.client('sts')
            identity = sts.get_caller_identity()
            print(f"SSO login valid for account: {identity['Account']}")
            return True
        except Exception as e:
            print(f"SSO login expired or invalid: {e}")
            print(f"Please run: aws sso login --profile {self.aws_profile}")
            return False
    
    def create_s3_bucket(self, bucket_name: str) -> str:
        """Create and configure S3 bucket for static hosting."""
        print(f"Creating S3 bucket: {bucket_name}")
        
        s3 = self.get_s3_client()
        
        try:
            if self.aws_region == 'us-east-1':
                s3.create_bucket(Bucket=bucket_name)
            else:
                s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': self.aws_region}
                )
            
            print("Configuring bucket for public access...")
            s3.put_public_access_block(
                Bucket=bucket_name,
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': False,
                    'IgnorePublicAcls': False,
                    'BlockPublicPolicy': False,
                    'RestrictPublicBuckets': False
                }
            )
            
            time.sleep(2)
            
            print("Configuring static website hosting...")
            s3.put_bucket_website(
                Bucket=bucket_name,
                WebsiteConfiguration={
                    'IndexDocument': {'Suffix': 'index.html'},
                    'ErrorDocument': {'Key': 'error.html'}
                }
            )
            
            print("Setting bucket policy for public access...")
            policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/*"
                }]
            }
            
            s3.put_bucket_policy(
                Bucket=bucket_name,
                Policy=json.dumps(policy)
            )
            
            print("S3 bucket created and configured successfully")
            return f"http://{bucket_name}.s3-website.{self.aws_region}.amazonaws.com"
            
        except Exception as e:
            if "BucketAlreadyExists" in str(e) or "BucketAlreadyOwnedByYou" in str(e):
                print(f"Bucket {bucket_name} already exists, configuring for public access...")
                
                try:
                    s3.put_public_access_block(
                        Bucket=bucket_name,
                        PublicAccessBlockConfiguration={
                            'BlockPublicAcls': False,
                            'IgnorePublicAcls': False,
                            'BlockPublicPolicy': False,
                            'RestrictPublicBuckets': False
                        }
                    )
                    
                    time.sleep(2)
                    
                    s3.put_bucket_website(
                        Bucket=bucket_name,
                        WebsiteConfiguration={
                            'IndexDocument': {'Suffix': 'index.html'},
                            'ErrorDocument': {'Key': 'error.html'}
                        }
                    )
                    
                    policy = {
                        "Version": "2012-10-17",
                        "Statement": [{
                            "Sid": "PublicReadGetObject",
                            "Effect": "Allow",
                            "Principal": "*",
                            "Action": "s3:GetObject",
                            "Resource": f"arn:aws:s3:::{bucket_name}/*"
                        }]
                    }
                    
                    s3.put_bucket_policy(
                        Bucket=bucket_name,
                        Policy=json.dumps(policy)
                    )
                    
                    print("Existing bucket configured successfully")
                    
                except Exception as config_error:
                    print(f"Warning: Could not configure existing bucket: {config_error}")
                
                return f"http://{bucket_name}.s3-website.{self.aws_region}.amazonaws.com"
            else:
                raise e
    
    def upload_to_s3(self, build_dir: str, bucket_name: str) -> int:
        """Upload files to S3 bucket."""
        print("Uploading files to S3...")
        
        s3 = self.get_s3_client()
        file_count = 0
        
        content_types = {
            '.html': 'text/html',
            '.js': 'application/javascript',
            '.css': 'text/css',
            '.json': 'application/json',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.ico': 'image/x-icon'
        }
        
        import os
        for root, dirs, files in os.walk(build_dir):
            for file in files:
                local_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_path, build_dir)
                s3_path = relative_path.replace('\\', '/')
                
                file_ext = os.path.splitext(file)[1].lower()
                content_type = content_types.get(file_ext, 'application/json' if file == 'health' else 'text/html')
                
                s3.upload_file(
                    local_path,
                    bucket_name,
                    s3_path,
                    ExtraArgs={'ContentType': content_type}
                )
                
                file_count += 1
                print(f"  Uploaded: {s3_path}")
        
        print(f"Upload completed ({file_count} files)")
        return file_count
    
    def backup_current_deployment(self, bucket_name: str, backup_prefix: str) -> bool:
        """Backup current deployment before rollback."""
        print("Creating backup of current deployment...")
        
        s3 = self.get_s3_client()
        
        try:
            response = s3.list_objects_v2(Bucket=bucket_name)
            
            if 'Contents' not in response:
                print("No files to backup")
                return True
            
            backup_folder = f"{backup_prefix}/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            for obj in response['Contents']:
                source_key = obj['Key']
                backup_key = f"{backup_folder}/{source_key}"
                
                s3.copy_object(
                    Bucket=bucket_name,
                    CopySource={'Bucket': bucket_name, 'Key': source_key},
                    Key=backup_key
                )
            
            print(f"Backup created at: s3://{bucket_name}/{backup_folder}")
            return True
            
        except Exception as e:
            print(f"Warning: Could not create backup: {e}")
            return False
    
    def clear_s3_bucket(self, bucket_name: str) -> bool:
        """Clear all objects from S3 bucket."""
        print("Clearing current deployment from S3...")
        
        s3 = self.get_s3_client()
        
        try:
            response = s3.list_objects_v2(Bucket=bucket_name)
            
            if 'Contents' not in response:
                print("No files to clear")
                return True
            
            objects_to_delete = [{'Key': obj['Key']} for obj in response['Contents']]
            
            s3.delete_objects(
                Bucket=bucket_name,
                Delete={'Objects': objects_to_delete}
            )
            
            print(f"Cleared {len(objects_to_delete)} objects from bucket")
            return True
            
        except Exception as e:
            print(f"Error clearing bucket: {e}")
            return False
 
