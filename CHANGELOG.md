# Changelog

All notable changes to **NexTunnel** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## 📖 Version Format

Versions follow `MAJOR.MINOR.PATCH`:

- **MAJOR** — Incompatible API changes or breaking changes
- **MINOR** — New features, backward compatible
- **PATCH** — Bug fixes, backward compatible

**Categories used in this changelog:**

| Emoji | Category | Description |
|-------|----------|-------------|
| ✨ | **Added** | New features |
| 🔄 | **Changed** | Changes to existing functionality |
| 🗑️ | **Deprecated** | Soon-to-be-removed features |
| ❌ | **Removed** | Removed features |
| 🐛 | **Fixed** | Bug fixes |
| 🔒 | **Security** | Security-related changes |

---

## [Unreleased]

### ✨ Added
- Placeholder for upcoming features

### 🔄 Changed
- Placeholder for upcoming changes

### 🐛 Fixed
- Placeholder for upcoming fixes

---

## [1.0.0] — 2025-01-15

**🎉 Initial Release** — The first stable version of NexTunnel.

### ✨ Added

#### Core Features
- **Web-based control panel** for managing Iran → Foreign tunnels
- **Single-file architecture** (`nextunnel.py`) for easy deployment
- **SQLite database** with WAL mode for performance and reliability
- **REST API** with JSON responses for all operations
- **Auto-port detection** — finds a free port if 8088 is busy

#### Authentication & Security
- **PBKDF2-HMAC-SHA256** password hashing with **200,000 iterations**
- **16-byte random salt** generated per user and per password change
- **CSRF protection** with per-session tokens on all write operations
- **Rate limiting** — 5 failed login attempts trigger a 15-minute lockout
- **Session management** with **30-minute idle timeout** (sliding window)
- **HttpOnly + SameSite=Lax cookies** for session storage
- **Forced password change** on first login
- **Random first-run credentials** generated automatically
- **Security headers** on every response (`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`)
- **Constant-time password comparison** using `hmac.compare_digest`

#### Tunnel Protocols (11 Total)
- **GOST v3** — TCP, WS, TLS, QUIC, gRPC transports
- **Hysteria2** — QUIC with Salamander obfuscation
- **Rathole** — TCP, WS, TLS transports
- **Chisel** — HTTP/WebSocket tunnel
- **FRP** — Fast Reverse Proxy (frps + frpc)
- **Paqet** — KCP raw socket tunnel
- **Backhaul** — Multi-transport (TCP, WS, TLS, SMUX, YAMUX)
- **WSTunnel** — WebSocket tunneling
- **Socat** — Simple TCP port forwarding
- **SSH** — Encrypted tunnel via SSH
- **iptables** — Kernel-level NAT forwarding

#### Tunnel Management
- **Create, update, delete** tunnels with a full CRUD interface
- **Bulk actions** — start, stop, restart, or delete multiple tunnels at once
- **Search and filter** by name, IP, protocol, or status
- **Auto-generated secrets** (URL-safe, 24 bytes) per tunnel
- **Config export** as JSON with copy-to-clipboard functionality
- **Health checks** — TCP port + process alive verification
- **Ping test** — measures latency to Kharej server
- **Auto-restart** — monitors health and restarts failed tunnels
- **Boot restore** — automatically restores running tunnels after reboot
- **PID tracking** with per-tunnel PID files for reliable process management
- **Graceful shutdown** using `os.killpg` with SIGTERM → SIGKILL fallback

#### ISP Optimization (18 Profiles)
- **Built-in ISP profiles** for Iranian networks:
  - Irancell (MTN)
  - MCI (Hamrah Aval)
  - Rightel
  - Shatel
  - Mobinnet
  - Pars Online
  - Asiatech
  - HiWeb
  - Respina
  - Zitel
  - Pishgaman
  - Fanava
  - Samantel
  - Khatf
  - Afranet
  - Mokhaberat
  - Custom / Auto
  - Custom SNI Bypass
- **Custom ISP profile creation** via the UI
- **One-click apply** — fills the Create form with recommended settings
- **Per-ISP protocol + transport + port + obfs** recommendations

