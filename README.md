# Autonomous Penetration Testing Copilot

<p align="center">
  <img src="banner.svg" alt="Autonomous Pentest Copilot" width="100%">
</p>

An open-source, AI-powered penetration testing agent that connects to an attack box (Kali/Parrot) via SSH, autonomously runs security tools, analyses output, plans next steps, documents findings, and generates reports — all driven by an LLM agentic loop.

## Overview

| | |
|---|---|
| **Scanner** | `pentest_copilot.py` |
| **Version** | 1.0.0 |
| **Lines** | ~1,656 |
| **Python** | 3.8+ |
| **Dependencies** | `anthropic` or `openai` + `paramiko` |
| **License** | MIT |

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

# Use OpenAI GPT-4o
export OPENAI_API_KEY=sk-...
python pentest_copilot.py --target 10.0.0.1 --local \
    --provider openai --model gpt-4o

# Use any OpenAI-compatible endpoint (Ollama, vLLM, etc.)
python pentest_copilot.py --target 10.0.0.1 --local \
    --provider openai --model llama3 \
    --base-url http://localhost:11434/v1
```

## Features

### AI Agent Loop
- **Agentic execution** — the AI runs commands, reads output, decides next steps, and iterates autonomously (up to 25 iterations per turn)
- **Multi-provider** — supports Claude (Anthropic), OpenAI, and any OpenAI-compatible endpoint (Ollama, vLLM, LM Studio)
- **Tool calling** — native function calling with 7 agent tools
- **Context management** — automatic conversation history trimming to stay within token limits

### 7 Agent Tools

| Tool | Description |
|------|-------------|
| `run_command` | Execute any bash command on the attack box (nmap, sqlmap, etc.) |
| `run_script` | Write and execute Python scripts for custom exploits |
| `install_tool` | Install security tools on demand (apt, pip, go, git) |
| `read_file` | Read files — scan results, configs, exploit output |
| `write_file` | Write files — wordlists, exploit scripts, configs |
| `report_finding` | Document a confirmed vulnerability with severity, evidence, and remediation |
| `ask_user` | Ask the user for clarification, approval, or additional info |

### 60+ Pentest Tool Registry

Organized across 7 categories:

| Category | Tools |
|----------|-------|
| **Reconnaissance** | nmap, masscan, subfinder, httpx, whatweb, amass, theHarvester, dnsrecon, wafw00f |
| **Web Application** | nikto, ffuf, gobuster, dirsearch, nuclei, katana, wpscan, sqlmap, dalfox, feroxbuster |
| **Exploitation** | metasploit, searchsploit, ghauri, commix, hydra, medusa, john, hashcat, crackmapexec, impacket |
| **Post-Exploitation** | linpeas, winpeas, pspy, chisel, ligolo-ng, bloodhound, mimikatz, evil-winrm |
| **Network & Wireless** | netcat, socat, tcpdump, wireshark, responder, bettercap, aircrack-ng |
| **OSINT** | sherlock, recon-ng, spiderfoot, waybackurls, gau, photon |
| **Utilities** | curl, wget, jq, python3, git, gcc, proxychains |

### Safety Controls
- **Dangerous command detection** — regex-based detection of destructive commands (rm -rf /, mkfs, dd, fork bombs, etc.)
- **User approval required** — dangerous commands prompt for explicit approval before execution
- **Auto-approve mode** — `--auto-approve` flag for CI/CD pipelines (use with extreme caution)
- **Scope enforcement** — agent system prompt restricts testing to defined scope

### Execution Modes

| Mode | Flag | Description |
|------|------|-------------|
| **SSH** | `--ssh-host` | Connect to a remote attack box via SSH (Kali, Parrot, etc.) |
| **Local** | `--local` | Execute commands directly on the local machine |

### Session Management
- **Save sessions** — `/save` exports session state, findings, and command history to JSON
- **Load sessions** — `--load-session` resumes from a previous session's findings
- **Command history** — `/history` shows all commands executed during the session

### Report Generation
- **JSON report** — structured findings with severity, category, evidence, CVSS, remediation
- **HTML report** — self-contained dark-themed report with severity badges and filterable findings (Catppuccin Mocha theme)

## CLI Reference

```
usage: pentest_copilot [-h] --target TARGET [--scope SCOPE] [--objective OBJ]
                       (--local | --ssh-host HOST) [--ssh-port PORT]
                       [--ssh-user USER] [--ssh-key KEY] [--ssh-password PASS]
                       [--provider {claude,openai}] [--model MODEL]
                       [--api-key KEY] [--base-url URL]
                       [--auto-approve] [--max-iterations N]
                       [--load-session FILE] [--version]
