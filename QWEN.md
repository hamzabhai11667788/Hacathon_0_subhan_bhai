# Personal AI Employee Hackathon Project

## Project Overview

This is a **hackathon project** for building a "Digital FTE" (Full-Time Equivalent) — an autonomous AI employee that manages personal and business affairs 24/7. The project uses a local-first, agent-driven architecture with human-in-the-loop safeguards.

**Core Concept:** Transform Claude Code from a chatbot into a proactive business partner that:
- Monitors communications (Gmail, WhatsApp)
- Manages business tasks (invoicing, social media, payments)
- Provides weekly "CEO Briefings" with revenue/bottleneck analysis
- Operates autonomously with approval workflows for sensitive actions

## Architecture

### Tech Stack
| Component | Technology | Purpose |
|-----------|------------|---------|
| **Brain** | Claude Code | Reasoning engine with Ralph Wiggum loop for autonomy |
| **Memory/GUI** | Obsidian | Local Markdown knowledge base & dashboard |
| **Senses** | Python Watchers | Monitor Gmail, WhatsApp, filesystems |
| **Hands** | MCP Servers | External actions (email, browser, payments) |
| **Browser Automation** | Playwright MCP | Web interactions, form filling, scraping |

### Folder Structure
```
Hacathon_0_subhan_bhai/
├── .qwen/skills/
│   └── browsing-with-playwright/    # Playwright MCP integration
│       ├── SKILL.md                 # Skill documentation
│       ├── references/
│       │   └── playwright-tools.md  # Tool API reference
│       └── scripts/
│           ├── mcp-client.py        # MCP client for tool calls
│           ├── start-server.sh      # Start Playwright server
│           ├── stop-server.sh       # Stop Playwright server
│           └── verify.py            # Server health check
├── Personal AI Employee Hacathon 0_...  # Main hackathon document (991 lines)
├── skills-lock.json                 # Skill versioning
└── QWEN.md                          # This file
```

### Obsidian Vault Structure (To Be Created)
```
AI_Employee_Vault/
├── Inbox/                    # Raw incoming items
├── Needs_Action/             # Items requiring processing
├── Plans/                    # Generated action plans
├── Pending_Approval/         # Awaiting human approval
├── Approved/                 # Approved for execution
├── Done/                     # Completed items
├── Accounting/               # Financial records
├── Logs/                     # Audit logs
├── Dashboard.md              # Real-time status summary
├── Company_Handbook.md       # Rules of engagement
└── Business_Goals.md         # Quarterly objectives
```

## Key Patterns

### 1. Watcher Architecture
Lightweight Python scripts run continuously, monitoring inputs:
```python
# Base pattern for all watchers
class BaseWatcher:
    def check_for_updates() -> list  # Return new items
    def create_action_file(item) -> Path  # Create .md in Needs_Action
    def run()  # Infinite loop with check_interval
```

### 2. Human-in-the-Loop (HITL)
For sensitive actions, Claude creates approval files instead of acting directly:
```
/Vault/Pending_Approval/PAYMENT_Client_A.md
  → Human moves to /Approved/
    → Orchestrator triggers MCP action
      → File moved to /Done/
```

### 3. Ralph Wiggum Loop
A Stop hook pattern that keeps Claude working autonomously until task completion:
- Intercepts Claude's exit attempt
- Checks if task file is in `/Done`
- If not complete, re-injects prompt and continues loop

### 4. Process Management
Watchers need process managers for production reliability:
```bash
# Using PM2 (recommended)
npm install -g pm2
pm2 start gmail_watcher.py --interpreter python3
pm2 save
pm2 startup
```

## Building & Running

### Prerequisites
- **Claude Code**: Active subscription
- **Obsidian**: v1.10.6+
- **Python**: 3.13+
- **Node.js**: v24+ LTS
- **Git**: For vault sync

### Setup Commands
```bash
# Verify installations
claude --version
python --version  # Should be 3.13+
node --version    # Should be v24+

# Create Obsidian vault
mkdir AI_Employee_Vault
cd AI_Employee_Vault
mkdir Inbox Needs_Action Plans Pending_Approval Approved Done Accounting Logs

# Install Playwright browsers
npx playwright install

# Start Playwright MCP server
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh

# Verify server
python .qwen/skills/browsing-with-playwright/scripts/verify.py
```

