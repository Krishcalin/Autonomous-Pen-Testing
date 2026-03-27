# Autonomous Penetration Testing Copilot

<p align="center">
  <img src="banner.svg" alt="Autonomous Pentest Copilot" width="100%">
</p>

<p align="center">
  <strong>AI-powered pentest agent with LLM agentic loop, subagent parallelism, credential vault, and stealth mode</strong><br>
  23 agent tools &bull; 60+ pentest tools &bull; 5 methodology playbooks &bull; 20 CLI commands &bull; 3,681 lines of Python
</p>

---

## Overview

A single-file Python agent that connects to a Kali/Parrot attack box via SSH (or runs locally), autonomously executes security tools, analyses output, plans next steps, stores credentials for reuse, spawns parallel subagents, and documents findings — all driven by an LLM agentic loop with Claude or OpenAI.

| | |
|---|---|
| **File** | `pentest_copilot.py` |
| **Version** | 2.2.0 |
| **Lines** | ~3,681 |
| **Agent Tools** | 23 |
| **CLI Commands** | 20 |
| **Pentest Tools** | 60+ in registry |
| **Playbooks** | 5 (webapp, network, api, ad, cloud) |
| **Python** | 3.8+ |
| **Dependencies** | `anthropic` or `openai` + `paramiko` |
| **License** | MIT |

---

## Quick Start

```bash
# Install dependencies
pip install anthropic paramiko        # Claude (recommended)
pip install openai paramiko           # OpenAI alternative

# SSH to a remote Kali attack box
export ANTHROPIC_API_KEY=sk-ant-...
python pentest_copilot.py --target 10.0.0.1 \
    --ssh-host kali.local --ssh-user root --ssh-key ~/.ssh/id_rsa

# Run locally on a Kali/Parrot machine
python pentest_copilot.py --target 10.0.0.1 --local

# Stealth mode (rate limiting + IDS evasion flags)
python pentest_copilot.py --target 10.0.0.1 --local --stealth

# Use OpenAI GPT-4o
export OPENAI_API_KEY=sk-...
python pentest_copilot.py --target 10.0.0.1 --local \
    --provider openai --model gpt-4o

# Use any OpenAI-compatible endpoint (Ollama, vLLM, etc.)
python pentest_copilot.py --target 10.0.0.1 --local \
    --provider openai --model llama3 \
    --base-url http://localhost:11434/v1
```

---

## 23 Agent Tools

### Core (7)

| Tool | Description |
|------|-------------|
| `run_command` | Execute any bash command on the attack box |
| `run_script` | Write and execute Python scripts for custom exploits |
| `install_tool` | Install security tools on demand (apt, pip, go, git) |
| `read_file` | Read scan results, configs, exploit output |
| `write_file` | Create wordlists, exploit scripts, configs |
| `report_finding` | Document a vulnerability with severity, evidence, CVSS |
| `ask_user` | Ask for clarification, approval, or additional info |

### Tier 1 — Parallelism & State (6)

| Tool | Description |
|------|-------------|
| `spawn_subagent` | Spawn background agents for concurrent tasks (dir brute-force + subdomain enum simultaneously) |
| `store_credential` | Store discovered credentials (password, hash, token, key, cookie) for reuse |
| `list_credentials` | List all credentials in the vault for cross-service reuse |
| `open_shell` | Open a named persistent shell session (recon, exploit, listener) |
| `run_in_shell` | Run a command in a specific named shell |
| `use_playbook` | Load a methodology playbook (webapp, network, api, ad, cloud) |

### Tier 2 — Detection & Exploitation (7)

| Tool | Description |
|------|-------------|
| `detect_tools` | Scan attack box for installed vs missing pentest tools |
| `search_exploits` | Search ExploitDB/searchsploit for CVEs by service version |
| `start_listener` | Start a netcat reverse shell listener |
| `stop_listener` | Stop a running listener |
| `check_listener` | Check if a listener caught a reverse shell connection |
| `generate_payload` | Generate reverse shell payloads (bash, python, nc, php, perl, powershell) |
| `run_phalanx_scanner` | Run a Phalanx Cyber scanner (SAST, API, Cloud, Nuclei CVE) |

### Tier 3 — Methodology & Stealth (3)

| Tool | Description |
|------|-------------|
| `set_phase` | Track pentest progress across 5 methodology phases |
| `get_compliance_map` | Get OWASP Top 10, PTES, NIST 800-53, CWE mappings for a finding category |
| `toggle_stealth` | Enable/disable rate limiting and IDS evasion flags |

---

## 5 Methodology Playbooks

| Playbook | Name | Phases |
|----------|------|--------|
| `webapp` | Web Application Pentest | Recon, Content Discovery, Vuln Scanning, Exploitation, Report |
| `network` | Network Penetration Test | Host Discovery, Service Enum, Vuln Assessment, Exploitation, Post-Exploit |
| `api` | API Security Assessment | API Discovery, Auth Testing, Input Validation, Business Logic, Report |
| `ad` | Active Directory Assessment | AD Recon, Credential Attacks, Lateral Movement, Priv Esc, Domain Dominance |
| `cloud` | Cloud Security Assessment | Cloud Recon, IAM, Services, Data Exfiltration, Report |

