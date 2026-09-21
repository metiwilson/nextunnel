#!/usr/bin/env bash
#
# NexTunnel - Universal Tunnel Management Platform
# Installer Script
# Author: metiwilson (https://github.com/metiwilson)
# License: MIT
#

set -e

# ─── Colors ─────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

# ─── Config ─────────────────────────────────────────────────────────────
APP_NAME="NexTunnel"
INSTALL_DIR="/opt/nextunnel"
SERVICE_NAME="nextunnel"
PY_FILE="nextunnel.py"
PORT="${NEXTUNNEL_PORT:-8088}"
REPO="metiwilson/nextunnel"
BRANCH="main"
LOG_FILE="$INSTALL_DIR/logs/service.log"

AUTO_INSTALL="${NEXTUNNEL_AUTO_TOOLS:-yes}"

CRED_USER=""
CRED_PASS=""
CRED_FOUND=0

# ─── Banner ─────────────────────────────────────────────────────────────
banner() {
    clear
    echo -e "${PURPLE}${BOLD}"
    cat << "EOF"
    _   _         _____                    _
   | \ | |       |_   _|                  | |
   |  \| | _____   | |  _   _ _ __  _ __   | | ___
   | . ` |/ _ \ \/ / | | | | | | '_ \| '_ \| |/ _ \
   | |\  |  __/>  <  | | | |_| | | | | | | | |  __/
   \_| \_/\___/_/\_\ |_|  \__,_|_| |_|_| |_|_|\___|
EOF
    echo -e "${NC}"
    echo -e "${CYAN}         Universal Tunnel Management Platform${NC}"
    echo -e "${CYAN}                 v1.1.1 — by metiwilson${NC}"
    echo -e "${CYAN}       https://github.com/metiwilson/nextunnel${NC}"
    echo ""
}

log()   { echo -e "${GREEN}[✓]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
err()   { echo -e "${RED}[✗]${NC} $*"; }
info()  { echo -e "${BLUE}[i]${NC} $*"; }
step()  { echo -e "\n${PURPLE}${BOLD}▶ $*${NC}"; }

# ─── Checks ─────────────────────────────────────────────────────────────
check_root() {
    if [ "$(id -u)" -ne 0 ]; then
        err "This installer must be run as root."
        echo -e "    Try: ${BOLD}sudo bash install.sh${NC}"
        exit 1
    fi
}

check_os() {
    step "Detecting OS"
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        info "OS: $PRETTY_NAME"
    else
        warn "Unknown OS — proceeding anyway"
    fi
    ARCH=$(uname -m)
    info "Architecture: $ARCH"
}

# ─── Dependencies ───────────────────────────────────────────────────────
install_deps() {
    step "Installing system dependencies"
    if command -v apt-get >/dev/null 2>&1; then
        apt-get update -qq
        DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
            python3 python3-pip curl wget unzip tar socat \
            sqlite3 iptables net-tools procps ca-certificates openssh-client
    elif command -v yum >/dev/null 2>&1; then
        yum install -y python3 curl wget unzip tar socat \
            sqlite iptables net-tools procps ca-certificates openssh-clients
    elif command -v dnf >/dev/null 2>&1; then
        dnf install -y python3 curl wget unzip tar socat \
            sqlite iptables net-tools procps ca-certificates openssh-clients
    elif command -v apk >/dev/null 2>&1; then
        apk add --no-cache python3 curl wget unzip tar socat \
            sqlite iptables net-tools procps ca-certificates openssh-client
    else
        warn "Package manager not detected — install python3 manually."
    fi
    log "Dependencies installed"
}

# ─── Install app ────────────────────────────────────────────────────────
install_app() {
    step "Installing $APP_NAME to $INSTALL_DIR"
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$INSTALL_DIR"/{tunnels,logs,backups,pids}

    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    if [ -f "$SCRIPT_DIR/$PY_FILE" ]; then
        cp "$SCRIPT_DIR/$PY_FILE" "$INSTALL_DIR/$PY_FILE"
        log "Copied $PY_FILE from local source"
    else
        info "Downloading $PY_FILE from GitHub..."
        curl -fsSL "https://raw.githubusercontent.com/$REPO/$BRANCH/$PY_FILE" \
            -o "$INSTALL_DIR/$PY_FILE" || {
            err "Failed to download. Please place $PY_FILE next to install.sh"
            exit 1
        }
        log "Downloaded from GitHub"
    fi

    chmod +x "$INSTALL_DIR/$PY_FILE"
    log "Installed to $INSTALL_DIR"
}

# ─── Systemd service ────────────────────────────────────────────────────
create_service() {
    step "Creating systemd service"
    cat > "/etc/systemd/system/${SERVICE_NAME}.service" << EOF
[Unit]
Description=NexTunnel - Universal Tunnel Management Platform
Documentation=https://github.com/$REPO
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/env python3 -u $INSTALL_DIR/$PY_FILE
Restart=always
RestartSec=10
StandardOutput=append:$INSTALL_DIR/logs/service.log
StandardError=append:$INSTALL_DIR/logs/service.log
LimitNOFILE=1048576
LimitNPROC=65535

NoNewPrivileges=false
ProtectSystem=false
ProtectHome=false

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable "$SERVICE_NAME" >/dev/null 2>&1
    log "Service created and enabled"
}

# ─── Firewall ───────────────────────────────────────────────────────────
setup_firewall() {
    step "Configuring firewall"
    if command -v ufw >/dev/null 2>&1; then
        ufw allow "$PORT"/tcp >/dev/null 2>&1 || true
        log "ufw: allowed port $PORT"
    fi
    if command -v firewall-cmd >/dev/null 2>&1; then
        firewall-cmd --permanent --add-port="$PORT"/tcp >/dev/null 2>&1 || true
        firewall-cmd --reload >/dev/null 2>&1 || true
        log "firewalld: allowed port $PORT"
    fi
    iptables -C INPUT -p tcp --dport "$PORT" -j ACCEPT 2>/dev/null || \
        iptables -I INPUT -p tcp --dport "$PORT" -j ACCEPT 2>/dev/null || true
}

# ─── Auto-install tunnel tools ──────────────────────────────────────────
install_tunnel_tools() {
    if [ "$AUTO_INSTALL" != "yes" ]; then
        info "Skipping tunnel tools auto-install"
        return
    fi
    step "Installing tunnel tools (gost, rathole)"

    ARCH=$(uname -m)
    case "$ARCH" in
        x86_64)  A_GO=amd64; A_RS=x86_64 ;;
        aarch64) A_GO=arm64; A_RS=aarch64 ;;
        *)       A_GO=amd64; A_RS=x86_64 ;;
    esac

    if ! command -v gost >/dev/null 2>&1; then
        info "Installing gost v3..."
        if curl -fsSL "https://github.com/go-gost/gost/releases/download/v3.0.0/gost_3.0.0_linux_${A_GO}.tar.gz" \
            | tar -xz -C /usr/local/bin/ gost 2>/dev/null; then
            chmod +x /usr/local/bin/gost
            log "gost installed"
        else
            warn "gost install failed (continue anyway)"
        fi
    else
        log "gost already installed"
    fi

    if ! command -v rathole >/dev/null 2>&1; then
        info "Installing rathole..."
        if curl -fsSL "https://github.com/rapiz1/rathole/releases/download/v0.5.0/rathole-${A_RS}-unknown-linux-gnu.zip" \
            -o /tmp/rathole.zip 2>/dev/null; then
            (cd /tmp && unzip -oq rathole.zip && mv rathole /usr/local/bin/ && chmod +x /usr/local/bin/rathole) \
                && log "rathole installed" || warn "rathole install failed"
            rm -f /tmp/rathole.zip
        else
            warn "rathole download failed"
        fi
    else
        log "rathole already installed"
    fi

    if command -v socat >/dev/null 2>&1; then
        log "socat already installed"
    fi
}

# ─── Start service & capture first-run credentials ──────────────────────
start_and_capture() {
    step "Starting $APP_NAME"

    FRESH_INSTALL=0
    if [ ! -f "$INSTALL_DIR/nextunnel.db" ]; then
        FRESH_INSTALL=1
        info "Fresh install detected — a new admin will be created"
        : > "$LOG_FILE" 2>/dev/null || true
    else
        info "Existing installation detected — reusing existing admin"
    fi

    systemctl restart "$SERVICE_NAME"
    sleep 2

    if [ "$FRESH_INSTALL" -eq 1 ]; then
        info "Waiting for first-run credentials..."
        for i in $(seq 1 20); do
            if grep -q "FIRST-RUN CREDENTIALS" "$LOG_FILE" 2>/dev/null; then
                break
            fi
            sleep 1
        done
    fi

    if ! systemctl is-active --quiet "$SERVICE_NAME"; then
        err "Service failed to start."
        echo "--- last 40 log lines ---"
        journalctl -u "$SERVICE_NAME" -n 40 --no-pager || true
        echo "--- service log ---"
        tail -n 40 "$LOG_FILE" 2>/dev/null || true
        exit 1
    fi

    log "$APP_NAME is running"

    if [ "$FRESH_INSTALL" -eq 1 ] && [ -f "$LOG_FILE" ]; then
        CRED_USER=$(grep -m1 "👤  Username" "$LOG_FILE" | sed -E 's/.*Username[[:space:]]*:[[:space:]]*//' | tr -d '\r' || true)
        CRED_PASS=$(grep -m1 "🔑  Password" "$LOG_FILE" | sed -E 's/.*Password[[:space:]]*:[[:space:]]*//' | tr -d '\r' || true)
        if [ -n "$CRED_USER" ] && [ -n "$CRED_PASS" ]; then
            CRED_FOUND=1
        fi
    fi
}

# ─── Show credentials ───────────────────────────────────────────────────
show_credentials() {
    if [ "$CRED_FOUND" -eq 1 ]; then
        echo ""
        echo -e "${YELLOW}${BOLD}════════════════════════════════════════════════════════════${NC}"
        echo -e "${YELLOW}${BOLD}  🔐  FIRST-RUN ADMIN CREDENTIALS${NC}"
        echo -e "${YELLOW}${BOLD}════════════════════════════════════════════════════════════${NC}"
        echo ""
        echo -e "     ${BOLD}👤  Username :${NC}  ${GREEN}${BOLD}${CRED_USER}${NC}"
        echo -e "     ${BOLD}🔑  Password :${NC}  ${GREEN}${BOLD}${CRED_PASS}${NC}"
        echo ""
        echo -e "${YELLOW}${BOLD}════════════════════════════════════════════════════════════${NC}"
        echo -e "${RED}${BOLD}  ⚡ SAVE THESE NOW! They will NOT be shown again.${NC}"
        echo -e "${RED}${BOLD}  ⚡ You must change the password after first login.${NC}"
        echo -e "${YELLOW}${BOLD}════════════════════════════════════════════════════════════${NC}"
    else
        echo ""
        echo -e "${BLUE}${BOLD}════════════════════════════════════════════════════════════${NC}"
        echo -e "${BLUE}${BOLD}  🔐  EXISTING INSTALLATION${NC}"
        echo -e "${BLUE}${BOLD}════════════════════════════════════════════════════════════${NC}"
        echo -e "     ${BOLD}Use your previously configured credentials.${NC}"
        echo -e "${BLUE}${BOLD}════════════════════════════════════════════════════════════${NC}"
    fi
}

# ─── Tool status ────────────────────────────────────────────────────────
show_tool_status() {
    step "Tunnel tools status"
    for t in gost rathole socat hysteria chisel frps wstunnel; do
        if command -v "$t" >/dev/null 2>&1; then
            echo -e "    ${GREEN}✓${NC} $t"
        else
            echo -e "    ${YELLOW}○${NC} $t ${CYAN}(install from Web UI → Tools)${NC}"
        fi
    done
}

# ─── Summary ────────────────────────────────────────────────────────────
show_summary() {
    IP=$(hostname -I 2>/dev/null | awk '{print $1}')
    [ -z "$IP" ] && IP="127.0.0.1"

    echo ""
    echo -e "${GREEN}${BOLD}════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}${BOLD}  ✅  $APP_NAME installed successfully!${NC}"
    echo -e "${GREEN}${BOLD}════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "  🌐  ${BOLD}Local URL  :${NC}  http://127.0.0.1:$PORT"
    echo -e "  🌐  ${BOLD}Public URL :${NC}  http://$IP:$PORT"
    echo ""
    echo -e "  ${BOLD}Service commands:${NC}"
    echo -e "    ${CYAN}systemctl status $SERVICE_NAME${NC}   — check status"
    echo -e "    ${CYAN}systemctl restart $SERVICE_NAME${NC}  — restart"
    echo -e "    ${CYAN}systemctl stop $SERVICE_NAME${NC}     — stop"
    echo -e "    ${CYAN}journalctl -u $SERVICE_NAME -f${NC}   — live logs"
    echo ""
    echo -e "  ${BOLD}Files:${NC}"
    echo -e "    ${CYAN}$INSTALL_DIR${NC}                — install dir"
    echo -e "    ${CYAN}$INSTALL_DIR/nextunnel.db${NC}   — database"
    echo -e "    ${CYAN}$INSTALL_DIR/logs/${NC}          — logs"
    echo ""
    echo -e "  ${BOLD}Uninstall:${NC}"
    echo -e "    ${CYAN}systemctl stop $SERVICE_NAME && systemctl disable $SERVICE_NAME${NC}"
    echo -e "    ${CYAN}rm -rf $INSTALL_DIR /etc/systemd/system/$SERVICE_NAME.service${NC}"
    echo ""
    echo -e "  ${PURPLE}GitHub:${NC} https://github.com/$REPO"
    echo -e "  ${PURPLE}Author:${NC} metiwilson"
    echo ""
}

# ─── Main ───────────────────────────────────────────────────────────────
main() {
    banner
    check_root
    check_os
    install_deps
    install_app
    create_service
    setup_firewall
    install_tunnel_tools
    start_and_capture
    show_credentials
    show_tool_status
    show_summary
}

main "$@"
