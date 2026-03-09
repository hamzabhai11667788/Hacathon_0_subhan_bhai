"""
Orchestrator - Master process for the AI Employee.

The orchestrator:
1. Monitors the Needs_Action folder for new items
2. Triggers Claude Code to process pending items
3. Updates the Dashboard.md with current status
4. Manages the overall workflow
"""

import logging
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent


class DashboardUpdater:
    """Updates the Dashboard.md with current status."""
    
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.dashboard = vault_path / 'Dashboard.md'
    
    def update(self):
        """Update the dashboard with current folder counts."""
        needs_action = self.vault_path / 'Needs_Action'
        done = self.vault_path / 'Done'
        pending_approval = self.vault_path / 'Pending_Approval'
        plans = self.vault_path / 'Plans'
        
        # Count files in each folder
        pending_count = self._count_files(needs_action)
        done_count = self._count_files(done)
        approval_count = self._count_files(pending_approval)
        plans_count = self._count_files(plans)
        
        # Calculate today's completions
        today = datetime.now().strftime('%Y-%m-%d')
        today_done = self._count_today(done, today)
        
        # Read current dashboard
        if self.dashboard.exists():
            content = self.dashboard.read_text()
        else:
            content = self._create_default_dashboard()
        
        # Update the Quick Status table
        content = self._update_status_table(content, {
            'Pending Items': pending_count,
            'In Progress': plans_count,
            'Awaiting Approval': approval_count,
            'Completed Today': today_done
        })
        
        # Update timestamp
        content = content.replace(
            'last_updated: ', 
            f'last_updated: {datetime.now().isoformat()}'
        )
        
        # Write updated dashboard
        self.dashboard.write_text(content)
        
        logging.info(f'Dashboard updated: {pending_count} pending, {today_done} completed today')
    
    def _count_files(self, folder: Path) -> int:
        """Count non-directory files in a folder."""
        if not folder.exists():
            return 0
        return sum(1 for f in folder.iterdir() if f.is_file())
    
    def _count_today(self, folder: Path, today: str) -> int:
        """Count files modified today."""
        if not folder.exists():
            return 0
        count = 0
        for f in folder.iterdir():
            if f.is_file():
                mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d')
                if mtime == today:
                    count += 1
        return count
    
    def _create_default_dashboard(self) -> str:
        """Create a default dashboard if none exists."""
        return '''---
last_updated: 2026-03-08T00:00:00Z
status: active
---

# AI Employee Dashboard

## Quick Status

| Metric | Value |
|--------|-------|
| Pending Items | 0 |
| In Progress | 0 |
| Awaiting Approval | 0 |
| Completed Today | 0 |

## Recent Activity

## Active Projects

## System Health

| Component | Status |
|-----------|--------|
| Filesystem Watcher | Running |
| Orchestrator | Running |

---
*AI Employee v0.1 (Bronze Tier)*
'''
    
    def _update_status_table(self, content: str, values: dict) -> str:
        """Update the status table with new values."""
        lines = content.split('\n')
        new_lines = []
        in_table = False
        
        for line in lines:
            if '| Pending Items |' in line:
                in_table = True
                new_lines.append(f'| Pending Items | {values.get("Pending Items", 0)} |')
            elif '| In Progress |' in line:
                new_lines.append(f'| In Progress | {values.get("In Progress", 0)} |')
            elif '| Awaiting Approval |' in line:
                new_lines.append(f'| Awaiting Approval | {values.get("Awaiting Approval", 0)} |')
            elif '| Completed Today |' in line:
                new_lines.append(f'| Completed Today | {values.get("Completed Today", 0)} |')
                in_table = False
            else:
                new_lines.append(line)
        
        return '\n'.join(new_lines)


class ActionHandler(FileSystemEventHandler):
    """Handles file creation events in Needs_Action folder."""
    
    def __init__(self, vault_path: Path, orchestrator):
        self.vault_path = vault_path
        self.orchestrator = orchestrator
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def on_created(self, event):
        """Handle new file creation."""
        if event.is_directory:
            return
        
        if 'Needs_Action' in str(event.src_path):
            self.logger.info(f'New action file detected: {event.src_path}')
            self.orchestrator.trigger_claude()


