#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════
  NexTunnel - Universal Tunnel Management Platform
  Version : 1.1.1
  Author  : metiwilson (https://github.com/metiwilson)
  License : MIT
  GitHub  : https://github.com/metiwilson/nextunnel
═══════════════════════════════════════════════════════════════════════
"""

import http.server
import socketserver
import socket
import base64
import json
import os
import sys
import subprocess
import platform
import threading
import time
import signal
import shutil
import re
import secrets
import hashlib
import hmac
import sqlite3
import urllib.request
import urllib.parse
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta
from http.cookies import SimpleCookie
from collections import defaultdict

# ═══════════════════════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════════════════════
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG = {
    "host": "0.0.0.0",
    "port": 8088,
    "auto_port": True,
    "db_file": os.path.join(BASE_DIR, "nextunnel.db"),
    "tunnel_dir": os.path.join(BASE_DIR, "tunnels"),
    "log_dir": os.path.join(BASE_DIR, "logs"),
    "backup_dir": os.path.join(BASE_DIR, "backups"),
    "pid_dir": os.path.join(BASE_DIR, "pids"),
    # ★ Server-side session TTL: ~10 years (session never really expires in DB)
    "session_minutes": 5256000,
    # ★ Cookie Max-Age cap: 400 days (Chrome/Firefox reject anything longer!)
    "cookie_max_age_days": 400,
    "author": "metiwilson",
    "github": "https://github.com/metiwilson",
    "repo": "metiwilson/nextunnel",
    "app_name": "NexTunnel",
    "version": "1.1.1",
    "default_tunnel_port": 443,
    "max_login_attempts": 5,
    "lockout_minutes": 15,
    "pbkdf2_iterations": 200_000,
    "debug_sessions": False,   # ★ Set True to log cookie/session issues
}

for d in ('tunnel_dir', 'log_dir', 'backup_dir', 'pid_dir'):
    os.makedirs(CONFIG[d], exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════
#  SECURITY
# ═══════════════════════════════════════════════════════════════════════
def hash_password(password, salt_hex=None):
    if salt_hex is None:
        salt = secrets.token_bytes(16)
        salt_hex = salt.hex()
    else:
        salt = bytes.fromhex(salt_hex)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, CONFIG['pbkdf2_iterations'])
    return dk.hex(), salt_hex

def verify_password(password, stored_hash, stored_salt):
    try:
        dk = hashlib.pbkdf2_hmac(
            'sha256', password.encode('utf-8'),
            bytes.fromhex(stored_salt), CONFIG['pbkdf2_iterations']
        )
        return hmac.compare_digest(dk.hex(), stored_hash)
    except Exception:
        return False

def generate_random_credentials():
    adjectives = ['swift', 'dark', 'silent', 'rapid', 'steel', 'nova', 'prime', 'cyber', 'quantum', 'aurora']
    nouns = ['tunnel', 'relay', 'gate', 'shield', 'node', 'core', 'link', 'edge', 'nexus', 'bridge']
    username = f"{secrets.choice(adjectives)}_{secrets.choice(nouns)}_{secrets.randbelow(900)+100}"
    password = secrets.token_urlsafe(16)
    return username, password

def generate_token(nbytes=48):
    return secrets.token_urlsafe(nbytes)

def now_ts():
    return int(time.time())

# ═══════════════════════════════════════════════════════════════════════
#  DATABASE
# ═══════════════════════════════════════════════════════════════════════
_db_lock = threading.RLock()
SCHEMA_VERSION = 1

def db_connect():
    conn = sqlite3.connect(CONFIG['db_file'], check_same_thread=False, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def db_init():
    with _db_lock:
        conn = db_connect()
        try:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                role TEXT DEFAULT 'admin',
                must_change_password INTEGER DEFAULT 0,
                language TEXT DEFAULT 'en',
                created_at INTEGER NOT NULL,
                last_login INTEGER DEFAULT 0,
                last_ip TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                csrf_token TEXT NOT NULL,
                ip TEXT,
                user_agent TEXT,
                language TEXT DEFAULT 'en',
                created_at INTEGER NOT NULL,
                expires_at INTEGER NOT NULL,
                last_activity INTEGER NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS login_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip TEXT NOT NULL,
                username TEXT,
                success INTEGER DEFAULT 0,
                attempted_at INTEGER NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_login_attempts_ip_time
                ON login_attempts(ip, attempted_at);

            CREATE TABLE IF NOT EXISTS tunnels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                protocol TEXT NOT NULL,
                transport TEXT NOT NULL,
                iran_port INTEGER NOT NULL,
                kharej_ip TEXT NOT NULL,
                kharej_port INTEGER NOT NULL,
                secret TEXT NOT NULL,
                sni TEXT DEFAULT '',
                isp_profile TEXT DEFAULT 'auto',
                status TEXT DEFAULT 'stopped',
                auto_restart INTEGER DEFAULT 1,
                pid INTEGER DEFAULT 0,
                created_at INTEGER NOT NULL,
                updated_at INTEGER NOT NULL,
                config_iran TEXT,
                config_kharej TEXT,
                notes TEXT DEFAULT '',
                tags TEXT DEFAULT '',
                traffic_up INTEGER DEFAULT 0,
                traffic_down INTEGER DEFAULT 0,
                last_check INTEGER DEFAULT 0,
                health_status TEXT DEFAULT 'unknown',
                latency INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tunnel_id INTEGER,
                level TEXT DEFAULT 'info',
                message TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                FOREIGN KEY(tunnel_id) REFERENCES tunnels(id) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_logs_time ON logs(created_at DESC);

            CREATE TABLE IF NOT EXISTS isp_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                display_name_en TEXT NOT NULL,
                display_name_fa TEXT NOT NULL,
                protocol TEXT NOT NULL,
                transport TEXT NOT NULL,
                port INTEGER DEFAULT 443,
                fragmentation TEXT DEFAULT 'none',
                sni_mode TEXT DEFAULT 'random',
                obfs TEXT DEFAULT 'none',
                notes_en TEXT DEFAULT '',
                notes_fa TEXT DEFAULT '',
                is_builtin INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            );
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT DEFAULT 'info',
                title_en TEXT,
                title_fa TEXT,
                body_en TEXT,
                body_fa TEXT,
                is_read INTEGER DEFAULT 0,
                created_at INTEGER NOT NULL
            );
            """)

            default_profiles = [
                ("irancell", "Irancell (MTN)", "ایرانسل (MTN)", "hysteria2", "quic", 443, "medium", "random", "salamander",
                 "QUIC usually allowed. Best performance.", "QUIC معمولاً مجاز است. بهترین عملکرد."),
                ("mci", "MCI (Hamrah Aval)", "همراه اول (MCI)", "gost", "tcp", 80, "high", "random", "http",
                 "TCP+HTTP without TLS works best.", "TCP+HTTP بدون TLS بهترین گزینه."),
                ("rightel", "Rightel", "رایتل", "gost", "ws", 443, "medium", "random", "none",
                 "WS on port 443 is stable.", "WS روی پورت 443 پایدار."),
                ("shatel", "Shatel", "شاتل", "gost", "tls", 443, "medium", "banking", "none",
                 "Requires cover SNI.", "نیاز به Cover SNI."),
                ("mobinnet", "Mobinnet", "مبین‌نت", "hysteria2", "quic", 8443, "low", "random", "salamander",
                 "Salamander for resistance.", "Salamander برای مقاومت."),
                ("parsonline", "Pars Online", "پارس آنلاین", "rathole", "tcp", 443, "medium", "random", "none",
                 "Rathole TCP works well.", "Rathole TCP خوب کار می‌کند."),
                ("asiatech", "Asiatech", "آسیاتک", "gost", "tls", 8443, "high", "random", "none",
                 "TLS with high fragmentation.", "TLS با fragmentation بالا."),
                ("hiweb", "HiWeb", "های‌وب", "hysteria2", "quic", 443, "medium", "random", "salamander",
                 "Hysteria2 recommended.", "Hysteria2 پیشنهاد می‌شود."),
                ("respina", "Respina", "رسپینا", "gost", "ws", 2087, "medium", "random", "none",
                 "WS on non-standard port.", "WS روی پورت غیراستاندارد."),
                ("zitel", "Zitel", "زیتل", "gost", "grpc", 443, "medium", "random", "none",
                 "gRPC tunnel recommended.", "تانل gRPC پیشنهاد می‌شود."),
                ("pishgaman", "Pishgaman", "پیشگامان", "rathole", "tls", 443, "high", "random", "none",
                 "TLS with fragmentation.", "TLS با fragmentation."),
                ("fanava", "Fanava", "فن‌آوا", "frp", "tcp", 8443, "medium", "random", "none",
                 "FRP TCP tunnel.", "تانل FRP TCP."),
                ("samantel", "Samantel", "سامانتل", "gost", "tcp", 8080, "high", "random", "http",
                 "HTTP obfs recommended.", "HTTP obfs پیشنهاد می‌شود."),
                ("khatf", "Khatf", "خاتم", "hysteria2", "quic", 443, "low", "random", "salamander",
                 "Hysteria2 QUIC.", "Hysteria2 QUIC."),
                ("afranet", "Afranet", "افرانت", "gost", "ws", 443, "medium", "random", "none",
                 "WS over 443.", "WS روی 443."),
                ("mokhaberat", "Mokhaberat", "مخابرات", "gost", "tls", 443, "high", "banking", "none",
                 "Bank SNI recommended.", "SNI بانکی پیشنهاد می‌شود."),
                ("custom-auto", "Custom / Auto", "سفارشی / خودکار", "gost", "tcp", 443, "medium", "random", "none",
                 "Auto-detect best config.", "بهترین کانفیگ خودکار."),
                ("custom-sni", "Custom SNI Bypass", "بایپس SNI سفارشی", "gost", "tls", 443, "high", "custom", "none",
                 "Custom SNI bypass.", "بایپس SNI سفارشی."),
            ]
            for p in default_profiles:
                conn.execute("""
                    INSERT OR IGNORE INTO isp_profiles
                    (name, display_name_en, display_name_fa, protocol, transport, port,
                     fragmentation, sni_mode, obfs, notes_en, notes_fa, is_builtin)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,1)
                """, p)
            conn.commit()

            conn.execute(
                "INSERT OR IGNORE INTO settings (key, value) VALUES ('schema_version', ?)",
                (str(SCHEMA_VERSION),)
            )
            conn.execute(
                "INSERT OR IGNORE INTO settings (key, value) VALUES ('language_default', 'en')"
            )
            conn.commit()
        finally:
            conn.close()

def get_setting(key, default=None):
    with _db_lock:
        conn = db_connect()
        try:
            row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
            return row['value'] if row else default
        finally:
            conn.close()

def set_setting(key, value):
    with _db_lock:
        conn = db_connect()
        try:
            conn.execute(
                "INSERT INTO settings (key, value) VALUES (?,?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, str(value))
            )
            conn.commit()
        finally:
            conn.close()

def log_event(tunnel_id, level, message):
    with _db_lock:
        conn = db_connect()
        try:
            conn.execute(
                "INSERT INTO logs (tunnel_id, level, message, created_at) VALUES (?,?,?,?)",
                (tunnel_id, level, message, now_ts())
            )
            conn.commit()
        finally:
            conn.close()

# ═══════════════════════════════════════════════════════════════════════
#  FIRST-RUN
# ═══════════════════════════════════════════════════════════════════════
FIRST_RUN_CREDENTIALS = None

def ensure_admin_user():
    global FIRST_RUN_CREDENTIALS
    with _db_lock:
        conn = db_connect()
        try:
            row = conn.execute("SELECT COUNT(*) as c FROM users").fetchone()
            if row['c'] == 0:
                username, password = generate_random_credentials()
                pw_hash, pw_salt = hash_password(password)
                conn.execute("""
                    INSERT INTO users (username, password_hash, password_salt, role,
                        must_change_password, language, created_at)
                    VALUES (?,?,?,'admin',1,?,?)
                """, (username, pw_hash, pw_salt, get_setting('language_default', 'en'), now_ts()))
                conn.commit()
                FIRST_RUN_CREDENTIALS = {"username": username, "password": password}
                return FIRST_RUN_CREDENTIALS
            return None
        finally:
            conn.close()

def get_user_by_username(username):
    with _db_lock:
        conn = db_connect()
        try:
            row = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

def get_user(user_id):
    with _db_lock:
        conn = db_connect()
        try:
            row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

def update_user_password(user_id, new_password, must_change=0):
    pw_hash, pw_salt = hash_password(new_password)
    with _db_lock:
        conn = db_connect()
        try:
            conn.execute(
                "UPDATE users SET password_hash=?, password_salt=?, must_change_password=? WHERE id=?",
                (pw_hash, pw_salt, must_change, user_id)
            )
            conn.commit()
        finally:
            conn.close()

def update_username(user_id, new_username):
    with _db_lock:
        conn = db_connect()
        try:
            conn.execute("UPDATE users SET username=? WHERE id=?", (new_username, user_id))
            conn.commit()
        finally:
            conn.close()

def update_user_language(user_id, lang):
    if lang not in ('en', 'fa'):
        return
    with _db_lock:
        conn = db_connect()
        try:
            conn.execute("UPDATE users SET language=? WHERE id=?", (lang, user_id))
            conn.commit()
        finally:
            conn.close()

# ═══════════════════════════════════════════════════════════════════════
#  SESSIONS — Server 10y, Cookie 400d (browser-safe)
# ═══════════════════════════════════════════════════════════════════════
SESSION_TTL = CONFIG['session_minutes'] * 60             # Server-side: ~10 years
COOKIE_MAX_AGE = CONFIG['cookie_max_age_days'] * 86400   # ★ 400 days for browser

