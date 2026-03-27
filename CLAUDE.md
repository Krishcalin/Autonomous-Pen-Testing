# CLAUDE.md — Autonomous Penetration Testing Copilot

## Project Overview

An AI-powered penetration testing agent that connects to a Kali/Parrot attack
box via SSH, runs security tools autonomously, analyses output, plans next steps,
stores credentials for reuse, spawns parallel subagents, and documents findings.

**Repository**: https://github.com/Krishcalin/Autonomous-Pen-Testing
**License**: MIT
**Python**: 3.8+
**Dependencies**: `anthropic` or `openai` + `paramiko`

## File Inventory

| File | Version | Lines | Purpose |
|------|---------|------:|---------|
| `pentest_copilot.py` | 2.2.0 | 3,681 | Complete pentest agent |
| `banner.svg` | — | — | GitHub README banner |
| `README.md` | — | — | Documentation |
| `CLAUDE.md` | — | — | This file |

## Architecture

```
pentest_copilot.py
├── LLM Providers: ClaudeProvider, OpenAIProvider
├── Executors: SSHExecutor (paramiko), LocalExecutor (subprocess)
├── 23 Agent Tools (LLM function-calling)
├── 9 Supporting Systems (vault, shells, subagents, etc.)
├── PentestAgent (core agentic loop)
├── Report Generation (JSON + HTML)
└── CLI (20 slash commands)
```

## 23 Agent Tools

### Core (7)
| Tool | Handler Function | Purpose |
|------|-----------------|---------|
| `run_command` | `handle_run_command` | Execute bash on attack box |
| `run_script` | `handle_run_script` | Write + execute Python scripts |
| `install_tool` | `handle_install_tool` | Install tools (apt/pip/go/git) |
| `read_file` | `handle_read_file` | Read files on attack box |
| `write_file` | `handle_write_file` | Write files on attack box |
| `report_finding` | `handle_report_finding` | Document a vulnerability |
| `ask_user` | `handle_ask_user` | Ask user a question |

### Tier 1 — Parallelism & State (6)
| Tool | Handler Function | Purpose |
|------|-----------------|---------|
| `spawn_subagent` | `handle_spawn_subagent` | Background parallel agent |
| `store_credential` | `handle_store_credential` | Store creds in vault |
| `list_credentials` | `handle_list_credentials` | List vault contents |
| `open_shell` | `handle_open_shell` | Open named shell session |
| `run_in_shell` | `handle_run_in_shell` | Run command in named shell |
| `use_playbook` | `handle_use_playbook` | Load methodology playbook |

### Tier 2 — Detection & Exploitation (7)
| Tool | Handler Function | Purpose |
|------|-----------------|---------|
| `detect_tools` | `handle_detect_tools` | Check installed tools |
| `search_exploits` | `handle_search_exploits` | SearchSploit CVE lookup |
| `start_listener` | `handle_start_listener` | Start netcat listener |
| `stop_listener` | `handle_stop_listener` | Stop a listener |
| `check_listener` | `handle_check_listener` | Check for connections |
| `generate_payload` | `handle_generate_payload` | Reverse shell payloads |
| `run_phalanx_scanner` | `handle_run_phalanx_scanner` | Run Phalanx Cyber scanner |

### Tier 3 — Methodology & Stealth (3)
| Tool | Handler Function | Purpose |
|------|-----------------|---------|
| `set_phase` | `handle_set_phase` | Track pentest phase progress |
| `get_compliance_map` | `handle_get_compliance_map` | OWASP/PTES/NIST mapping |
| `toggle_stealth` | `handle_toggle_stealth` | Rate limiting + IDS evasion |

## Supporting Systems (9 classes)

| Class | Purpose |
|-------|---------|
| `CredentialVault` | Thread-safe credential storage with dedup and reuse hints |
| `ShellManager` | Named persistent shell sessions |
| `SubagentManager` | Background parallel agent spawning with own LLM context |
| `ToolDetector` | Scan attack box for installed tools with caching |
| `ExploitSearcher` | SearchSploit, nmap vuln scripts, nuclei CVE templates |
| `ReverseShellHandler` | Netcat listener management + 7 payload generators |
| `ProgressTracker` | 5-phase methodology tracking with command/finding counts |
| `EvidenceCollector` | Auto-capture command outputs as timestamped evidence files |
| `StealthController` | Rate limiting, jitter, auto-stealth flags for 9 tools |

## 5 Methodology Playbooks

| Key | Name | Focus |
|-----|------|-------|
| `webapp` | Web Application Pentest | Recon, content discovery, vuln scan, exploit, report |
| `network` | Network Penetration Test | Host discovery, service enum, vuln assessment, post-exploit |
| `api` | API Security Assessment | API discovery, auth testing, input validation, business logic |
| `ad` | Active Directory Assessment | LDAP/Kerberos/SMB enum, credential attacks, lateral movement |
| `cloud` | Cloud Security Assessment | Cloud recon, IAM, services, data exfiltration |

## LLM Tool Schema

All 23 tools use the Claude `input_schema` format. For OpenAI, they are auto-converted
to `function.parameters` format by `_openai_tools()`.