#### Tool Management
- **One-click installation** of 10 tools from official GitHub releases:
  - GOST v3
  - Rathole
  - Hysteria2
  - Chisel
  - FRP (frps + frpc)
  - Paqet
  - Backhaul
  - WSTunnel
  - Socat
  - Smite
- **Architecture-aware** installers — auto-detects x86_64 vs aarch64
- **Installation status tracking** with installed/not-installed indicators

#### Monitoring & Dashboard
- **Real-time system stats** — CPU, RAM, Disk usage
- **Load average** display (1/5/15 min)
- **System uptime** display
- **Network statistics** — RX/TX bytes
- **Server information** — OS, IP, time, root access
- **Tunnel count summary** — total, running, healthy, stopped
- **Protocol breakdown** — count per protocol

#### 3x-ui Integration
- **Read-only access** to 3x-ui SQLite database
- **Auto-detection** of 3x-ui installation (file + process)
- **Inbound listing** from 3x-ui panel
- **Config generation** — Inbound, Outbound, Routing JSON for 3x-ui
- **Supported paths:** `/etc/x-ui/x-ui.db`, `/usr/local/x-ui/x-ui.db`

#### Internationalization (i18n)
- **Bilingual UI** — English and Persian (فارسی)
- **Instant language switching** without page reload
- **RTL support** for Persian layout
- **Persisted language preference** per user and per browser
- **Bilingual backend messages** based on user language

#### User Interface
- **Modern, responsive design** — works on desktop, tablet, and mobile
- **Dark / Light themes** with localStorage persistence
- **Toast notifications** for all user actions
- **Modal dialogs** for details, configs, and forms
- **Sidebar navigation** with collapsible mobile menu
- **Search bar** with debounced input
- **Progress bars** for CPU, RAM, and Disk usage
- **Status pills** with color coding
- **Session countdown timer** in the top bar
- **Copy-to-clipboard** buttons for all configs

#### Update System
- **GitHub Releases API integration** for version checks
- **Hourly background checks** for new releases
- **In-app banner** when a new version is available
- **Toast notification** on first login after update detection
- **Manual force-check** endpoint (`/api/update-check`)

#### Backup & Restore
- **One-click JSON export** including:
  - All tunnels (with configs)
  - ISP profiles
  - Settings
  - Version metadata
- **Download via browser** with timestamped filename

#### Installation
- **Automated `install.sh`** script that:
  - Detects OS and architecture
  - Installs dependencies (Python 3, sqlite3, socat, etc.)
  - Copies files to `/opt/nextunnel`
  - Creates systemd service
  - Opens firewall port
  - Starts the service
  - Prints first-run credentials
- **Multi-distro support** — apt, yum, dnf, apk
- **Systemd integration** with auto-restart and boot persistence

#### Documentation
- **English README** with full feature documentation
- **Persian README** (README.fa.md) with RTL layout
- **11 tunnel tutorials** — step-by-step guides for each protocol
- **ISP optimization guide** with quick-pick table
- **Systemd templates** for common tools
- **Troubleshooting section** with 7+ common issues
- **FAQ section** with 10+ questions
- **Nginx reverse proxy example**

### 🔄 Changed

- **N/A** — Initial release

### 🐛 Fixed

- **N/A** — Initial release

### 🔒 Security

- Implemented secure password hashing (PBKDF2 with 200k iterations)
- Implemented CSRF protection on all state-changing operations
- Implemented rate limiting to prevent brute-force attacks
- Implemented session expiration with sliding window
- Restricted `X-Forwarded-For` trust — uses `client_address` by default
- Added `Referrer-Policy: same-origin` header
- Password comparison uses constant-time function
- Body size limit (1 MB) on JSON parsing to prevent DoS
- Input validation on all API endpoints
- SQL injection prevention via parameterized queries
- XSS prevention via `textContent` and escaping in frontend

---

## 🔮 Planned for Future Releases

The following features are under consideration for future versions:

### Version 1.1.0 (Q2 2025)
- [ ] **Multi-user support** with role-based access control
- [ ] **2FA authentication** (TOTP)
- [ ] **Traffic statistics per tunnel** (RX/TX, connections)
- [ ] **Real-time bandwidth graphs** with Chart.js
- [ ] **Email notifications** for tunnel failures
- [ ] **Telegram bot integration** for status updates
- [ ] **Multi-language expansion** (Arabic, Russian, Chinese)

