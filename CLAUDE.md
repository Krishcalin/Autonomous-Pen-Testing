# CLAUDE.md — Autonomous Penetration Testing Copilot

## Project Overview

An AI-powered penetration testing agent that connects to a Kali/Parrot attack
box via SSH, runs security tools autonomously, analyses output, plans next steps,
stores credentials for reuse, spawns parallel subagents, sprays credentials across
services, builds MITRE ATT&CK attack graphs, validates findings through a 6-stage
pipeline, scores exploits by risk priority, correlates findings across tools, and
documents findings.

**Repository**: https://github.com/Krishcalin/Autonomous-Pen-Testing
**License**: MIT
**Python**: 3.8+
**Dependencies**: `anthropic` or `openai` + `paramiko`

## File Inventory

| File | Version | Lines | Purpose |
|------|---------|------:|---------|
| `pentest_copilot.py` | 2.4.0 | 5,075 | Complete pentest agent |
| `banner.svg` | — | — | GitHub README banner |
| `README.md` | — | — | Documentation |
| `CLAUDE.md` | — | — | This file |

## Architecture

```
pentest_copilot.py
├── LLM Providers: ClaudeProvider, OpenAIProvider
├── Executors: SSHExecutor (paramiko), LocalExecutor (subprocess)
├── 30 Agent Tools (LLM function-calling)
├── 16 Supporting Systems
├── PentestAgent (core agentic loop, up to 25 iterations/turn)
├── Report Generation (JSON + HTML)
└── CLI (21 slash commands)
```

## 30 Agent Tools — Complete Reference

### Core (7)
| Tool | Handler | Purpose |
|------|---------|---------|
| `run_command` | `handle_run_command` | Execute bash on attack box |
| `run_script` | `handle_run_script` | Write + execute Python scripts |
| `install_tool` | `handle_install_tool` | Install tools (apt/pip/go/git) |
| `read_file` | `handle_read_file` | Read files on attack box |
| `write_file` | `handle_write_file` | Write files on attack box |
| `report_finding` | `handle_report_finding` | Document a vulnerability |
| `ask_user` | `handle_ask_user` | Ask user a question |

### Tier 1 — Parallelism & State (6)
| Tool | Handler | Purpose |
|------|---------|---------|
| `spawn_subagent` | `handle_spawn_subagent` | Background parallel agent |
| `store_credential` | `handle_store_credential` | Store creds in vault |
| `list_credentials` | `handle_list_credentials` | List vault contents |
| `open_shell` | `handle_open_shell` | Open named shell session |
| `run_in_shell` | `handle_run_in_shell` | Run command in named shell |
| `use_playbook` | `handle_use_playbook` | Load methodology playbook |

### Tier 2 — Detection & Exploitation (7)
| Tool | Handler | Purpose |
|------|---------|---------|
| `detect_tools` | `handle_detect_tools` | Check installed tools |
| `search_exploits` | `handle_search_exploits` | SearchSploit CVE lookup |
| `start_listener` | `handle_start_listener` | Start netcat listener |
| `stop_listener` | `handle_stop_listener` | Stop a listener |
| `check_listener` | `handle_check_listener` | Check for connections |
| `generate_payload` | `handle_generate_payload` | Reverse shell payloads |
| `run_phalanx_scanner` | `handle_run_phalanx_scanner` | Run Phalanx Cyber scanner |

### Tier 3 — Methodology & Stealth (3)
| Tool | Handler | Purpose |
|------|---------|---------|
| `set_phase` | `handle_set_phase` | Track pentest phase progress |
| `get_compliance_map` | `handle_get_compliance_map` | OWASP/PTES/NIST mapping |
| `toggle_stealth` | `handle_toggle_stealth` | Rate limiting + IDS evasion |

### Tier 4 — Intelligence & Autonomy (4)
| Tool | Handler | Purpose |
|------|---------|---------|
| `run_recon_pipeline` | `handle_run_recon_pipeline` | Auto-chain recon tools (4 pipelines) |
| `smart_exploit_search` | `handle_smart_exploit_search` | Parse nmap + rank ExploitDB results |
| `credential_spray` | `handle_credential_spray` | Spray vault creds via hydra (14 protocols) |
| `add_attack_step` | `handle_add_attack_step` | Record kill chain step (11 ATT&CK stages) |

