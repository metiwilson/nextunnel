<div align="center">

# 🚇 NexTunnel

### Universal Tunnel Management Platform

**Professional web panel for managing Iran → Foreign tunnels with 11 protocols, bilingual UI (EN/FA), and 3x-ui integration.**

[![Version](https://img.shields.io/badge/version-1.0.0-blue?style=for-the-badge)](https://github.com/metiwilson/nextunnel/releases)
[![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-yellow?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Platform](https://img.shields.io/badge/platform-Linux-lightgrey?style=for-the-badge&logo=linux)](https://kernel.org)
[![Stars](https://img.shields.io/github/stars/metiwilson/nextunnel?style=for-the-badge)](https://github.com/metiwilson/nextunnel/stargazers)

**Made with ❤️ by [metiwilson](https://github.com/metiwilson)**

🇬🇧 **English** | 🇮🇷 **[فارسی](README.fa.md)**

</div>

---

## 📑 Table of Contents

- [Features](#-features)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [First Login](#-first-login)
- [Tunnel Tutorials](#-tunnel-tutorials)
- [ISP Optimization](#-isp-optimization)
- [3x-ui Integration](#-3x-ui-integration)
- [Service Management](#-service-management)
- [Systemd Template](#-systemd-template)
- [Update](#-update)
- [Uninstall](#-uninstall)
- [Security](#-security)
- [Troubleshooting](#-troubleshooting)
- [FAQ](#-faq)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)

---

## ✨ Features

| | |
|---|---|
| 🌍 **Bilingual** | English + Persian, instant switch |
| 🚇 **11 Protocols** | GOST, Hysteria2, Rathole, Chisel, FRP, Paqet, Backhaul, WSTunnel, Socat, SSH, iptables |
| 🎯 **18 ISP Profiles** | Irancell, MCI, Rightel, Shatel, Mobinnet, and more |
| 🛠️ **Auto-Install** | One-click tool installation from GitHub |
| 🔒 **Secure** | PBKDF2 200k, CSRF, rate limit, 30-min session |
| 📊 **Monitoring** | CPU, RAM, Disk, Load, Uptime |
| 🔔 **Update Checker** | GitHub release notifications |
| 🤖 **Auto-Restart** | Health checks + boot restore |
| 🔌 **3x-ui** | Reads inbounds, generates configs |
| 💾 **Backup** | One-click JSON export |
| ⚙️ **Systemd** | Auto-start, survives reboots |
| 📱 **Responsive** | Desktop, tablet, mobile |

---

## 📋 Requirements

- **OS:** Ubuntu 20.04+, Debian 11+, CentOS 7+, Alpine 3.15+
- **Arch:** x86_64 or aarch64
- **RAM:** 512 MB · **Disk:** 1 GB free
- **Access:** Root (required for install & tool management)
- **Port:** 8088 (panel, configurable)

---

## 🚀 Installation

### Quick Install (Recommended)

```bash
git clone https://github.com/metiwilson/nextunnel.git
cd nextunnel
sudo bash install.sh
```

### One-Liner

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/metiwilson/nextunnel/main/install.sh)
```

### What the Installer Does

1. Detects OS and CPU architecture
2. Installs dependencies (Python 3, sqlite3, socat, etc.)
3. Copies files to `/opt/nextunnel`
4. Creates systemd service `nextunnel`
5. Opens firewall port (8088)
6. Starts the service
7. Prints first-run credentials

### Access the Panel

```
http://YOUR_SERVER_IP:8088
```

---

## 🔐 First Login

1. Open the panel URL in your browser.
2. Use the credentials printed by the installer (**shown only once**).
3. Change your password (**mandatory on first login**).
4. Pick your language — EN / FA toggle at the top.

**Session:** 30 minutes idle → auto-logout. Any activity resets the timer.

---

## 🚇 Tunnel Tutorials

All examples use: `IRAN_IP` (entry server), `KHAREJ_IP` (exit server), `443` (default port).

### 1. GOST v3 — Most Versatile

| | |
|---|---|
| **Best for** | Any ISP |
| **Transports** | TCP, WS, TLS, QUIC, gRPC |
| **Recommendation** | `tls` transport + Cover SNI |

**Steps:**

1. **Tools** → Install **GOST v3**
2. **Create** → fill form → **Create Tunnel**
3. Click **Config** → copy **Kharej JSON**
4. On Kharej server: 
   ```bash
   gost -L relay+secret://:443?secret=YOUR_SECRET
   ```
5. Click **Start** on Iran side
6. Test:
   ```bash
   curl -x socks5://IRAN_IP:443 https://ifconfig.me
   ```

---

### 2. Hysteria2 — Best for QUIC ISPs

| | |
|---|---|
| **Best for** | Irancell, Mobinnet, HiWeb |
| **Transport** | QUIC + Salamander obfuscation |

**Steps:**

1. **Tools** → Install **Hysteria2**
2. **Create** → ISP `irancell` → port `443`
3. Copy **Kharej YAML** → save to `/etc/hysteria/config.yaml`
4. On Kharej server:
   ```bash
   hysteria -c /etc/hysteria/config.yaml server
   ```
5. Click **Start** on Iran

---

### 3. Rathole — Lightweight Reverse Tunnel

| | |
|---|---|
| **Best for** | Low-resource VPS, TCP-heavy workloads |
| **Transports** | TCP, WS, TLS |

**Steps:**

1. **Tools** → Install **Rathole**
2. **Create** → transport `tcp`
3. Copy **Kharej TOML** → save to `/etc/rathole/kharej.toml`
4. On Kharej server:
   ```bash
   rathole -c /etc/rathole/kharej.toml
   ```
5. Click **Start** on Iran

---

### 4. Chisel — Firewall-Friendly

| | |
|---|---|
| **Best for** | Strict firewalls (HTTP/WS only) |

**Steps:**

1. Install **Chisel**
2. Create tunnel (Iran port `8080`, Kharej port `8888`)
3. On Kharej server:
   ```bash
   chisel client IRAN_IP:8080 R:8888:127.0.0.1:8888 --auth SECRET:SECRET
   ```
4. Click **Start** on Iran

---

### 5. FRP — Professional Reverse Tunnel

| | |
|---|---|
| **Best for** | Stable, feature-rich tunneling with dashboard |

**Steps:**

1. Install **FRP** (installs both `frps` + `frpc`)
2. Create tunnel (Iran port `7000`)
3. On Kharej server:
   ```bash
   frpc -c /etc/frp/frpc.toml
   ```
4. Click **Start** on Iran

---

### 6. Backhaul — Multi-Transport

| | |
|---|---|
| **Best for** | Advanced users needing WS/TLS/SMUX/YAMUX |

**Steps:**

1. Install **Backhaul**
2. Create tunnel (transport `tls`)
3. On Kharej server:
   ```bash
   backhaul -c IRAN_IP:443 -l 127.0.0.1:443 -t tls -token SECRET
   ```
4. Click **Start** on Iran

---

### 7. WSTunnel — WebSocket Tunnel

| | |
|---|---|
| **Best for** | CDN-friendly, WebSocket-only environments |

**Steps:**

1. Install **WSTunnel**
2. Create tunnel (Iran port `8443`)
3. On Kharej server:
   ```bash
   wstunnel client -L tcp://127.0.0.1:443:127.0.0.1:443 ws://IRAN_IP:8443
   ```
4. Click **Start** on Iran

---

### 8. Paqet — Raw Socket Performance

| | |
|---|---|
| **Best for** | High-throughput, latency-sensitive traffic |

**Steps:**

1. Install **Paqet**
2. Create tunnel
3. On Kharej server:
   ```bash
   paqet -L kcp://:443
   ```
4. Click **Start** on Iran

---

### 9. Socat — Simplest Port Forward

| | |
|---|---|
| **Best for** | Quick port forwarding, no dependencies |

**Steps:**

1. Install **Socat**
2. Create tunnel → click **Start**
3. ✅ No Kharej-side configuration needed

---

### 10. SSH Tunnel — Encrypted via SSH

| | |
|---|---|
| **Best for** | Existing SSH access, zero extra software |

**Prerequisites:**

```bash
ssh-keygen -t ed25519
ssh-copy-id root@KHAREJ_IP
```

**Steps:**

1. Create tunnel (Iran port `1080`)
2. Click **Start**

---

### 11. iptables NAT — Kernel-Level

| | |
|---|---|
| **Best for** | Maximum performance, no userspace overhead |

**Steps:**

1. Create tunnel
2. Click **Start** — the panel applies:
   ```bash
   sysctl -w net.ipv4.ip_forward=1
   iptables -t nat -A PREROUTING -p tcp --dport 443 -j DNAT --to-destination KHAREJ_IP:443
   iptables -t nat -A POSTROUTING -j MASQUERADE
   ```

> ⚠️ Install `iptables-persistent` to survive reboots:
> ```bash
> sudo apt install iptables-persistent
> sudo netfilter-persistent save
> ```

---

## 🎯 ISP Optimization

18 pre-tuned profiles shipped with NexTunnel. **How to use:**

1. **ISP Profiles** → find your ISP → click **Apply**
2. Form auto-fills with recommended settings
3. Continue with the tutorial for that protocol

### Quick Picks

| ISP | Protocol | Transport |
|-----|----------|-----------|
| Irancell / HiWeb / Mobinnet | Hysteria2 | QUIC |
| MCI (Hamrah Aval) | GOST | TCP (port 80) |
| Shatel / Mokhaberat | GOST | TLS + cover SNI |
| Rightel / Afranet | GOST | WS (port 443) |
| Zitel | GOST | gRPC |
| Pars Online / Pishgaman | Rathole | TCP / TLS |
| Others / Unknown | GOST | TLS (port 443) |

### Adding Custom ISP

**ISP Profiles** → **+ Add Custom ISP Profile** → fill form → **Save**

---

## 🔌 3x-ui Integration

NexTunnel **reads** the 3x-ui SQLite database (never writes to it).

- **View inbounds:** Dashboard → 3x-ui Status card
- **Generate config:** Config → **X-UI Integration** tab → copy Inbound/Outbound/Routing JSON
- **Supported paths:**
  - `/etc/x-ui/x-ui.db`
  - `/usr/local/x-ui/x-ui.db`

Paste the generated JSON into your 3x-ui panel via **Inbounds → Add**.

---

## ⚙️ Service Management

```bash
systemctl status nextunnel      # Check status
systemctl restart nextunnel     # Restart
systemctl stop nextunnel        # Stop
systemctl start nextunnel       # Start
systemctl enable nextunnel      # Auto-start on boot
systemctl disable nextunnel     # Disable auto-start
journalctl -u nextunnel -f      # Live logs
journalctl -u nextunnel -n 100  # Last 100 lines
```

### Log Locations

| Log | Path |
|-----|------|
| Service output | `/opt/nextunnel/logs/service.log` |
| Per-tunnel logs | `/opt/nextunnel/logs/tunnel_<id>.log` |
| System (journald) | `journalctl -u nextunnel` |

---

## 🧩 Systemd Template (for Kharej side)

Use this template to run Kharej-side tools as persistent services:

```bash
sudo tee /etc/systemd/system/YOUR-SERVICE.service << 'EOF'
[Unit]
Description=YOUR DESCRIPTION
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/YOUR_BINARY -c /etc/path/config
Restart=always
RestartSec=5
LimitNOFILE=1048576

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now YOUR-SERVICE
```

### Ready-to-Use Examples

**Hysteria2 Server:**
```ini
ExecStart=/usr/local/bin/hysteria -c /etc/hysteria/config.yaml server
```

**Rathole Client:**
```ini
ExecStart=/usr/local/bin/rathole -c /etc/rathole/kharej.toml
```

**GOST Client:**
```ini
ExecStart=/usr/local/bin/gost -L relay+secret://:443?secret=YOUR_SECRET
```

**FRP Client:**
```ini
ExecStart=/usr/local/bin/frpc -c /etc/frp/frpc.toml
```

---

## 🔄 Update

### Manual Update

```bash
cd /path/to/nextunnel
git pull
sudo systemctl restart nextunnel
```

### Update Notification

The panel checks GitHub Releases API hourly. When a new version is available:

- A **green banner** appears on the Dashboard
- A **toast notification** shows on next login

Click the banner to open the release page.

---

## 🗑️ Uninstall

```bash
sudo systemctl stop nextunnel
sudo systemctl disable nextunnel
sudo rm /etc/systemd/system/nextunnel.service
sudo rm -rf /opt/nextunnel
sudo systemctl daemon-reload
```

> ⚠️ `rm -rf /opt/nextunnel` deletes the database, tunnels, and logs. Backup `nextunnel.db` first if needed.

---

## 🔒 Security

| Feature | Detail |
|---------|--------|
| Password hashing | PBKDF2-HMAC-SHA256, 200,000 iterations |
| Salt | 16 bytes per user, per change |
| Session | HttpOnly cookie, 30-min idle timeout |
| CSRF | Per-session token on all write operations |
| Rate limiting | 5 failed logins → 15-min lockout |
| HTTP headers | `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` |

### Recommendations

1. **Use HTTPS** — put behind Nginx or Caddy with TLS
2. **Restrict access** — firewall panel port to your IP or VPN
3. **Strong passwords** — minimum 12 characters
4. **Regular updates** — enable the update checker
5. **Backup regularly** — use built-in JSON export

### Nginx Reverse Proxy Example

```nginx
server {
    listen 443 ssl http2;
    server_name panel.example.com;

    ssl_certificate     /etc/letsencrypt/live/panel.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/panel.example.com/privkey.pem;

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

---

## 🐛 Troubleshooting

| Problem | Fix |
|---------|-----|
| **Panel not accessible** | `systemctl restart nextunnel` · check firewall port 8088 |
| **Forgot password** | Stop service, delete `nextunnel.db`, restart, check journalctl |
| **Tool install fails** | Ensure root access · check internet · verify disk space |
| **Tunnel won't start** | Verify tool installed · port free · check `/opt/nextunnel/logs/` |
| **Not restored after reboot** | `systemctl enable nextunnel` · wait 60s after boot |
| **Session expires too fast** | Edit `CONFIG["session_minutes"]` in `nextunnel.py`, restart |
| **Update checker not working** | Test `curl -I https://api.github.com`, restart service |

### Forgot Password — Reset

```bash
sudo systemctl stop nextunnel
sudo rm /opt/nextunnel/nextunnel.db
sudo systemctl start nextunnel
sudo journalctl -u nextunnel -n 50 | grep -A4 CREDENTIALS
```

### Port Already In Use

```bash
# Find what's using the port
ss -tlnp | grep 443

# Kill the process (if safe)
sudo kill <PID>
```

### Tool Manual Install

```bash
# Example for GOST
curl -fsSL https://github.com/go-gost/gost/releases/download/v3.0.0/gost_3.0.0_linux_amd64.tar.gz \
  | tar -xz -C /usr/local/bin/ gost
chmod +x /usr/local/bin/gost
gost -V
```

---

## ❓ FAQ

**Q: Which protocol should I use?**
- Irancell / HiWeb / Mobinnet → **Hysteria2**
- MCI → **GOST (TCP, port 80)**
- Shatel / Mokhaberat → **GOST (TLS + cover SNI)**
- Unknown ISP → **GOST (TLS, port 443)**

**Q: Does NexTunnel modify 3x-ui?**
No — it only reads the database. Never writes.

**Q: Can I run it on a non-Iran server?**
Technically yes, but it's designed for the Iran side. Kharej configs are deployed manually.

**Q: Multi-user support?**
Currently single admin. Schema is ready for future expansion.

**Q: How many tunnels can I create?**
No hard limit — depends on server resources (CPU/RAM/network).

**Q: How do I change the panel port?**
Edit `CONFIG["port"]` in `nextunnel.py`, restart service, update firewall.

**Q: Does it support IPv6?**
Partially — panel binds IPv4, but tunnel IPs can be IPv6 if the tool supports it.

**Q: How do I backup?**
Two ways:
1. Settings → **Download JSON Backup**
2. Copy `/opt/nextunnel/nextunnel.db` and `/opt/nextunnel/tunnels/`

**Q: What if the panel crashes?**
Systemd auto-restarts in 10s. Running tunnels keep going as detached processes.

**Q: Are secrets encrypted at rest?**
No — secrets are stored in plain text in SQLite. Secure your server with disk encryption.

---

## 📁 Project Structure

```
nextunnel/
├── nextunnel.py       # Main app (Python 3, single file)
├── install.sh         # Installer script
├── README.md          # This file
├── LICENSE            # MIT License
└── .github/
    └── workflows/
        └── release.yml

# Runtime files (created at install):
/opt/nextunnel/
├── nextunnel.py       # Installed copy
├── nextunnel.db       # SQLite database
├── tunnels/           # Tunnel configs (JSON)
├── logs/              # Application logs
├── pids/              # PID files for tunnels
└── backups/           # Backup exports
```

### Database Tables

| Table | Purpose |
|-------|---------|
| `users` | Admin accounts |
| `sessions` | Active login sessions |
| `login_attempts` | Rate-limiting history |
| `tunnels` | Tunnel definitions and configs |
| `logs` | Event log (per-tunnel + system) |
| `isp_profiles` | Built-in + custom ISP profiles |
| `settings` | Key/value settings |

---

## 🤝 Contributing

### How to Contribute

1. **Fork** the repository
2. **Create a branch:** `git checkout -b feature/my-feature`
3. **Commit:** `git commit -am 'Add feature'`
4. **Push:** `git push origin feature/my-feature`
5. **Open a Pull Request**

### Guidelines

- Follow **PEP 8** for Python code
- Keep single-file architecture for `nextunnel.py`
- Test on **Ubuntu 22.04** and **Debian 12**
- Update README for user-facing changes
- Add entries to the event log for significant actions

### Reporting Bugs

Open an issue with:
- NexTunnel version (shown in footer)
- OS and architecture (`uname -a`)
- Steps to reproduce
- Expected vs. actual behavior
- Relevant log excerpts

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for the full text.

```
MIT License · Copyright (c) 2025 metiwilson
```

---

## 🙏 Acknowledgments

NexTunnel is built on top of excellent open-source tools:

- [**GOST**](https://github.com/go-gost/gost) — Versatile tunneling and proxy
- [**Hysteria2**](https://github.com/apernet/hysteria) — QUIC-based proxy
- [**Rathole**](https://github.com/rapiz1/rathole) — Lightweight reverse tunnel
- [**Chisel**](https://github.com/jpillora/chisel) — HTTP/WS tunnel
- [**FRP**](https://github.com/fatedier/frp) — Fast reverse proxy
- [**Backhaul**](https://github.com/Musixal/Backhaul) — Multi-transport tunnel
- [**WSTunnel**](https://github.com/erebe/wstunnel) — WebSocket tunnel
- [**Paqet**](https://github.com/hans-thomas/paqet) — KCP raw socket
- [**3x-ui**](https://github.com/MHSanaei/3x-ui) — Xray panel

Special thanks to the Persian networking community for their knowledge sharing.

---

<div align="center">

### ⭐ If this project helps you, please give it a star!

**It motivates continued development and helps others discover the project.**

[![Star History Chart](https://api.star-history.com/svg?repos=metiwilson/nextunnel&type=Date)](https://star-history.com/#metiwilson/nextunnel&Date)

---

**NexTunnel** — Universal Tunnel Management Platform

Made with ❤️ by [metiwilson](https://github.com/metiwilson)

[🏠 Repository](https://github.com/metiwilson/nextunnel) · [🐛 Issues](https://github.com/metiwilson/nextunnel/issues) · [💬 Discussions](https://github.com/metiwilson/nextunnel/discussions) · [📄 License](LICENSE)

</div>