---

## 60+ Pentest Tool Registry

| Category | Tools |
|----------|-------|
| **Reconnaissance** | nmap, masscan, subfinder, httpx, whatweb, amass, theHarvester, dnsrecon, wafw00f, whois |
| **Web Application** | nikto, ffuf, gobuster, dirsearch, nuclei, katana, wpscan, sqlmap, dalfox, feroxbuster |
| **Exploitation** | metasploit, searchsploit, ghauri, commix, hydra, medusa, john, hashcat, crackmapexec, impacket |
| **Post-Exploitation** | linpeas, winpeas, pspy, chisel, ligolo-ng, bloodhound, mimikatz, evil-winrm |
| **Network & Wireless** | netcat, socat, tcpdump, wireshark, responder, bettercap, aircrack-ng |
| **OSINT** | sherlock, recon-ng, spiderfoot, waybackurls, gau, photon |
| **Utilities** | curl, wget, jq, python3, git, gcc, proxychains |

---

## Key Features

### Subagent Parallelism
Spawn background agents for concurrent tasks. Each subagent gets its own LLM conversation and tool access. Results auto-injected into the main agent's context.

### Credential Vault
Thread-safe credential storage with deduplication. Supports password, hash, token, key, cookie types. Auto-injected into system prompt so the agent knows what creds are available for cross-service reuse.

### Multi-Shell Management
Named persistent shell sessions for context separation — `recon` for scanning, `exploit` for exploitation, `listener` for catching reverse shells.

### Reverse Shell Handler
Built-in netcat listener management (start/stop/check) + 7 reverse shell payload generators (bash, python, nc, mkfifo, php, perl, powershell).

### Exploit Search
SearchSploit (ExploitDB) wrapper for CVE lookup after service version discovery. Also supports nmap NSE vuln scripts and nuclei CVE templates.

### Tool Auto-Detection
Scans the attack box for installed vs missing tools with caching. Knows what's available before the agent tries to use it.

### Phalanx Cyber Integration
9 specialized scanners from the Phalanx Cyber collection — Java/Python/MERN/PHP SAST, OWASP LLM Top 10, API Security, AWS Cloud, and Nuclei CVE. Auto-clones repos from GitHub if not present.

### Progress Tracker
Visual phase tracking across 5 methodology phases with command/finding counts per phase.

### Compliance Mapping
14-category mapping table covering OWASP Top 10 2021, PTES, NIST 800-53, and CWE identifiers.

### Evidence Auto-Capture
Every `run_command` output auto-saved as timestamped evidence files on the attack box.

### Stealth Mode
Rate limiting with configurable delay + random jitter. Auto-applies stealth flags to 9 tools (nmap `-sS -T2 -f`, sqlmap `--delay --random-agent`, ffuf `-rate 10`, etc.).

### Safety Controls
Regex-based dangerous command detection. User approval prompts for destructive operations. Auto-approve mode for CI/CD. Output truncation (15K chars).

---

## 20 CLI Commands

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/target [new]` | Show or change the target |
| `/scope [new]` | Show or change the scope |
| `/tools` | List all 60+ pentest tools |
| `/findings` | Show discovered findings |
| `/creds` | Show credential vault |
| `/shells` | Show active named shells |
| `/subagents` | Show background subagent status |
| `/playbooks` | List methodology playbooks |
| `/listeners` | Show active reverse shell listeners |
| `/phalanx` | List Phalanx Cyber scanners |
| `/detect` | Scan attack box for installed tools |
| `/progress` | Show pentest phase progress |
| `/evidence` | Show evidence capture summary |
| `/stealth` | Toggle stealth mode on/off |
| `/history` | Show command execution history |
| `/save [file]` | Save session to JSON |
| `/report [base]` | Generate JSON + HTML pentest report |
| `/clear` | Clear conversation history |
| `/quit` | Exit the copilot |

---

## CLI Reference

```
usage: pentest_copilot [-h] --target TARGET [--scope SCOPE] [--objective OBJ]
                       (--local | --ssh-host HOST) [--ssh-port PORT]
                       [--ssh-user USER] [--ssh-key KEY] [--ssh-password PASS]
                       [--provider {claude,openai}] [--model MODEL]
                       [--api-key KEY] [--base-url URL]
                       [--auto-approve] [--stealth] [--stealth-delay SEC]
                       [--max-iterations N] [--load-session FILE] [--version]