### Tier 5 — Validation, Analysis & Correlation (3)
| Tool | Handler | Purpose |
|------|---------|---------|
| `validate_finding` | `handle_validate_finding` | 6-stage validation pipeline (inventory→analysis→sanity→ruling→feasibility→validated) |
| `analyze_exploit` | `handle_analyze_exploit` | Risk scoring: Impact × Exploitability / Detection Time → P1-P4 priority |
| `correlate_findings` | `handle_correlate_findings` | Cross-tool dedup, CVE matching, confidence boosting |

## 16 Supporting Systems

| Class | Section | Purpose |
|-------|---------|---------|
| `CredentialVault` | Credential Vault | Thread-safe cred storage with dedup and reuse hints |
| `ShellManager` | Multi-Shell Manager | Named persistent shell sessions |
| `SubagentManager` | Subagent Manager | Background parallel agent spawning with own LLM context |
| `ToolDetector` | Tool Auto-Detection | Scan attack box for installed tools with caching |
| `ExploitSearcher` | Exploit Search Engine | SearchSploit, nmap vuln scripts, nuclei CVE templates |
| `ReverseShellHandler` | Reverse Shell Handler | Netcat listener management + 7 payload generators |
| `ProgressTracker` | Progress Tracker | 5-phase methodology tracking with per-phase stats |
| `EvidenceCollector` | Evidence Auto-Capture | Auto-capture command outputs as timestamped files |
| `StealthController` | Stealth Mode | Rate limiting, jitter, auto-stealth flags for 9 tools |
| `ReconPipeline` | Autonomous Recon Pipeline | 4 multi-tool auto-chain pipelines |
| `SmartExploitSelector` | Smart Exploit Selection | Nmap output parser + ExploitDB ranker |
| `CredentialSprayEngine` | Credential Spray Engine | Hydra-based 14-protocol credential spraying |
| `AttackGraph` | Attack Graph | 11-stage MITRE ATT&CK kill chain tracker |
| `VulnValidator` | Validation Pipeline | 6-stage finding validation (inventory→validated), false positive elimination |
| `ExploitAnalyzer` | Exploit Analysis | Impact×Exploitability/Detection scoring, P1-P4 priority, 8 modifiers |
| `FindingCorrelator` | Finding Correlation | Cross-tool dedup by host+port+CVE, confidence boosting (50%→80%→95%) |

## Recon Pipelines

| Key | Tools Chained |
|-----|---------------|
| `full` | nmap → whatweb → wafw00f → nikto → ffuf → nuclei |
| `quick` | nmap → whatweb → ffuf |
| `subdomain` | subfinder → httpx |
| `stealth` | nmap (slow SYN) → whatweb |

Defined in `ReconPipeline.PIPELINES` dict. Each entry is a list of `(tool_name, cmd_template)` tuples with `{target}` placeholder.

## Methodology Playbooks

| Key | Name |
|-----|------|
| `webapp` | Web Application Pentest |
| `network` | Network Penetration Test |
| `api` | API Security Assessment |
| `ad` | Active Directory Assessment |
| `cloud` | Cloud Security Assessment |

Defined in `PLAYBOOKS` dict. Each entry has `name` and `prompt` (structured methodology text).

## Attack Graph Stages (MITRE ATT&CK)

```python
KILL_CHAIN_STAGES = [
    ("initial_access",  "Initial Access"),
    ("execution",       "Execution"),
    ("persistence",     "Persistence"),
    ("priv_escalation", "Privilege Escalation"),
    ("defense_evasion", "Defense Evasion"),
    ("cred_access",     "Credential Access"),
    ("discovery",       "Discovery"),
    ("lateral_movement","Lateral Movement"),
    ("collection",      "Collection"),
    ("exfiltration",    "Exfiltration"),
    ("impact",          "Impact"),
]
```

## Credential Spray Protocols

```python
SERVICE_MODULES = {
    "ssh": "ssh", "ftp": "ftp", "http": "http-get", "https": "https-get",
    "smb": "smb", "rdp": "rdp", "mysql": "mysql", "mssql": "mssql",
    "postgres": "postgres", "telnet": "telnet", "vnc": "vnc",
    "smtp": "smtp", "pop3": "pop3", "imap": "imap", "ldap": "ldap",
}
```

## Compliance Mapping Categories

`COMPLIANCE_MAP` covers 14 categories, each mapped to OWASP Top 10, PTES, NIST 800-53, CWE:
SQLi, XSS, RCE, Auth, IDOR, Misconfig, Crypto, SSRF, Deserialization, InfoDisclosure, PrivEsc, DefaultCreds, LFI, BruteForce.

## Phalanx Cyber Scanners

