# Personal AI Employee - Bronze Tier

A local-first, autonomous AI employee that manages personal and business affairs using Claude Code and Obsidian.

## Overview

This project implements a **Digital FTE (Full-Time Equivalent)** - an AI agent that works 24/7 to:
- Monitor files dropped into the Inbox folder
- Process items using Claude Code reasoning
- Create action plans and execute tasks
- Maintain audit logs and update dashboards

**Bronze Tier Deliverables:**
- ✅ Obsidian vault with Dashboard.md and Company_Handbook.md
- ✅ Filesystem Watcher script (monitors Inbox folder)
- ✅ Claude Code integration for reading/writing to vault
- ✅ Basic folder structure: /Inbox, /Needs_Action, /Done
- ✅ Orchestrator for coordinating workflows

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL TRIGGER                          │
│              (File dropped in Inbox folder)                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   PERCEPTION LAYER                           │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Filesystem Watcher (Python)                            │ │
│  │  - Monitors Inbox folder                                │ │
│  │  - Creates action files in Needs_Action                 │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    OBSIDIAN VAULT                            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  /Needs_Action/  │  /Plans/  │  /Done/  │  /Logs/     │ │
│  │  /Pending_Approval/  │  /Approved/  │  /Accounting/   │ │
│  │  Dashboard.md  │  Company_Handbook.md  │  Business_Goals.md │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   REASONING LAYER                            │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  CLAUDE CODE                                             │ │
│  │  - Reads pending items                                   │ │
│  │  - Reviews Company Handbook for rules                    │ │
│  │  - Creates plans with checkboxes                         │ │
│  │  - Executes actions or requests approval                 │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

| Component | Requirement | Purpose |
|-----------|-------------|---------|
| Claude Code | Active subscription | Primary reasoning engine |
| Obsidian | v1.10.6+ (free) | Knowledge base & dashboard |
| Python | 3.13 or higher | Watcher scripts & orchestration |
| Node.js | v24+ LTS | MCP servers (future tiers) |

## Installation

### 1. Clone and Setup

```bash
# Navigate to project directory
cd Hacathon_0_subhan_bhai

# Install Python dependencies
pip install -r src/requirements.txt
```

### 2. Open Obsidian Vault

```bash
# Open the vault in Obsidian
# File → Open Folder → Select AI_Employee_Vault
```

### 3. Verify Claude Code

```bash
claude --version
```

## Usage

### Quick Start (Dry Run Mode)

Start the orchestrator in dry-run mode to see what would happen without executing:

```bash
cd src
python orchestrator.py ../AI_Employee_Vault --dry-run --verbose
```

### Start Filesystem Watcher

In a separate terminal:

```bash
cd src
python filesystem_watcher.py ../AI_Employee_Vault
```

### Test the Workflow

1. **Drop a file** into the `AI_Employee_Vault/Inbox` folder
2. **Watcher detects** the file and creates action files in `Needs_Action`
3. **Orchestrator triggers** Claude Code to process the item
4. **Claude reads** the Company Handbook and creates a plan
5. **Actions executed** or approval requested
6. **Completed items** moved to `Done` folder

### Manual Claude Processing

You can also manually trigger Claude Code:

```bash
cd AI_Employee_Vault
claude "Check the Needs_Action folder and process any pending items. Review Company_Handbook.md for rules."
```

## Folder Structure

```
Hacathon_0_subhan_bhai/
├── AI_Employee_Vault/          # Obsidian vault
│   ├── Inbox/                  # Drop files here for processing
│   ├── Needs_Action/           # Items awaiting processing
│   ├── Plans/                  # Claude's action plans
│   ├── Pending_Approval/       # Awaiting human approval
│   ├── Approved/               # Approved for execution
│   ├── Done/                   # Completed items
│   ├── Accounting/             # Financial records
│   ├── Logs/                   # Audit logs
│   ├── Briefings/              # CEO briefings
│   ├── Dashboard.md            # Real-time status
│   ├── Company_Handbook.md     # Rules of engagement
│   └── Business_Goals.md       # Objectives & targets
├── src/
│   ├── base_watcher.py         # Base class for watchers
│   ├── filesystem_watcher.py   # File monitoring watcher
│   ├── orchestrator.py         # Main coordinator
│   └── requirements.txt        # Python dependencies
└── README.md                   # This file
```

## Configuration

### Environment Variables

Create a `.env` file in the `src` directory for sensitive configuration:

```bash
# .env - NEVER commit this file
DRY_RUN=true
VAULT_PATH=./AI_Employee_Vault
LOG_LEVEL=INFO
```

### Company Handbook

Edit `AI_Employee_Vault/Company_Handbook.md` to customize:
- Communication guidelines
- Financial rules and approval thresholds
- File operation permissions
- Escalation rules

### Business Goals

Edit `AI_Employee_Vault/Business_Goals.md` to set:
- Revenue targets
- Key metrics to track
- Active projects
- Subscription audit rules

## Testing

### Test Filesystem Watcher

```bash
# Start watcher
python src/filesystem_watcher.py AI_Employee_Vault

# In another terminal, drop a test file
echo "Test content" > AI_Employee_Vault/Inbox/test.txt

# Watch for action file creation in Needs_Action folder
```

### Test Orchestrator

```bash
# Start orchestrator in verbose dry-run mode
python src/orchestrator.py AI_Employee_Vault --dry-run --verbose
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `claude: command not found` | Install Claude Code: `npm install -g @anthropic/claude-code` |
| Watcher not detecting files | Check folder permissions, ensure Inbox folder exists |
| Orchestrator not triggering Claude | Verify `--dry-run` flag, check logs for errors |
| Dashboard not updating | Ensure Dashboard.md has write permissions |

## Next Steps (Silver Tier)

To upgrade to Silver tier, add:
1. Gmail Watcher for email monitoring
2. WhatsApp Watcher for message monitoring
3. MCP server for sending emails
4. Human-in-the-loop approval workflow
5. Scheduled tasks via cron/Task Scheduler

## Security Notes

- **Never commit** `.env` files or credentials
- Use **dry-run mode** during development
- Review all **approval requests** before executing sensitive actions
- Maintain **audit logs** in the `Logs` folder

## License

This project is part of the Personal AI Employee Hackathon 0.

## Resources

- [Hackathon Document](./Personal%20AI%20Employee%20Hacathon%200_%20Building%20Antunomous%20FTEs%20in%20%202026)
- [Claude Code Docs](https://agentfactory.panaversity.org/docs/AI-Tool-Landscape/claude-code-features-and-workflows)
- [Obsidian Help](https://help.obsidian.md/Getting+started)
- [Wednesday Research Meetings](https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1)