Tool definitions are in `AGENT_TOOLS_SCHEMA` (list of dicts).

## Agentic Loop

```
user_message → build_system_prompt() → LLM.call()
                                         ↓
                              text response  OR  tool_use
                                   ↓                ↓
                              print & done    execute handler → feed result → loop
                                                                   (up to 25 iterations)
```

- Subagent results from `SubagentManager.get_completed_results()` are auto-injected
  into the user message before each LLM call.
- The system prompt includes dynamic context: credential vault, shell list, subagent
  status, listener status, tool detection summary, progress tracker, stealth mode.

## Safety Controls

- `DANGEROUS_PATTERNS` — 13 regex patterns for destructive commands
- `is_dangerous()` → `request_approval()` user prompt
- `--auto-approve` flag bypasses approval (CI/CD use)
- `truncate_output()` caps tool output at 15K chars
- `MAX_HISTORY_MESSAGES = 60` for conversation trimming

## Compliance Mapping

`COMPLIANCE_MAP` dict covers 14 categories, each mapping to:
- **OWASP**: Top 10 2021 categories
- **PTES**: Penetration Testing Execution Standard sections
- **NIST**: 800-53 control families
- **CWE**: Common Weakness Enumeration IDs

## Phalanx Cyber Scanners

`PHALANX_SCANNERS` dict registers 9 scanners:
- `sast_java`, `sast_python`, `sast_mern`, `sast_php` — Static analysis
- `owasp_llm` — AI/LLM security
- `api_security` — OWASP API Top 10
- `aws_cloud` — CloudFormation + Terraform
- `nuclei_templates` — CVE template scanning

Each entry includes `command`, `repo` (GitHub URL for auto-clone), `file`, `description`.

## CLI

```
python pentest_copilot.py --target TARGET (--local | --ssh-host HOST)
    [--ssh-port PORT] [--ssh-user USER] [--ssh-key KEY] [--ssh-password PASS]
    [--provider {claude,openai}] [--model MODEL] [--api-key KEY] [--base-url URL]
    [--auto-approve] [--stealth] [--stealth-delay SEC]
    [--max-iterations N] [--load-session FILE] [--version]
```

20 slash commands: `/help`, `/target`, `/scope`, `/tools`, `/findings`, `/creds`,
`/shells`, `/subagents`, `/playbooks`, `/listeners`, `/phalanx`, `/detect`,
`/progress`, `/evidence`, `/stealth`, `/history`, `/save`, `/report`, `/clear`, `/quit`

## Development Guidelines

### Adding a New Agent Tool
1. Add the tool schema dict to `AGENT_TOOLS_SCHEMA` list
2. Create a `handle_<tool_name>()` function in the Tool Handlers section
3. Add the dispatch case in `PentestAgent._handle_tool()`
4. If it has state, add context to `build_system_prompt()`
5. Optionally add a `/command` in the CLI section

### Adding a New Playbook
1. Add entry to the `PLAYBOOKS` dict (key, name, prompt)
2. The `use_playbook` tool will automatically pick it up

### Adding a New Phalanx Scanner
1. Add entry to `PHALANX_SCANNERS` dict
2. Include `command` (with `{target}` placeholder), `repo`, `file`, `description`

### Conventions
- Single-file architecture — entire agent in one `.py` file
- `__slots__` on Finding class for memory efficiency
- ANSI colour codes for terminal output
- HTML reports use Catppuccin Mocha dark theme
- Thread-safe classes use `threading.Lock()`
- Exit code 1 on CRITICAL/HIGH findings for CI/CD gating

## Version History

| Version | Lines | Tools | Commands | Milestone |
|---------|------:|:-----:|:--------:|-----------|
| v1.0.0 | 1,656 | 7 | 10 | Core agent, SSH/local, Claude/OpenAI |
| v2.0.0 | 2,468 | 13 | 14 | Subagents, vault, multi-shell, playbooks |
| v2.1.0 | 3,095 | 20 | 17 | Tool detection, exploits, revshell, Phalanx |
| v2.2.0 | 3,681 | 23 | 20 | Progress, compliance, evidence, stealth |

## Related Projects

| Project | Repo |
|---------|------|
| SAST Scanners | [Static-Application-Security-Testing](https://github.com/Krishcalin/Static-Application-Security-Testing) |
| DAST Scanner | [Dynamic-Application-Security-Testing](https://github.com/Krishcalin/Dynamic-Application-Security-Testing) |
| API Security | [API-Security](https://github.com/Krishcalin/API-Security) |
| AWS Security | [AWS-Security-Scanner](https://github.com/Krishcalin/AWS-Security-Scanner) |
| Windows Red Teaming | [Windows-Red-Teaming](https://github.com/Krishcalin/Windows-Red-Teaming) |
| Oracle EBS Audit | [Oracle-EBS-Security-Audit](https://github.com/Krishcalin/Oracle-EBS-Security-Audit) |
| Phalanx Cyber Portal | [My-Portal](https://github.com/Krishcalin/My-Portal) |