class Orchestrator:
    """
    Main orchestrator for the AI Employee.
    
    Coordinates watchers, Claude Code, and dashboard updates.
    """
    
    def __init__(self, vault_path: str, dry_run: bool = True):
        """
        Initialize the orchestrator.
        
        Args:
            vault_path: Path to the Obsidian vault
            dry_run: If True, log Claude commands instead of executing
        """
        self.vault_path = Path(vault_path)
        self.dry_run = dry_run
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.dashboard_updater = DashboardUpdater(self.vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'
        
        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.done.mkdir(parents=True, exist_ok=True)
        self.logs.mkdir(parents=True, exist_ok=True)
        
        # Setup file watcher
        self.observer = Observer()
        self.handler = ActionHandler(self.vault_path, self)
        self.observer.schedule(self.handler, str(self.needs_action), recursive=False)
    
    def trigger_claude(self):
        """
        Trigger Claude Code to process pending items.
        
        In dry_run mode, just logs what would happen.
        """
        pending_files = list(self.needs_action.glob('*.md'))
        
        if not pending_files:
            self.logger.info('No pending items to process')
            return
        
        self.logger.info(f'Triggering Claude for {len(pending_files)} pending items')
        
        prompt = self._build_claude_prompt(pending_files)
        
        if self.dry_run:
            self.logger.info('[DRY RUN] Would execute Claude with prompt:')
            self.logger.info(prompt[:500] + '...' if len(prompt) > 500 else prompt)
        else:
            self._execute_claude(prompt)
    
    def _build_claude_prompt(self, pending_files: list) -> str:
        """Build the prompt for Claude Code."""
        files_info = '\n'.join([f'- {f.name}' for f in pending_files])
        
        return f'''You are the AI Employee. Process the pending items in the vault.

Vault Path: {self.vault_path}

## Pending Items
{files_info}

## Your Task
1. Read each pending item in /Needs_Action
2. Review the Company_Handbook.md for rules of engagement
3. Check Business_Goals.md for context
4. For each item:
   - Understand what action is needed
   - Create a plan in /Plans with checkboxes
   - Execute non-sensitive actions
   - Create approval requests in /Pending_Approval for sensitive actions
   - Move completed items to /Done

## Important Rules
- Never send messages to unknown contacts without approval
- Flag payments over $500 for approval
- Log all actions
- Be polite and professional

Start by reading the pending items and the Company Handbook.
'''
    
    def _execute_claude(self, prompt: str):
        """Execute Claude Code with the given prompt."""
        try:
            # Change to vault directory and run claude
            result = subprocess.run(
                ['claude', '--prompt', prompt],
                cwd=str(self.vault_path),
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            self.logger.info(f'Claude exit code: {result.returncode}')
            if result.stdout:
                self.logger.info(f'Claude output: {result.stdout[:500]}')
            if result.stderr:
                self.logger.error(f'Claude error: {result.stderr[:500]}')
                
        except subprocess.TimeoutExpired:
            self.logger.error('Claude execution timed out')
        except Exception as e:
            self.logger.error(f'Error executing Claude: {e}')
    
    def update_dashboard(self):
        """Update the dashboard with current status."""
        self.dashboard_updater.update()
    
    def run(self):
        """
        Run the orchestrator.
        
        Starts the file watcher and periodically updates the dashboard.
        """
        self.logger.info(f'Starting Orchestrator for vault: {self.vault_path}')
        self.logger.info(f'Dry run mode: {self.dry_run}')
        
        # Start file watcher
        self.observer.start()
        self.logger.info('File watcher started')
        
        # Initial dashboard update
        self.update_dashboard()
        
        # Main loop
        try:
            while True:
                # Periodic dashboard update
                self.update_dashboard()
                
                # Check for any pending items
                self.trigger_claude()
                
                # Wait before next check
                import time
                time.sleep(30)
                
        except KeyboardInterrupt:
            self.logger.info('Orchestrator shutting down...')
            self.observer.stop()
            self.observer.join()


def main():
    """Run the orchestrator."""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Employee Orchestrator')
    parser.add_argument('vault_path', help='Path to the Obsidian vault')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Log actions instead of executing')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    orchestrator = Orchestrator(args.vault_path, dry_run=args.dry_run)
    orchestrator.run()


if __name__ == '__main__':
    main()