```

---

## Architecture

```
pentest_copilot.py  (3,681 lines)
│
├── LLM Providers
│     ├── ClaudeProvider           — Anthropic Claude with tool calling
│     └── OpenAIProvider           — OpenAI / Ollama / vLLM compatible
│
├── Execution Engines
│     ├── SSHExecutor              — paramiko SSH to remote attack box
│     └── LocalExecutor            — subprocess on local machine
│
├── Agent Tools (23)
│     ├── Core (7)                 — run_command, run_script, install_tool,
│     │                              read/write_file, report_finding, ask_user
│     ├── Parallelism (3)          — spawn_subagent, open_shell, run_in_shell
│     ├── Credential Vault (2)     — store_credential, list_credentials
│     ├── Methodology (1)          — use_playbook
│     ├── Detection (3)            — detect_tools, search_exploits, run_phalanx
│     ├── Reverse Shell (4)        — start/stop/check_listener, generate_payload
│     └── Tracking & Stealth (3)   — set_phase, get_compliance_map, toggle_stealth
│
├── Supporting Systems
│     ├── CredentialVault          — thread-safe cred storage + reuse hints
│     ├── ShellManager             — named persistent shell sessions
│     ├── SubagentManager          — background parallel agent spawning
│     ├── ToolDetector             — installed tool scanning + caching
│     ├── ExploitSearcher          — searchsploit / nuclei CVE lookup
│     ├── ReverseShellHandler      — netcat listener + payload generation
│     ├── ProgressTracker          — 5-phase methodology tracking
│     ├── EvidenceCollector        — auto-capture command outputs
│     └── StealthController        — rate limiting + IDS evasion flags
│
├── PentestAgent (core loop)
│     ├── build_system_prompt()    — full context injection
│     ├── run_turn()               — agentic loop (up to 25 iterations)
│     └── Session save/load
│
├── Report Generation
│     ├── JSON report
│     └── HTML report (Catppuccin Mocha)
│
└── CLI Interface
      ├── Interactive chat loop
      ├── 20 slash commands
      └── Colored terminal output
```

---

## Version History

| Version | Lines | Agent Tools | CLI Commands | Key Features |
|---------|------:|:-----------:|:------------:|--------------|
| v1.0.0 | 1,656 | 7 | 10 | Core agent, SSH/local, Claude/OpenAI, safety controls |
| v2.0.0 | 2,468 | 13 | 14 | Subagents, credential vault, multi-shell, 5 playbooks |
| v2.1.0 | 3,095 | 20 | 17 | Tool detection, exploit search, reverse shells, Phalanx integration |
| **v2.2.0** | **3,681** | **23** | **20** | **Progress tracker, compliance mapping, evidence capture, stealth mode** |

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | API key for Claude |
| `OPENAI_API_KEY` | API key for OpenAI |
| `DEBUG` | Set to any value to show full tracebacks |

---

## Example Session

```
You: Use the webapp playbook to pentest http://10.0.0.1

[PLAYBOOK] Loaded: Web Application Pentest

[Agent] Starting Phase 1 — Reconnaissance. Let me detect available tools first.

  [TOOL] detect_tools: checking all tools
  Installed (24): nmap, nikto, ffuf, sqlmap, nuclei, ...
  Missing (8): dalfox, feroxbuster, ...

  [TOOL] set_phase: recon
  [+] Recon  -->  [ ] Vuln Analysis  -->  [ ] Exploitation  -->  ...

  [TOOL] run_command: nmap -sV -sC -p- 10.0.0.1
  PORT     STATE SERVICE VERSION
  22/tcp   open  ssh     OpenSSH 8.2p1
  80/tcp   open  http    Apache httpd 2.4.41
  3306/tcp open  mysql   MySQL 5.7.33

  [TOOL] search_exploits: Apache 2.4.41
  ... 3 exploits found ...

  [TOOL] spawn_subagent: Run ffuf directory brute-force on http://10.0.0.1
  [SUBAGENT] Spawned a1b2c3d4: directory brute-force (running in background)

  [TOOL] run_command: sqlmap -u "http://10.0.0.1/login" --batch --dbs
  ...

  [FINDING] [HIGH] SQL Injection in /login
  Category: SQLi | ID: e5f6g7h8

  [TOOL] store_credential: admin:P@ssw0rd123 [password] @ http://10.0.0.1
  [CRED] Stored: admin:P@s*** [password] @ http://10.0.0.1
```

---

## Related Projects

| Project | Description |
|---------|-------------|
| [Static-Application-Security-Testing](https://github.com/Krishcalin/Static-Application-Security-Testing) | SAST scanners (Java, PHP, Python, MERN, LLM) |
| [Dynamic-Application-Security-Testing](https://github.com/Krishcalin/Dynamic-Application-Security-Testing) | DAST scanner with 58 checks |
| [API-Security](https://github.com/Krishcalin/API-Security) | API security scanner, 112+ rules |
| [AWS-Security-Scanner](https://github.com/Krishcalin/AWS-Security-Scanner) | CloudFormation + Terraform IaC scanner |
| [Windows-Red-Teaming](https://github.com/Krishcalin/Windows-Red-Teaming) | Windows ATT&CK red teaming framework |
| [Detection-Engineering](https://github.com/Krishcalin/Detection-Engineering) | SIEM detection rules |
| [Oracle-EBS-Security-Audit](https://github.com/Krishcalin/Oracle-EBS-Security-Audit) | Oracle EBS security audit (live DB + offline CSV) |

---

## License

MIT License — see [LICENSE](LICENSE) for details.
