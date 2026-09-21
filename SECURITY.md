# Security Policy

<div align="center">

**NexTunnel** takes security seriously.

If you believe you've found a security vulnerability, please report it responsibly.

[![Security](https://img.shields.io/badge/security-policy-brightgreen?style=for-the-badge)](SECURITY.md)
[![Responsible Disclosure](https://img.shields.io/badge/disclosure-responsible-blue?style=for-the-badge)](SECURITY.md#-responsible-disclosure)

</div>

---

## 📑 Table of Contents

- [Supported Versions](#-supported-versions)
- [Reporting a Vulnerability](#-reporting-a-vulnerability)
- [Responsible Disclosure](#-responsible-disclosure)
- [What to Include in Your Report](#-what-to-include-in-your-report)
- [What to Expect](#-what-to-expect)
- [Out of Scope](#-out-of-scope)
- [Security Measures Implemented](#-security-measures-implemented)
- [Security Best Practices](#-security-best-practices-for-users)
- [Known Limitations](#-known-limitations)
- [Security Hall of Fame](#-security-hall-of-fame)
- [Additional Resources](#-additional-resources)

---

## 🛡️ Supported Versions

We provide security updates for the following versions:

| Version | Supported | End of Life |
|---------|-----------|-------------|
| **1.0.x** | ✅ Yes | TBD |
| 0.x (alpha) | ❌ No | 2024-12-31 |

**Only the latest stable release receives security patches.**

If you're running an older version, please upgrade to the latest release as soon as possible:

```bash
cd /path/to/nextunnel
git pull
sudo systemctl restart nextunnel
```

> ⚠️ **Note:** The first stable release is `1.0.0`. Pre-1.0 versions were alpha/prototype and are not supported.

---

## 🚨 Reporting a Vulnerability

**⚠️ Please DO NOT open a public GitHub issue for security vulnerabilities.**

Public disclosure before a fix is available puts all NexTunnel users at risk.

### How to Report Privately

Choose one of the following methods:

#### Method 1: GitHub Security Advisories (Preferred)

1. Go to the [Security tab](https://github.com/metiwilson/nextunnel/security) of the repository
2. Click **"Report a vulnerability"**
3. Fill in the advisory form with details
4. Submit — only the maintainer will see it

#### Method 2: Email

Send an email to the maintainer:

- **To:** (see profile on [github.com/metiwilson](https://github.com/metiwilson))
- **Subject:** `[SECURITY] Brief description of the issue`
- **PGP:** Available on request

#### Method 3: GitHub Direct Message

Contact [@metiwilson](https://github.com/metiwilson) directly on GitHub.

---

## 🤝 Responsible Disclosure

We follow the **Coordinated Vulnerability Disclosure** (CVD) model.

### Our Commitments

When you report a vulnerability responsibly, we commit to:

- ✅ **Acknowledge** your report within **72 hours**
- ✅ **Provide an initial assessment** within **7 days**
- ✅ **Keep you informed** of progress throughout the process
- ✅ **Credit you** in the security advisory (unless you prefer to stay anonymous)
- ✅ **Not take legal action** against good-faith research
- ✅ **Work with you** to understand and reproduce the issue

### Your Commitments

By reporting responsibly, you agree to:

- ✅ **Give us reasonable time** to fix the issue before public disclosure (90 days suggested)
- ✅ **Not exploit** the vulnerability beyond what's needed to demonstrate it
- ✅ **Not access, modify, or delete** other users' data
- ✅ **Not disrupt** production services
- ✅ **Communicate openly** with us about your findings

### Disclosure Timeline

Our typical timeline:

| Phase | Duration |
|-------|----------|
| Acknowledge receipt | ≤ 72 hours |
| Initial assessment | ≤ 7 days |
| Develop and test fix | 7-30 days (depends on complexity) |
| Release patched version | ASAP after fix validated |
| Public disclosure | 90 days after initial report, or upon release |
| Credit in advisory | Upon disclosure |

We may extend the timeline for complex issues, but we'll keep you informed.

---

## 📋 What to Include in Your Report

The more detail you provide, the faster we can respond. Please include:

### Required Information

- **Vulnerability type** — e.g., XSS, SQL injection, CSRF, RCE, authentication bypass
- **Affected component** — e.g., login page, tunnel creation, API endpoint, session management
- **Affected version(s)** — e.g., `1.0.0`, `main` branch, or specific commit hash
- **Steps to reproduce** — numbered list, as specific as possible
- **Proof of concept** — code, request, or screenshot demonstrating the issue
- **Impact assessment** — what an attacker could do with this vulnerability
- **Suggested fix** — if you have one (optional but appreciated)

### Optional but Helpful

- **Environment details** — OS, Python version, browser
- **Logs** — relevant excerpts (sanitize any secrets!)
- **Network captures** — for network-related issues
- **Screenshots or videos** — for UI-related issues
- **Your availability** — for follow-up questions

### Report Template

```markdown
## Vulnerability Summary
Brief description of the vulnerability.

## Affected Component
- File/function: `nextunnel.py` → `handle_login()`
- Endpoint: `/api/login`
- Version: 1.0.0

## Vulnerability Type
- [ ] XSS
- [ ] SQL Injection
- [ ] CSRF
- [ ] Authentication bypass
- [ ] Authorization bypass
- [ ] Remote Code Execution
- [ ] Information disclosure
- [ ] Denial of Service
- [ ] Other: __________

## Severity Assessment
- [ ] Critical — Full system compromise
- [ ] High — Significant impact
- [ ] Medium — Limited impact
- [ ] Low — Minimal impact

## Steps to Reproduce
1. ...
2. ...
3. ...

## Proof of Concept
```http
POST /api/login HTTP/1.1
...
```

## Impact
Describe what an attacker could achieve.

## Suggested Fix
If you have an idea for a fix.

## Additional Information
Any other details, screenshots, logs, etc.
```

---

## ⏱️ What to Expect

### Our Response Process

1. **Receipt** — We'll acknowledge your report within 72 hours.
2. **Triage** — We'll assess severity and validity within 7 days.
3. **Investigation** — We'll reproduce the issue and identify root cause.
4. **Fix Development** — We'll develop and test a fix.
5. **Verification** — We may ask you to verify the fix.
6. **Release** — We'll release a patched version.
7. **Disclosure** — We'll publish a security advisory (with your permission to credit you).

### Severity Classification

We use the [CVSS v3.1](https://www.first.org/cvss/) scoring system:

| Severity | Score | Response Time |
|----------|-------|---------------|
| 🔴 **Critical** | 9.0 – 10.0 | 24-48 hours |
| 🟠 **High** | 7.0 – 8.9 | 3-7 days |
| 🟡 **Medium** | 4.0 – 6.9 | 7-14 days |
| 🟢 **Low** | 0.1 – 3.9 | Next release cycle |

### What We Won't Do

- ❌ We will **not** pay bug bounties (this is a free, open-source project)
- ❌ We will **not** take legal action for good-faith research
- ❌ We will **not** publicly disclose before a fix is ready (unless you request it)

### What We Will Do

- ✅ We **will** credit you in the security advisory (unless you prefer anonymity)
- ✅ We **will** list you in our [Security Hall of Fame](#-security-hall-of-fame)
- ✅ We **will** mention your contribution in the `CHANGELOG.md`

---

## 🚫 Out of Scope

The following are **not** considered security vulnerabilities for NexTunnel:

### By Design

- **Plaintext secrets in SQLite** — This is by design; NexTunnel expects you to secure your server (disk encryption, file permissions). Not a vulnerability.
- **No HTTPS by default** — NexTunnel binds to HTTP. HTTPS is the operator's responsibility (use Nginx/Caddy). Not a vulnerability.
- **No 2FA** — Planned for a future release. Not currently a vulnerability.
- **No multi-user isolation** — Currently single-admin. Not a vulnerability.

### Environment-Specific

- **Weak passwords chosen by the user** — Not a vulnerability.
- **Misconfigured firewall** — Not a vulnerability.
- **Compromised server via other means** — Not a NexTunnel vulnerability.
- **Physical access to the server** — Not a vulnerability.
- **Root access already achieved** — Once an attacker has root, all bets are off.

### Third-Party

- **Vulnerabilities in tunnel tools** (GOST, Hysteria2, Rathole, etc.) — Report to the respective projects.
- **Vulnerabilities in Python standard library** — Report to [python.org](https://python.org).
- **Vulnerabilities in SQLite** — Report to [sqlite.org](https://sqlite.org).
- **Vulnerabilities in 3x-ui** — Report to [MHSanaei/3x-ui](https://github.com/MHSanaei/3x-ui).

### Low-Impact

- **Missing security headers that have no real impact** — We implement the important ones.
- **Self-XSS** — XSS that only affects the user typing it themselves.
- **Clickjacking on non-sensitive pages** — We set `X-Frame-Options: DENY` globally.
- **Tabnabbing** — We use `rel="noopener"` where needed.
- **Rate limiting bypass via IPv6 rotation** — Acceptable trade-off.

### Best Practices (Not Vulnerabilities)

- Missing HSTS header (we recommend HTTPS but don't enforce it)
- No Content-Security-Policy header (would break inline styles/scripts)
- No Subresource Integrity (no external resources used)

If you're unsure whether something is in scope, **report it anyway** — we'd rather evaluate it ourselves than have it reported publicly.

---

## 🔒 Security Measures Implemented

NexTunnel implements multiple layers of security. Here's what's in place:

### Authentication

| Feature | Implementation |
|---------|----------------|
| **Password hashing** | PBKDF2-HMAC-SHA256 |
| **Iterations** | 200,000 |
| **Salt** | 16 bytes, cryptographically random |
| **Salt storage** | Per-user, per-password-change |
| **Comparison** | Constant-time (`hmac.compare_digest`) |
| **First-run password** | 16-char URL-safe random (shown once) |
| **Forced change** | On first login only |
| **Min password length** | 8 characters |

### Session Management

| Feature | Implementation |
|---------|----------------|
| **Storage** | Server-side SQLite table |
| **Cookie name** | `nt_session` |
| **Cookie flags** | `HttpOnly`, `SameSite=Lax`, `Path=/` |
| **Token generation** | `secrets.token_urlsafe(48)` (384 bits) |
| **Timeout** | 30 minutes idle (sliding window) |
| **Cleanup** | Expired sessions removed every 60 seconds |
| **Revocation** | Individual + all-at-once from UI |

### Authorization

| Feature | Implementation |
|---------|----------------|
| **CSRF protection** | Per-session token on all `POST`/`PUT`/`DELETE` |
| **Token generation** | `secrets.token_urlsafe(24)` (192 bits) |
| **Comparison** | Constant-time |
| **Session binding** | CSRF tied to session, not global |
| **Ownership checks** | Users can only revoke their own sessions |

### Rate Limiting

| Feature | Implementation |
|---------|----------------|
| **Trigger** | 5 failed login attempts |
| **Duration** | 15-minute lockout |
| **Scope** | Per-IP address |
| **Storage** | `login_attempts` table |
| **Cleanup** | Attempts older than 24h removed |
| **IP source** | `client_address` (no XFF trust) |

### Input Validation

| Feature | Implementation |
|---------|----------------|
| **SQL injection** | Parameterized queries everywhere |
| **XSS prevention** | `textContent` + `esc()` in JS |
| **Path traversal** | `os.path.basename()` on file names |
| **Command injection** | `shell=False` where possible; validated commands |
| **Body size limit** | 1 MB max on JSON bodies |
| **JSON parsing** | Safe `json.loads()` with error handling |
| **Input length** | Username: 3-40 chars, password: 8+ chars |
| **Username format** | `[a-zA-Z0-9_.-]+` enforced |

### HTTP Headers

Every response includes:

```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: same-origin
Cache-Control: no-store
```

### Process Management

| Feature | Implementation |
|---------|----------------|
| **PID tracking** | Per-tunnel PID files in `/opt/nextunnel/pids/` |
| **Graceful shutdown** | `SIGTERM` → wait 1s → `SIGKILL` |
| **Process groups** | Uses `os.killpg()` for correct cleanup |
| **Privilege** | Requires root (by design — manages system services) |
| **Command sanitization** | Generated commands only (no user input in shell) |

### Database

| Feature | Implementation |
|---------|----------------|
| **Journal mode** | WAL (Write-Ahead Logging) |
| **Foreign keys** | Enabled (`PRAGMA foreign_keys=ON`) |
| **Locking** | Thread lock (`_db_lock`) around all writes |
| **Connection timeout** | 15 seconds |
| **Parameterized queries** | 100% of SQL statements |

### Code Quality

| Feature | Implementation |
|---------|----------------|
| **Single file** | Easier to audit (`nextunnel.py`) |
| **No external deps** | Only Python standard library |
| **No eval/exec** | Never used with user input |
| **Safe defaults** | Deny-by-default on auth |
| **Consistent error handling** | Exceptions logged, not leaked |

---

## 🛡️ Security Best Practices for Users

NexTunnel is only as secure as its deployment. Follow these recommendations:

### Essential (Do These First)

1. **🔐 Change the default password immediately** — mandatory on first login
2. **🔒 Use HTTPS** — put NexTunnel behind Nginx or Caddy with a TLS certificate
3. **🔥 Restrict panel access** — firewall port 8088 to your IP or VPN
4. **💾 Enable disk encryption** — secrets are stored plaintext in SQLite
5. **🔄 Keep NexTunnel updated** — `git pull && systemctl restart nextunnel`
6. **📦 Back up regularly** — `/opt/nextunnel/nextunnel.db` is critical

### Recommended

7. **Use a reverse proxy** — never expose port 8088 directly to the internet
8. **Strong passwords** — 16+ characters, mixed case, digits, symbols
9. **Restrict SSH** — disable password auth, use keys only
10. **Monitor logs** — `journalctl -u nextunnel -f` regularly
11. **Set up fail2ban** — for SSH at minimum
12. **Use a firewall** — ufw, firewalld, or iptables
13. **Regular audits** — check active sessions, revoke suspicious ones
14. **Separate server** — don't run NexTunnel on a server with other critical services

### Nginx Reverse Proxy Example

```nginx
server {
    listen 443 ssl http2;
    server_name panel.example.com;

    ssl_certificate     /etc/letsencrypt/live/panel.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/panel.example.com/privkey.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;

    # Add authentication as an extra layer
    # auth_basic "Restricted";
    # auth_basic_user_file /etc/nginx/.htpasswd;

    location / {
        proxy_pass http://127.0.0.1:8088;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Firewall Configuration

**UFW (Ubuntu/Debian):**

```bash
# Restrict to your IP only
sudo ufw allow from YOUR_IP to any port 8088
sudo ufw enable
```

**firewalld (CentOS/RHEL):**

```bash
sudo firewall-cmd --permanent --add-rich-rule='
  rule family="ipv4"
  source address="YOUR_IP/32"
  port protocol="tcp" port="8088" accept'
sudo firewall-cmd --reload
```

**iptables:**

```bash
sudo iptables -A INPUT -p tcp --dport 8088 -s YOUR_IP -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8088 -j DROP
sudo netfilter-persistent save
```

### File Permissions

Ensure only root can read NexTunnel files:

```bash
sudo chown -R root:root /opt/nextunnel
sudo chmod 700 /opt/nextunnel
sudo chmod 600 /opt/nextunnel/nextunnel.db
```

### Fail2ban Configuration

Create `/etc/fail2ban/jail.d/nextunnel.conf`:

```ini
[nextunnel]
enabled = true
port = 8088
filter = nextunnel
logpath = /opt/nextunnel/logs/service.log
maxretry = 5
bantime = 3600
```

Create `/etc/fail2ban/filter.d/nextunnel.conf`:

```ini
[Definition]
failregex = ^.*"POST /api/login.*" 401.*$
ignoreregex =
```

---

## ⚠️ Known Limitations

NexTunnel is honest about its limitations. These are **not** vulnerabilities, but they do affect security:

### Architectural

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| **Single admin user** | No role separation | Use strong password, restrict IP |
| **Secrets in plaintext** | DB compromise = tunnel compromise | Disk encryption, file permissions |
| **No HTTPS by default** | Traffic sniffing if exposed | Reverse proxy with TLS |
| **No 2FA** | Password-only auth | Strong password, IP restriction |
| **Root required** | Full system access | Run on dedicated server |

### Technical

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| **No CSP header** | XSS impact higher | We escape all output, use `textContent` |
| **HTTP-only cookies** | Cookie can be sent over plaintext | Use HTTPS via reverse proxy |
| **No HSTS by default** | Downgrade attacks possible | Set HSTS in reverse proxy |
| **Fixed window rate limiting** | Possible burst bypass | Acceptable trade-off |
| **No audit log signing** | Logs can be tampered with by root | Not solvable without HSMs |

### Environmental

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| **No container isolation** | Processes share kernel | Run on dedicated server |
| **Uses `subprocess`** | Command injection risk if not careful | All commands generated internally |
| **Requires Python 3.8+** | Older systems unsupported | Update your OS |

---

## 🏆 Security Hall of Fame

We thank the following researchers for responsibly disclosing vulnerabilities:

> 🎖️ **No vulnerabilities have been publicly disclosed yet.**

**Want to be here?** Report a valid security issue responsibly and we'll credit you (with your permission).

---

## 📚 Additional Resources

### Security Standards

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CVSS Calculator](https://www.first.org/cvss/calculator/3.1)
- [CWE Database](https://cwe.mitre.org/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

### Tools for Security Testing

- [OWASP ZAP](https://www.zaproxy.org/) — Web application security scanner
- [Burp Suite](https://portswigger.net/burp) — Web security testing
- [nmap](https://nmap.org/) — Network scanning
- [Nikto](https://cirt.net/Nikto2) — Web server scanner
- [SQLMap](https://sqlmap.org/) — SQL injection testing

### Related Documentation

- [README.md](README.md) — Main documentation
- [CHANGELOG.md](CHANGELOG.md) — Version history
- [CONTRIBUTING.md](CONTRIBUTING.md) — Contribution guidelines
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) — Community guidelines

### External References

- [Python Security Guide](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [SQLite Security](https://www.sqlite.org/security.html)
- [MDN Web Security](https://developer.mozilla.org/en-US/docs/Web/Security)

---

## 📞 Contact

For **general questions** about security:
- Open a [GitHub Discussion](https://github.com/metiwilson/nextunnel/discussions)

For **security vulnerabilities**:
- Use [GitHub Security Advisories](https://github.com/metiwilson/nextunnel/security/advisories/new) (preferred)
- Or contact [@metiwilson](https://github.com/metiwilson) directly

For **urgent issues**:
- Mark your message with `[URGENT]` in the subject

---

<div align="center">

**🔒 Security is everyone's responsibility.**

Thank you for helping keep NexTunnel and its users safe!

[🏠 Repository](https://github.com/metiwilson/nextunnel) · [🔐 Advisories](https://github.com/metiwilson/nextunnel/security/advisories) · [🐛 Issues](https://github.com/metiwilson/nextunnel/issues) · [📄 License](LICENSE)

Made with ❤️ by [metiwilson](https://github.com/metiwilson)

</div>