```

### Interactive Commands

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/target [new]` | Show or change the target |
| `/scope [new]` | Show or change the scope |
| `/tools` | List all available pentest tools |
| `/findings` | Show discovered findings |
| `/history` | Show command execution history |
| `/save [file]` | Save session to JSON |
| `/report [base]` | Generate JSON + HTML pentest report |
| `/clear` | Clear conversation history |
| `/quit` | Exit the copilot |

## Architecture

```
pentest_copilot.py
│
├── LLM Providers
│     ├── ClaudeProvider      — Anthropic Claude with tool calling
│     └── OpenAIProvider      — OpenAI / compatible endpoints
│
├── Execution Engines
│     ├── SSHExecutor         — paramiko SSH to remote attack box
│     └── LocalExecutor       — subprocess on local machine
│
├── Agent Tools (7)
│     ├── run_command          — bash execution
│     ├── run_script           — Python script execution
│     ├── install_tool         — tool installation
│     ├── read_file / write_file — file I/O
│     ├── report_finding       — vulnerability documentation
│     └── ask_user             — user interaction
│
├── Safety Controls
│     ├── Dangerous command regex patterns
│     ├── User approval prompts
│     └── Output truncation (15K char limit)
│
├── PentestAgent (core loop)
│     ├── build_system_prompt() — context + methodology + tools
│     ├── run_turn()            — agentic loop (up to 25 iterations)
│     └── Session save/load
│
├── Report Generation
│     ├── JSON report
│     └── HTML report (Catppuccin Mocha)
│
└── CLI Interface
      ├── Interactive chat loop
      ├── 10 slash commands
      └── Colored terminal output
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | API key for Claude |
| `OPENAI_API_KEY` | API key for OpenAI |
| `DEBUG` | Set to any value to show full tracebacks |

## Pentest Methodology

The agent follows a structured methodology:

1. **Reconnaissance** — Port scanning, service detection, technology fingerprinting
2. **Vulnerability Analysis** — Misconfiguration checks, CVE lookups, injection testing
3. **Exploitation** — Attempt confirmed vulnerabilities with appropriate tools
4. **Post-Exploitation** — Privilege escalation, lateral movement, data extraction
5. **Reporting** — Document every finding with evidence and remediation

## Example Session

```
You: Scan 10.0.0.1 for open ports and services

[Agent] I'll start with a comprehensive Nmap scan.

  [TOOL] run_command: nmap -sV -sC -O -A -p- 10.0.0.1
  [EXEC] Running on root@kali.local...
  PORT     STATE SERVICE VERSION
  22/tcp   open  ssh     OpenSSH 8.2p1
  80/tcp   open  http    Apache httpd 2.4.41
  3306/tcp open  mysql   MySQL 5.7.33
  [OK in 45.2s]

[Agent] Found 3 open ports. Let me check the web server for vulnerabilities.

  [TOOL] run_command: nikto -h http://10.0.0.1
  ...

  [FINDING] [HIGH] SQL Injection in login form
  Category: SQLi | ID: a1b2c3d4
```

## Related Projects

| Project | Description |
|---------|-------------|
| [Static-Application-Security-Testing](https://github.com/Krishcalin/Static-Application-Security-Testing) | SAST scanners (Java, PHP, Python, MERN, LLM) |
| [Dynamic-Application-Security-Testing](https://github.com/Krishcalin/Dynamic-Application-Security-Testing) | DAST scanner with 58 checks |
| [Windows-Red-Teaming](https://github.com/Krishcalin/Windows-Red-Teaming) | Windows ATT&CK red teaming framework |
| [Detection-Engineering](https://github.com/Krishcalin/Detection-Engineering) | SIEM detection rules |

## License

MIT License — see [LICENSE](LICENSE) for details.