### MCP Server Configuration
```json
// ~/.config/claude-code/mcp.json
{
  "servers": [
    {
      "name": "browser",
      "command": "npx",
      "args": ["@playwright/mcp@latest", "--port", "8808", "--shared-browser-context"]
    }
  ]
}
```

## Development Tiers

| Tier | Time | Deliverables |
|------|------|--------------|
| **Bronze** | 8-12h | Obsidian vault, 1 watcher, Claude reading/writing |
| **Silver** | 20-30h | 2+ watchers, Plan.md generation, 1 MCP server, HITL workflow |
| **Gold** | 40+h | Full integration, Odoo accounting, social media, weekly briefings |
| **Platinum** | 60+h | Cloud deployment, domain specialization, synced vault |

## Security Guidelines

### Credential Management
- Never store credentials in vault or code
- Use `.env` files (add to `.gitignore`)
- Use secrets manager for banking credentials
- Rotate credentials monthly

### Dry-Run Pattern
```python
DRY_RUN = os.getenv('DRY_RUN', 'true').lower() == 'true'

def send_email(to, subject, body):
    if DRY_RUN:
        logger.info(f'[DRY RUN] Would send email to {to}')
        return
    # Actual send logic
```

### Audit Logging
```json
{
  "timestamp": "2026-01-07T10:30:00Z",
  "action_type": "email_send",
  "actor": "claude_code",
  "target": "client@example.com",
  "approval_status": "approved",
  "approved_by": "human",
  "result": "success"
}
```

## Testing Practices

1. **Start in Dev Mode**: Set `DRY_RUN=true` for all initial testing
2. **Use Sandbox Accounts**: Test Gmail/banking with test accounts
3. **Verify Each Component**:
   - Watchers create files correctly
   - Claude reads and plans appropriately
   - Approval workflow moves files
   - MCP servers execute actions
4. **Run Verification**: `python scripts/verify.py` for Playwright server

## Common Workflows

### Invoice Flow (End-to-End)
1. **Detection**: WhatsApp Watcher finds "invoice" keyword
2. **Action File**: Creates `/Needs_Action/WHATSAPP_client_a.md`
3. **Reasoning**: Claude reads, creates `/Plans/PLAN_invoice_client_a.md`
4. **Approval**: Claude creates `/Pending_Approval/EMAIL_invoice.md`
5. **Human Review**: Move file to `/Approved/`
6. **Execution**: Orchestrator triggers Email MCP
7. **Completion**: Files moved to `/Done/`, Dashboard updated

### CEO Briefing Generation
Scheduled task (weekly) that:
1. Reads `Business_Goals.md` for targets
2. Scans `Tasks/Done` for completed work
3. Analyzes `Bank_Transactions.md` for revenue
4. Generates `/Briefings/YYYY-MM-DD_Monday_Briefing.md`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Claude "command not found" | `npm install -g @anthropic/claude-code`, restart terminal |
| Watchers stop overnight | Use PM2 or supervisord for process management |
| Gmail API 403 | Enable Gmail API in Google Cloud, verify OAuth consent |
| MCP server won't connect | Check process running, verify absolute path in `mcp.json` |
| Playwright verification fails | Run `bash scripts/stop-server.sh && bash scripts/start-server.sh` |

## Learning Resources

- [Claude Code Fundamentals](https://agentfactory.panaversity.org/docs/AI-Tool-Landscape/claude-code-features-and-workflows)
- [MCP Introduction](https://modelcontextprotocol.io/introduction)
- [Playwright Docs](https://playwright.dev/python/docs/intro)
- [Odoo 19 API](https://www.odoo.com/documentation/19.0/developer/reference/external_api.html)

## Project Status

- **Current State**: Initial setup with Playwright MCP skill installed
- **Next Steps**: Create Obsidian vault structure, implement first watcher script
- **Hackathon Meeting**: Wednesdays 10:00 PM PKT on Zoom
