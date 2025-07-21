"""Base command class."""

from abc import ABC, abstractmethod
from core.config import ConfigManager
from core.aws_client import AWSClient
from core.git_operations import GitOperations


class BaseCommand(ABC):
    def __init__(self):
        self.config_manager = ConfigManager()
        self.aws_client = AWSClient(
            profile=self.config_manager.get('aws_profile', 'abhinav'),
            region=self.config_manager.get('aws_region', 'ap-south-1')
        )
        self.git_ops = GitOperations()
    
    @abstractmethod
    def execute(self, args):
        """Execute the command."""
        pass
    
    def cleanup(self):
        """Cleanup resources."""
        if hasattr(self.git_ops, 'temp_dir') and self.git_ops.temp_dir:
            self.git_ops.cleanup_temp_dir()
 
