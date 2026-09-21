<div align="center" dir="rtl">

# 🚇 NexTunnel

### پلتفرم مدیریت تانل همه‌کاره

**پنل وب حرفه‌ای برای مدیریت تانل‌های ایران ← خارج با ۱۱ پروتکل، رابط کاربری دوزبانه (فارسی/انگلیسی) و یکپارچه‌سازی با 3x-ui**

[![Version](https://img.shields.io/badge/version-1.0.0-blue?style=for-the-badge)](https://github.com/metiwilson/nextunnel/releases)
[![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-yellow?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Platform](https://img.shields.io/badge/platform-Linux-lightgrey?style=for-the-badge&logo=linux)](https://kernel.org)
[![Stars](https://img.shields.io/github/stars/metiwilson/nextunnel?style=for-the-badge)](https://github.com/metiwilson/nextunnel/stargazers)

**ساخته شده با ❤️ توسط [metiwilson](https://github.com/metiwilson)**

🇬🇧 **[English Version](README.md)** &nbsp;|&nbsp; 🇮🇷 **فارسی**

</div>

---

<div dir="rtl">

## 📑 فهرست مطالب

- [ویژگی‌ها](#-ویژگیها)
- [پیش‌نیازها](#-پیشنیازها)
- [نصب](#-نصب)
- [اولین ورود](#-اولین-ورود)
- [آموزش ساخت تانل‌ها](#-آموزش-ساخت-تانلها)
- [بهینه‌سازی ISP](#-بهینهسازی-isp)
- [یکپارچه‌سازی با 3x-ui](#-یکپارچهسازی-با-3x-ui)
- [مدیریت سرویس](#-مدیریت-سرویس)
- [تمپلیت Systemd](#-تمپلیت-systemd)
- [بروزرسانی](#-بروزرسانی)
- [حذف](#-حذف)
- [امنیت](#-امنیت)
- [عیب‌یابی](#-عیبیابی)
- [سؤالات متداول](#-سؤالات-متداول)
- [ساختار پروژه](#-ساختار-پروژه)
- [مشارکت](#-مشارکت)
- [لایسنس](#-لایسنس)
- [تشکر و قدردانی](#-تشکر-و-قدردانی)

---

## ✨ ویژگی‌ها

| | |
|---|---|
| 🌍 **دوزبانه** | فارسی + انگلیسی، تغییر لحظه‌ای |
| 🚇 **۱۱ پروتکل** | GOST، Hysteria2، Rathole، Chisel، FRP، Paqet، Backhaul، WSTunnel، Socat، SSH، iptables |
| 🎯 **۱۸ پروفایل ISP** | ایرانسل، همراه اول، رایتل، شاتل، مبین‌نت و بیشتر |
| 🛠️ **نصب خودکار** | نصب ابزارها با یک کلیک از GitHub |
| 🔒 **امنیت بالا** | PBKDF2 با ۲۰۰ هزار تکرار، CSRF، Rate Limit، نشست ۳۰ دقیقه‌ای |
| 📊 **مانیتورینگ** | CPU، RAM، دیسک، Load، آپ‌تایم |
| 🔔 **چکر بروزرسانی** | اطلاع‌رسانی نسخه جدید از GitHub |
| 🤖 **ریستارت خودکار** | بررسی سلامت + بازیابی بعد از ریبوت |
| 🔌 **یکپارچه با 3x-ui** | خواندن Inbound، ساخت کانفیگ |
| 💾 **پشتیبان‌گیری** | دانلود JSON با یک کلیک |
| ⚙️ **Systemd** | اجرای خودکار در بوت، مقاوم در برابر ریستارت |
| 📱 **ریسپانسیو** | دسکتاپ، تبلت و موبایل |

---

## 📋 پیش‌نیازها

- **سیستم‌عامل:** Ubuntu 20.04+، Debian 11+، CentOS 7+، Alpine 3.15+
- **معماری:** x86_64 یا aarch64
- **RAM:** ۵۱۲ مگابایت · **دیسک:** ۱ گیگابایت فضای آزاد
- **دسترسی:** Root (برای نصب و مدیریت ابزارها الزامی است)
- **پورت:** 8088 (پنل، قابل تغییر)

---

## 🚀 نصب

### نصب سریع (توصیه‌شده)

```bash
git clone https://github.com/metiwilson/nextunnel.git
cd nextunnel
sudo bash install.sh
```

### نصب یک‌خطی

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/metiwilson/nextunnel/main/install.sh)
```

### کاری که نصب‌کننده انجام می‌دهد

۱. تشخیص سیستم‌عامل و معماری CPU
۲. نصب پیش‌نیازها (Python 3، sqlite3، socat و...)
۳. کپی فایل‌ها به `/opt/nextunnel`
۴. ساخت سرویس systemd با نام `nextunnel`
۵. باز کردن پورت 8088 در فایروال
۶. راه‌اندازی سرویس
۷. نمایش اعتبارنامه ورود اولیه (فقط یک بار)

### دسترسی به پنل

```
http://IP-سرور-شما:8088
```

---

## 🔐 اولین ورود

۱. آدرس پنل را در مرورگر باز کنید.
۲. اطلاعات نمایش داده شده توسط نصب‌کننده را وارد کنید (**فقط یک بار نمایش داده می‌شود**).
۳. رمز عبور را تغییر دهید (**در اولین ورود اجباری است**).
۴. زبان خود را انتخاب کنید — دکمه تغییر زبان بالای صفحه ورود.

**نشست:** پس از ۳۰ دقیقه بی‌کاری، خودکار خارج می‌شوید. هر فعالیتی تایمر را ریست می‌کند.

---

## 🚇 آموزش ساخت تانل‌ها

در تمام مثال‌ها فرض می‌شود:

- `IRAN_IP` = IP سرور ایران (نقطه ورود)
- `KHAREJ_IP` = IP سرور خارج (خروجی)
- پورت پیش‌فرض = `443`

---

### ۱. GOST v3 — همه‌کاره‌ترین

| | |
|---|---|
| **مناسب برای** | همه ISPها |
| **ترنسپورت‌ها** | TCP، WS، TLS، QUIC، gRPC |
| **پیشنهاد** | ترنسپورت `tls` + Cover SNI |

**مراحل:**

۱. **ابزارها** → نصب **GOST v3**
۲. **ایجاد تانل** → پر کردن فرم → **ایجاد تانل**
۳. کلیک روی **کانفیگ** → کپی **Kharej JSON**
۴. روی سرور خارج اجرا کنید:
   ```bash
   gost -L relay+secret://:443?secret=YOUR_SECRET
   ```
۵. کلیک روی **اجرا** در سمت ایران
۶. تست:
   ```bash
   curl -x socks5://IRAN_IP:443 https://ifconfig.me
   ```

---

### ۲. Hysteria2 — بهترین برای ISP‌های سازگار با QUIC

| | |
|---|---|
| **مناسب برای** | ایرانسل، مبین‌نت، های‌وب |
| **ترنسپورت** | QUIC + Obfuscation Salamander |

**مراحل:**

۱. **ابزارها** → نصب **Hysteria2**
۲. **ایجاد تانل** → ISP `irancell` → پورت `443`
۳. کپی **Kharej YAML** → ذخیره در `/etc/hysteria/config.yaml`
۴. روی سرور خارج اجرا کنید:
   ```bash
   hysteria -c /etc/hysteria/config.yaml server
   ```
۵. کلیک روی **اجرا** در سمت ایران

---

### ۳. Rathole — تانل معکوس سبک

| | |
|---|---|
| **مناسب برای** | VPS کم‌منبع، بار سنگین TCP |
| **ترنسپورت‌ها** | TCP، WS، TLS |

**مراحل:**

۱. **ابزارها** → نصب **Rathole**
۲. **ایجاد تانل** → ترنسپورت `tcp`
۳. کپی **Kharej TOML** → ذخیره در `/etc/rathole/kharej.toml`
۴. روی سرور خارج اجرا کنید:
   ```bash
   rathole -c /etc/rathole/kharej.toml
   ```
۵. کلیک روی **اجرا** در سمت ایران

---

### ۴. Chisel — سازگار با فایروال‌های سختگیر

| | |
|---|---|
| **مناسب برای** | فایروال‌های سختگیر (فقط HTTP/WS) |

**مراحل:**

۱. نصب **Chisel**
۲. ساخت تانل (پورت ایران `8080`، پورت خارج `8888`)
۳. روی سرور خارج اجرا کنید:
   ```bash
   chisel client IRAN_IP:8080 R:8888:127.0.0.1:8888 --auth SECRET:SECRET
   ```
۴. کلیک روی **اجرا** در سمت ایران

---

### ۵. FRP — تانل معکوس حرفه‌ای

| | |
|---|---|
| **مناسب برای** | تانل پایدار با داشبورد مدیریت |

**مراحل:**

۱. نصب **FRP** (هر دو `frps` و `frpc` نصب می‌شوند)
۲. ساخت تانل (پورت ایران `7000`)
۳. روی سرور خارج اجرا کنید:
   ```bash
   frpc -c /etc/frp/frpc.toml
   ```
۴. کلیک روی **اجرا** در سمت ایران

---

### ۶. Backhaul — چند ترنسپورت

| | |
|---|---|
| **مناسب برای** | کاربران پیشرفته با نیاز WS/TLS/SMUX/YAMUX |

**مراحل:**

۱. نصب **Backhaul**
۲. ساخت تانل (ترنسپورت `tls`)
۳. روی سرور خارج اجرا کنید:
   ```bash
   backhaul -c IRAN_IP:443 -l 127.0.0.1:443 -t tls -token SECRET
   ```
۴. کلیک روی **اجرا** در سمت ایران

---

### ۷. WSTunnel — تانل WebSocket

| | |
|---|---|
| **مناسب برای** | محیط‌های WebSocket-only سازگار با CDN |

**مراحل:**

۱. نصب **WSTunnel**
۲. ساخت تانل (پورت ایران `8443`)
۳. روی سرور خارج اجرا کنید:
   ```bash
   wstunnel client -L tcp://127.0.0.1:443:127.0.0.1:443 ws://IRAN_IP:8443
   ```
۴. کلیک روی **اجرا** در سمت ایران

---

### ۸. Paqet — عملکرد Raw Socket

| | |
|---|---|
| **مناسب برای** | ترافیک با throughput بالا و حساس به تأخیر |

**مراحل:**

۱. نصب **Paqet**
۲. ساخت تانل
۳. روی سرور خارج اجرا کنید:
   ```bash
   paqet -L kcp://:443
   ```
۴. کلیک روی **اجرا** در سمت ایران

---

### ۹. Socat — ساده‌ترین فورواردینگ پورت

| | |
|---|---|
| **مناسب برای** | فوروارد سریع پورت بدون نیاز به نرم‌افزار اضافه |

**مراحل:**

۱. نصب **Socat**
۲. ساخت تانل → کلیک روی **اجرا**
۳. ✅ نیاز به کانفیگ سمت خارج ندارد

---

### ۱۰. تانل SSH — رمزنگاری شده با SSH

| | |
|---|---|
| **مناسب برای** | دسترسی SSH موجود، بدون نرم‌افزار اضافه |

**پیش‌نیازها:**

```bash
ssh-keygen -t ed25519
ssh-copy-id root@KHAREJ_IP
```

**مراحل:**

۱. ساخت تانل (پورت ایران `1080`)
۲. کلیک روی **اجرا**

---

### ۱۱. iptables NAT — سطح کرنل

| | |
|---|---|
| **مناسب برای** | بیشترین کارایی، بدون overhead کاربر‌فضا |

**مراحل:**

۱. ساخت تانل
۲. کلیک روی **اجرا** — پنل این دستورات را اعمال می‌کند:
   ```bash
   sysctl -w net.ipv4.ip_forward=1
   iptables -t nat -A PREROUTING -p tcp --dport 443 -j DNAT --to-destination KHAREJ_IP:443
   iptables -t nat -A POSTROUTING -j MASQUERADE
   ```

> ⚠️ برای ماندگاری پس از ریبوت، `iptables-persistent` نصب کنید:
> ```bash
> sudo apt install iptables-persistent
> sudo netfilter-persistent save
> ```

---

## 🎯 بهینه‌سازی ISP

NexTunnel با **۱۸ پروفایل ISP** از پیش تنظیم‌شده ارائه می‌شود. **روش استفاده:**

۱. **پروفایل‌های ISP** → ISP خود را پیدا کنید → کلیک روی **اعمال**
۲. فرم به‌طور خودکار با تنظیمات پیشنهادی پر می‌شود
۳. با آموزش پروتکل مربوطه ادامه دهید

### انتخاب سریع

| ISP | پروتکل | ترنسپورت |
|-----|--------|-----------|
| ایرانسل / های‌وب / مبین‌نت | Hysteria2 | QUIC |
| همراه اول (MCI) | GOST | TCP (پورت 80) |
| شاتل / مخابرات | GOST | TLS + Cover SNI |
| رایتل / افرانت | GOST | WS (پورت 443) |
| زیتل | GOST | gRPC |
| پارس آنلاین / پیشگامان | Rathole | TCP / TLS |
| سایر / نامشخص | GOST | TLS (پورت 443) |

### افزودن ISP سفارشی

**پروفایل‌های ISP** → **+ افزودن پروفایل سفارشی** → پر کردن فرم → **ذخیره**

---

## 🔌 یکپارچه‌سازی با 3x-ui

NexTunnel پایگاه داده SQLite پنل 3x-ui را **فقط می‌خواند** (هرگز به آن نمی‌نویسد).

- **مشاهده Inbound‌ها:** داشبورد → کارت وضعیت 3x-ui
- **تولید کانفیگ:** کانفیگ → تب **یکپارچه‌سازی X-UI** → کپی JSON‌های Inbound/Outbound/Routing
- **مسیرهای پشتیبانی‌شده:**
  - `/etc/x-ui/x-ui.db`
  - `/usr/local/x-ui/x-ui.db`

JSON‌های تولید شده را در پنل 3x-ui از طریق **Inbounds → Add** پیست کنید.

---

## ⚙️ مدیریت سرویس

```bash
systemctl status nextunnel      # بررسی وضعیت
systemctl restart nextunnel     # ریستارت
systemctl stop nextunnel        # توقف
systemctl start nextunnel       # شروع
systemctl enable nextunnel      # اجرای خودکار در بوت
systemctl disable nextunnel     # غیرفعال کردن اجرای خودکار
journalctl -u nextunnel -f      # لاگ زنده
journalctl -u nextunnel -n 100  # ۱۰۰ خط آخر
```

### مسیر لاگ‌ها

| لاگ | مسیر |
|-----|------|
| خروجی سرویس | `/opt/nextunnel/logs/service.log` |
| لاگ هر تانل | `/opt/nextunnel/logs/tunnel_<id>.log` |
| سیستم (journald) | `journalctl -u nextunnel` |

---

## 🧩 تمپلیت Systemd (برای سمت خارج)

از این تمپلیت برای اجرای ابزارهای سمت خارج به صورت سرویس دائمی استفاده کنید:

```bash
sudo tee /etc/systemd/system/نام-سرویس.service << 'EOF'
[Unit]
Description=توضیح سرویس شما
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/باینری -c /etc/مسیر/کانفیگ
Restart=always
RestartSec=5
LimitNOFILE=1048576

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now نام-سرویس
```

### مثال‌های آماده

**سرور Hysteria2:**
```ini
ExecStart=/usr/local/bin/hysteria -c /etc/hysteria/config.yaml server
```

**کلاینت Rathole:**
```ini
ExecStart=/usr/local/bin/rathole -c /etc/rathole/kharej.toml
```

**کلاینت GOST:**
```ini
ExecStart=/usr/local/bin/gost -L relay+secret://:443?secret=YOUR_SECRET
```

**کلاینت FRP:**
```ini
ExecStart=/usr/local/bin/frpc -c /etc/frp/frpc.toml
```

---

## 🔄 بروزرسانی

### بروزرسانی دستی

```bash
cd /path/to/nextunnel
git pull
sudo systemctl restart nextunnel
```

### اطلاع‌رسانی بروزرسانی

پنل هر ساعت یک بار GitHub Releases API را بررسی می‌کند. وقتی نسخه جدید در دسترس باشد:

- یک **بنر سبز** در داشبورد نمایش داده می‌شود
- یک **اعلان toast** در ورود بعدی ظاهر می‌شود

روی بنر کلیک کنید تا صفحه انتشار باز شود.

---

## 🗑️ حذف

```bash
sudo systemctl stop nextunnel
sudo systemctl disable nextunnel
sudo rm /etc/systemd/system/nextunnel.service
sudo rm -rf /opt/nextunnel
sudo systemctl daemon-reload
```

> ⚠️ دستور `rm -rf /opt/nextunnel` پایگاه داده، تانل‌ها و لاگ‌ها را حذف می‌کند. اگر نیاز دارید، ابتدا از `nextunnel.db` پشتیبان بگیرید.

---

## 🔒 امنیت

| ویژگی | جزئیات |
|-------|--------|
| هش رمز عبور | PBKDF2-HMAC-SHA256، ۲۰۰ هزار تکرار |
| Salt | ۱۶ بایت به ازای هر کاربر، در هر تغییر |
| نشست | کوکی HttpOnly، با timeout ۳۰ دقیقه‌ای |
| CSRF | توکن به ازای هر نشست، در تمام عملیات نوشتن |
| Rate Limiting | ۵ ورود ناموفق → قفل ۱۵ دقیقه‌ای |
| HTTP Headers | `X-Content-Type-Options`، `X-Frame-Options`، `Referrer-Policy` |

### توصیه‌های امنیتی

۱. **از HTTPS استفاده کنید** — پنل را پشت Nginx یا Caddy با TLS قرار دهید
۲. **دسترسی را محدود کنید** — پورت پنل را به IP یا VPN خود محدود کنید
۳. **رمز عبور قوی** — حداقل ۱۲ کاراکتر
۴. **بروزرسانی منظم** — چکر بروزرسانی را فعال نگه دارید
۵. **پشتیبان‌گیری منظم** — از خروجی JSON داخلی استفاده کنید

### نمونه Reverse Proxy با Nginx

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

## 🐛 عیب‌یابی

| مشکل | راه‌حل |
|------|-------|
| **پنل باز نمی‌شود** | `systemctl restart nextunnel` · بررسی فایروال پورت 8088 |
| **رمز عبور فراموش شده** | توقف سرویس، حذف `nextunnel.db`، شروع مجدد، بررسی journalctl |
| **نصب ابزار ناموفق** | دسترسی root · اتصال اینترنت · فضای دیسک |
| **تانل اجرا نمی‌شود** | بررسی نصب ابزار · خالی بودن پورت · بررسی لاگ در `/opt/nextunnel/logs/` |
| **بعد از ریبوت بازیابی نمی‌شود** | `systemctl enable nextunnel` · ۶۰ ثانیه بعد از بوت صبر کنید |
| **نشست سریع منقضی می‌شود** | ویرایش `CONFIG["session_minutes"]` در `nextunnel.py`، ریستارت |
| **چکر بروزرسانی کار نمی‌کند** | تست `curl -I https://api.github.com`، ریستارت سرویس |

### بازیابی رمز فراموش شده

```bash
sudo systemctl stop nextunnel
sudo rm /opt/nextunnel/nextunnel.db
sudo systemctl start nextunnel
sudo journalctl -u nextunnel -n 50 | grep -A4 CREDENTIALS
```

### پورت اشغال است

```bash
# پیدا کردن پروسه استفاده‌کننده از پورت
ss -tlnp | grep 443

# کشتن پروسه (اگر امن است)
sudo kill <PID>
```

### نصب دستی ابزار

```bash
# مثال برای GOST
curl -fsSL https://github.com/go-gost/gost/releases/download/v3.0.0/gost_3.0.0_linux_amd64.tar.gz \
  | tar -xz -C /usr/local/bin/ gost
chmod +x /usr/local/bin/gost
gost -V
```

---

## ❓ سؤالات متداول

**س: کدام پروتکل را استفاده کنم؟**
- ایرانسل / های‌وب / مبین‌نت → **Hysteria2**
- همراه اول (MCI) → **GOST (TCP، پورت 80)**
- شاتل / مخابرات → **GOST (TLS + Cover SNI)**
- ISP نامشخص → **GOST (TLS، پورت 443)**

**س: آیا NexTunnel پنل 3x-ui را تغییر می‌دهد؟**
خیر — فقط می‌خواند. هرگز نمی‌نویسد.

**س: می‌توانم روی سرور غیر ایران اجرا کنم؟**
فنی بله، اما طراحی برای سمت ایران است. کانفیگ‌های سمت خارج به صورت دستی مستقر می‌شوند.

**س: پشتیبانی از چند کاربر؟**
فعلاً یک admin. ساختار پایگاه داده آماده توسعه در آینده است.

**س: چند تانل می‌توانم بسازم؟**
محدودیت سخت‌افزاری ندارد — به منابع سرور (CPU/RAM/شبکه) بستگی دارد.

**س: چطور پورت پنل را تغییر دهم؟**
`CONFIG["port"]` را در `nextunnel.py` ویرایش کنید، سرویس را ریستارت کنید، فایروال را به‌روز کنید.

**س: از IPv6 پشتیبانی می‌کند؟**
جزئی — پنل به IPv4 متصل می‌شود، اما IP تانل‌ها می‌تواند IPv6 باشد اگر ابزار پشتیبانی کند.

**س: چطور پشتیبان بگیرم؟**
دو روش:
۱. تنظیمات → **دانلود پشتیبان JSON**
۲. کپی `/opt/nextunnel/nextunnel.db` و `/opt/nextunnel/tunnels/`

**س: اگر پنل کرش کند چه می‌شود؟**
Systemd در ۱۰ ثانیه auto-restart می‌کند. تانل‌های در حال اجرا به عنوان پروسه‌های detached ادامه می‌دهند.

**س: آیا Secretها رمزنگاری شده ذخیره می‌شوند؟**
خیر — به صورت plain text در SQLite ذخیره می‌شوند. سرور خود را با رمزنگاری دیسک امن کنید.

---

## 📁 ساختار پروژه

```
nextunnel/
├── nextunnel.py       # فایل اصلی (Python 3، تک‌فایل)
├── install.sh         # اسکریپت نصب
├── README.md          # نسخه انگلیسی
├── README.fa.md       # این فایل (فارسی)
├── LICENSE            # لایسنس MIT
└── .github/
    └── workflows/
        └── release.yml

# فایل‌های Runtime (در زمان نصب ساخته می‌شوند):
/opt/nextunnel/
├── nextunnel.py       # کپی نصب‌شده
├── nextunnel.db       # پایگاه داده SQLite
├── tunnels/           # کانفیگ تانل‌ها (JSON)
├── logs/              # لاگ‌های برنامه
├── pids/              # فایل‌های PID تانل‌ها
└── backups/           # خروجی‌های پشتیبان
```

### جداول پایگاه داده

| جدول | کاربرد |
|------|--------|
| `users` | حساب‌های admin |
| `sessions` | نشست‌های فعال |
| `login_attempts` | تاریخچه Rate Limiting |
| `tunnels` | تعریف و کانفیگ تانل‌ها |
| `logs` | لاگ رویدادها |
| `isp_profiles` | پروفایل‌های ISP داخلی + سفارشی |
| `settings` | تنظیمات key/value |

---

## 🤝 مشارکت

### چطور مشارکت کنم

۱. **Fork** کنید
۲. **شاخه جدید بسازید:** `git checkout -b feature/my-feature`
۳. **Commit کنید:** `git commit -am 'Add feature'`
۴. **Push کنید:** `git push origin feature/my-feature`
۵. **Pull Request باز کنید**

### راهنماها

- **PEP 8** را برای کد پایتون رعایت کنید
- معماری تک‌فایل برای `nextunnel.py` را حفظ کنید
- روی **Ubuntu 22.04** و **Debian 12** تست کنید
- برای تغییرات user-facing، README را به‌روز کنید
- برای اقدامات مهم، ورودی در event log اضافه کنید

### گزارش باگ

یک Issue باز کنید و این موارد را ذکر کنید:
- نسخه NexTunnel (در footer نمایش داده می‌شود)
- سیستم‌عامل و معماری (`uname -a`)
- مراحل بازتولید
- رفتار انتظاری در مقابل رفتار واقعی
- بخش‌های مرتبط از لاگ

---

## 📄 لایسنس

این پروژه تحت **لایسنس MIT** منتشر شده است — متن کامل در [LICENSE](LICENSE).

```
MIT License · Copyright (c) 2025 metiwilson
```

---

## 🙏 تشکر و قدردانی

NexTunnel بر پایه ابزارهای فوق‌العاده open-source ساخته شده است:

- [**GOST**](https://github.com/go-gost/gost) — تانل و پروکسی همه‌کاره
- [**Hysteria2**](https://github.com/apernet/hysteria) — پروکسی مبتنی بر QUIC
- [**Rathole**](https://github.com/rapiz1/rathole) — تانل معکوس سبک
- [**Chisel**](https://github.com/jpillora/chisel) — تانل HTTP/WS
- [**FRP**](https://github.com/fatedier/frp) — پروکسی معکوس سریع
- [**Backhaul**](https://github.com/Musixal/Backhaul) — تانل چند ترنسپورت
- [**WSTunnel**](https://github.com/erebe/wstunnel) — تانل WebSocket
- [**Paqet**](https://github.com/hans-thomas/paqet) — KCP raw socket
- [**3x-ui**](https://github.com/MHSanaei/3x-ui) — پنل Xray

تشکر ویژه از جامعه شبکه‌ای فارسی‌زبان برای اشتراک دانش و بازخورد.

---

<div align="center">

### ⭐ اگر این پروژه برایتان مفید بود، لطفاً ستاره بدهید!

**این انگیزه‌بخش توسعه مداوم است و به دیگران کمک می‌کند پروژه را کشف کنند.**

[![Star History Chart](https://api.star-history.com/svg?repos=metiwilson/nextunnel&type=Date)](https://star-history.com/#metiwilson/nextunnel&Date)

---

**NexTunnel** — پلتفرم مدیریت تانل همه‌کاره

ساخته شده با ❤️ توسط [metiwilson](https://github.com/metiwilson)

[🏠 مخزن](https://github.com/metiwilson/nextunnel) · [🐛 مشکلات](https://github.com/metiwilson/nextunnel/issues) · [💬 بحث‌ها](https://github.com/metiwilson/nextunnel/discussions) · [📄 لایسنس](LICENSE)

</div>

</div>