`PHALANX_SCANNERS` registers 9 scanners: `sast_java`, `sast_python`, `sast_mern`, `sast_php`, `owasp_llm`, `api_security`, `aws_cloud`, `nuclei_templates`. Auto-clones from GitHub if not present.

## LLM Tool Schema

All 27 tools use the Claude `input_schema` format in `AGENT_TOOLS_SCHEMA`. For OpenAI, auto-converted to `function.parameters` format by `_openai_tools()`.

## Agentic Loop

```
user_message → inject subagent results → build_system_prompt(13 systems)
  → LLM.call() → text | tool_use
                    ↓         ↓
               print     stealth.wait() → execute handler → evidence.capture()
                              → feed result → loop (up to 25 iterations)
```

The system prompt dynamically injects context from all 16 supporting systems:
credential vault, shells, subagents, listeners, tool status, progress, stealth,
attack graph, validation pipeline, exploit analysis, finding correlation, findings.

## Safety Controls

- `DANGEROUS_PATTERNS` — 13 regex patterns for destructive commands
- `is_dangerous()` → `request_approval()` user prompt
- `--auto-approve` flag bypasses approval
- `truncate_output()` caps tool output at 15K chars
- `MAX_HISTORY_MESSAGES = 60` for conversation trimming
- Stealth mode auto-applies evasion flags to 9 tools

## CLI

```
python pentest_copilot.py --target TARGET (--local | --ssh-host HOST)
    [--ssh-port PORT] [--ssh-user USER] [--ssh-key KEY] [--ssh-password PASS]
    [--provider {claude,openai}] [--model MODEL] [--api-key KEY] [--base-url URL]
    [--auto-approve] [--stealth] [--stealth-delay SEC]
    [--max-iterations N] [--load-session FILE] [--version]
```

21 slash commands: `/help`, `/target`, `/scope`, `/tools`, `/findings`, `/creds`,
`/shells`, `/subagents`, `/playbooks`, `/listeners`, `/phalanx`, `/detect`,
`/progress`, `/evidence`, `/stealth`, `/attack`, `/history`, `/save`, `/report`,
`/clear`, `/quit`

## Session Export Format

JSON session includes: `session_id`, `target`, `scope`, `objective`, `findings[]`,
`credentials[]`, `attack_graph[]`, `command_history[]`, `total_iterations`, `message_count`.

## Development Guidelines

### Adding a New Agent Tool
1. Add tool schema dict to `AGENT_TOOLS_SCHEMA`
2. Create `handle_<tool_name>()` function in Tool Handlers section
3. Add dispatch case in `PentestAgent._handle_tool()`
4. If stateful, add context to `build_system_prompt()`
5. Optionally add a `/command` in CLI section

### Adding a New Recon Pipeline
1. Add entry to `ReconPipeline.PIPELINES` dict
2. Update the `run_recon_pipeline` tool's enum list

### Adding a New Playbook
1. Add entry to `PLAYBOOKS` dict (key, name, prompt)
2. Update the `use_playbook` tool's enum list

### Adding a New Phalanx Scanner
1. Add entry to `PHALANX_SCANNERS` dict
2. Include `command` (with `{target}` placeholder), `repo`, `file`, `description`

### Adding a New Kill Chain Stage
1. Add tuple to `KILL_CHAIN_STAGES` list
2. Update the `add_attack_step` tool's enum list

### Conventions
- Single-file architecture — entire agent in one `.py` file
- `__slots__` on Finding class for memory efficiency
- ANSI colour codes for terminal output (R, B, DIM, RED, GRN, YEL, BLU, MAG, CYN, WHT)
- HTML reports use Catppuccin Mocha dark theme
- Thread-safe classes use `threading.Lock()`
- Exit code 1 on CRITICAL/HIGH findings for CI/CD gating
- Tool output truncated at 15K chars via `truncate_output()`

## Version History

| Version | Lines | Tools | Commands | Milestone |
|---------|------:|:-----:|:--------:|-----------|
| v1.0.0 | 1,656 | 7 | 10 | Core agent, SSH/local, Claude/OpenAI |
| v2.0.0 | 2,468 | 13 | 14 | Subagents, vault, multi-shell, playbooks |
| v2.1.0 | 3,095 | 20 | 17 | Tool detection, exploits, revshell, Phalanx |
| v2.2.0 | 3,681 | 23 | 20 | Progress, compliance, evidence, stealth |
| v2.3.0 | 4,365 | 27 | 21 | Recon pipeline, exploit selector, cred spray, attack graph |
| v2.4.0 | 5,075 | 30 | 21 | Vulnerability validation pipeline, exploit analysis engine, finding correlation |
