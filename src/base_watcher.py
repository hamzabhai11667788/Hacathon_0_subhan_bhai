"""
Base Watcher - Abstract base class for all AI Employee watchers.

Watchers are lightweight Python scripts that run continuously,
monitoring various inputs and creating actionable files for Claude to process.
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime


class BaseWatcher(ABC):
    """
    Abstract base class for all watcher implementations.
    
    All watchers follow the same pattern:
    1. Continuously monitor a data source
    2. Detect new/updated items
    3. Create action files in the Needs_Action folder
    """
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 60)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.inbox = self.vault_path / 'Inbox'
        self.check_interval = check_interval
        
        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.inbox.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        
        # Track processed items to avoid duplicates
        self.processed_ids = set()
    
    @abstractmethod
    def check_for_updates(self) -> list:
        """
        Check the data source for new or updated items.
        
        Returns:
            List of items that need processing
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item) -> Path:
        """
        Create a Markdown action file in the Needs_Action folder.
        
        Args:
            item: The item to create an action file for
            
        Returns:
            Path to the created file
        """
        pass
    
    def run(self):
        """
        Main run loop - continuously monitors and creates action files.
        
        This method runs indefinitely until interrupted.
        """
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        
        while True:
            try:
                items = self.check_for_updates()
                for item in items:
                    filepath = self.create_action_file(item)
                    self.logger.info(f'Created action file: {filepath}')
            except Exception as e:
                self.logger.error(f'Error during check: {e}')
            
            time.sleep(self.check_interval)
    
    def generate_filename(self, prefix: str, unique_id: str) -> str:
        """
        Generate a unique filename for an action file.
        
        Args:
            prefix: File prefix (e.g., 'EMAIL', 'FILE')
            unique_id: Unique identifier for the item
            
        Returns:
            Filename with .md extension
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f'{prefix}_{unique_id}_{timestamp}.md'
    
    def create_frontmatter(self, item_type: str, **kwargs) -> str:
        """
        Create YAML frontmatter for an action file.
        
        Args:
            item_type: Type of item (email, file, message, etc.)
            **kwargs: Additional frontmatter fields
            
        Returns:
            YAML frontmatter string
        """
        lines = [
            '---',
            f'type: {item_type}',
            f'created: {datetime.now().isoformat()}',
            'status: pending',
        ]
        
        for key, value in kwargs.items():
            lines.append(f'{key}: {value}')
        
        lines.append('---')
        return '\n'.join(lines)