### Version 1.2.0 (Q3 2025)
- [ ] **Docker support** with official image
- [ ] **docker-compose** example
- [ ] **Kubernetes Helm chart**
- [ ] **REST API authentication tokens** (for external integrations)
- [ ] **Webhook support** for events
- [ ] **Tunnel templates** (save/load configs)
- [ ] **Scheduled tunnel restarts** (cron-like)

### Version 2.0.0 (Q4 2025)
- [ ] **Multi-server management** (manage multiple Iran servers from one panel)
- [ ] **Load balancing** across multiple Kharej servers
- [ ] **Failover** — automatic switching to backup tunnels
- [ ] **Certificate management** (Let's Encrypt integration)
- [ ] **PostgreSQL support** as alternative to SQLite
- [ ] **REST API v2** with OpenAPI documentation
- [ ] **Mobile app** (React Native)

---

## 📅 Version History Summary

| Version | Date | Type | Highlights |
|---------|------|------|------------|
| **1.0.0** | 2025-01-15 | 🎉 Initial Release | 11 protocols, bilingual UI, 3x-ui integration |
| **0.1.0** | 2024-12-01 | 🧪 Alpha | Prototype with GOST support only |

---

## 📝 How to Update This File

When making changes to the project, follow these rules:

### Before Releasing a New Version

1. **Move items from `[Unreleased]`** to a new version section
2. **Add the release date** in `YYYY-MM-DD` format
3. **Group changes** by category (Added, Changed, Deprecated, Removed, Fixed, Security)
4. **Write in past tense** — "Added X", "Fixed Y", "Changed Z"
5. **Link to relevant issues/PRs** when possible: `(#123)`
6. **Update version in code** (`CONFIG['version']` in `nextunnel.py`)

### Example Entry Format

```markdown
## [1.1.0] — 2025-04-20

### ✨ Added
- **Multi-user support** with admin and viewer roles (#45)
- **Traffic graphs** on the dashboard using Chart.js (#52)
- **Telegram notifications** for tunnel failures (#58)

### 🔄 Changed
- **Session timeout** now configurable per user (#47)
- **Dashboard layout** improved for mobile devices (#51)

### 🐛 Fixed
- **Fixed** race condition in session cleanup (#49)
- **Fixed** incorrect RAM calculation on systems with >16 GB (#53)
- **Fixed** XFF header handling behind reverse proxy (#55)

### 🔒 Security
- **Updated** PBKDF2 iterations to 300,000 (#56)
- **Added** CSRF token rotation on privilege escalation (#57)
```

### Semantic Versioning Rules

| Change Type | Version Bump | Example |
|-------------|--------------|---------|
| Breaking API change | MAJOR | 1.0.0 → 2.0.0 |
| New feature (backward compatible) | MINOR | 1.0.0 → 1.1.0 |
| Bug fix | PATCH | 1.0.0 → 1.0.1 |
| Documentation only | PATCH | 1.0.0 → 1.0.1 |
| Security fix | PATCH or MINOR | 1.0.0 → 1.0.1 |

---

## 🔗 Links

- **Repository:** [github.com/metiwilson/nextunnel](https://github.com/metiwilson/nextunnel)
- **Issues:** [github.com/metiwilson/nextunnel/issues](https://github.com/metiwilson/nextunnel/issues)
- **Releases:** [github.com/metiwilson/nextunnel/releases](https://github.com/metiwilson/nextunnel/releases)
- **Discussions:** [github.com/metiwilson/nextunnel/discussions](https://github.com/metiwilson/nextunnel/discussions)

---

## 📚 References

- [Keep a Changelog](https://keepachangelog.com/) — This changelog format
- [Semantic Versioning](https://semver.org/) — Version numbering standard
- [Conventional Commits](https://www.conventionalcommits.org/) — Commit message convention

---

<div align="center">

**NexTunnel** — Universal Tunnel Management Platform

Made with ❤️ by [metiwilson](https://github.com/metiwilson)

</div>