def create_session(user_id, ip, user_agent, lang='en'):
    token = generate_token(48)
    csrf = generate_token(24)
    ts = now_ts()
    expires = ts + SESSION_TTL
    with _db_lock:
        conn = db_connect()
        try:
            conn.execute("""
                INSERT INTO sessions (token, user_id, csrf_token, ip, user_agent,
                    language, created_at, expires_at, last_activity)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, (token, user_id, csrf, ip, (user_agent or '')[:200], lang, ts, expires, ts))
            conn.commit()
        finally:
            conn.close()
    return token, csrf

def get_session(token):
    if not token:
        return None
    with _db_lock:
        conn = db_connect()
        try:
            row = conn.execute("""
                SELECT s.*, u.username, u.role, u.must_change_password
                FROM sessions s JOIN users u ON u.id = s.user_id
                WHERE s.token=?
            """, (token,)).fetchone()
            if not row:
                return None
            # Only update last_activity; expires_at stays at 10y
            conn.execute(
                "UPDATE sessions SET last_activity=? WHERE token=?",
                (now_ts(), token)
            )
            conn.commit()
            return dict(row)
        finally:
            conn.close()

def delete_session(token):
    with _db_lock:
        conn = db_connect()
        try:
            conn.execute("DELETE FROM sessions WHERE token=?", (token,))
            conn.commit()
        finally:
            conn.close()

def delete_all_sessions(user_id, except_token=None):
    with _db_lock:
        conn = db_connect()
        try:
            if except_token:
                conn.execute("DELETE FROM sessions WHERE user_id=? AND token!=?",
                             (user_id, except_token))
            else:
                conn.execute("DELETE FROM sessions WHERE user_id=?", (user_id,))
            conn.commit()
        finally:
            conn.close()

def list_sessions(user_id, current_token=None):
    with _db_lock:
        conn = db_connect()
        try:
            rows = conn.execute("""
                SELECT token, ip, user_agent, created_at, last_activity
                FROM sessions WHERE user_id=?
                ORDER BY last_activity DESC
            """, (user_id,)).fetchall()
            result = []
            for r in rows:
                d = dict(r)
                d['current'] = (d['token'] == current_token)
                result.append(d)
            return result
        finally:
            conn.close()

def cleanup_expired_sessions():
    """Only login_attempts get cleaned. Sessions never expire server-side."""
    with _db_lock:
        conn = db_connect()
        try:
            conn.execute("DELETE FROM login_attempts WHERE attempted_at<?",
                         (now_ts() - 86400,))
            conn.commit()
        finally:
            conn.close()

def build_session_cookie(token, max_age=None):
    """★ Builds a browser-safe Set-Cookie header."""
    if max_age is None:
        max_age = COOKIE_MAX_AGE
    return (f"nt_session={token}; Path=/; HttpOnly; "
            f"Max-Age={max_age}; SameSite=Lax")

def build_logout_cookie():
    return "nt_session=; Path=/; HttpOnly; Max-Age=0; SameSite=Lax"

# ═══════════════════════════════════════════════════════════════════════
#  RATE LIMITING
# ═══════════════════════════════════════════════════════════════════════
def is_rate_limited(ip):
    cutoff = now_ts() - CONFIG['lockout_minutes'] * 60
    with _db_lock:
        conn = db_connect()
        try:
            row = conn.execute("""
                SELECT COUNT(*) as c FROM login_attempts
                WHERE ip=? AND success=0 AND attempted_at>?
            """, (ip, cutoff)).fetchone()
            return row['c'] >= CONFIG['max_login_attempts']
        finally:
            conn.close()

def record_login_attempt(ip, username, success):
    with _db_lock:
        conn = db_connect()
        try:
            conn.execute("""
                INSERT INTO login_attempts (ip, username, success, attempted_at)
                VALUES (?,?,?,?)
            """, (ip, username, 1 if success else 0, now_ts()))
            conn.commit()
        finally:
            conn.close()

# ═══════════════════════════════════════════════════════════════════════
#  UPDATE CHECKER
# ═══════════════════════════════════════════════════════════════════════
_update_cache = {"checked_at": 0, "latest": None, "url": None}

def check_for_updates(force=False):
    global _update_cache
    if not force and (now_ts() - _update_cache['checked_at']) < 3600:
        return _update_cache
    try:
        req = urllib.request.Request(
            f"https://api.github.com/repos/{CONFIG['repo']}/releases/latest",
            headers={'User-Agent': 'NexTunnel', 'Accept': 'application/vnd.github+json'}
        )
        with urllib.request.urlopen(req, timeout=6) as r:
            data = json.loads(r.read().decode())
            latest = (data.get('tag_name') or '').lstrip('v')
            url = data.get('html_url', '')
            _update_cache = {
                "checked_at": now_ts(),
                "latest": latest,
                "url": url,
                "has_update": bool(latest and latest != CONFIG['version']),
            }
    except Exception:
        _update_cache = {"checked_at": now_ts(), "latest": None, "url": None, "has_update": False}
    return _update_cache

# ═══════════════════════════════════════════════════════════════════════
#  SYSTEM
# ═══════════════════════════════════════════════════════════════════════
def is_root():
    try:
        return os.geteuid() == 0
    except AttributeError:
        return False

def check_command(cmd):
    return shutil.which(cmd) is not None

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def detect_public_ip():
    cached = get_setting('public_ip')
    cached_ts = int(get_setting('public_ip_ts', '0') or 0)
    if cached and (now_ts() - cached_ts) < 3600:
        return cached
    for url in ['https://api.ipify.org', 'https://ifconfig.me/ip', 'https://icanhazip.com']:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'curl/7.8'})
            with urllib.request.urlopen(req, timeout=4) as r:
                ip = r.read().decode().strip()
                if re.match(r'^\d+\.\d+\.\d+\.\d+$', ip):
                    set_setting('public_ip', ip)
                    set_setting('public_ip_ts', str(now_ts()))
                    return ip
        except Exception:
            continue
    return get_local_ip()

def get_os_info():
    try:
        with open('/etc/os-release') as f:
            info = {}
            for line in f:
                if '=' in line:
                    k, v = line.strip().split('=', 1)
                    info[k] = v.strip('"')
        return info.get('PRETTY_NAME', platform.system())
    except Exception:
        return platform.system()

def detect_xui():
    paths = ['/usr/local/x-ui/x-ui', '/etc/x-ui/x-ui.db', '/usr/local/x-ui/x-ui.db']
    file_ok = any(os.path.exists(p) for p in paths)
    proc_ok = False
    try:
        r = subprocess.run(['pgrep', '-f', 'x-ui'], capture_output=True, timeout=3)
        proc_ok = r.returncode == 0
    except Exception:
        pass
    return file_ok or proc_ok, file_ok

def get_xui_db_path():
    for c in ['/etc/x-ui/x-ui.db', '/usr/local/x-ui/x-ui.db']:
        if os.path.exists(c):
            return c
    return None

def read_xui_inbounds():
    db_path = get_xui_db_path()
    if not db_path:
        return []
    try:
        conn = sqlite3.connect(db_path, timeout=5)
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT id, remark, port, protocol, tag FROM inbounds").fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception:
        return []

def ping_host(host, count=2, timeout=3):
    try:
        r = subprocess.run(
            ['ping', '-c', str(count), '-W', str(timeout), host],
            capture_output=True, text=True, timeout=timeout * count + 2
        )
        return r.returncode == 0, r.stdout
    except Exception as e:
        return False, str(e)

def tcp_check(host, port, timeout=3):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        r = s.connect_ex((host, port))
        s.close()
        return r == 0
    except Exception:
        return False

def get_system_stats():
    stats = {"cpu": 0, "ram": 0, "ram_total": 0, "ram_used": 0,
             "disk": 0, "disk_total": 0, "disk_used": 0,
             "load": [0, 0, 0], "uptime": 0, "net_rx": 0, "net_tx": 0}
    try:
        with open('/proc/stat') as f:
            parts = f.readline().split()
            idle = int(parts[4])
            total = sum(int(x) for x in parts[1:])
        time.sleep(0.1)
        with open('/proc/stat') as f:
            parts2 = f.readline().split()
            idle2 = int(parts2[4])
            total2 = sum(int(x) for x in parts2[1:])
        dt = total2 - total
        if dt > 0:
            stats['cpu'] = round(100 * (1 - (idle2 - idle) / dt), 1)

        with open('/proc/meminfo') as f:
            mem = {}
            for line in f:
                k, v = line.split(':', 1)
                mem[k.strip()] = int(v.strip().split()[0])
        stats['ram_total'] = mem.get('MemTotal', 0) // 1024
        avail = mem.get('MemAvailable', mem.get('MemFree', 0))
        stats['ram_used'] = stats['ram_total'] - (avail // 1024)
        if stats['ram_total'] > 0:
            stats['ram'] = round(100 * stats['ram_used'] / stats['ram_total'], 1)

        du = shutil.disk_usage('/')
        stats['disk_total'] = du.total // (1024**3)
        stats['disk_used'] = du.used // (1024**3)
        stats['disk'] = round(100 * du.used / du.total, 1)

        with open('/proc/loadavg') as f:
            la = f.read().split()
            stats['load'] = [float(la[0]), float(la[1]), float(la[2])]

        with open('/proc/uptime') as f:
            stats['uptime'] = int(float(f.read().split()[0]))

        with open('/proc/net/dev') as f:
            for line in f.readlines()[2:]:
                parts = line.split()
                iface = parts[0].rstrip(':')
                if iface == 'lo':
                    continue
                stats['net_rx'] += int(parts[1])
                stats['net_tx'] += int(parts[9])
    except Exception:
        pass
    return stats

# ═══════════════════════════════════════════════════════════════════════
#  TUNNEL CONFIG GENERATORS
# ═══════════════════════════════════════════════════════════════════════
def generate_tunnel_config(tunnel_id, protocol, transport, iran_port,
                           kharej_ip, kharej_port, secret, sni='',
                           isp_profile='auto', obfs='none'):
    iran_ip = get_setting('public_ip') or detect_public_ip()
    gens = {
        'gost': lambda: _gen_gost(tunnel_id, transport, iran_port, kharej_ip, kharej_port, secret, sni),
        'rathole': lambda: _gen_rathole(tunnel_id, transport, iran_ip, iran_port, kharej_port, secret),
        'hysteria2': lambda: _gen_hysteria2(tunnel_id, iran_port, kharej_ip, kharej_port, secret, obfs),
        'chisel': lambda: _gen_chisel(tunnel_id, iran_ip, iran_port, kharej_port, secret),
        'frp': lambda: _gen_frp(tunnel_id, iran_ip, iran_port, kharej_port, secret),
        'paqet': lambda: _gen_paqet(tunnel_id, iran_ip, iran_port, kharej_port, secret),
        'backhaul': lambda: _gen_backhaul(tunnel_id, transport, iran_ip, iran_port, kharej_port, secret),
        'wstunnel': lambda: _gen_wstunnel(tunnel_id, iran_ip, iran_port, kharej_port, secret),
        'socat': lambda: _gen_socat(tunnel_id, iran_port, kharej_ip, kharej_port),
        'ssh': lambda: _gen_ssh(tunnel_id, iran_port, kharej_ip, kharej_port),
        'iptables': lambda: _gen_iptables(tunnel_id, iran_port, kharej_ip, kharej_port),
    }
    if protocol in gens:
        return gens[protocol]()
    return None

def _gen_gost(tid, transport, iran_port, kharej_ip, kharej_port, secret, sni):
    if transport == 'tcp':
        iran_cmd = f"gost -L tcp://:{iran_port}/{kharej_ip}:{kharej_port} -F relay+secret://{secret}"
        kharej_cmd = f"gost -L relay+secret://:{kharej_port}?secret={secret}"
    elif transport == 'ws':
        iran_cmd = f"gost -L tcp://:{iran_port}/{kharej_ip}:{kharej_port} -F ws://{kharej_ip}:{kharej_port}?secret={secret}"
        kharej_cmd = f"gost -L ws://:{kharej_port}?secret={secret}"
    elif transport == 'tls':
        s = f"&sni={sni}" if sni else ""
        iran_cmd = f"gost -L tcp://:{iran_port}/{kharej_ip}:{kharej_port} -F tls://{kharej_ip}:{kharej_port}?secret={secret}{s}"
        kharej_cmd = f"gost -L tls://:{kharej_port}?secret={secret}{s}"
    elif transport == 'quic':
        iran_cmd = f"gost -L tcp://:{iran_port}/{kharej_ip}:{kharej_port} -F quic://{kharej_ip}:{kharej_port}?secret={secret}"
        kharej_cmd = f"gost -L quic://:{kharej_port}?secret={secret}"
    elif transport == 'grpc':
        iran_cmd = f"gost -L tcp://:{iran_port}/{kharej_ip}:{kharej_port} -F grpc://{kharej_ip}:{kharej_port}?secret={secret}"
        kharej_cmd = f"gost -L grpc://:{kharej_port}?secret={secret}"
    else:
        return None
    return {
        "iran": {"type": "gost", "command": iran_cmd, "service": f"gost-iran-{tid}"},
        "kharej": {"type": "gost", "command": kharej_cmd, "service": f"gost-kharej-{tid}"},
    }

def _gen_rathole(tid, transport, iran_ip, iran_port, kharej_port, secret):
    if transport not in ('tcp', 'ws', 'tls'):
        transport = 'tcp'
    t_conf = ""
    c_conf = ""
    if transport == 'ws':
        t_conf = '\n[server.transport]\ntype = "websocket"\n'
        c_conf = '\n[client.transport]\ntype = "websocket"\n'
    elif transport == 'tls':
        t_conf = '\n[server.transport]\ntype = "tls"\n'
        c_conf = '\n[client.transport]\ntype = "tls"\n'

    iran_toml = f"""[server]
bind_addr = "0.0.0.0:{iran_port}"
default_token = "{secret}"
{t_conf}
[server.services.tunnel-{tid}]
token = "{secret}"
"""
    kharej_toml = f"""[client]
remote_addr = "{iran_ip}:{iran_port}"
default_token = "{secret}"
{c_conf}
[client.services.tunnel-{tid}]
local_addr = "127.0.0.1:{kharej_port}"
token = "{secret}"
"""
    return {
        "iran": {"type": "rathole", "config_toml": iran_toml,
                 "command": f"rathole -s -c {CONFIG['tunnel_dir']}/rathole-iran-{tid}.toml",
                 "service": f"rathole-iran-{tid}"},
        "kharej": {"type": "rathole", "config_toml": kharej_toml,
                   "command": f"rathole -c {CONFIG['tunnel_dir']}/rathole-kharej-{tid}.toml",
                   "service": f"rathole-kharej-{tid}"},
    }

def _gen_hysteria2(tid, iran_port, kharej_ip, kharej_port, secret, obfs):
    obfs_block = ""
    if obfs == 'salamander':
        obfs_block = f"\nobfs:\n  type: salamander\n  salamander:\n    password: {secret}\n"

    kharej_yaml = f"""listen: :{kharej_port}
auth:
  type: password
  password: {secret}
{obfs_block}"""
    iran_yaml = f"""server: {kharej_ip}:{kharej_port}
auth: {secret}
tls:
  sni: www.bing.com
  insecure: true
{obfs_block}
socks5:
  listen: 0.0.0.0:{iran_port}
"""
    return {
        "iran": {"type": "hysteria2", "config_yaml": iran_yaml,
                 "command": f"hysteria -c {CONFIG['tunnel_dir']}/hysteria-iran-{tid}.yaml client",
                 "service": f"hysteria-iran-{tid}"},
        "kharej": {"type": "hysteria2", "config_yaml": kharej_yaml,
                   "command": f"hysteria -c {CONFIG['tunnel_dir']}/hysteria-kharej-{tid}.yaml server",
                   "service": f"hysteria-kharej-{tid}"},
    }

def _gen_chisel(tid, iran_ip, iran_port, kharej_port, secret):
    auth = f"{secret}:{secret}"
    iran_cmd = f"chisel server --port {iran_port} --auth {auth} --reverse"
    kharej_cmd = f"chisel client {iran_ip}:{iran_port} R:{kharej_port}:127.0.0.1:{kharej_port} --auth {auth}"
    return {
        "iran": {"type": "chisel", "command": iran_cmd, "service": f"chisel-iran-{tid}"},
        "kharej": {"type": "chisel", "command": kharej_cmd, "service": f"chisel-kharej-{tid}"},
    }

def _gen_frp(tid, iran_ip, iran_port, kharej_port, secret):
    iran_toml = f"""[common]
bind_port = {iran_port}
token = {secret}
"""
    kharej_toml = f"""[common]
server_addr = {iran_ip}
server_port = {iran_port}
token = {secret}

[tunnel-{tid}]
type = tcp
local_ip = 127.0.0.1
local_port = {kharej_port}
remote_port = {iran_port}
"""
    return {
        "iran": {"type": "frp", "config_toml": iran_toml,
                 "command": f"frps -c {CONFIG['tunnel_dir']}/frp-iran-{tid}.toml",
                 "service": f"frp-iran-{tid}"},
        "kharej": {"type": "frp", "config_toml": kharej_toml,
                   "command": f"frpc -c {CONFIG['tunnel_dir']}/frp-kharej-{tid}.toml",
                   "service": f"frp-kharej-{tid}"},
    }

def _gen_paqet(tid, iran_ip, iran_port, kharej_port, secret):
    iran_cmd = f"paqet -L kcp://:{iran_port} -F tcp://127.0.0.1:{kharej_port}"
    kharej_cmd = f"paqet -L kcp://:{kharej_port}"
    return {
        "iran": {"type": "paqet", "command": iran_cmd, "service": f"paqet-iran-{tid}"},
        "kharej": {"type": "paqet", "command": kharej_cmd, "service": f"paqet-kharej-{tid}"},
    }

def _gen_backhaul(tid, transport, iran_ip, iran_port, kharej_port, secret):
    t = transport if transport in ('tcp', 'ws', 'tls', 'wss', 'smux', 'yamux') else 'tcp'
    iran_cmd = f"backhaul -l :{iran_port} -t {t} -token {secret}"
    kharej_cmd = f"backhaul -c {iran_ip}:{iran_port} -l 127.0.0.1:{kharej_port} -t {t} -token {secret}"
    return {
        "iran": {"type": "backhaul", "command": iran_cmd, "service": f"backhaul-iran-{tid}"},
        "kharej": {"type": "backhaul", "command": kharej_cmd, "service": f"backhaul-kharej-{tid}"},
    }

def _gen_wstunnel(tid, iran_ip, iran_port, kharej_port, secret):
    iran_cmd = f"wstunnel server --restrictTo=127.0.0.1:{kharej_port} ws://0.0.0.0:{iran_port}"
    kharej_cmd = f"wstunnel client -L tcp://127.0.0.1:{kharej_port}:127.0.0.1:{kharej_port} ws://{iran_ip}:{iran_port}"
    return {
        "iran": {"type": "wstunnel", "command": iran_cmd, "service": f"wstunnel-iran-{tid}"},
        "kharej": {"type": "wstunnel", "command": kharej_cmd, "service": f"wstunnel-kharej-{tid}"},
    }

def _gen_socat(tid, iran_port, kharej_ip, kharej_port):
    iran_cmd = f"socat TCP-LISTEN:{iran_port},fork,reuseaddr TCP:{kharej_ip}:{kharej_port}"
    return {
        "iran": {"type": "socat", "command": iran_cmd, "service": f"socat-iran-{tid}"},
        "kharej": {"type": "socat", "command": "# No server-side needed", "service": ""},
    }

def _gen_ssh(tid, iran_port, kharej_ip, kharej_port):
    iran_cmd = f"ssh -N -L 0.0.0.0:{iran_port}:127.0.0.1:{kharej_port} root@{kharej_ip} -o ServerAliveInterval=30 -o ExitOnForwardFailure=yes"
    return {
        "iran": {"type": "ssh", "command": iran_cmd, "service": f"ssh-iran-{tid}"},
        "kharej": {"type": "ssh", "command": "# SSH server must be running", "service": ""},
    }

def _gen_iptables(tid, iran_port, kharej_ip, kharej_port):
    iran_cmd = (f"sysctl -w net.ipv4.ip_forward=1 && "
                f"iptables -t nat -A PREROUTING -p tcp --dport {iran_port} -j DNAT --to-destination {kharej_ip}:{kharej_port} && "
                f"iptables -t nat -A POSTROUTING -j MASQUERADE")
    return {
        "iran": {"type": "iptables", "command": iran_cmd, "service": f"iptables-iran-{tid}"},
        "kharej": {"type": "iptables", "command": "# Kernel-level forwarding", "service": ""},
    }

def save_tunnel_config(tunnel_id, iran_config, kharej_config):
    for fname, data in [
        (f"tunnel_{tunnel_id}_iran.json", iran_config),
        (f"tunnel_{tunnel_id}_kharej.json", kharej_config),
    ]:
        with open(os.path.join(CONFIG['tunnel_dir'], fname), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

# ═══════════════════════════════════════════════════════════════════════
#  TUNNEL CRUD
# ═══════════════════════════════════════════════════════════════════════
def get_tunnel_list(search=None, protocol=None, status=None):
    sql = "SELECT * FROM tunnels WHERE 1=1"
    params = []
    if search:
        sql += " AND (name LIKE ? OR kharej_ip LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    if protocol and protocol != 'all':
        sql += " AND protocol=?"
        params.append(protocol)
    if status and status != 'all':
        sql += " AND status=?"
        params.append(status)
    sql += " ORDER BY created_at DESC"
    with _db_lock:
        conn = db_connect()
        try:
            return [dict(r) for r in conn.execute(sql, params).fetchall()]
        finally:
            conn.close()

def get_tunnel(tunnel_id):
    with _db_lock:
        conn = db_connect()
        try:
            row = conn.execute("SELECT * FROM tunnels WHERE id=?", (tunnel_id,)).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

VALID_PROTOCOLS = ('gost', 'rathole', 'hysteria2', 'chisel', 'frp', 'paqet', 'backhaul', 'wstunnel', 'socat', 'ssh', 'iptables')
VALID_TRANSPORTS = ('tcp', 'ws', 'tls', 'quic', 'grpc', 'wss', 'smux', 'yamux')

def create_tunnel(data):
    name = (data.get('name') or '').strip()
    protocol = (data.get('protocol') or 'gost').strip()
    transport = (data.get('transport') or 'tcp').strip()
    iran_port = int(data.get('iran_port') or CONFIG['default_tunnel_port'])
    kharej_ip = (data.get('kharej_ip') or '').strip()
    kharej_port = int(data.get('kharej_port') or 443)
    sni = (data.get('sni') or '').strip()
    isp_profile = (data.get('isp_profile') or 'auto').strip()
    notes = (data.get('notes') or '').strip()
    tags = (data.get('tags') or '').strip()

    if not name:
        return {"ok": False, "error": "Tunnel name is required"}
    if not kharej_ip:
        return {"ok": False, "error": "Kharej IP is required"}
    if not (1 <= iran_port <= 65535) or not (1 <= kharej_port <= 65535):
        return {"ok": False, "error": "Invalid port"}
    if protocol not in VALID_PROTOCOLS:
        return {"ok": False, "error": "Invalid protocol"}
    if transport not in VALID_TRANSPORTS:
        return {"ok": False, "error": "Invalid transport"}

    secret = secrets.token_urlsafe(24)
    ts = now_ts()
    obfs = 'salamander' if (isp_profile in ('mobinnet', 'irancell', 'hiweb', 'khatf') or protocol == 'hysteria2') else 'none'

    with _db_lock:
        conn = db_connect()
        try:
            cur = conn.execute("""
                INSERT INTO tunnels (name, protocol, transport, iran_port, kharej_ip,
                    kharej_port, secret, sni, isp_profile, status, created_at, updated_at,
                    notes, auto_restart, health_status, tags)
                VALUES (?,?,?,?,?,?,?,?,?,'stopped',?,?,?,?,?,?)
            """, (name, protocol, transport, iran_port, kharej_ip, kharej_port,
                  secret, sni, isp_profile, ts, ts, notes, 1, 'unknown', tags))
            tunnel_id = cur.lastrowid
            conn.commit()
        finally:
            conn.close()

    cfgs = generate_tunnel_config(tunnel_id, protocol, transport, iran_port,
                                  kharej_ip, kharej_port, secret, sni, isp_profile, obfs)
    if cfgs and cfgs.get('iran') and cfgs.get('kharej'):
        save_tunnel_config(tunnel_id, cfgs['iran'], cfgs['kharej'])
        with _db_lock:
            conn = db_connect()
            try:
                conn.execute(
                    "UPDATE tunnels SET config_iran=?, config_kharej=? WHERE id=?",
                    (json.dumps(cfgs['iran'], ensure_ascii=False),
                     json.dumps(cfgs['kharej'], ensure_ascii=False), tunnel_id)
                )
                conn.commit()
            finally:
                conn.close()

    log_event(tunnel_id, 'info', f"Tunnel '{name}' created")
    return {"ok": True, "tunnel_id": tunnel_id, "secret": secret}

def update_tunnel(tunnel_id, data):
    allowed = ('name', 'protocol', 'transport', 'iran_port', 'kharej_ip',
               'kharej_port', 'sni', 'isp_profile', 'notes', 'tags',
               'auto_restart')
    fields, params = [], []
    for k in allowed:
        if k in data:
            fields.append(f"{k}=?")
            params.append(data[k])
    if not fields:
        return {"ok": False, "error": "Nothing to update"}
    params.extend([now_ts(), tunnel_id])
    with _db_lock:
        conn = db_connect()
        try:
            conn.execute(f"UPDATE tunnels SET {','.join(fields)}, updated_at=? WHERE id=?", params)
            conn.commit()
        finally:
            conn.close()
    log_event(tunnel_id, 'info', 'Tunnel updated')
    return {"ok": True}

def delete_tunnel(tunnel_id):
    try:
        stop_tunnel_process(tunnel_id)
    except Exception:
        pass
    with _db_lock:
        conn = db_connect()
        try:
            conn.execute("DELETE FROM tunnels WHERE id=?", (tunnel_id,))
            conn.commit()
        finally:
            conn.close()
    for f in [f"tunnel_{tunnel_id}_iran.json", f"tunnel_{tunnel_id}_kharej.json"]:
        path = os.path.join(CONFIG['tunnel_dir'], f)
        if os.path.exists(path):
            os.remove(path)
    return {"ok": True}

def bulk_action(ids, action):
    results = {"ok": True, "count": 0, "errors": []}
    for tid in ids:
        try:
            if action == 'start':
                r = start_tunnel_process(tid)
            elif action == 'stop':
                r = stop_tunnel_process(tid)
            elif action == 'delete':
                r = delete_tunnel(tid)
            elif action == 'restart':
                stop_tunnel_process(tid)
                time.sleep(1)
                r = start_tunnel_process(tid)
            else:
                continue
            if r.get('ok'):
                results['count'] += 1
            else:
                results['errors'].append(f"#{tid}: {r.get('error')}")
        except Exception as e:
            results['errors'].append(f"#{tid}: {str(e)}")
    return results

# ═══════════════════════════════════════════════════════════════════════
#  PROCESS MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════
def _pid_file(tid):
    return os.path.join(CONFIG['pid_dir'], f"tunnel_{tid}.pid")

def _save_pid(tid, pid):
    try:
        with open(_pid_file(tid), 'w') as f:
            f.write(str(pid))
    except Exception:
        pass

def _read_pid(tid):
    try:
        with open(_pid_file(tid)) as f:
            return int(f.read().strip())
    except Exception:
        return 0

def _remove_pid(tid):
    try:
        os.remove(_pid_file(tid))
    except Exception:
        pass

def _is_pid_alive(pid):
    if not pid:
        return False
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False

def start_tunnel_process(tunnel_id):
    tunnel = get_tunnel(tunnel_id)
    if not tunnel:
        return {"ok": False, "error": "Tunnel not found"}

    pid = tunnel.get('pid') or _read_pid(tunnel_id)
    if tunnel['status'] == 'running' and _is_pid_alive(pid):
        return {"ok": False, "error": "Tunnel is already running"}

    tool_map = {
        'gost': 'gost', 'rathole': 'rathole', 'hysteria2': 'hysteria',
        'chisel': 'chisel', 'frp': 'frps', 'paqet': 'paqet', 'backhaul': 'backhaul',
        'wstunnel': 'wstunnel', 'socat': 'socat', 'ssh': 'ssh', 'iptables': 'iptables',
    }
    tool = tool_map.get(tunnel['protocol'], tunnel['protocol'])
    if not check_command(tool):
        return {"ok": False, "error": f"{tool} is not installed. Install it from Tools section."}

    config = json.loads(tunnel['config_iran'] or '{}')
    cmd = config.get('command', '')
    if not cmd:
        return {"ok": False, "error": "Invalid config"}

    cfg_key_map = {'config_toml': '.toml', 'config_yaml': '.yaml', 'config_json': '.json'}
    for k, ext in cfg_key_map.items():
        if config.get(k):
            target = os.path.join(CONFIG['tunnel_dir'], f"{tunnel['protocol']}-iran-{tunnel_id}{ext}")
            try:
                with open(target, 'w') as f:
                    f.write(config[k])
            except Exception as e:
                log_event(tunnel_id, 'warning', f"Config write error: {e}")

    try:
        log_file = os.path.join(CONFIG['log_dir'], f"tunnel_{tunnel_id}.log")
        lf = open(log_file, 'a')
        proc = subprocess.Popen(
            cmd, shell=True, stdout=lf, stderr=lf,
            start_new_session=True, cwd=CONFIG['tunnel_dir']
        )
        _save_pid(tunnel_id, proc.pid)
        with _db_lock:
            conn = db_connect()
            try:
                conn.execute(
                    "UPDATE tunnels SET status='running', pid=?, updated_at=?, health_status='starting' WHERE id=?",
                    (proc.pid, now_ts(), tunnel_id)
                )
                conn.commit()
            finally:
                conn.close()
        log_event(tunnel_id, 'success', f"Tunnel started (PID: {proc.pid})")
        return {"ok": True, "pid": proc.pid}
    except Exception as e:
        log_event(tunnel_id, 'error', f"Start error: {str(e)}")
        return {"ok": False, "error": str(e)}

def stop_tunnel_process(tunnel_id):
    tunnel = get_tunnel(tunnel_id)
    if not tunnel:
        return {"ok": False, "error": "Tunnel not found"}

    pid = tunnel.get('pid') or _read_pid(tunnel_id)
    killed = False
    if pid and _is_pid_alive(pid):
        try:
            os.killpg(os.getpgid(pid), signal.SIGTERM)
            time.sleep(1)
            if _is_pid_alive(pid):
                os.killpg(os.getpgid(pid), signal.SIGKILL)
            killed = True
        except Exception:
            try:
                os.kill(pid, signal.SIGTERM)
                time.sleep(1)
                if _is_pid_alive(pid):
                    os.kill(pid, signal.SIGKILL)
                killed = True
            except Exception:
                pass

    _remove_pid(tunnel_id)
    with _db_lock:
        conn = db_connect()
        try:
            conn.execute(
                "UPDATE tunnels SET status='stopped', pid=0, updated_at=?, health_status='stopped' WHERE id=?",
                (now_ts(), tunnel_id)
            )
            conn.commit()
        finally:
            conn.close()
    log_event(tunnel_id, 'info', 'Tunnel stopped')
    return {"ok": True, "killed": killed}

def check_tunnel_health(tunnel_id):
    tunnel = get_tunnel(tunnel_id)
    if not tunnel:
        return {"ok": False, "error": "Tunnel not found"}
    port_open = tcp_check('127.0.0.1', tunnel['iran_port'], 3)
    pid = tunnel.get('pid') or _read_pid(tunnel_id)
    proc_alive = _is_pid_alive(pid)
    health = 'healthy' if (port_open and (proc_alive or tunnel['protocol'] in ('iptables', 'socat'))) else 'unhealthy'
    with _db_lock:
        conn = db_connect()
        try:
            conn.execute(
                "UPDATE tunnels SET health_status=?, last_check=? WHERE id=?",
                (health, now_ts(), tunnel_id)
            )
            conn.commit()
        finally:
            conn.close()
    return {"ok": True, "health": health, "port_open": port_open, "proc_alive": proc_alive}

def auto_restart_check():
    while True:
        try:
            interval = int(get_setting('auto_restart_interval', '60') or 60)
            time.sleep(max(interval, 30))
            tunnels = get_tunnel_list()
            for t in tunnels:
                if t['auto_restart'] and t['status'] == 'running':
                    r = check_tunnel_health(t['id'])
                    if r.get('ok') and r.get('health') == 'unhealthy':
                        log_event(t['id'], 'warning', 'Tunnel down, restarting...')
                        stop_tunnel_process(t['id'])
                        time.sleep(2)
                        start_tunnel_process(t['id'])
            cleanup_expired_sessions()
        except Exception:
            time.sleep(30)

def restore_tunnels_on_boot():
    try:
        tunnels = get_tunnel_list()
        for t in tunnels:
            if t['status'] == 'running' or t['auto_restart']:
                pid = t.get('pid') or _read_pid(t['id'])
                if not _is_pid_alive(pid):
                    if t['status'] == 'running':
                        log_event(t['id'], 'info', 'Restoring tunnel after restart')
                        start_tunnel_process(t['id'])
    except Exception as e:
        log_event(None, 'warning', f'Boot restore failed: {e}')

# ═══════════════════════════════════════════════════════════════════════
#  TOOLS
# ═══════════════════════════════════════════════════════════════════════
TOOLS = {
    'gost': {'name': 'GOST v3', 'cmd': 'gost'},
    'rathole': {'name': 'Rathole', 'cmd': 'rathole'},
    'hysteria2': {'name': 'Hysteria2', 'cmd': 'hysteria'},
    'chisel': {'name': 'Chisel', 'cmd': 'chisel'},
    'frp': {'name': 'FRP', 'cmd': 'frps'},
    'paqet': {'name': 'Paqet', 'cmd': 'paqet'},
    'backhaul': {'name': 'Backhaul', 'cmd': 'backhaul'},
    'wstunnel': {'name': 'WSTunnel', 'cmd': 'wstunnel'},
    'socat': {'name': 'Socat', 'cmd': 'socat'},
    'smite': {'name': 'Smite', 'cmd': 'smite'},
}

def get_tool_status():
    return {k: {'name': v['name'], 'installed': check_command(v['cmd'])} for k, v in TOOLS.items()}

INSTALL_SCRIPTS = {
    'gost': (
        'ARCH=$(uname -m); case $ARCH in x86_64) A=amd64;; aarch64) A=arm64;; *) A=amd64;; esac; '
        'curl -fsSL "https://github.com/go-gost/gost/releases/download/v3.0.0/gost_3.0.0_linux_${A}.tar.gz" | '
        'tar -xz -C /usr/local/bin/ gost && chmod +x /usr/local/bin/gost'
    ),
    'rathole': (
        'ARCH=$(uname -m); case $ARCH in x86_64) A=x86_64;; aarch64) A=aarch64;; *) A=x86_64;; esac; '
        'curl -fsSL "https://github.com/rapiz1/rathole/releases/download/v0.5.0/rathole-${A}-unknown-linux-gnu.zip" '
        '-o /tmp/rathole.zip && cd /tmp && unzip -o rathole.zip && mv rathole /usr/local/bin/ && chmod +x /usr/local/bin/rathole'
    ),
    'hysteria2': 'bash -c "$(curl -fsSL https://get.hy2.sh/)"',
    'chisel': (
        'ARCH=$(uname -m); case $ARCH in x86_64) A=amd64;; aarch64) A=arm64;; *) A=amd64;; esac; '
        'curl -fsSL "https://github.com/jpillora/chisel/releases/download/v1.9.1/chisel_1.9.1_linux_${A}.gz" | '
        'gunzip > /usr/local/bin/chisel && chmod +x /usr/local/bin/chisel'
    ),
    'frp': (
        'ARCH=$(uname -m); case $ARCH in x86_64) A=amd64;; aarch64) A=arm64;; *) A=amd64;; esac; '
        'curl -fsSL "https://github.com/fatedier/frp/releases/download/v0.58.0/frp_0.58.0_linux_${A}.tar.gz" | '
        'tar -xz -C /tmp/ && mv /tmp/frp_0.58.0_linux_${A}/frps /usr/local/bin/ && '
        'mv /tmp/frp_0.58.0_linux_${A}/frpc /usr/local/bin/ && chmod +x /usr/local/bin/frps /usr/local/bin/frpc'
    ),
    'paqet': 'bash <(curl -Ls https://raw.githubusercontent.com/hans-thomas/paqet/main/install.sh)',
    'backhaul': (
        'ARCH=$(uname -m); case $ARCH in x86_64) A=amd64;; aarch64) A=arm64;; *) A=amd64;; esac; '
        'curl -fsSL "https://github.com/Musixal/Backhaul/releases/download/v0.5.5/backhaul-linux-${A}" '
        '-o /usr/local/bin/backhaul && chmod +x /usr/local/bin/backhaul'
    ),
    'wstunnel': (
        'ARCH=$(uname -m); case $ARCH in x86_64) A=x86_64;; aarch64) A=aarch64;; *) A=x86_64;; esac; '
        'curl -fsSL "https://github.com/erebe/wstunnel/releases/latest/download/wstunnel_linux_${A}" '
        '-o /usr/local/bin/wstunnel && chmod +x /usr/local/bin/wstunnel'
    ),
    'socat': 'apt-get install -y socat 2>/dev/null || yum install -y socat 2>/dev/null || apk add socat 2>/dev/null || true',
    'smite': 'bash <(curl -Ls https://raw.githubusercontent.com/zZedix/Smite/main/install.sh)',
}

def install_tool(tool):
    if tool not in INSTALL_SCRIPTS:
        return {"ok": False, "error": "Invalid tool"}
    if not is_root():
        return {"ok": False, "error": "Root required (use sudo)"}
    try:
        r = subprocess.run(['bash', '-c', INSTALL_SCRIPTS[tool]],
                           capture_output=True, text=True, timeout=300)
        cmd = TOOLS.get(tool, {}).get('cmd', tool)
        if r.returncode == 0 and check_command(cmd):
            log_event(None, 'success', f"Tool {tool} installed")
            return {"ok": True, "message": f"{tool} installed successfully"}
        return {"ok": False, "error": (r.stderr or r.stdout or "Install failed")[-400:]}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "Install timeout"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

# ═══════════════════════════════════════════════════════════════════════
#  ISP PROFILES
# ═══════════════════════════════════════════════════════════════════════
def get_isp_profiles():
    with _db_lock:
        conn = db_connect()
        try:
            return [dict(r) for r in conn.execute("SELECT * FROM isp_profiles ORDER BY id").fetchall()]
        finally:
            conn.close()

def get_isp_profile(name):
    with _db_lock:
        conn = db_connect()
        try:
            row = conn.execute("SELECT * FROM isp_profiles WHERE name=?", (name,)).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

def save_custom_isp(data):
    name = (data.get('name') or '').strip().lower().replace(' ', '-')
    if not name or len(name) < 2:
        return {"ok": False, "error": "Invalid name"}
    try:
        with _db_lock:
            conn = db_connect()
            try:
                conn.execute("""
                    INSERT INTO isp_profiles (name, display_name_en, display_name_fa, protocol,
                        transport, port, fragmentation, sni_mode, obfs, notes_en, notes_fa, is_builtin)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,0)
                    ON CONFLICT(name) DO UPDATE SET
                        display_name_en=excluded.display_name_en,
                        display_name_fa=excluded.display_name_fa,
                        protocol=excluded.protocol,
                        transport=excluded.transport,
                        port=excluded.port,
                        fragmentation=excluded.fragmentation,
                        sni_mode=excluded.sni_mode,
                        obfs=excluded.obfs,
                        notes_en=excluded.notes_en,
                        notes_fa=excluded.notes_fa
                """, (
                    name, data.get('display_name_en', name), data.get('display_name_fa', name),
                    data.get('protocol', 'gost'), data.get('transport', 'tcp'),
                    int(data.get('port', 443)), data.get('fragmentation', 'none'),
                    data.get('sni_mode', 'random'), data.get('obfs', 'none'),
                    data.get('notes_en', ''), data.get('notes_fa', '')
                ))
                conn.commit()
            finally:
                conn.close()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def delete_isp(name):
    with _db_lock:
        conn = db_connect()
        try:
            conn.execute("DELETE FROM isp_profiles WHERE name=? AND is_builtin=0", (name,))
            conn.commit()
        finally:
            conn.close()
    return {"ok": True}

# ═══════════════════════════════════════════════════════════════════════
#  DASHBOARD STATS
# ═══════════════════════════════════════════════════════════════════════
def get_dashboard_stats():
    with _db_lock:
        conn = db_connect()
        try:
            total = conn.execute("SELECT COUNT(*) c FROM tunnels").fetchone()['c']
            running = conn.execute("SELECT COUNT(*) c FROM tunnels WHERE status='running'").fetchone()['c']
            healthy = conn.execute("SELECT COUNT(*) c FROM tunnels WHERE health_status='healthy'").fetchone()['c']
            unhealthy = conn.execute("SELECT COUNT(*) c FROM tunnels WHERE health_status='unhealthy'").fetchone()['c']
            proto_rows = conn.execute(
                "SELECT protocol, COUNT(*) c FROM tunnels GROUP BY protocol"
            ).fetchall()
        finally:
            conn.close()

    xui_installed, _ = detect_xui()
    sys_stats = get_system_stats()
    update_info = check_for_updates()

    return {
        "total_tunnels": total,
        "running_tunnels": running,
        "healthy_tunnels": healthy,
        "unhealthy_tunnels": unhealthy,
        "stopped_tunnels": total - running,
        "protocols": {r['protocol']: r['c'] for r in proto_rows},
        "server_ip": get_setting('public_ip') or get_local_ip(),
        "local_ip": get_local_ip(),
        "os_info": get_os_info(),
        "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "xui_installed": xui_installed,
        "xui_inbound_count": len(read_xui_inbounds()),
        "root_access": is_root(),
        "version": CONFIG['version'],
        "system": sys_stats,
        "update": {
            "available": update_info.get('has_update', False),
            "latest": update_info.get('latest'),
            "url": update_info.get('url'),
            "current": CONFIG['version'],
        }
    }

# ═══════════════════════════════════════════════════════════════════════
#  I18N
# ═══════════════════════════════════════════════════════════════════════
MESSAGES = {
    "en": {
        "unauthorized": "Unauthorized",
        "invalid_credentials": "Invalid username or password",
        "rate_limited": "Too many attempts. Try again in {min} minutes.",
        "csrf_invalid": "Invalid CSRF token",
        "not_found": "Not found",
    },
    "fa": {
        "unauthorized": "غیرمجاز",
        "invalid_credentials": "نام کاربری یا رمز اشتباه است",
        "rate_limited": "تعداد تلاش‌ها بیش از حد. {min} دقیقه دیگر تلاش کنید.",
        "csrf_invalid": "توکن CSRF نامعتبر",
        "not_found": "یافت نشد",
    },
}

def msg(key, lang='en', **kw):
    tpl = MESSAGES.get(lang, MESSAGES['en']).get(key, key)
    return tpl.format(**kw) if kw else tpl

# ═══════════════════════════════════════════════════════════════════════
#  HTML FRONTEND
# ═══════════════════════════════════════════════════════════════════════
HTML = r"""<!DOCTYPE html>
<html lang="en" dir="ltr" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>NexTunnel</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%235b8def' stroke-width='2'%3E%3Cpath d='M4 21v-7a4 4 0 0 1 4-4h8a4 4 0 0 1 4 4v7'/%3E%3Cpath d='M12 3v7'/%3E%3Ccircle cx='12' cy='12' r='2'/%3E%3C/svg%3E">
<link href="https://fonts.cdnfonts.com/css/dana" rel="stylesheet">
<style>
:root,[data-theme="dark"]{--primary:#5b8def;--primary-2:#7c5cff;--accent:#06b6d4;--bg:#0a0e1a;--bg-2:#0f172a;--surface:#131a2b;--surface-2:#1a2238;--surface-3:#222c46;--border:#1f2940;--border-2:#2a3654;--text:#e5e9f0;--text-2:#b8c1d9;--muted:#7b859c;--success:#10b981;--warning:#f59e0b;--danger:#ef4444;--info:#06b6d4;--shadow:0 8px 32px rgba(0,0,0,.4);--glow:0 0 24px rgba(91,141,239,.35)}
[data-theme="light"]{--primary:#4f6ef7;--primary-2:#7c5cff;--accent:#0891b2;--bg:#eef1f8;--bg-2:#f5f7fb;--surface:#fff;--surface-2:#f8fafc;--surface-3:#eef2f7;--border:#e2e8f0;--border-2:#cbd5e1;--text:#0f172a;--text-2:#334155;--muted:#64748b;--shadow:0 8px 32px rgba(15,23,42,.08);--glow:0 0 24px rgba(79,70,229,.2)}
*{margin:0;padding:0;box-sizing:border-box}
html,body{height:100%;overflow:hidden}
body{font-family:'Dana','Segoe UI',Tahoma,sans-serif;background:var(--bg);color:var(--text);font-size:14px;line-height:1.6;-webkit-tap-highlight-color:transparent}
[dir="ltr"] body{font-family:'Segoe UI','Dana',Tahoma,sans-serif}
button,input,textarea,select{font-family:inherit;color:inherit;font-size:inherit}
::-webkit-scrollbar{width:6px;height:6px}::-webkit-scrollbar-thumb{background:var(--border-2);border-radius:3px}::-webkit-scrollbar-track{background:transparent}
#auth{position:fixed;inset:0;display:flex;align-items:center;justify-content:center;background:radial-gradient(circle at 30% 20%,rgba(91,141,239,.18),transparent 50%),radial-gradient(circle at 70% 80%,rgba(124,92,255,.15),transparent 50%),var(--bg);z-index:100;padding:16px;overflow-y:auto}
.auth-card{width:100%;max-width:420px;background:var(--surface);border:1px solid var(--border);border-radius:20px;padding:32px 24px;box-shadow:var(--shadow);animation:pop .4s ease-out;margin:auto}
@keyframes pop{from{opacity:0;transform:translateY(20px) scale(.96)}to{opacity:1;transform:none}}
.auth-logo{width:72px;height:72px;margin:0 auto 18px;border-radius:20px;background:linear-gradient(135deg,var(--primary),var(--primary-2));display:flex;align-items:center;justify-content:center;box-shadow:var(--glow)}
.auth-logo svg{width:36px;height:36px;stroke:#fff}
.auth-card h1{text-align:center;font-size:1.35rem;margin-bottom:4px;font-weight:800}
.auth-card .sub{text-align:center;color:var(--muted);font-size:.8rem;margin-bottom:22px}
.field{margin-bottom:12px}
.field label{display:block;font-size:.75rem;color:var(--text-2);margin-bottom:6px;font-weight:600}
.field input,.field select,.field textarea{width:100%;padding:11px 13px;background:var(--bg-2);border:1px solid var(--border);border-radius:10px;color:var(--text);font-size:.9rem;transition:all .2s}
.field input:focus,.field select:focus,.field textarea:focus{outline:none;border-color:var(--primary);box-shadow:0 0 0 3px rgba(91,141,239,.15)}
.field.mono input{direction:ltr;text-align:left;font-family:'Courier New',monospace}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:6px;padding:10px 16px;border:1px solid transparent;border-radius:10px;cursor:pointer;font-size:.85rem;font-weight:600;transition:all .15s;white-space:nowrap;background:transparent}
.btn svg{width:15px;height:15px;stroke-width:2;flex-shrink:0}
.btn-primary{background:linear-gradient(135deg,var(--primary),var(--primary-2));color:#fff;box-shadow:0 4px 12px rgba(91,141,239,.3)}
.btn-primary:hover{transform:translateY(-1px);box-shadow:var(--glow)}
.btn-primary:disabled{opacity:.5;cursor:not-allowed}
.btn-ghost{background:var(--surface-2);border-color:var(--border);color:var(--text-2)}
.btn-ghost:hover{border-color:var(--primary);color:var(--text)}
.btn-danger{background:rgba(239,68,68,.12);color:var(--danger);border-color:rgba(239,68,68,.3)}
.btn-danger:hover{background:rgba(239,68,68,.2)}
.btn-success{background:rgba(16,185,129,.12);color:var(--success);border-color:rgba(16,185,129,.3)}
.btn-warning{background:rgba(245,158,11,.12);color:var(--warning);border-color:rgba(245,158,11,.3)}
.btn-full{width:100%}
.btn-icon{width:40px;height:40px;padding:0;background:var(--surface-2);border-color:var(--border);color:var(--text-2)}
.btn-icon:hover{border-color:var(--primary);color:var(--primary)}.btn-icon svg{width:18px;height:18px}
.btn-sm{padding:6px 10px;font-size:.74rem;border-radius:8px}.btn-sm svg{width:12px;height:12px}
.err{color:var(--danger);font-size:.8rem;text-align:center;min-height:18px;margin-bottom:8px}
#app{display:none;height:100vh}#app.show{display:flex}
.sidebar{width:270px;background:var(--surface);border-inline-end:1px solid var(--border);display:flex;flex-direction:column;flex-shrink:0;transition:transform .25s;z-index:200}
.brand{padding:16px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:12px}
.brand-logo{width:46px;height:46px;border-radius:12px;background:linear-gradient(135deg,var(--primary),var(--primary-2));display:flex;align-items:center;justify-content:center;box-shadow:var(--glow);flex-shrink:0}
.brand-logo svg{width:26px;height:26px;stroke:#fff}
.brand-text h1{font-size:1rem;font-weight:800}.brand-text .ver{font-size:.68rem;color:var(--muted);direction:ltr;text-align:left;font-family:'Courier New',monospace}
.nav{flex:1;padding:12px 10px;overflow-y:auto;display:flex;flex-direction:column;gap:3px}
.nav-item{display:flex;align-items:center;gap:10px;padding:11px 13px;border-radius:10px;cursor:pointer;color:var(--text-2);font-size:.85rem;font-weight:600;transition:all .15s;user-select:none}
.nav-item svg{width:18px;height:18px;flex-shrink:0;stroke-width:2}
.nav-item:hover{background:var(--surface-2);color:var(--text)}
.nav-item.active{background:linear-gradient(135deg,var(--primary),var(--primary-2));color:#fff;box-shadow:var(--glow)}
.nav-item.active svg{stroke:#fff}
.nav-item .badge{margin-inline-start:auto;font-size:.68rem;padding:1px 8px;border-radius:10px;background:rgba(255,255,255,.15);direction:ltr;font-weight:700}
.sidebar-footer{padding:12px;border-top:1px solid var(--border)}
.main{flex:1;display:flex;flex-direction:column;overflow:hidden;background:var(--bg-2)}
.topbar{padding:12px 20px;background:var(--surface);border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}
.topbar h2{font-size:1rem;font-weight:700;display:flex;align-items:center;gap:8px}
.topbar h2 svg{width:20px;height:20px;stroke:var(--primary)}
.topbar-actions{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.content{flex:1;overflow-y:auto;padding:18px 22px;-webkit-overflow-scrolling:touch}
.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin-bottom:20px}
.stat{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:16px;position:relative;overflow:hidden;transition:all .3s}
.stat::before{content:'';position:absolute;top:-30px;inset-inline-start:-30px;width:120px;height:120px;border-radius:50%;filter:blur(50px);opacity:.18;pointer-events:none}
.stat.total::before{background:var(--primary)}.stat.running::before{background:var(--success)}
.stat.stopped::before{background:var(--warning)}.stat.info::before{background:var(--info)}
.stat.healthy::before{background:var(--success)}.stat.danger::before{background:var(--danger)}
.stat:hover{transform:translateY(-3px);border-color:var(--primary);box-shadow:var(--shadow)}
.stat-head{display:flex;align-items:center;gap:10px;margin-bottom:10px}
.stat-ico{width:38px;height:38px;border-radius:10px;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.stat-ico svg{width:20px;height:20px;stroke-width:2}
.stat.total .stat-ico{background:rgba(91,141,239,.14)}.stat.total .stat-ico svg{stroke:var(--primary)}
.stat.running .stat-ico,.stat.healthy .stat-ico{background:rgba(16,185,129,.14)}.stat.running .stat-ico svg,.stat.healthy .stat-ico svg{stroke:var(--success)}
.stat.stopped .stat-ico{background:rgba(245,158,11,.14)}.stat.stopped .stat-ico svg{stroke:var(--warning)}
.stat.info .stat-ico{background:rgba(6,182,212,.14)}.stat.info .stat-ico svg{stroke:var(--info)}
.stat.danger .stat-ico{background:rgba(239,68,68,.14)}.stat.danger .stat-ico svg{stroke:var(--danger)}
.stat-label{font-size:.75rem;color:var(--muted);font-weight:600}
.stat-val{font-size:1.8rem;font-weight:800;direction:ltr;text-align:start;line-height:1.15}
.stat-sub{font-size:.7rem;color:var(--muted);margin-top:4px;direction:ltr;text-align:start;font-family:'Courier New',monospace;word-break:break-all}
.progress{height:6px;background:var(--border);border-radius:3px;overflow:hidden;margin-top:8px}
.progress-bar{height:100%;transition:width .5s;border-radius:3px;background:linear-gradient(90deg,var(--primary),var(--primary-2))}
.card{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:18px;box-shadow:var(--shadow);margin-bottom:16px}
.card-head{display:flex;align-items:center;gap:10px;margin-bottom:14px;padding-bottom:12px;border-bottom:1px solid var(--border);flex-wrap:wrap}
.card-head svg{width:20px;height:20px;stroke:var(--primary);flex-shrink:0;stroke-width:2}
.card-head h3{font-size:.98rem;font-weight:700}
.card-head .badge{margin-inline-start:auto;font-size:.72rem;padding:3px 12px;background:rgba(91,141,239,.12);color:var(--primary);border-radius:20px;font-weight:700}
.table-wrap{overflow-x:auto;border-radius:10px;-webkit-overflow-scrolling:touch}
table{width:100%;border-collapse:collapse;font-size:.82rem;min-width:720px}
thead th{padding:10px 12px;text-align:start;background:var(--surface-2);color:var(--muted);font-weight:700;font-size:.72rem;text-transform:uppercase;letter-spacing:.3px;border-bottom:1px solid var(--border);white-space:nowrap}
tbody td{padding:10px 12px;border-bottom:1px solid rgba(31,41,64,.4);vertical-align:middle}
tbody tr:hover td{background:rgba(91,141,239,.05)}
tbody tr:last-child td{border-bottom:none}
td.num,th.num{direction:ltr;text-align:start;font-family:'Courier New',monospace}
.pill{display:inline-block;padding:3px 10px;border-radius:14px;font-size:.72rem;font-weight:700;direction:ltr}
.pill.running,.pill.healthy{background:rgba(16,185,129,.15);color:var(--success)}
.pill.stopped,.pill.warning{background:rgba(245,158,11,.15);color:var(--warning)}
.pill.error,.pill.unhealthy{background:rgba(239,68,68,.15);color:var(--danger)}
.pill.unknown,.pill.info{background:rgba(120,120,120,.15);color:var(--muted)}
.pill.gost{background:rgba(91,141,239,.15);color:var(--primary)}
.pill.rathole{background:rgba(124,92,255,.15);color:var(--primary-2)}
.pill.hysteria2{background:rgba(16,185,129,.15);color:var(--success)}
.pill.chisel{background:rgba(6,182,212,.15);color:var(--info)}
.pill.frp{background:rgba(245,158,11,.15);color:var(--warning)}
.pill.paqet{background:rgba(239,68,68,.15);color:var(--danger)}
.pill.backhaul{background:rgba(168,85,247,.15);color:#a855f7}
.pill.wstunnel{background:rgba(236,72,153,.15);color:#ec4899}
.pill.socat,.pill.ssh,.pill.iptables{background:rgba(107,114,128,.15);color:#6b7280}
.form-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px}
.form-grid .full{grid-column:1/-1}
.tunnel-info{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px;margin-bottom:14px}
.info-item{padding:10px 12px;background:var(--surface-2);border:1px solid var(--border);border-radius:10px}
.info-item .lbl{font-size:.7rem;color:var(--muted);font-weight:600;margin-bottom:4px}
.info-item .val{font-size:.85rem;font-weight:700;direction:ltr;text-align:start;font-family:'Courier New',monospace;word-break:break-all}
.modal-bg{position:fixed;inset:0;background:rgba(0,0,0,.7);backdrop-filter:blur(4px);z-index:500;display:none;align-items:center;justify-content:center;padding:16px}
.modal-bg.open{display:flex}
.modal{background:var(--surface);border:1px solid var(--border);border-radius:16px;width:100%;max-width:720px;max-height:92vh;display:flex;flex-direction:column;box-shadow:var(--shadow);animation:pop .25s}
.modal.wide{max-width:960px}
.modal-head{padding:14px 18px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;gap:10px;flex-shrink:0}
.modal-head h3{font-size:.98rem;font-weight:700;display:flex;align-items:center;gap:8px}
.modal-head h3 svg{width:18px;height:18px;stroke:var(--primary)}
.modal-body{padding:18px;overflow-y:auto;flex:1}
.modal-foot{padding:12px 18px;border-top:1px solid var(--border);display:flex;gap:8px;justify-content:flex-end;flex-shrink:0;flex-wrap:wrap}
.code-block{background:#06090f;border:1px solid var(--border);border-radius:10px;padding:12px;font-family:'Courier New',monospace;font-size:.8rem;direction:ltr;text-align:left;white-space:pre-wrap;word-break:break-all;color:#86efac;max-height:280px;overflow-y:auto;line-height:1.7;position:relative}
.toasts{position:fixed;bottom:16px;inset-inline-start:16px;display:flex;flex-direction:column;gap:8px;z-index:2000;max-width:calc(100vw - 32px)}
.toast{background:var(--surface);border:1px solid var(--border);border-inline-start:3px solid var(--primary);border-radius:10px;padding:11px 14px;box-shadow:var(--shadow);display:flex;align-items:center;gap:10px;animation:slideIn .3s;font-size:.82rem;min-width:220px}
@keyframes slideIn{from{transform:translateX(var(--tx,-30px));opacity:0}to{transform:translateX(0);opacity:1}}
.toast.success{border-inline-start-color:var(--success)}.toast.error{border-inline-start-color:var(--danger)}
.toast.warning{border-inline-start-color:var(--warning)}
.toast svg{width:18px;height:18px;flex-shrink:0;stroke-width:2}
.toast.success svg{stroke:var(--success)}.toast.error svg{stroke:var(--danger)}
.toast.warning svg{stroke:var(--warning)}.toast.info svg{stroke:var(--primary)}
.search-bar{display:flex;gap:8px;margin-bottom:14px;flex-wrap:wrap}
.search-bar input,.search-bar select{padding:9px 12px;background:var(--surface-2);border:1px solid var(--border);border-radius:10px;color:var(--text);font-size:.82rem}
.search-bar input{flex:1;min-width:160px}
.checkbox-col{width:32px;text-align:center}
input[type=checkbox]{width:16px;height:16px;cursor:pointer;accent-color:var(--primary)}
.mobile-toggle{display:none}
.sidebar-backdrop{display:none;position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:150}
.sidebar-backdrop.show{display:block}
.tabs{display:flex;gap:4px;border-bottom:1px solid var(--border);margin-bottom:14px;overflow-x:auto}
.tab{padding:8px 14px;cursor:pointer;font-size:.82rem;font-weight:600;color:var(--muted);border-bottom:2px solid transparent;white-space:nowrap;transition:all .15s}
.tab.active{color:var(--primary);border-bottom-color:var(--primary)}
.tab:hover{color:var(--text)}
.footer{text-align:center;padding:14px;color:var(--muted);font-size:.75rem}
.footer a{color:var(--primary);text-decoration:none}
.alert{padding:10px 14px;border-radius:10px;margin-bottom:14px;font-size:.82rem;line-height:1.8}
.alert-warning{background:rgba(245,158,11,.12);border:1px solid rgba(245,158,11,.3);color:var(--warning)}
.alert-danger{background:rgba(239,68,68,.12);border:1px solid rgba(239,68,68,.3);color:var(--danger)}
.alert-info{background:rgba(6,182,212,.12);border:1px solid rgba(6,182,212,.3);color:var(--info)}
.alert-success{background:rgba(16,185,129,.12);border:1px solid rgba(16,185,129,.3);color:var(--success)}
.pw-strength{height:4px;background:var(--border);border-radius:2px;margin-top:6px;overflow:hidden}
.pw-strength-bar{height:100%;transition:all .3s;border-radius:2px}
.lang-switch{display:flex;gap:4px;background:var(--surface-2);padding:3px;border-radius:10px;border:1px solid var(--border)}
.lang-btn{padding:5px 10px;border:none;background:transparent;color:var(--muted);cursor:pointer;border-radius:7px;font-size:.75rem;font-weight:700;transition:all .15s}
.lang-btn.active{background:var(--primary);color:#fff}
.update-banner{background:linear-gradient(135deg,rgba(16,185,129,.15),rgba(6,182,212,.15));border:1px solid var(--success);border-radius:12px;padding:12px 16px;margin-bottom:16px;display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.update-banner svg{width:24px;height:24px;stroke:var(--success);flex-shrink:0}
.update-banner .txt{flex:1;min-width:200px}
.update-banner .txt strong{display:block;color:var(--success);font-size:.85rem}
.update-banner .txt span{font-size:.75rem;color:var(--text-2)}
@media(max-width:900px){
.sidebar{position:fixed;top:0;inset-inline-end:0;bottom:0;transform:translateX(100%);box-shadow:-10px 0 40px rgba(0,0,0,.5)}
[dir="rtl"] .sidebar{transform:translateX(-100%)}
.sidebar.open{transform:translateX(0)!important}
.mobile-toggle{display:flex}
.content{padding:12px}
.stats-grid{grid-template-columns:1fr 1fr;gap:10px}
.stat-val{font-size:1.4rem}.stat{padding:12px}
.form-grid{grid-template-columns:1fr}
.tunnel-info{grid-template-columns:1fr}
.modal{max-height:95vh}
}
@media(max-width:500px){
.stats-grid{grid-template-columns:1fr}
.topbar{padding:10px 12px}.topbar h2{font-size:.9rem}
.card{padding:14px}
.modal-body{padding:14px}
}
</style>
</head>
<body>

<div id="auth">
  <div class="auth-card">
    <div class="auth-logo">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 21v-7a4 4 0 0 1 4-4h8a4 4 0 0 1 4 4v7"/><path d="M12 3v7"/><circle cx="12" cy="12" r="2"/></svg>
    </div>
    <h1>NexTunnel</h1>
    <div class="sub" id="auth-sub" data-i18n="loginSub">Sign in to continue</div>
    <div class="lang-switch" style="width:fit-content;margin:0 auto 16px">
      <button class="lang-btn" onclick="setLang('en')" id="lang-en">EN</button>
      <button class="lang-btn" onclick="setLang('fa')" id="lang-fa">FA</button>
    </div>
    <div class="err" id="auth-err"></div>

    <div id="login-form">
      <div class="field mono"><label data-i18n="username">Username</label>
        <input type="text" id="login-user" autocomplete="username" dir="ltr">
      </div>
      <div class="field mono"><label data-i18n="password">Password</label>
        <input type="password" id="login-pass" autocomplete="current-password" onkeydown="if(event.key==='Enter')doLogin()" dir="ltr">
      </div>
      <button class="btn btn-primary btn-full" onclick="doLogin()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
        <span data-i18n="login">Login</span>
      </button>
    </div>

    <div id="change-pw-form" style="display:none">
      <div class="alert alert-warning" data-i18n="mustChangePw">⚠️ For security, you must change your password.</div>
      <div class="field mono"><label data-i18n="newPassword">New Password</label>
        <input type="password" id="new-pw1" dir="ltr" oninput="checkPwStrength('new-pw1','pw1-bar')">
        <div class="pw-strength"><div class="pw-strength-bar" id="pw1-bar"></div></div>
      </div>
      <div class="field mono"><label data-i18n="confirmPassword">Confirm Password</label>
        <input type="password" id="new-pw2" dir="ltr" onkeydown="if(event.key==='Enter')doChangePassword()">
      </div>
      <button class="btn btn-primary btn-full" onclick="doChangePassword()" data-i18n="savePassword">Save New Password</button>
    </div>

    <div class="footer" style="margin-top:16px">
      <span data-i18n="madeBy">Made by</span> <a href="https://github.com/metiwilson" target="_blank">metiwilson</a>
    </div>
  </div>
</div>

<div id="app">
  <div class="sidebar-backdrop" id="sb-backdrop" onclick="closeSidebar()"></div>
  <aside class="sidebar" id="sidebar">
    <div class="brand">
      <div class="brand-logo">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 21v-7a4 4 0 0 1 4-4h8a4 4 0 0 1 4 4v7"/><path d="M12 3v7"/><circle cx="12" cy="12" r="2"/></svg>
      </div>
      <div class="brand-text">
        <h1>NexTunnel</h1>
        <div class="ver">v1.1.1</div>
      </div>
    </div>
    <nav class="nav" id="nav">
      <div class="nav-item active" data-page="dashboard">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="9"/><rect x="14" y="3" width="7" height="5"/><rect x="14" y="12" width="7" height="9"/><rect x="3" y="16" width="7" height="5"/></svg>
        <span data-i18n="dashboard">Dashboard</span>
      </div>
      <div class="nav-item" data-page="tunnels">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 21v-7a4 4 0 0 1 4-4h8a4 4 0 0 1 4 4v7"/><path d="M12 3v7"/><circle cx="12" cy="12" r="2"/></svg>
        <span data-i18n="tunnels">Tunnels</span> <span class="badge" id="nav-tunnel-count">0</span>
      </div>
      <div class="nav-item" data-page="create">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        <span data-i18n="create">Create</span>
      </div>
      <div class="nav-item" data-page="tools">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>
        <span data-i18n="tools">Tools</span>
      </div>
      <div class="nav-item" data-page="isp">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
        <span data-i18n="isp">ISP Profiles</span>
      </div>
      <div class="nav-item" data-page="sessions">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
        <span data-i18n="sessions">Sessions</span>
      </div>
      <div class="nav-item" data-page="logs">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        <span data-i18n="logs">Logs</span>
      </div>
      <div class="nav-item" data-page="settings">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
        <span data-i18n="settings">Settings</span>
      </div>
    </nav>
    <div class="sidebar-footer">
      <div style="display:flex;gap:6px;margin-bottom:8px">
        <button class="btn btn-ghost btn-sm" style="flex:1" onclick="toggleTheme()" title="Theme">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
        </button>
        <button class="btn btn-ghost btn-sm" style="flex:1" onclick="setLang(LANG==='fa'?'en':'fa')" title="Language">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
        </button>
        <button class="btn btn-danger btn-sm" style="flex:1" onclick="doLogout()" title="Logout">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
        </button>
      </div>
      <div style="font-size:.68rem;color:var(--muted);text-align:center;direction:ltr">
        <span id="sidebar-user">-</span>
      </div>
    </div>
  </aside>

  <main class="main">
    <div class="topbar">
      <h2>
        <button class="btn btn-icon mobile-toggle" onclick="openSidebar()">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
        </button>
        <span id="page-title" data-i18n="dashboard">Dashboard</span>
      </h2>
      <div class="topbar-actions">
        <button class="btn btn-ghost btn-sm" onclick="refreshCurrent()">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>
          <span data-i18n="refresh">Refresh</span>
        </button>
      </div>
    </div>
    <div class="content" id="content"></div>
  </main>
</div>

<div class="modal-bg" id="modal">
  <div class="modal" id="modal-inner">
    <div class="modal-head">
      <h3 id="modal-title">Details</h3>
      <button class="btn btn-icon" onclick="closeModal()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </div>
    <div class="modal-body" id="modal-body"></div>
    <div class="modal-foot" id="modal-foot"></div>
  </div>
</div>

<div class="toasts" id="toasts"></div>

<script>
// ═══════════ I18N ═══════════
const I18N = {
  en: {
    dashboard:'Dashboard', tunnels:'Tunnels', create:'Create', tools:'Tools', isp:'ISP Profiles',
    sessions:'Sessions', logs:'Logs', settings:'Settings', refresh:'Refresh', login:'Login',
    username:'Username', password:'Password', loginSub:'Sign in to continue',
    mustChangePw:'⚠️ For security, you must change your password.',
    newPassword:'New Password', confirmPassword:'Confirm Password', savePassword:'Save New Password',
    madeBy:'Made by', totalTunnels:'Total Tunnels', running:'Running', healthy:'Healthy',
    stopped:'Stopped', publicIP:'Public IP', systemInfo:'System Info', xuiStatus:'3x-ui Status',
    inboundCount:'Inbound Count', rootAccess:'Root Access', localIP:'Local IP', serverTime:'Server Time',
    yes:'Yes', no:'No', installed:'Installed', notInstalled:'Not Installed', has:'Has', noAccess:'No',
    searchPlaceholder:'Search (name or IP)...', allProtocols:'All Protocols', allStatus:'All Status',
    name:'Name', protocol:'Protocol', transport:'Transport', port:'Port', kharej:'Kharej',
    status:'Status', health:'Health', actions:'Actions', start:'Start', stop:'Stop', restart:'Restart',
    delete:'Delete', viewConfig:'Config', checkHealth:'Check', ping:'Ping', bulkActions:'Bulk Actions',
    selected:'selected', cancel:'Cancel', deleteAll:'Delete All', noTunnels:'No tunnels yet',
    noResults:'No results', createFirst:'Create First Tunnel',
    tunnelName:'Tunnel Name', iranPort:'Iran Port', kharejIP:'Kharej IP', kharejPort:'Kharej Port',
    coverSNI:'Cover SNI (optional)', tags:'Tags (optional)', notes:'Notes', createTunnel:'Create Tunnel',
    ispProfile:'ISP Profile', autoDetect:'Auto-detect', recommended:'Recommended',
    apply:'Apply', toolInstall:'Install Tools', install:'Install', installed_short:'Installed',
    notInstalled_short:'Not Installed', ispProfiles:'ISP Profiles', addCustomISP:'Add Custom ISP Profile',
    sessions_active:'Active Sessions', current:'Current', revoke:'Revoke', revokeAll:'Revoke All Others',
    logs_system:'System Logs', clearLogs:'Clear Logs', level:'Level', message:'Message',
    tunnel:'Tunnel', time:'Time', noLogs:'No logs',
    accountInfo:'Account Info', changePassword:'Change Password', currentPw:'Current Password',
    newPw:'New Password', confirmNewPw:'Confirm New Password', saveUsername:'Save Username',
    changePwBtn:'Change Password', serverSettings:'Server Settings',
    publicIPLabel:'Public IP (for configs)', autoRestartInterval:'Auto-Restart Interval (seconds)',
    save:'Save', redetectIP:'Re-detect IP', backup:'Backup', backupDesc:'Download full backup of tunnels and settings',
    downloadBackup:'Download JSON Backup', configKharej:'Kharej Server Config (run on foreign server)',
    configIran:'Iran Server Config (run locally)', xuiIntegration:'X-UI Integration',
    copyKharej:'Copy Kharej', copyIran:'Copy Iran', copyXui:'Copy X-UI', close:'Close',
    updateAvailable:'Update Available', newVersion:'New version', viewUpdate:'View Update',
    uptime:'Uptime', cpu:'CPU', ram:'RAM', disk:'Disk', load:'Load', netRx:'Net RX', netTx:'Net TX',
    confirmDelete:'Delete this tunnel?', confirmDeleteAll:'Delete', tunnels_q:'tunnels?',
    confirmRevoke:'Revoke this session?', confirmRevokeAll:'Revoke all other sessions?',
    confirmClearLogs:'Clear all logs?', copied:'Copied!', copyFailed:'Copy failed',
    pinging:'Pinging...', reachable:'Reachable', notReachable:'Not reachable',
    tunnelStarted:'Tunnel started', tunnelStopped:'Tunnel stopped', tunnelCreated:'Tunnel created',
    tunnelDeleted:'Deleted', healthOK:'Healthy', healthBad:'Unhealthy',
    enterName:'Enter tunnel name', enterKharejIP:'Enter Kharej IP',
    allFieldsRequired:'All fields required', passwordMin:'Password must be at least 8 chars',
    passwordsMatch:'Passwords do not match', saved:'Saved', error:'Error',
    bulkStart:'Start All', bulkStop:'Stop All', bulkRestart:'Restart', bulkDelete:'Delete All',
    clearSelection:'Cancel', itemsCount:'items', sessionNote:'Session stays active — no expiry.',
  },
  fa: {
    dashboard:'داشبورد', tunnels:'تانل‌ها', create:'ایجاد تانل', tools:'ابزارها', isp:'پروفایل‌های ISP',
    sessions:'نشست‌ها', logs:'لاگ‌ها', settings:'تنظیمات', refresh:'بروزرسانی', login:'ورود',
    username:'نام کاربری', password:'رمز عبور', loginSub:'برای ادامه وارد شوید',
    mustChangePw:'⚠️ برای امنیت، باید رمز عبور خود را تغییر دهید.',
    newPassword:'رمز عبور جدید', confirmPassword:'تکرار رمز عبور', savePassword:'ذخیره رمز جدید',
    madeBy:'سازنده:', totalTunnels:'کل تانل‌ها', running:'فعال', healthy:'سالم',
    stopped:'متوقف', publicIP:'آی‌پی عمومی', systemInfo:'اطلاعات سیستم', xuiStatus:'وضعیت 3x-ui',
    inboundCount:'تعداد Inbound', rootAccess:'دسترسی Root', localIP:'آی‌پی محلی', serverTime:'زمان سرور',
    yes:'بله', no:'خیر', installed:'نصب شده', notInstalled:'نصب نشده', has:'دارد', noAccess:'ندارد',
    searchPlaceholder:'جستجو (نام یا IP)...', allProtocols:'همه پروتکل‌ها', allStatus:'همه وضعیت‌ها',
    name:'نام', protocol:'پروتکل', transport:'ترنسپورت', port:'پورت', kharej:'خارج',
    status:'وضعیت', health:'سلامت', actions:'عملیات', start:'اجرا', stop:'توقف', restart:'ریستارت',
    delete:'حذف', viewConfig:'کانفیگ', checkHealth:'بررسی', ping:'پینگ', bulkActions:'عملیات گروهی',
    selected:'انتخاب شده', cancel:'لغو', deleteAll:'حذف همه', noTunnels:'هنوز تانلی نیست',
    noResults:'نتیجه‌ای یافت نشد', createFirst:'ایجاد اولین تانل',
    tunnelName:'نام تانل', iranPort:'پورت ایران', kharejIP:'آی‌پی خارج', kharejPort:'پورت خارج',
    coverSNI:'Cover SNI (اختیاری)', tags:'تگ‌ها (اختیاری)', notes:'توضیحات', createTunnel:'ایجاد تانل',
    ispProfile:'پروفایل ISP', autoDetect:'تشخیص خودکار', recommended:'پیشنهادی',
    apply:'اعمال', toolInstall:'نصب ابزارها', install:'نصب', installed_short:'نصب',
    notInstalled_short:'نیست', ispProfiles:'پروفایل‌های ISP', addCustomISP:'افزودن پروفایل سفارشی',
    sessions_active:'نشست‌های فعال', current:'فعلی', revoke:'لغو', revokeAll:'لغو همه دیگران',
    logs_system:'لاگ‌های سیستم', clearLogs:'پاک‌سازی لاگ‌ها', level:'سطح', message:'پیام',
    tunnel:'تانل', time:'زمان', noLogs:'لاگی نیست',
    accountInfo:'اطلاعات کاربری', changePassword:'تغییر رمز عبور', currentPw:'رمز فعلی',
    newPw:'رمز جدید', confirmNewPw:'تکرار رمز جدید', saveUsername:'ذخیره نام کاربری',
    changePwBtn:'تغییر رمز', serverSettings:'تنظیمات سرور',
    publicIPLabel:'آی‌پی عمومی (برای کانفیگ)', autoRestartInterval:'بازه Auto-Restart (ثانیه)',
    save:'ذخیره', redetectIP:'تشخیص مجدد IP', backup:'پشتیبان‌گیری', backupDesc:'دریافت نسخه پشتیبان از تانل‌ها و تنظیمات',
    downloadBackup:'دانلود پشتیبان JSON', configKharej:'کانفیگ سرور خارج (روی سرور خارجی اجرا شود)',
    configIran:'کانفیگ سرور ایران (اجرای محلی)', xuiIntegration:'یکپارچه‌سازی X-UI',
    copyKharej:'کپی خارج', copyIran:'کپی ایران', copyXui:'کپی X-UI', close:'بستن',
    updateAvailable:'بروزرسانی موجود', newVersion:'نسخه جدید', viewUpdate:'مشاهده بروزرسانی',
    uptime:'آپ‌تایم', cpu:'پردازنده', ram:'حافظه', disk:'دیسک', load:'لود', netRx:'دریافت', netTx:'ارسال',
    confirmDelete:'حذف این تانل؟', confirmDeleteAll:'حذف', tunnels_q:'تانل؟',
    confirmRevoke:'لغو این نشست؟', confirmRevokeAll:'لغو همه نشست‌های دیگر؟',
    confirmClearLogs:'پاک کردن همه لاگ‌ها؟', copied:'کپی شد!', copyFailed:'کپی ناموفق',
    pinging:'در حال پینگ...', reachable:'پاسخ دارد', notReachable:'بدون پاسخ',
    tunnelStarted:'تانل فعال شد', tunnelStopped:'تانل متوقف شد', tunnelCreated:'تانل ایجاد شد',
    tunnelDeleted:'حذف شد', healthOK:'سالم', healthBad:'ناسالم',
    enterName:'نام تانل را وارد کنید', enterKharejIP:'آی‌پی خارج را وارد کنید',
    allFieldsRequired:'همه فیلدها الزامی است', passwordMin:'رمز حداقل ۸ کاراکتر',
    passwordsMatch:'رمزها یکسان نیستند', saved:'ذخیره شد', error:'خطا',
    bulkStart:'اجرای همه', bulkStop:'توقف همه', bulkRestart:'ریستارت', bulkDelete:'حذف همه',
    clearSelection:'لغو', itemsCount:'مورد', sessionNote:'نشست فعال می‌ماند — بدون انقضا.',
  }
};
let LANG = localStorage.getItem('lang') || 'en';
function setLang(l){
  LANG = l;
  localStorage.setItem('lang', l);
  document.documentElement.lang = l;
  document.documentElement.dir = l === 'fa' ? 'rtl' : 'ltr';
  document.getElementById('lang-en').classList.toggle('active', l === 'en');
  document.getElementById('lang-fa').classList.toggle('active', l === 'fa');
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const k = el.dataset.i18n;
    if (I18N[l][k]) el.textContent = I18N[l][k];
  });
  if (CSRF) api('/api/settings/language', {method:'POST', body: JSON.stringify({language:l})});
  if (document.getElementById('app').classList.contains('show')) refreshCurrent();
}
function t(k){ return I18N[LANG][k] || k; }

// ═══════════ HELPERS ═══════════
const $ = id => document.getElementById(id);
const esc = s => { const d = document.createElement('div'); d.textContent = String(s ?? ''); return d.innerHTML; };
let CSRF = '';

async function api(path, opts={}) {
  try {
    const headers = { 'Content-Type': 'application/json' };
    if (CSRF && opts.method && opts.method !== 'GET') headers['X-CSRF-Token'] = CSRF;
    const r = await fetch(path, { credentials:'same-origin', ...opts, headers: { ...headers, ...(opts.headers||{}) }});
    if (r.status === 401) return {ok:false, error:'unauthorized'};
    const data = await r.json().catch(()=>({ok:false,error:'invalid json'}));
    return data;
  } catch(e) { return {ok:false, error:e.message}; }
}

function fmtDate(ts) {
  if (!ts) return '-';
  const d = new Date(ts*1000);
  return d.toLocaleString(LANG === 'fa' ? 'fa-IR' : 'en-US',
    {year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit'});
}
function fmtUptime(s) {
  const d = Math.floor(s/86400), h = Math.floor(s%86400/3600), m = Math.floor(s%3600/60);
  if (d) return `${d}d ${h}h`;
  if (h) return `${h}h ${m}m`;
  return `${m}m`;
}
function toast(msg, type='info') {
  const icons = {
    success:'<polyline points="20 6 9 17 4 12"/>',
    error:'<circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>',
    warning:'<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
    info:'<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>'
  };
  const el = document.createElement('div');
  el.className = 'toast ' + type;
  el.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round">${icons[type]||icons.info}</svg><div>${esc(msg)}</div>`;
  $('toasts').appendChild(el);
  setTimeout(()=>{el.style.transition='all .3s';el.style.opacity='0';el.style.transform='translateX(-30px)';setTimeout(()=>el.remove(),300)},3500);
}
function toggleTheme(){const c=document.documentElement.getAttribute('data-theme');const n=c==='dark'?'light':'dark';document.documentElement.setAttribute('data-theme',n);localStorage.setItem('theme',n)}
(function(){const th=localStorage.getItem('theme');if(th)document.documentElement.setAttribute('data-theme',th);setLang(LANG);})();
function copyToClipboard(text){navigator.clipboard.writeText(text).then(()=>toast(t('copied'),'success')).catch(()=>toast(t('copyFailed'),'error'))}
function openSidebar(){$('sidebar').classList.add('open');$('sb-backdrop').classList.add('show')}
function closeSidebar(){$('sidebar').classList.remove('open');$('sb-backdrop').classList.remove('show')}

function resetSessionTimer() { /* disabled */ }
function startSessionTimer() { /* disabled */ }

// ═══════════ AUTH ═══════════
let PENDING_USER = '';
async function doLogin() {
  const username = $('login-user').value.trim();
  const password = $('login-pass').value;
  if (!username || !password) { $('auth-err').textContent = t('allFieldsRequired'); return; }
  const r = await api('/api/login', {method:'POST', body: JSON.stringify({username, password, language:LANG})});
  if (!r.ok) { $('auth-err').textContent = r.error || 'Login failed'; return; }
  if (r.must_change_password) {
    PENDING_USER = username;
    CSRF = r.csrf_token || '';
    $('login-form').style.display = 'none';
    $('change-pw-form').style.display = 'block';
    $('auth-sub').textContent = t('mustChangePw');
    return;
  }
  CSRF = r.csrf_token;
  enterApp(r.user || {});
}
async function doChangePassword() {
  const pw1 = $('new-pw1').value;
  const pw2 = $('new-pw2').value;
  if (pw1.length < 8) { $('auth-err').textContent = t('passwordMin'); return; }
  if (pw1 !== pw2) { $('auth-err').textContent = t('passwordsMatch'); return; }
  const r = await api('/api/change-password', {method:'POST', body: JSON.stringify({new_password: pw1, force: true})});
  if (!r.ok) { $('auth-err').textContent = r.error || t('error'); return; }
  toast(t('saved'), 'success');
  const r2 = await api('/api/check');
  if (r2.ok) { CSRF = r2.csrf_token; enterApp(r2.user || {}); }
}
function checkPwStrength(inputId, barId) {
  const pw = $(inputId).value;
  let score = 0;
  if (pw.length >= 8) score++;
  if (pw.length >= 12) score++;
  if (/[A-Z]/.test(pw)) score++;
  if (/[0-9]/.test(pw)) score++;
  if (/[^A-Za-z0-9]/.test(pw)) score++;
  const pct = (score / 5) * 100;
  const color = score <= 2 ? '#ef4444' : score <= 3 ? '#f59e0b' : '#10b981';
  const bar = $(barId);
  bar.style.width = pct + '%';
  bar.style.background = color;
}
async function doLogout() {
  await api('/api/logout', {method:'POST'});
  location.reload();
}
async function checkAuth() {
  const r = await api('/api/check');
  if (r.ok) { CSRF = r.csrf_token; enterApp(r.user || {}); }
}
function enterApp(user) {
  $('auth').style.display = 'none';
  $('app').classList.add('show');
  $('sidebar-user').textContent = user.username ? '@' + user.username : '';
  loadDashboard();
}

// ═══════════ NAV ═══════════
const PAGE_LOADERS = {
  dashboard: loadDashboard,
  tunnels: loadTunnels,
  create: loadCreateForm,
  tools: loadTools,
  isp: loadIspPage,
  sessions: loadSessions,
  logs: loadLogs,
  settings: loadSettings,
};
document.querySelectorAll('.nav-item').forEach(n => n.addEventListener('click', () => {
  document.querySelectorAll('.nav-item').forEach(x => x.classList.remove('active'));
  n.classList.add('active');
  const page = n.dataset.page;
  const k = n.querySelector('[data-i18n]')?.dataset.i18n || 'dashboard';
  $('page-title').textContent = t(k);
  $('page-title').dataset.i18n = k;
  closeSidebar();
  if (PAGE_LOADERS[page]) PAGE_LOADERS[page]();
}));
function refreshCurrent() {
  const active = document.querySelector('.nav-item.active')?.dataset.page;
  if (PAGE_LOADERS[active]) PAGE_LOADERS[active]();
}

// ═══════════ DASHBOARD ═══════════
async function loadDashboard() {
  const r = await api('/api/stats');
  if (!r.ok) return;
  const d = r.stats;
  const s = d.system;
  let updateBanner = '';
  if (d.update && d.update.available) {
    updateBanner = `
      <div class="update-banner">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
        <div class="txt">
          <strong>${t('updateAvailable')} — v${esc(d.update.latest)}</strong>
          <span>${t('newVersion')}: ${esc(d.update.current)} → ${esc(d.update.latest)}</span>
        </div>
        <a href="${esc(d.update.url)}" target="_blank" class="btn btn-primary btn-sm">${t('viewUpdate')}</a>
      </div>`;
  }
  $('content').innerHTML = `
    ${updateBanner}
    <div class="stats-grid">
      <div class="stat total">
        <div class="stat-head"><div class="stat-ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M4 21v-7a4 4 0 0 1 4-4h8a4 4 0 0 1 4 4v7"/><path d="M12 3v7"/><circle cx="12" cy="12" r="2"/></svg></div>
        <div class="stat-label">${t('totalTunnels')}</div></div>
        <div class="stat-val">${d.total_tunnels}</div>
        <div class="stat-sub">Total</div>
      </div>
      <div class="stat running">
        <div class="stat-head"><div class="stat-ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><polyline points="20 6 9 17 4 12"/></svg></div>
        <div class="stat-label">${t('running')}</div></div>
        <div class="stat-val" style="color:var(--success)">${d.running_tunnels}</div>
        <div class="stat-sub">Running</div>
      </div>
      <div class="stat healthy">
        <div class="stat-head"><div class="stat-ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg></div>
        <div class="stat-label">${t('healthy')}</div></div>
        <div class="stat-val" style="color:var(--success)">${d.healthy_tunnels}</div>
        <div class="stat-sub">Healthy</div>
      </div>
      <div class="stat stopped">
        <div class="stat-head"><div class="stat-ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><rect x="6" y="6" width="12" height="12" rx="2"/></svg></div>
        <div class="stat-label">${t('stopped')}</div></div>
        <div class="stat-val" style="color:var(--warning)">${d.stopped_tunnels}</div>
        <div class="stat-sub">Stopped</div>
      </div>
    </div>

    <div class="card">
      <div class="card-head">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
        <h3>${t('systemInfo')}</h3>
        <span class="badge">${esc(d.os_info)}</span>
      </div>
      <div class="stats-grid" style="margin-bottom:0">
        <div class="stat info">
          <div class="stat-head"><div class="stat-ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg></div>
          <div class="stat-label">${t('cpu')}</div></div>
          <div class="stat-val" style="font-size:1.4rem">${s.cpu}%</div>
          <div class="progress"><div class="progress-bar" style="width:${s.cpu}%"></div></div>
        </div>
        <div class="stat info">
          <div class="stat-head"><div class="stat-ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><rect x="3" y="4" width="18" height="16" rx="2"/><line x1="3" y1="10" x2="21" y2="10"/></svg></div>
          <div class="stat-label">${t('ram')}</div></div>
          <div class="stat-val" style="font-size:1.4rem">${s.ram}%</div>
          <div class="stat-sub">${s.ram_used} / ${s.ram_total} MB</div>
          <div class="progress"><div class="progress-bar" style="width:${s.ram}%"></div></div>
        </div>
        <div class="stat info">
          <div class="stat-head"><div class="stat-ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/><path d="M3 12c0 1.66 4 3 9 3s9-1.34 9-3"/></svg></div>
          <div class="stat-label">${t('disk')}</div></div>
          <div class="stat-val" style="font-size:1.4rem">${s.disk}%</div>
          <div class="stat-sub">${s.disk_used} / ${s.disk_total} GB</div>
          <div class="progress"><div class="progress-bar" style="width:${s.disk}%"></div></div>
        </div>
        <div class="stat info">
          <div class="stat-head"><div class="stat-ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg></div>
          <div class="stat-label">${t('uptime')}</div></div>
          <div class="stat-val" style="font-size:1.2rem">${fmtUptime(s.uptime)}</div>
          <div class="stat-sub">Load: ${s.load.map(x=>x.toFixed(2)).join(' / ')}</div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-head">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
        <h3>${t('xuiStatus')}</h3>
        <span class="badge" style="background:${d.xui_installed?'rgba(16,185,129,.15)':'rgba(239,68,68,.15)'};color:${d.xui_installed?'var(--success)':'var(--danger)'}">${d.xui_installed?t('yes'):t('no')}</span>
      </div>
      <div class="tunnel-info">
        <div class="info-item"><div class="lbl">${t('xuiStatus')}</div><div class="val" style="color:${d.xui_installed?'var(--success)':'var(--danger)'}">${d.xui_installed?t('installed'):t('notInstalled')}</div></div>
        <div class="info-item"><div class="lbl">${t('inboundCount')}</div><div class="val">${d.xui_inbound_count}</div></div>
        <div class="info-item"><div class="lbl">${t('rootAccess')}</div><div class="val" style="color:${d.root_access?'var(--success)':'var(--warning)'}">${d.root_access?t('has'):t('noAccess')}</div></div>
        <div class="info-item"><div class="lbl">${t('localIP')}</div><div class="val">${esc(d.local_ip)}</div></div>
        <div class="info-item"><div class="lbl">${t('publicIP')}</div><div class="val">${esc(d.server_ip)}</div></div>
        <div class="info-item"><div class="lbl">${t('serverTime')}</div><div class="val">${esc(d.server_time)}</div></div>
      </div>
    </div>

    <div class="footer">NexTunnel v${esc(d.version)} — ${t('madeBy')} <a href="https://github.com/metiwilson" target="_blank">metiwilson</a></div>
  `;
}

// ═══════════ TUNNELS ═══════════
let tunnelState = {search:'', protocol:'all', status:'all', selected:new Set()};
async function loadTunnels() {
  const params = new URLSearchParams();
  if (tunnelState.search) params.set('search', tunnelState.search);
  if (tunnelState.protocol !== 'all') params.set('protocol', tunnelState.protocol);
  if (tunnelState.status !== 'all') params.set('status', tunnelState.status);
  const r = await api('/api/tunnels?' + params.toString());
  if (!r.ok) return;
  const tunnels = r.tunnels || [];
  $('nav-tunnel-count').textContent = tunnels.length;

  $('content').innerHTML = `
    <div class="card">
      <div class="card-head">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 21v-7a4 4 0 0 1 4-4h8a4 4 0 0 1 4 4v7"/><path d="M12 3v7"/><circle cx="12" cy="12" r="2"/></svg>
        <h3>${t('tunnels')}</h3>
        <span class="badge">${tunnels.length}</span>
      </div>
      <div class="search-bar">
        <input type="text" id="search-in" placeholder="${t('searchPlaceholder')}" value="${esc(tunnelState.search)}" oninput="onSearchChange(this.value)">
        <select id="proto-filter" onchange="onFilterChange('protocol', this.value)">
          <option value="all">${t('allProtocols')}</option>
          ${['gost','rathole','hysteria2','chisel','frp','paqet','backhaul','wstunnel','socat','ssh','iptables'].map(p=>`<option value="${p}" ${tunnelState.protocol===p?'selected':''}>${p.toUpperCase()}</option>`).join('')}
        </select>
        <select id="status-filter" onchange="onFilterChange('status', this.value)">
          <option value="all">${t('allStatus')}</option>
          <option value="running" ${tunnelState.status==='running'?'selected':''}>${t('running')}</option>
          <option value="stopped" ${tunnelState.status==='stopped'?'selected':''}>${t('stopped')}</option>
        </select>
      </div>
      ${tunnelState.selected.size > 0 ? `
      <div class="alert alert-info" style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px">
        <span>${tunnelState.selected.size} ${t('selected')}</span>
        <div style="display:flex;gap:6px;flex-wrap:wrap">
          <button class="btn btn-success btn-sm" onclick="doBulk('start')">${t('bulkStart')}</button>
          <button class="btn btn-warning btn-sm" onclick="doBulk('stop')">${t('bulkStop')}</button>
          <button class="btn btn-ghost btn-sm" onclick="doBulk('restart')">${t('bulkRestart')}</button>
          <button class="btn btn-danger btn-sm" onclick="doBulk('delete')">${t('bulkDelete')}</button>
          <button class="btn btn-ghost btn-sm" onclick="clearSelection()">${t('clearSelection')}</button>
        </div>
      </div>` : ''}
      ${tunnels.length === 0 ? `
        <div style="text-align:center;padding:40px;color:var(--muted)">
          <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="opacity:.3;margin-bottom:10px"><path d="M4 21v-7a4 4 0 0 1 4-4h8a4 4 0 0 1 4 4v7"/><path d="M12 3v7"/><circle cx="12" cy="12" r="2"/></svg>
          <p>${tunnelState.search || tunnelState.protocol!=='all' || tunnelState.status!=='all' ? t('noResults') : t('noTunnels')}</p>
          ${tunnelState.search || tunnelState.protocol!=='all' || tunnelState.status!=='all' ? '' : `<button class="btn btn-primary" style="margin-top:14px" onclick="document.querySelector('[data-page=create]').click()">${t('createFirst')}</button>`}
        </div>
      ` : `
      <div class="table-wrap">
        <table>
          <thead><tr>
            <th class="checkbox-col"><input type="checkbox" onchange="toggleAll(this.checked)"></th>
            <th>${t('name')}</th><th>${t('protocol')}</th><th>${t('transport')}</th>
            <th class="num">${t('port')}</th><th class="num">${t('kharej')}</th>
            <th>${t('status')}</th><th>${t('health')}</th><th style="text-align:center">${t('actions')}</th>
          </tr></thead>
          <tbody>
            ${tunnels.map(tn => `
              <tr>
                <td class="checkbox-col"><input type="checkbox" ${tunnelState.selected.has(tn.id)?'checked':''} onchange="toggleSelect(${tn.id}, this.checked)"></td>
                <td><strong>${esc(tn.name)}</strong>${tn.tags?`<br><span style="font-size:.7rem;color:var(--muted)">${esc(tn.tags)}</span>`:''}</td>
                <td><span class="pill ${tn.protocol}">${esc(tn.protocol.toUpperCase())}</span></td>
                <td class="num">${esc(tn.transport.toUpperCase())}</td>
                <td class="num">${tn.iran_port}</td>
                <td class="num">${esc(tn.kharej_ip)}:${tn.kharej_port}</td>
                <td><span class="pill ${tn.status}">${tn.status==='running'?t('running'):t('stopped')}</span></td>
                <td><span class="pill ${tn.health_status||'unknown'}">${tn.health_status==='healthy'?t('healthy'):tn.health_status==='unhealthy'?t('healthBad'):'—'}</span></td>
                <td style="text-align:center;white-space:nowrap">
                  ${tn.status==='running'
                    ? `<button class="btn btn-danger btn-sm" onclick="toggleTunnel(${tn.id},'stop')">${t('stop')}</button>`
                    : `<button class="btn btn-success btn-sm" onclick="toggleTunnel(${tn.id},'start')">${t('start')}</button>`}
                  <button class="btn btn-ghost btn-sm" onclick="viewTunnel(${tn.id})">${t('viewConfig')}</button>
                  <button class="btn btn-ghost btn-sm" onclick="checkHealth(${tn.id})" title="${t('checkHealth')}">✓</button>
                  <button class="btn btn-ghost btn-sm" onclick="pingTunnel(${tn.id})" title="${t('ping')}">P</button>
                  <button class="btn btn-danger btn-sm" onclick="deleteTunnel(${tn.id})">${t('delete')}</button>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>`}
    </div>
  `;
}
let searchTimer;
function onSearchChange(v){clearTimeout(searchTimer);searchTimer=setTimeout(()=>{tunnelState.search=v;loadTunnels()},400)}
function onFilterChange(k,v){tunnelState[k]=v;loadTunnels()}
function toggleSelect(id,checked){if(checked)tunnelState.selected.add(id);else tunnelState.selected.delete(id);loadTunnels()}
async function toggleAll(checked){
  if(checked){
    const r = await api('/api/tunnels');
    if(r.ok){(r.tunnels||[]).forEach(tn=>tunnelState.selected.add(tn.id));loadTunnels()}
  } else {tunnelState.selected.clear();loadTunnels()}
}
function clearSelection(){tunnelState.selected.clear();loadTunnels()}
async function doBulk(action){
  if(action==='delete' && !confirm(`${t('confirmDeleteAll')} ${tunnelState.selected.size} ${t('tunnels_q')}`)) return;
  const r = await api('/api/tunnels/bulk', {method:'POST', body: JSON.stringify({ids:[...tunnelState.selected], action})});
  if(r.ok){toast(`${r.count} ${t('itemsCount')}`,'success');tunnelState.selected.clear();loadTunnels()}
  else toast(r.error||t('error'),'error');
}
async function toggleTunnel(id, action){
  const r = await api(`/api/tunnels/${id}/${action}`, {method:'POST'});
  if(r.ok){toast(action==='start'?t('tunnelStarted'):t('tunnelStopped'),'success');loadTunnels()}
  else toast(r.error,'error');
}
async function checkHealth(id){
  const r = await api(`/api/tunnels/${id}/health`, {method:'POST'});
  if(r.ok){toast(`${t('health')}: ${r.health==='healthy'?t('healthOK'):t('healthBad')}`, r.health==='healthy'?'success':'warning');loadTunnels()}
  else toast(r.error,'error');
}
async function pingTunnel(id){
  toast(t('pinging'),'info');
  const r = await api(`/api/tunnels/${id}/ping`, {method:'POST'});
  if(r.ok) toast(r.reachable ? `${t('reachable')}: ${r.latency}ms` : t('notReachable'), r.reachable?'success':'warning');
  else toast(r.error,'error');
}
async function deleteTunnel(id){
  if(!confirm(t('confirmDelete'))) return;
  const r = await api(`/api/tunnels/${id}`, {method:'DELETE'});
  if(r.ok){toast(t('tunnelDeleted'),'success');loadTunnels()}
  else toast(r.error,'error');
}

async function viewTunnel(id){
  const r = await api(`/api/tunnels/${id}`);
  if(!r.ok){toast(r.error,'error');return}
  const tn = r.tunnel;
  const kharejConf = tn.config_kharej ? JSON.stringify(JSON.parse(tn.config_kharej),null,2) : 'N/A';
  const iranConf = tn.config_iran ? JSON.stringify(JSON.parse(tn.config_iran),null,2) : 'N/A';
  const xuiIn = JSON.stringify({port:tn.iran_port,protocol:"tunnel",settings:{address:tn.kharej_ip,port:tn.kharej_port,network:"tcp,udp"},streamSettings:{network:"tcp",security:"none"},tag:`tunnel-in-${tn.id}`,remark:`NexTunnel: ${tn.name}`},null,2);
  const xuiOut = JSON.stringify({protocol:"freedom",settings:{domainStrategy:"UseIP"},tag:`tunnel-out-${tn.id}`},null,2);
  const xuiRoute = JSON.stringify({type:"field",inboundTag:[`tunnel-in-${tn.id}`],outboundTag:`tunnel-out-${tn.id}`,domain:["geosite:geolocation-!cn"],enabled:true},null,2);

  $('modal-title').innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 21v-7a4 4 0 0 1 4-4h8a4 4 0 0 1 4 4v7"/><path d="M12 3v7"/><circle cx="12" cy="12" r="2"/></svg> ${esc(tn.name)}`;
  $('modal-inner').classList.add('wide');
  $('modal-body').innerHTML = `
    <div class="tunnel-info">
      <div class="info-item"><div class="lbl">${t('protocol')}</div><div class="val">${esc(tn.protocol.toUpperCase())}</div></div>
      <div class="info-item"><div class="lbl">${t('transport')}</div><div class="val">${esc(tn.transport.toUpperCase())}</div></div>
      <div class="info-item"><div class="lbl">${t('iranPort')}</div><div class="val">${tn.iran_port}</div></div>
      <div class="info-item"><div class="lbl">${t('kharej')}</div><div class="val">${esc(tn.kharej_ip)}:${tn.kharej_port}</div></div>
      <div class="info-item"><div class="lbl">ISP</div><div class="val">${esc(tn.isp_profile||'auto')}</div></div>
      <div class="info-item"><div class="lbl">${t('status')}</div><div class="val">${tn.status==='running'?t('running'):t('stopped')}</div></div>
    </div>
    <div class="tabs">
      <div class="tab active" onclick="showTab(this,'tab-kh')">${t('configKharej')}</div>
      <div class="tab" onclick="showTab(this,'tab-ir')">${t('configIran')}</div>
      <div class="tab" onclick="showTab(this,'tab-xui')">${t('xuiIntegration')}</div>
    </div>
    <div id="tab-kh">
      <div class="code-block">${esc(kharejConf)}</div>
    </div>
    <div id="tab-ir" style="display:none">
      <div class="code-block">${esc(iranConf)}</div>
    </div>
    <div id="tab-xui" style="display:none">
      <label style="font-size:.8rem;color:var(--text-2);display:block;margin-bottom:8px;font-weight:600">Inbound</label>
      <div class="code-block" style="margin-bottom:14px">${esc(xuiIn)}</div>
      <label style="font-size:.8rem;color:var(--text-2);display:block;margin-bottom:8px;font-weight:600">Outbound</label>
      <div class="code-block" style="margin-bottom:14px">${esc(xuiOut)}</div>
      <label style="font-size:.8rem;color:var(--text-2);display:block;margin-bottom:8px;font-weight:600">Routing</label>
      <div class="code-block">${esc(xuiRoute)}</div>
    </div>
  `;
  $('modal-foot').innerHTML = `
    <button class="btn btn-ghost" onclick="closeModal()">${t('close')}</button>
    <button class="btn btn-primary" onclick="copyToClipboard(${JSON.stringify(kharejConf)})">${t('copyKharej')}</button>
    <button class="btn btn-primary" onclick="copyToClipboard(${JSON.stringify(iranConf)})">${t('copyIran')}</button>
    <button class="btn btn-primary" onclick="copyToClipboard(${JSON.stringify(xuiIn)})">${t('copyXui')}</button>
  `;
  openModal();
}
function showTab(el, tabId){
  document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
  el.classList.add('active');
  ['tab-kh','tab-ir','tab-xui'].forEach(id=>$(id).style.display = id===tabId?'block':'none');
}

// ═══════════ CREATE ═══════════
async function loadCreateForm(){
  const r = await api('/api/isp-profiles');
  const profiles = r.profiles || [];
  $('content').innerHTML = `
    <div class="card">
      <div class="card-head">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        <h3>${t('createTunnel')}</h3>
      </div>
      <div class="form-grid">
        <div class="field"><label>${t('tunnelName')} *</label><input id="t-name" placeholder="Tunnel-01"></div>
        <div class="field"><label>${t('protocol')}</label>
          <select id="t-protocol" onchange="onProtocolChange()">
            <option value="gost">GOST v3</option>
            <option value="rathole">Rathole</option>
            <option value="hysteria2">Hysteria2</option>
            <option value="chisel">Chisel</option>
            <option value="frp">FRP</option>
            <option value="paqet">Paqet</option>
            <option value="backhaul">Backhaul</option>
            <option value="wstunnel">WSTunnel</option>
            <option value="socat">Socat (simple)</option>
            <option value="ssh">SSH Tunnel</option>
            <option value="iptables">iptables NAT</option>
          </select>
        </div>
        <div class="field"><label>${t('transport')}</label>
          <select id="t-transport">
            <option value="tcp">TCP</option><option value="ws">WebSocket</option>
            <option value="tls">TLS</option><option value="quic">QUIC</option>
            <option value="grpc">gRPC</option>
            <option value="wss">WSS</option>
          </select>
        </div>
        <div class="field"><label>${t('ispProfile')}</label>
          <select id="t-isp" onchange="onIspChange()">
            <option value="auto">${t('autoDetect')}</option>
            ${profiles.map(p=>`<option value="${esc(p.name)}">${esc(LANG==='fa'?p.display_name_fa:p.display_name_en)}</option>`).join('')}
          </select>
        </div>
        <div class="field"><label>${t('iranPort')} *</label><input id="t-iran-port" type="number" value="443" min="1" max="65535"></div>
        <div class="field"><label>${t('kharejIP')} *</label><input id="t-kharej-ip" placeholder="1.2.3.4" dir="ltr"></div>
        <div class="field"><label>${t('kharejPort')}</label><input id="t-kharej-port" type="number" value="443" min="1" max="65535"></div>
        <div class="field"><label>${t('coverSNI')}</label><input id="t-sni" placeholder="shaparak.ir" dir="ltr"></div>
        <div class="field"><label>${t('tags')}</label><input id="t-tags" placeholder="production, europe"></div>
        <div class="field full"><label>${t('notes')}</label><textarea id="t-notes" rows="2"></textarea></div>
      </div>
      <button class="btn btn-primary" style="margin-top:16px" onclick="createTunnel()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        ${t('createTunnel')}
      </button>
    </div>
    <div class="card" id="isp-hint" style="display:none">
      <div class="card-head"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg><h3>${t('recommended')}</h3></div>
      <div id="isp-hint-body" style="font-size:.85rem;line-height:2;color:var(--text-2)"></div>
    </div>
  `;
}
function onProtocolChange(){
  const p=$('t-protocol').value;const tr=$('t-transport');
  if(p==='hysteria2'){tr.value='quic';tr.disabled=true}
  else if(p==='chisel'||p==='socat'||p==='ssh'||p==='iptables'){tr.value='tcp';tr.disabled=true}
  else tr.disabled=false;
}
function onIspChange(){
  const isp=$('t-isp').value;
  if(isp==='auto'){$('isp-hint').style.display='none';return}
  api('/api/isp-profiles/'+isp).then(r=>{
    if(!r.ok)return;
    const p=r.profile;
    $('isp-hint').style.display='block';
    $('isp-hint-body').innerHTML=`
      <p><strong>${t('protocol')}:</strong> ${esc(p.protocol)}</p>
      <p><strong>${t('transport')}:</strong> ${esc(p.transport)}</p>
      <p><strong>${t('port')}:</strong> ${p.port}</p>
      <p><strong>Obfs:</strong> ${esc(p.obfs)}</p>
      <p><strong>${t('notes')}:</strong> ${esc(LANG==='fa'?p.notes_fa:p.notes_en)}</p>
      <button class="btn btn-primary btn-sm" style="margin-top:8px" onclick="applyIsp('${esc(p.protocol)}','${esc(p.transport)}',${p.port})">${t('apply')}</button>
    `;
  });
}
function applyIsp(protocol,transport,port){
  $('t-protocol').value=protocol;
  $('t-transport').value=transport;
  $('t-iran-port').value=port;
  $('t-kharej-port').value=port;
  onProtocolChange();
  toast(t('saved'),'success');
}
async function createTunnel(){
  const body={
    name:$('t-name').value.trim(),
    protocol:$('t-protocol').value,
    transport:$('t-transport').value,
    iran_port:parseInt($('t-iran-port').value)||443,
    kharej_ip:$('t-kharej-ip').value.trim(),
    kharej_port:parseInt($('t-kharej-port').value)||443,
    sni:$('t-sni').value.trim(),
    isp_profile:$('t-isp').value,
    tags:$('t-tags').value.trim(),
    notes:$('t-notes').value.trim(),
  };
  if(!body.name){toast(t('enterName'),'warning');return}
  if(!body.kharej_ip){toast(t('enterKharejIP'),'warning');return}
  const r = await api('/api/tunnels',{method:'POST',body:JSON.stringify(body)});
  if(r.ok){toast(t('tunnelCreated'),'success');document.querySelector('[data-page=tunnels]').click()}
  else toast(r.error,'error');
}

// ═══════════ TOOLS ═══════════
async function loadTools(){
  const r = await api('/api/tools');
  if(!r.ok)return;
  const tools=r.tools||{};
  const desc = {
    gost:{en:'Multi-protocol proxy (TCP/WS/TLS/QUIC/gRPC)', fa:'پروکسی چندمنظوره'},
    rathole:{en:'Lightweight reverse tunnel', fa:'تانل معکوس سبک'},
    hysteria2:{en:'QUIC proxy with Salamander obfs', fa:'پروکسی QUIC با Salamander'},
    chisel:{en:'Simple HTTP/WS tunnel', fa:'تانل HTTP/WS ساده'},
    frp:{en:'Professional reverse tunnel', fa:'تانل معکوس حرفه‌ای'},
    paqet:{en:'KCP Raw Socket tunnel', fa:'تانل KCP Raw Socket'},
    backhaul:{en:'Multi-node reverse tunnel', fa:'تانل معکوس چندنودی'},
    wstunnel:{en:'WebSocket tunneling tool', fa:'ابزار تانل WebSocket'},
    socat:{en:'Simple port forwarder', fa:'فورواردر پورت ساده'},
    smite:{en:'All-in-one orchestrator', fa:'اورکستراتور همه‌کاره'},
  };
  $('content').innerHTML=`
    <div class="card">
      <div class="card-head">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>
        <h3>${t('toolInstall')}</h3>
        <span class="badge">${Object.keys(tools).length}</span>
      </div>
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:14px">
        ${Object.entries(tools).map(([k,tl])=>`
          <div style="padding:16px;background:var(--surface-2);border:1px solid var(--border);border-radius:12px">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
              <h4 style="font-size:.92rem">${esc(tl.name)}</h4>
              <span class="pill ${tl.installed?'running':'stopped'}" style="font-size:.65rem">${tl.installed?t('installed_short'):t('notInstalled_short')}</span>
            </div>
            <p style="font-size:.75rem;color:var(--muted);margin-bottom:12px;min-height:36px">${esc(desc[k]?.[LANG]||'')}</p>
            <button class="btn ${tl.installed?'btn-ghost':'btn-primary'} btn-full" onclick="installTool('${k}')" ${tl.installed?'disabled':''}>${tl.installed?t('installed'):t('install')}</button>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}
async function installTool(tool){
  toast(t('install') + ' ' + tool + '...','info');
  const r = await api('/api/tools/install',{method:'POST',body:JSON.stringify({tool})});
  if(r.ok){toast(r.message,'success');loadTools()}
  else toast(r.error,'error');
}

// ═══════════ ISP ═══════════
async function loadIspPage(){
  const r = await api('/api/isp-profiles');
  const profiles=r.profiles||[];
  $('content').innerHTML=`
    <div class="card">
      <div class="card-head">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
        <h3>${t('ispProfiles')}</h3>
        <span class="badge">${profiles.length}</span>
      </div>
      <button class="btn btn-primary btn-sm" style="margin-bottom:14px" onclick="showAddIsp()">+ ${t('addCustomISP')}</button>
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px">
        ${profiles.map(p=>`
          <div style="padding:16px;background:var(--surface-2);border:1px solid var(--border);border-radius:12px;position:relative">
            ${!p.is_builtin ? `<button class="btn btn-danger btn-sm" style="position:absolute;top:8px;inset-inline-end:8px;padding:2px 8px" onclick="deleteIsp('${esc(p.name)}')">×</button>` : ''}
            <h4 style="font-size:.92rem;margin-bottom:10px">${esc(LANG==='fa'?p.display_name_fa:p.display_name_en)}</h4>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:.78rem;margin-bottom:10px">
              <div><span style="color:var(--muted)">${t('protocol')}:</span> <strong>${esc(p.protocol)}</strong></div>
              <div><span style="color:var(--muted)">${t('transport')}:</span> <strong>${esc(p.transport)}</strong></div>
              <div><span style="color:var(--muted)">${t('port')}:</span> <strong>${p.port}</strong></div>
              <div><span style="color:var(--muted)">Obfs:</span> <strong>${esc(p.obfs)}</strong></div>
            </div>
            <p style="font-size:.74rem;color:var(--muted);margin-bottom:10px">${esc(LANG==='fa'?p.notes_fa:p.notes_en)}</p>
            <button class="btn btn-primary btn-sm" onclick="applyIsp('${esc(p.protocol)}','${esc(p.transport)}',${p.port});document.querySelector('[data-page=create]').click()">${t('apply')}</button>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}
function showAddIsp(){
  $('modal-title').innerHTML = `+ ${t('addCustomISP')}`;
  $('modal-inner').classList.remove('wide');
  $('modal-body').innerHTML = `
    <div class="form-grid">
      <div class="field"><label>Name (slug)</label><input id="isp-name" dir="ltr" placeholder="my-isp"></div>
      <div class="field"><label>Display EN</label><input id="isp-en" dir="ltr"></div>
      <div class="field"><label>Display FA</label><input id="isp-fa" dir="ltr"></div>
      <div class="field"><label>${t('protocol')}</label><select id="isp-proto">
        <option>gost</option><option>rathole</option><option>hysteria2</option><option>chisel</option>
        <option>frp</option><option>backhaul</option><option>wstunnel</option>
      </select></div>
      <div class="field"><label>${t('transport')}</label><select id="isp-trans">
        <option>tcp</option><option>ws</option><option>tls</option><option>quic</option><option>grpc</option>
      </select></div>
      <div class="field"><label>${t('port')}</label><input id="isp-port" type="number" value="443"></div>
      <div class="field"><label>Obfs</label><select id="isp-obfs">
        <option>none</option><option>salamander</option><option>http</option>
      </select></div>
      <div class="field full"><label>Notes EN</label><input id="isp-notes-en" dir="ltr"></div>
      <div class="field full"><label>Notes FA</label><input id="isp-notes-fa" dir="ltr"></div>
    </div>
  `;
  $('modal-foot').innerHTML = `
    <button class="btn btn-ghost" onclick="closeModal()">${t('cancel')}</button>
    <button class="btn btn-primary" onclick="saveIsp()">${t('save')}</button>
  `;
  openModal();
}
async function saveIsp(){
  const data = {
    name:$('isp-name').value.trim(),
    display_name_en:$('isp-en').value.trim(),
    display_name_fa:$('isp-fa').value.trim(),
    protocol:$('isp-proto').value,
    transport:$('isp-trans').value,
    port:parseInt($('isp-port').value)||443,
    obfs:$('isp-obfs').value,
    notes_en:$('isp-notes-en').value.trim(),
    notes_fa:$('isp-notes-fa').value.trim(),
  };
  if(!data.name){toast('Name required','warning');return}
  const r = await api('/api/isp-profiles/save',{method:'POST',body:JSON.stringify(data)});
  if(r.ok){toast(t('saved'),'success');closeModal();loadIspPage()}
  else toast(r.error,'error');
}
async function deleteIsp(name){
  if(!confirm(t('confirmDelete'))) return;
  const r = await api('/api/isp-profiles/'+name,{method:'DELETE'});
  if(r.ok){toast(t('tunnelDeleted'),'success');loadIspPage()}
  else toast(r.error,'error');
}

// ═══════════ SESSIONS ═══════════
async function loadSessions(){
  const r = await api('/api/sessions');
  if(!r.ok)return;
  const sessions=r.sessions||[];
  $('content').innerHTML=`
    <div class="card">
      <div class="card-head">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
        <h3>${t('sessions_active')}</h3>
        <span class="badge">${sessions.length}</span>
      </div>
      <div class="alert alert-success">✓ ${t('sessionNote')}</div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>IP</th><th>User Agent</th><th>${t('time')}</th><th>Activity</th><th style="text-align:center">${t('actions')}</th></tr></thead>
          <tbody>
            ${sessions.map(s=>`
              <tr>
                <td class="num">${esc(s.ip)}</td>
                <td style="font-size:.75rem">${esc((s.user_agent||'').slice(0,60))}</td>
                <td class="num">${fmtDate(s.created_at)}</td>
                <td class="num">${fmtDate(s.last_activity)}</td>
                <td style="text-align:center">
                  ${s.current?'<span class="pill running">'+t('current')+'</span>':`<button class="btn btn-danger btn-sm" onclick="revokeSession('${esc(s.token)}')">${t('revoke')}</button>`}
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
      <button class="btn btn-danger" style="margin-top:14px" onclick="revokeAllSessions()">${t('revokeAll')}</button>
    </div>
  `;
}
async function revokeSession(token){
  if(!confirm(t('confirmRevoke'))) return;
  const r = await api('/api/sessions/revoke',{method:'POST',body:JSON.stringify({token})});
  if(r.ok){toast(t('tunnelDeleted'),'success');loadSessions()}
  else toast(r.error,'error');
}
async function revokeAllSessions(){
  if(!confirm(t('confirmRevokeAll'))) return;
  const r = await api('/api/sessions/revoke-all',{method:'POST'});
  if(r.ok){toast(t('tunnelDeleted'),'success');loadSessions()}
  else toast(r.error,'error');
}

// ═══════════ LOGS ═══════════
let currentLogs = [];
async function loadLogs(){
  const r = await api('/api/logs?limit=300');
  if(!r.ok)return;
  currentLogs = r.logs||[];
  renderLogs();
}
function renderLogs(){
  const filter = $('log-level')?.value || 'all';
  const logs = currentLogs.filter(l => filter==='all' || l.level===filter);
  $('content').innerHTML=`
    <div class="card">
      <div class="card-head">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        <h3>${t('logs_system')}</h3>
        <span class="badge">${logs.length}</span>
      </div>
      <div class="search-bar">
        <select id="log-level" onchange="renderLogs()">
          <option value="all" ${filter==='all'?'selected':''}>${t('allStatus')}</option>
          <option value="success" ${filter==='success'?'selected':''}>Success</option>
          <option value="info" ${filter==='info'?'selected':''}>Info</option>
          <option value="warning" ${filter==='warning'?'selected':''}>Warning</option>
          <option value="error" ${filter==='error'?'selected':''}>Error</option>
        </select>
        <button class="btn btn-ghost btn-sm" onclick="clearLogs()">${t('clearLogs')}</button>
        <button class="btn btn-ghost btn-sm" onclick="loadLogs()">${t('refresh')}</button>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>${t('level')}</th><th>${t('message')}</th><th>${t('tunnel')}</th><th>${t('time')}</th></tr></thead>
          <tbody>
            ${logs.length===0?`<tr><td colspan="4" style="text-align:center;padding:30px;color:var(--muted)">${t('noLogs')}</td></tr>`:
            logs.map(l=>`
              <tr>
                <td><span class="pill ${l.level==='success'?'running':l.level==='error'?'error':l.level==='warning'?'warning':'stopped'}">${esc(l.level)}</span></td>
                <td>${esc(l.message)}</td>
                <td class="num">${l.tunnel_id||'-'}</td>
                <td class="num">${fmtDate(l.created_at)}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </div>
  `;
}
async function clearLogs(){
  if(!confirm(t('confirmClearLogs'))) return;
  const r = await api('/api/logs/clear',{method:'POST'});
  if(r.ok){toast(t('tunnelDeleted'),'success');loadLogs()}
  else toast(r.error,'error');
}

// ═══════════ SETTINGS ═══════════
async function loadSettings(){
  const r = await api('/api/settings');
  if(!r.ok)return;
  const s=r.settings||{};
  const u=r.user||{};
  $('content').innerHTML=`
    <div class="card">
      <div class="card-head">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
        <h3>${t('accountInfo')}</h3>
      </div>
      <div class="form-grid">
        <div class="field"><label>${t('username')}</label><input id="set-username" value="${esc(u.username||'')}" dir="ltr"></div>
      </div>
      <button class="btn btn-primary" style="margin-top:10px" onclick="saveUsername()">${t('saveUsername')}</button>
    </div>

    <div class="card">
      <div class="card-head">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
        <h3>${t('changePassword')}</h3>
      </div>
      <div class="form-grid">
        <div class="field"><label>${t('currentPw')}</label><input type="password" id="set-old-pw" dir="ltr"></div>
        <div class="field"><label>${t('newPw')}</label>
          <input type="password" id="set-new-pw" dir="ltr" oninput="checkPwStrength('set-new-pw','set-pw-bar')">
          <div class="pw-strength"><div class="pw-strength-bar" id="set-pw-bar"></div></div>
        </div>
        <div class="field"><label>${t('confirmNewPw')}</label><input type="password" id="set-new-pw2" dir="ltr"></div>
      </div>
      <button class="btn btn-primary" style="margin-top:10px" onclick="savePassword()">${t('changePwBtn')}</button>
    </div>

    <div class="card">
      <div class="card-head">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
        <h3>${t('serverSettings')}</h3>
      </div>
      <div class="form-grid">
        <div class="field"><label>${t('publicIPLabel')}</label>
          <input id="set-ip" value="${esc(s.public_ip||'')}" dir="ltr" placeholder="${t('autoDetect')}">
        </div>
        <div class="field"><label>${t('autoRestartInterval')}</label>
          <input id="set-interval" type="number" value="${esc(s.auto_restart_interval||'60')}" min="30">
        </div>
      </div>
      <button class="btn btn-primary" style="margin-top:10px" onclick="saveSettings()">${t('save')}</button>
      <button class="btn btn-ghost" style="margin-top:10px" onclick="redetectIP()">${t('redetectIP')}</button>
    </div>

    <div class="card">
      <div class="card-head">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
        <h3>${t('backup')}</h3>
      </div>
      <p style="font-size:.85rem;color:var(--text-2);margin-bottom:12px">${t('backupDesc')}</p>
      <button class="btn btn-primary" onclick="downloadBackup()">${t('downloadBackup')}</button>
    </div>

    <div class="card">
      <div class="card-head">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
        <h3>About</h3>
      </div>
      <div class="tunnel-info">
        <div class="info-item"><div class="lbl">App</div><div class="val">NexTunnel v${esc(r.version||'1.1.1')}</div></div>
        <div class="info-item"><div class="lbl">Author</div><div class="val">metiwilson</div></div>
        <div class="info-item"><div class="lbl">GitHub</div><div class="val"><a href="https://github.com/metiwilson/nextunnel" target="_blank" style="color:var(--primary)">nextunnel</a></div></div>
        <div class="info-item"><div class="lbl">License</div><div class="val">MIT</div></div>
      </div>
    </div>
  `;
}
async function saveUsername(){
  const v=$('set-username').value.trim();
  if(v.length<3){toast('Min 3 chars','warning');return}
  const r = await api('/api/settings/username',{method:'POST',body:JSON.stringify({username:v})});
  if(r.ok){toast(t('saved'),'success')}else toast(r.error,'error');
}
async function savePassword(){
  const oldPw=$('set-old-pw').value;
  const p1=$('set-new-pw').value;
  const p2=$('set-new-pw2').value;
  if(p1.length<8){toast(t('passwordMin'),'warning');return}
  if(p1!==p2){toast(t('passwordsMatch'),'warning');return}
  const r = await api('/api/settings/password',{method:'POST',body:JSON.stringify({old_password:oldPw,new_password:p1})});
  if(r.ok){toast(t('saved'),'success');setTimeout(doLogout,1800)}
  else toast(r.error,'error');
}
async function saveSettings(){
  const body={
    public_ip:$('set-ip').value.trim(),
    auto_restart_interval:$('set-interval').value,
  };
  const r = await api('/api/settings',{method:'POST',body:JSON.stringify(body)});
  if(r.ok){toast(t('saved'),'success')}else toast(r.error,'error');
}
async function redetectIP(){
  const r = await api('/api/settings/redetect-ip',{method:'POST'});
  if(r.ok){toast('IP: '+r.ip,'success');loadSettings()}else toast(r.error,'error');
}
async function downloadBackup(){
  const r = await api('/api/backup');
  if(!r.ok){toast(r.error,'error');return}
  const blob = new Blob([JSON.stringify(r.data,null,2)],{type:'application/json'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href=url;a.download=`nextunnel-backup-${Date.now()}.json`;a.click();
  URL.revokeObjectURL(url);
  toast(t('saved'),'success');
}

// ═══════════ MODAL ═══════════
function openModal(){$('modal').classList.add('open')}
function closeModal(){$('modal').classList.remove('open');$('modal-inner').classList.remove('wide')}
$('modal').addEventListener('click',e=>{if(e.target===$('modal'))closeModal()});
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeModal()});

// ═══════════ INIT ═══════════
checkAuth();
setInterval(()=>checkForUpdates(true), 30*60*1000);
async function checkForUpdates(force){
  try {
    const r = await fetch('/api/update-check');
    const d = await r.json();
    if (d.ok && d.has_update && !sessionStorage.getItem('update_notified')) {
      sessionStorage.setItem('update_notified', '1');
      toast(`${t('updateAvailable')}: v${d.latest}`, 'info');
    }
  } catch(e) {}
}
</script>
</body>
</html>
"""

# ═══════════════════════════════════════════════════════════════════════
#  HTTP HANDLER
# ═══════════════════════════════════════════════════════════════════════
class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass

    def _json(self, data, status=200, cookie=None, extra_headers=None):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('Referrer-Policy', 'same-origin')
        if cookie:
            self.send_header('Set-Cookie', cookie)
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)
        self.end_headers()
        try:
            self.wfile.write(json.dumps(data, ensure_ascii=False, default=str).encode('utf-8'))
        except Exception:
            pass

    def _html(self, html, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def _read_json(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            if length <= 0:
                return {}
            if length > 1_000_000:
                return {}
            body = self.rfile.read(length).decode('utf-8')
            return json.loads(body) if body else {}
        except Exception:
            return {}

    def _client_ip(self):
        return self.client_address[0]

    def _get_session(self):
        raw = self.headers.get('Cookie', '')
        if not raw:
            if CONFIG['debug_sessions']:
                print(f"[DEBUG] No cookie from {self.client_address[0]} on {self.path}", flush=True)
            return None
        try:
            c = SimpleCookie()
            c.load(raw)
            token = c['nt_session'].value if 'nt_session' in c else None
            if not token:
                if CONFIG['debug_sessions']:
                    print(f"[DEBUG] No nt_session in cookie from {self.client_address[0]}", flush=True)
                return None
            session = get_session(token)
            if not session and CONFIG['debug_sessions']:
                print(f"[DEBUG] Session lookup failed for token {token[:8]}...", flush=True)
            return session
        except Exception as e:
            if CONFIG['debug_sessions']:
                print(f"[DEBUG] Cookie parse error: {e}", flush=True)
            return None

    def _check_csrf(self, session):
        if not session:
            return False
        token = self.headers.get('X-CSRF-Token')
        return token and hmac.compare_digest(token, session['csrf_token'])

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ('/', '/index.html'):
            return self._html(HTML)
        if path == '/api/update-check':
            return self._json({"ok": True, **check_for_updates()})
        if not path.startswith('/api/'):
            self.send_error(404)
            return

        if path == '/api/check':
            s = self._get_session()
            if s:
                user = get_user(s['user_id'])
                # ★ Refresh cookie on every successful check (sliding window)
                new_cookie = build_session_cookie(s['token'])
                return self._json({
                    "ok": True,
                    "csrf_token": s['csrf_token'],
                    "user": {"username": user['username'], "role": user['role'], "language": user.get('language', 'en')}
                }, cookie=new_cookie)
            return self._json({"ok": False}, 401)

        s = self._get_session()
        if not s:
            return self._json({"ok": False, "error": "unauthorized"}, 401)

        try:
            if path == '/api/stats':
                return self._json({"ok": True, "stats": get_dashboard_stats()})

            if path == '/api/tunnels':
                qs = parse_qs(urlparse(self.path).query)
                tunnels = get_tunnel_list(
                    search=(qs.get('search', [''])[0] or None),
                    protocol=(qs.get('protocol', ['all'])[0]),
                    status=(qs.get('status', ['all'])[0]),
                )
                return self._json({"ok": True, "tunnels": tunnels})

            if path.startswith('/api/tunnels/') and path.count('/') == 3:
                try:
                    tid = int(path.split('/')[-1])
                except ValueError:
                    return self._json({"ok": False, "error": "bad id"}, 400)
                t = get_tunnel(tid)
                if not t:
                    return self._json({"ok": False, "error": "not found"}, 404)
                return self._json({"ok": True, "tunnel": t})

            if path == '/api/logs':
                qs = parse_qs(urlparse(self.path).query)
                limit = min(int(qs.get('limit', ['100'])[0]), 500)
                with _db_lock:
                    conn = db_connect()
                    try:
                        rows = conn.execute(
                            "SELECT * FROM logs ORDER BY created_at DESC LIMIT ?",
                            (limit,)
                        ).fetchall()
                    finally:
                        conn.close()
                return self._json({"ok": True, "logs": [dict(r) for r in rows]})

            if path == '/api/tools':
                return self._json({"ok": True, "tools": get_tool_status()})

            if path == '/api/isp-profiles':
                return self._json({"ok": True, "profiles": get_isp_profiles()})

            if path.startswith('/api/isp-profiles/'):
                name = path.split('/')[-1]
                p = get_isp_profile(name)
                if p:
                    return self._json({"ok": True, "profile": p})
                return self._json({"ok": False, "error": "not found"}, 404)

            if path == '/api/sessions':
                sessions = list_sessions(s['user_id'], current_token=s['token'])
                return self._json({"ok": True, "sessions": sessions})

            if path == '/api/settings':
                return self._json({
                    "ok": True,
                    "version": CONFIG['version'],
                    "settings": {
                        "public_ip": get_setting('public_ip', ''),
                        "auto_restart_interval": get_setting('auto_restart_interval', '60'),
                    },
                    "user": {"username": get_user(s['user_id'])['username']}
                })

            if path == '/api/backup':
                data = {
                    "version": CONFIG['version'],
                    "exported_at": now_ts(),
                    "tunnels": get_tunnel_list(),
                    "isp_profiles": get_isp_profiles(),
                    "settings": {
                        "public_ip": get_setting('public_ip', ''),
                        "auto_restart_interval": get_setting('auto_restart_interval', '60'),
                    },
                }
                return self._json({"ok": True, "data": data})

            if path == '/api/xui/inbounds':
                return self._json({"ok": True, "inbounds": read_xui_inbounds()})

        except Exception as e:
            return self._json({"ok": False, "error": str(e)}, 500)
        return self._json({"ok": False, "error": "not found"}, 404)

    def do_POST(self):
        path = urlparse(self.path).path
        ip = self._client_ip()

        if path == '/api/login':
            if is_rate_limited(ip):
                return self._json({
                    "ok": False,
                    "error": msg('rate_limited', 'en', min=CONFIG['lockout_minutes'])
                }, 429)
            data = self._read_json()
            username = (data.get('username') or '').strip()
            password = data.get('password') or ''
            lang = (data.get('language') or 'en')[:2]
            user = get_user_by_username(username)
            if user and verify_password(password, user['password_hash'], user['password_salt']):
                record_login_attempt(ip, username, True)
                token, csrf = create_session(user['id'], ip, self.headers.get('User-Agent', ''), lang)
                with _db_lock:
                    conn = db_connect()
                    try:
                        conn.execute("UPDATE users SET last_login=?, last_ip=?, language=? WHERE id=?",
                                     (now_ts(), ip, lang, user['id']))
                        conn.commit()
                    finally:
                        conn.close()
                # ★ Cookie Max-Age = 400 days (browser-safe!)
                cookie = build_session_cookie(token)
                if CONFIG['debug_sessions']:
                    print(f"[DEBUG] Login OK for {username} from {ip}; cookie Max-Age={COOKIE_MAX_AGE}", flush=True)
                return self._json({
                    "ok": True,
                    "csrf_token": csrf,
                    "must_change_password": bool(user['must_change_password']),
                    "user": {"username": user['username'], "role": user['role']},
                }, cookie=cookie)
            record_login_attempt(ip, username, False)
            if CONFIG['debug_sessions']:
                print(f"[DEBUG] Login FAILED for '{username}' from {ip}", flush=True)
            return self._json({"ok": False, "error": msg('invalid_credentials', lang)}, 401)

        s = self._get_session()
        if not s:
            return self._json({"ok": False, "error": "unauthorized"}, 401)
        if not self._check_csrf(s):
            return self._json({"ok": False, "error": "csrf invalid"}, 403)

        try:
            data = self._read_json()

            if path == '/api/logout':
                delete_session(s['token'])
                return self._json({"ok": True}, cookie=build_logout_cookie())

            if path == '/api/change-password':
                new_pw = data.get('new_password') or ''
                if len(new_pw) < 8:
                    return self._json({"ok": False, "error": "min 8 chars"}, 400)
                update_user_password(s['user_id'], new_pw, must_change=0)
                log_event(None, 'info', f"Password changed for {s['username']}")
                return self._json({"ok": True})

            if path == '/api/settings/password':
                old_pw = data.get('old_password') or ''
                new_pw = data.get('new_password') or ''
                user = get_user(s['user_id'])
                if not verify_password(old_pw, user['password_hash'], user['password_salt']):
                    return self._json({"ok": False, "error": "Wrong current password"}, 401)
                if len(new_pw) < 8:
                    return self._json({"ok": False, "error": "min 8 chars"}, 400)
                update_user_password(s['user_id'], new_pw, must_change=0)
                delete_all_sessions(s['user_id'], except_token=s['token'])
                log_event(None, 'info', f"Password changed for {s['username']}")
                return self._json({"ok": True})

            if path == '/api/settings/username':
                new_u = (data.get('username') or '').strip()
                if len(new_u) < 3 or len(new_u) > 40:
                    return self._json({"ok": False, "error": "invalid username"}, 400)
                if not re.match(r'^[a-zA-Z0-9_\-\.]+$', new_u):
                    return self._json({"ok": False, "error": "invalid chars"}, 400)
                existing = get_user_by_username(new_u)
                if existing and existing['id'] != s['user_id']:
                    return self._json({"ok": False, "error": "taken"}, 409)
                update_username(s['user_id'], new_u)
                return self._json({"ok": True})

            if path == '/api/settings/language':
                lang = (data.get('language') or 'en')[:2]
                if lang not in ('en', 'fa'):
                    return self._json({"ok": False, "error": "invalid"}, 400)
                update_user_language(s['user_id'], lang)
                return self._json({"ok": True})

            if path == '/api/settings':
                if 'public_ip' in data:
                    set_setting('public_ip', data['public_ip'])
                    set_setting('public_ip_ts', str(now_ts()))
                if 'auto_restart_interval' in data:
                    try:
                        set_setting('auto_restart_interval', str(max(30, int(data['auto_restart_interval'] or 60))))
                    except Exception:
                        pass
                return self._json({"ok": True})

            if path == '/api/settings/redetect-ip':
                set_setting('public_ip_ts', '0')
                ip2 = detect_public_ip()
                return self._json({"ok": True, "ip": ip2})

            if path == '/api/tunnels':
                return self._json(create_tunnel(data))

            if path == '/api/tunnels/bulk':
                ids = data.get('ids') or []
                action = data.get('action')
                if not ids or action not in ('start', 'stop', 'delete', 'restart'):
                    return self._json({"ok": False, "error": "invalid params"}, 400)
                return self._json(bulk_action(ids, action))

            if path.startswith('/api/tunnels/'):
                parts = path.split('/')
                if len(parts) == 5:
                    try:
                        tid = int(parts[3])
                    except ValueError:
                        return self._json({"ok": False, "error": "bad id"}, 400)
                    action = parts[4]
                    if action == 'start':
                        return self._json(start_tunnel_process(tid))
                    if action == 'stop':
                        return self._json(stop_tunnel_process(tid))
                    if action == 'health':
                        return self._json(check_tunnel_health(tid))
                    if action == 'ping':
                        tn = get_tunnel(tid)
                        if not tn:
                            return self._json({"ok": False, "error": "not found"}, 404)
                        start = time.time()
                        ok, _ = ping_host(tn['kharej_ip'], count=1, timeout=3)
                        latency = int((time.time() - start) * 1000)
                        return self._json({"ok": True, "reachable": ok, "latency": latency})

            if path == '/api/tools/install':
                return self._json(install_tool(data.get('tool')))

            if path == '/api/isp-profiles/save':
                return self._json(save_custom_isp(data))

            if path == '/api/sessions/revoke':
                token = data.get('token')
                if not token:
                    return self._json({"ok": False, "error": "token required"}, 400)
                with _db_lock:
                    conn = db_connect()
                    try:
                        row = conn.execute(
                            "SELECT user_id FROM sessions WHERE token=?", (token,)
                        ).fetchone()
                    finally:
                        conn.close()
                if not row or row['user_id'] != s['user_id']:
                    return self._json({"ok": False, "error": "forbidden"}, 403)
                delete_session(token)
                return self._json({"ok": True})

            if path == '/api/sessions/revoke-all':
                delete_all_sessions(s['user_id'], except_token=s['token'])
                return self._json({"ok": True})

            if path == '/api/logs/clear':
                with _db_lock:
                    conn = db_connect()
                    try:
                        conn.execute("DELETE FROM logs")
                        conn.commit()
                    finally:
                        conn.close()
                return self._json({"ok": True})

        except Exception as e:
            return self._json({"ok": False, "error": str(e)}, 500)
        return self._json({"ok": False, "error": "not found"}, 404)

    def do_PUT(self):
        path = urlparse(self.path).path
        s = self._get_session()
        if not s:
            return self._json({"ok": False, "error": "unauthorized"}, 401)
        if not self._check_csrf(s):
            return self._json({"ok": False, "error": "csrf invalid"}, 403)
        try:
            data = self._read_json()
            if path.startswith('/api/tunnels/'):
                parts = path.split('/')
                if len(parts) == 4:
                    try:
                        tid = int(parts[3])
                    except ValueError:
                        return self._json({"ok": False, "error": "bad id"}, 400)
                    return self._json(update_tunnel(tid, data))
        except Exception as e:
            return self._json({"ok": False, "error": str(e)}, 500)
        return self._json({"ok": False, "error": "not found"}, 404)

    def do_DELETE(self):
        path = urlparse(self.path).path
        s = self._get_session()
        if not s:
            return self._json({"ok": False, "error": "unauthorized"}, 401)
        if not self._check_csrf(s):
            return self._json({"ok": False, "error": "csrf invalid"}, 403)
        if path.startswith('/api/tunnels/'):
            parts = path.split('/')
            if len(parts) == 4:
                try:
                    tid = int(parts[3])
                except ValueError:
                    return self._json({"ok": False, "error": "bad id"}, 400)
                return self._json(delete_tunnel(tid))
        if path.startswith('/api/isp-profiles/'):
            name = path.split('/')[-1]
            return self._json(delete_isp(name))
        return self._json({"ok": False, "error": "not found"}, 404)

# ═══════════════════════════════════════════════════════════════════════
#  SERVER
# ═══════════════════════════════════════════════════════════════════════
class ReusableTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True

def is_port_free(port, host="0.0.0.0"):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return True
        except OSError:
            return False

def find_free_port(start=8088, end=9100):
    for p in range(start, end):
        if is_port_free(p):
            return p
    raise RuntimeError("No free port found")

def print_banner(port, ip, credentials):
    print("\n" + "═" * 68, flush=True)
    print(f"  NexTunnel v{CONFIG['version']}", flush=True)
    print("  Universal Tunnel Management Platform", flush=True)
    print("═" * 68, flush=True)
    print(f"  🌐  Local   : http://127.0.0.1:{port}", flush=True)
    print(f"  🌐  Network : http://{ip}:{port}", flush=True)
    print("─" * 68, flush=True)
    if credentials:
        print("\n  ⚠️  FIRST-RUN CREDENTIALS (shown only once!)", flush=True)
        print("  " + "─" * 64, flush=True)
        print(f"  👤  Username : {credentials['username']}", flush=True)
        print(f"  🔑  Password : {credentials['password']}", flush=True)
        print("  " + "─" * 64, flush=True)
        print("\n  ⚡ Save these credentials now!", flush=True)
        print("  ⚡ You must change your password after first login.\n", flush=True)
    else:
        print("\n  🔐 Login with your existing credentials\n", flush=True)
    print("─" * 68, flush=True)
    print(f"  👤  Author : {CONFIG['author']}", flush=True)
    print(f"  🔗  GitHub : {CONFIG['github']}", flush=True)
    print(f"  🍪  Cookie : {CONFIG['cookie_max_age_days']} days (browser-safe)", flush=True)
    print("═" * 68, flush=True)
    print("  Ctrl+C to stop", flush=True)
    print("═" * 68 + "\n", flush=True)

def main():
    db_init()
    creds = ensure_admin_user()
    try:
        detect_public_ip()
    except Exception:
        pass

    port = CONFIG['port']
    if not is_port_free(port):
        if CONFIG['auto_port']:
            print(f"[!] Port {port} in use, searching...", flush=True)
            port = find_free_port(port + 1, port + 100)
            print(f"[+] Free port found: {port}", flush=True)
        else:
            print(f"[x] Port {port} is in use.", flush=True)
            sys.exit(1)

    threading.Thread(target=auto_restart_check, daemon=True).start()
    threading.Thread(target=restore_tunnels_on_boot, daemon=True).start()
    threading.Thread(target=lambda: check_for_updates(force=True), daemon=True).start()

    server = None
    try:
        server = ReusableTCPServer((CONFIG['host'], port), Handler)
        print_banner(port, get_local_ip(), creds)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Server stopped.", flush=True)
    except OSError as e:
        print(f"\n[x] Network error: {e}", flush=True)
        sys.exit(1)
    finally:
        if server:
            try:
                server.shutdown()
                server.server_close()
            except Exception:
                pass

if __name__ == '__main__':
    main()
