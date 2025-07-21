"""Config command implementation."""

import json
from commands.base import BaseCommand


class ConfigCommand(BaseCommand):
    def execute(self, args):
        """Handle configuration commands."""
        if args.set:
            key, value = args.set.split('=', 1)
            self.config_manager.set(key, value)
            print(f"Configuration updated: {key} = {value}")
        elif args.list:
            print("Configuration:")
            print(json.dumps(self.config_manager.config, indent=2))
        else:
            print("Use --set key=value or --list")
 
