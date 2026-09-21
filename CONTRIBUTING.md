# Contributing to NexTunnel

<div align="center">

**First off, thank you for considering contributing to NexTunnel! 🎉**

It's people like you that make NexTunnel such a great tool for the community.

[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/metiwilson/nextunnel/pulls)
[![Contributors](https://img.shields.io/github/contributors/metiwilson/nextunnel)](https://github.com/metiwilson/nextunnel/graphs/contributors)
[![Issues](https://img.shields.io/github/issues/metiwilson/nextunnel)](https://github.com/metiwilson/nextunnel/issues)
[![Forks](https://img.shields.io/github/forks/metiwilson/nextunnel?style=social)](https://github.com/metiwilson/nextunnel/network/members)

</div>

---

## 📑 Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [How Can I Contribute?](#-how-can-i-contribute)
  - [Reporting Bugs](#-reporting-bugs)
  - [Suggesting Features](#-suggesting-features)
  - [Improving Documentation](#-improving-documentation)
  - [Translating](#-translating)
  - [Writing Code](#-writing-code)
- [Development Setup](#-development-setup)
- [Development Workflow](#-development-workflow)
- [Coding Standards](#-coding-standards)
- [Commit Guidelines](#-commit-guidelines)
- [Pull Request Process](#-pull-request-process)
- [Review Process](#-review-process)
- [Testing Guidelines](#-testing-guidelines)
- [Project Structure](#-project-structure)
- [Community](#-community)
- [Recognition](#-recognition)
- [Questions?](#-questions)

---

## 📜 Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

**In short:**

- 🤝 Be respectful and inclusive
- 💬 Welcome newcomers and help them learn
- 🚫 No harassment, discrimination, or hate speech
- 🎯 Focus on what is best for the community
- ❤️ Assume good faith in every interaction

Please report unacceptable behavior to **metiwilson** via [GitHub Issues](https://github.com/metiwilson/nextunnel/issues) or email (see profile).

---

## 🎯 How Can I Contribute?

There are many ways to contribute to NexTunnel — you don't have to write code!

### 🐛 Reporting Bugs

Found a bug? Help us fix it by following these steps:

#### Before Submitting a Bug Report

1. **Check the [FAQ](README.md#-faq)** — your question might already be answered
2. **Search [existing issues](https://github.com/metiwilson/nextunnel/issues)** — someone may have reported it
3. **Check the [CHANGELOG](CHANGELOG.md)** — it may already be fixed in an unreleased version
4. **Update to the latest version** — `git pull && sudo systemctl restart nextunnel`

#### How to Submit a Bug Report

Open a [new issue](https://github.com/metiwilson/nextunnel/issues/new) and include:

**Required information:**

- **NexTunnel version** — shown in the footer or from `grep "version" nextunnel.py`
- **OS and architecture** — output of `uname -a` and `cat /etc/os-release`
- **Python version** — output of `python3 --version`
- **Steps to reproduce** — numbered list, as specific as possible
- **Expected behavior** — what you expected to happen
- **Actual behavior** — what actually happened
- **Relevant log excerpts** — from `journalctl -u nextunnel -n 100`

**Optional but helpful:**

- **Screenshots** — for UI-related bugs
- **Network details** — if related to specific ISPs or protocols
- **Config files** — sanitized (remove secrets!) versions of your tunnel configs

#### Bug Report Template

```markdown
### Description
A clear description of the bug.

### Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

### Expected Behavior
What should have happened.

### Actual Behavior
What actually happened.

### Environment
- NexTunnel version: v1.0.0
- OS: Ubuntu 22.04
- Architecture: x86_64
- Python: 3.10.12
- Browser: Chrome 120

### Logs
```
<paste relevant log excerpts here>
```

### Additional Context
Any other context about the problem.
```

#### ⚠️ Security Vulnerabilities

**Do NOT open a public issue for security vulnerabilities.**

Instead, follow the process in [SECURITY.md](SECURITY.md) or contact the maintainer directly.

---

### 💡 Suggesting Features

Have an idea that would make NexTunnel better? We'd love to hear it!

#### Before Suggesting a Feature

1. **Check the [roadmap](CHANGELOG.md#-planned-for-future-releases)** — it may already be planned
2. **Search [existing issues](https://github.com/metiwilson/nextunnel/issues?q=is%3Aissue+label%3Aenhancement)** — someone may have suggested it
3. **Consider scope** — is it a small improvement or a large feature?

#### How to Suggest a Feature

Open a [new issue](https://github.com/metiwilson/nextunnel/issues/new) with the `enhancement` label and include:

- **Problem statement** — what problem does this solve?
- **Proposed solution** — how would you implement it?
- **Alternatives considered** — any other approaches?
- **Use case** — who benefits and how?
- **Willingness to implement** — are you willing to code it?

#### Feature Request Template

```markdown
### Feature Description
A clear description of the feature.

### Problem Statement
What problem does this feature solve?
Example: "I'm always frustrated when..."

### Proposed Solution
How you would like it to work.

### Alternatives Considered
Any alternative solutions or features you've considered.

### Use Case
Describe who would benefit and how.

### Additional Context
Any other context, screenshots, or mockups.

### Willingness to Contribute
- [ ] I am willing to submit a PR for this feature
- [ ] I need guidance on how to implement it
```

---

### 📚 Improving Documentation

Documentation improvements are **highly valued**. You can help by:

- **Fixing typos** or grammatical errors
- **Clarifying confusing sections**
- **Adding examples** to tutorials
- **Translating** to new languages
- **Adding screenshots** or diagrams

Documentation files:

| File | Purpose |
|------|---------|
| `README.md` | English main documentation |
| `README.fa.md` | Persian documentation |
| `CHANGELOG.md` | Version history |
| `CONTRIBUTING.md` | This file |
| `SECURITY.md` | Security policy |
| Inline docstrings | Python code documentation |

**To improve docs:**

1. Fork the repo
2. Edit the relevant `.md` file
3. Ensure formatting renders correctly (preview on GitHub)
4. Submit a PR with a clear description

---

### 🌍 Translating

NexTunnel is currently available in **English** and **Persian (Farsi)**. We'd love help adding more languages!

#### Adding a New Language

1. **Frontend translations** — in `nextunnel.py`, find the `I18N` object inside the `HTML` string:

   ```javascript
   const I18N = {
     en: { dashboard:'Dashboard', ... },
     fa: { dashboard:'داشبورد', ... },
     // Add your language here:
     // ar: { dashboard:'لوحة القيادة', ... },
   };
   ```

2. **Backend messages** — find the `MESSAGES` dict:

   ```python
   MESSAGES = {
       "en": { "unauthorized": "Unauthorized", ... },
       "fa": { "unauthorized": "غیرمجاز", ... },
       # Add your language here:
   }
   ```

3. **Update the language toggle** in the HTML section to include your language.

4. **Test** thoroughly by switching to your language in the UI.

5. **Submit a PR** with:
   - The new language code (ISO 639-1: `ar`, `ru`, `zh`, etc.)
   - All UI strings translated
   - Screenshots showing the new language

#### Improving Existing Translations

If you notice incorrect or awkward translations in English or Persian:

1. Open an issue with the specific string and your suggested correction
2. Or submit a PR directly with the fix

---

### 💻 Writing Code

Want to write code? Excellent! Here's how to get started.

#### Areas We Need Help With

| Area | Difficulty | Description |
|------|------------|-------------|
| 🐛 **Bug fixes** | Easy → Hard | Check open issues |
| 📝 **Documentation** | Easy | Typos, examples, clarity |
| 🎨 **UI/UX** | Medium | Improve layout, add animations |
| 🌐 **Translations** | Easy | Add new languages |
| 🔧 **New protocols** | Medium | Add support for new tunnel tools |
| 📊 **Monitoring** | Medium | Traffic graphs, stats |
| 🔒 **Security** | Hard | Audit, harden, fix vulnerabilities |
| ⚡ **Performance** | Hard | Optimize queries, async operations |

#### Before You Start Coding

1. **Open an issue first** describing what you want to work on (unless it's a trivial fix)
2. **Wait for maintainer approval** to avoid wasted effort
3. **Comment on the issue** that you're working on it
4. **Ask questions** if anything is unclear

This prevents duplicate work and ensures your contribution aligns with the project's direction.

---

## 🛠️ Development Setup

### Prerequisites

- **Python 3.8+** — [python.org](https://python.org)
- **Git** — [git-scm.com](https://git-scm.com)
- **Linux** — Ubuntu 22.04, Debian 12, or similar (macOS may work but not officially supported)
- **Root access** — for testing tool installation (or use a VM/container)

### Fork and Clone

1. **Fork** the repository on GitHub (click the "Fork" button)

2. **Clone your fork:**

   ```bash
   git clone https://github.com/YOUR_USERNAME/nextunnel.git
   cd nextunnel
   ```

3. **Add upstream remote:**

   ```bash
   git remote add upstream https://github.com/metiwilson/nextunnel.git
   git fetch upstream
   ```

4. **Verify remotes:**

   ```bash
   git remote -v
   # origin    https://github.com/YOUR_USERNAME/nextunnel.git (fetch)
   # origin    https://github.com/YOUR_USERNAME/nextunnel.git (push)
   # upstream  https://github.com/metiwilson/nextunnel.git (fetch)
   # upstream  https://github.com/metiwilson/nextunnel.git (push)
   ```

### Run Locally

Since NexTunnel is a single-file application, running it locally is simple:

```bash
# Option 1: Direct run
sudo python3 nextunnel.py

# Option 2: In a virtual environment (recommended for development)
python3 -m venv venv
source venv/bin/activate
python3 nextunnel.py
```

Open `http://localhost:8088` in your browser.

### Development Database

For development, use a separate database to avoid clobbering your production data:

```bash
# Edit nextunnel.py temporarily or set an env var:
export NEXTUNNEL_DB=/tmp/nextunnel-dev.db
```

> 💡 **Tip:** Consider adding an env var override in your fork if you plan to develop frequently.

### Testing Without Root

Some features (tool installation, iptables) require root. For non-root development:

- Mock `is_root()` to return `False` and test UI paths
- Use a container or VM for full testing
- Skip root-only features

### Reset Development State

To reset everything:

```bash
rm -f nextunnel.db
rm -rf tunnels/ logs/ pids/ backups/
python3 nextunnel.py  # Will regenerate fresh credentials
```

---

## 🔄 Development Workflow

### 1. Sync with Upstream

Before starting work, always sync with upstream:

```bash
git checkout main
git fetch upstream
git merge upstream/main
git push origin main
```

### 2. Create a Feature Branch

Use descriptive branch names:

```bash
# Format: <type>/<short-description>
git checkout -b feature/multi-user-support
git checkout -b fix/session-timeout-bug
git checkout -b docs/update-installation-guide
git checkout -b translate/add-arabic
```

**Branch name prefixes:**

| Prefix | Purpose |
|--------|---------|
| `feature/` | New features |
| `fix/` | Bug fixes |
| `docs/` | Documentation |
| `translate/` | Translations |
| `refactor/` | Code refactoring |
| `test/` | Tests |
| `chore/` | Maintenance |

### 3. Make Your Changes

- **Write clean code** (see [Coding Standards](#-coding-standards))
- **Test your changes** thoroughly
- **Update documentation** if needed
- **Add to CHANGELOG** under `[Unreleased]`

### 4. Commit Your Changes

Follow [Conventional Commits](#-commit-guidelines):

```bash
git add .
git commit -m "feat: add multi-user support with role-based access"
```

### 5. Keep Your Branch Updated

If upstream has changed significantly:

```bash
git fetch upstream
git rebase upstream/main
# Resolve conflicts if any
git push -f origin feature/multi-user-support
```

### 6. Push to Your Fork

```bash
git push origin feature/multi-user-support
```

### 7. Open a Pull Request

Go to GitHub and open a PR from your branch to `metiwilson/nextunnel:main`.

See [Pull Request Process](#-pull-request-process) for details.

---

## 📐 Coding Standards

### Python Style

NexTunnel follows **PEP 8** with some pragmatic adjustments:

#### General Rules

- **Indentation:** 4 spaces (no tabs)
- **Line length:** Soft limit 100, hard limit 120 characters
- **Quotes:** Single quotes `'...'` by default; double quotes for strings containing single quotes
- **Encoding:** UTF-8 always; include `# -*- coding: utf-8 -*-` at the top
- **Shebang:** `#!/usr/bin/env python3` on executable files

#### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Functions | `snake_case` | `create_tunnel()`, `get_session()` |
| Variables | `snake_case` | `tunnel_id`, `user_agent` |
| Constants | `UPPER_SNAKE_CASE` | `CONFIG`, `SESSION_TTL` |
| Classes | `PascalCase` | `Handler`, `ReusableTCPServer` |
| Private | `_leading_underscore` | `_db_lock`, `_read_json()` |

#### Function Design

- **Keep functions focused** — one responsibility per function
- **Limit parameters** — max 5-6; use a dict for more
- **Return consistent types** — always return a dict with `ok` key for API-like functions
- **Document complex logic** with docstrings

Example:

```python
def create_tunnel(data):
    """
    Create a new tunnel from the given data dict.

    Args:
        data: Dict containing tunnel fields (name, protocol, etc.)

    Returns:
        Dict with 'ok' (bool) and either 'tunnel_id' or 'error'.
    """
    name = (data.get('name') or '').strip()
    if not name:
        return {"ok": False, "error": "Tunnel name is required"}
    # ...
```

#### Error Handling

- **Prefer explicit returns** over exceptions for expected errors
- **Use try/except** for external calls (subprocess, file I/O, network)
- **Log errors** with `log_event()` before returning
- **Never expose internal errors** to the frontend — sanitize error messages

```python
try:
    result = subprocess.run(cmd, timeout=30, capture_output=True)
except subprocess.TimeoutExpired:
    log_event(tunnel_id, 'error', 'Operation timed out')
    return {"ok": False, "error": "Operation timed out"}
except Exception as e:
    log_event(tunnel_id, 'error', f'Unexpected error: {e}')
    return {"ok": False, "error": "Internal error"}
```

#### Database Access

- **Always use parameterized queries** — never string interpolation
- **Always use the `_db_lock`** context for writes
- **Close connections** in `finally` blocks
- **Use `db_connect()`** helper for consistent setup

```python
# ✅ CORRECT
with _db_lock:
    conn = db_connect()
    try:
        conn.execute("SELECT * FROM tunnels WHERE id=?", (tunnel_id,))
        conn.commit()
    finally:
        conn.close()

# ❌ WRONG — SQL injection risk, no lock, no close
conn = sqlite3.connect(CONFIG['db_file'])
conn.execute(f"SELECT * FROM tunnels WHERE id={tunnel_id}")
```

### JavaScript / HTML Style

- **Indentation:** 2 spaces for JS/HTML/CSS inside the HTML string
- **Modern JS** — ES6+ (`const`, `let`, arrow functions, template literals)
- **`esc()` function** — always use for user-provided content in HTML
- **`t()` function** — always use for user-visible strings (for i18n)
- **No external dependencies** — keep everything self-contained

```javascript
// ✅ CORRECT
const html = `<div>${esc(userInput)}</div>`;

// ❌ WRONG — XSS vulnerability
const html = '<div>' + userInput + '</div>';
```

### SQL Style

- **Uppercase keywords** — `SELECT`, `INSERT`, `UPDATE`, `DELETE`
- **One clause per line** for complex queries
- **Parameterized values** — always use `?`
- **Explicit column names** — avoid `SELECT *` in production code

```sql
-- ✅ CORRECT
SELECT id, name, protocol, status
FROM tunnels
WHERE status = ?
  AND created_at > ?
ORDER BY created_at DESC

-- ❌ WRONG
select * from tunnels where status='running'
```

### CSS Style

- **CSS variables** for theming (`--primary`, `--surface`, etc.)
- **Mobile-first** — use `min-width` media queries
- **RTL-aware** — use `inset-inline-start` instead of `left`
- **No inline styles** in HTML except for dynamic values

---

## 📝 Commit Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat: add traffic statistics per tunnel` |
| `fix` | Bug fix | `fix: resolve rathole config generation error` |
| `docs` | Documentation | `docs: update installation instructions` |
| `style` | Formatting (no code change) | `style: fix indentation in handler` |
| `refactor` | Code refactor | `refactor: extract tunnel validation logic` |
| `perf` | Performance improvement | `perf: optimize session cleanup query` |
| `test` | Adding tests | `test: add unit tests for password hashing` |
| `chore` | Maintenance | `chore: update dependencies` |
| `ci` | CI/CD changes | `ci: add release workflow` |
| `security` | Security fix | `security: prevent XSS in log viewer` |
| `translate` | Translation | `translate: add Arabic language support` |
| `revert` | Revert a commit | `revert: revert "feat: multi-user support"` |

### Scope (Optional)

Use the module or area affected:

- `api`, `auth`, `tunnels`, `tools`, `isp`, `ui`, `db`, `security`, `docs`, `install`

### Examples

**Simple commit:**

```
feat(tunnels): add bulk start/stop actions
```

**Commit with body:**

```
fix(auth): correct session timeout calculation

The session timeout was using CONFIG['session_days'] instead
of SESSION_TTL, causing sessions to expire after 30 days
instead of 30 minutes.

Closes #42
```

**Breaking change:**

```
feat(api)!: change tunnel creation endpoint

BREAKING CHANGE: The /api/tunnels endpoint now requires
a `transport` field. Existing clients must be updated.

Migration: Add `"transport": "tcp"` to your request body.
```

### Commit Message Rules

- **Use imperative mood** — "add" not "added" or "adds"
- **Don't capitalize** the subject line
- **No period** at the end of the subject
- **Limit subject to 72 characters**
- **Separate subject and body** with a blank line
- **Wrap body at 72 characters**
- **Reference issues** with `Closes #123` or `Fixes #123`

---

## 🔀 Pull Request Process

### Before Submitting

Run through this checklist:

- [ ] I've synced my fork with `upstream/main`
- [ ] I'm working on a dedicated branch (not `main`)
- [ ] My code follows the [coding standards](#-coding-standards)
- [ ] I've tested my changes locally
- [ ] I've updated documentation (if needed)
- [ ] I've added an entry to `CHANGELOG.md` under `[Unreleased]`
- [ ] I've added tests (if applicable)
- [ ] My commit messages follow the [guidelines](#-commit-guidelines)
- [ ] I've checked for security issues

### PR Title

Use the same format as commit messages:

```
feat: add multi-user support with role-based access
fix: resolve session timeout bug on mobile devices
docs: add Hysteria2 setup tutorial
```

### PR Description Template

```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation update
- [ ] Translation
- [ ] Code refactoring
- [ ] Performance improvement
- [ ] Security fix

## Related Issues
Closes #123
Fixes #456

## Changes Made
- Added X
- Changed Y
- Removed Z

## Screenshots (if applicable)
Before | After
-------|------
![before](#) | ![after](#)

## Testing
Describe how you tested your changes:
- [ ] Tested on Ubuntu 22.04
- [ ] Tested on Debian 12
- [ ] Tested on mobile viewport
- [ ] Tested with different protocols
- [ ] Tested with both languages (EN/FA)

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I've performed a self-review of my code
- [ ] I've commented complex code
- [ ] I've updated documentation
- [ ] I've added to CHANGELOG.md
- [ ] My changes generate no new warnings
- [ ] I've tested thoroughly
```

### PR Best Practices

#### Keep PRs Small

- **Aim for < 500 lines changed**
- One feature or fix per PR
- Split large features into multiple PRs
- Smaller PRs get reviewed faster and more thoroughly

#### Keep PRs Focused

- Don't mix unrelated changes
- Don't fix formatting issues in unrelated files
- Don't upgrade dependencies as a "side task"

#### Respond to Feedback

- Address review comments promptly
- Ask questions if feedback is unclear
- Don't take criticism personally
- Push new commits to the same branch (don't force-push after review starts unless asked)

---

## 👀 Review Process

### What to Expect

1. **Acknowledgement** — Maintainer acknowledges your PR within 3-7 days
2. **Initial review** — Automated checks + manual review
3. **Feedback** — Specific comments on code, style, or approach
4. **Iteration** — You make changes based on feedback
5. **Approval** — Once approved, PR is merged
6. **Credits** — You're added to the contributors list

### Review Timeline

| Step | Expected Time |
|------|---------------|
| Acknowledgement | 3-7 days |
| Initial review | 1-2 weeks |
| Feedback iteration | As fast as you can respond |
| Final approval | 1-3 days after last change |
| Merge | Same day as approval |

> ⏰ **Note:** NexTunnel is maintained by a single person in their spare time. Delays are expected. Please be patient — your contribution is valued!

### What Reviewers Look For

- **Correctness** — Does it work as described?
- **Style** — Does it follow project conventions?
- **Tests** — Is it tested?
- **Docs** — Is documentation updated?
- **Security** — Are there any vulnerabilities?
- **Performance** — Any unnecessary overhead?
- **Scope** — Is the change focused and minimal?

### Automated Checks

We may have these running on PRs (once set up):

- **Python syntax check** — `python3 -m py_compile nextunnel.py`
- **Flake8 / Ruff** — code style
- **Security scan** — `bandit` for Python
- **Link check** — verify README links work

---

## 🧪 Testing Guidelines

### Manual Testing

Since NexTunnel is a single-file app with no automated test suite yet, **manual testing is essential**.

#### Test Checklist for Any Change

- [ ] Panel loads without errors
- [ ] Login works
- [ ] Dashboard renders correctly
- [ ] All navigation items load
- [ ] Language switch works (EN ↔ FA)
- [ ] Theme switch works (dark ↔ light)
- [ ] Mobile viewport (DevTools) renders correctly
- [ ] No console errors in browser
- [ ] No errors in `journalctl -u nextunnel`

#### Test Checklist for Tunnel Changes

- [ ] Create tunnel with valid inputs → success
- [ ] Create tunnel with invalid inputs → proper error
- [ ] Start tunnel → status becomes "running"
- [ ] Stop tunnel → status becomes "stopped"
- [ ] Delete tunnel → removed from list
- [ ] Bulk actions work
- [ ] Config copy buttons work
- [ ] Health check returns correct result
- [ ] Ping test works

#### Test Checklist for Auth Changes

- [ ] Login with correct credentials → success
- [ ] Login with wrong credentials → error, attempt recorded
- [ ] Rate limiting triggers after 5 failed attempts
- [ ] Session expires after 30 minutes idle
- [ ] Session extends with activity
- [ ] Logout works
- [ ] Password change works
- [ ] Forced password change on first login

### Testing Environment

Run these tests on **at least one** of:

- Ubuntu 22.04 LTS (recommended)
- Debian 12
- Ubuntu 24.04
- Alpine Linux (edge cases)

For multi-arch testing (if you have access):

- x86_64 VM
- ARM64 (Raspberry Pi, Oracle Ampere, etc.)

### Browser Testing

Test on:

- Chrome / Edge (latest)
- Firefox (latest)
- Safari (macOS/iOS)
- Mobile Chrome (Android)

### Writing Tests (Future)

We're working on adding automated tests. When the test framework is ready:

```python
# tests/test_auth.py (example structure)
import pytest
from nextunnel import hash_password, verify_password

def test_password_hashing():
    pw_hash, salt = hash_password("test123")
    assert verify_password("test123", pw_hash, salt)
    assert not verify_password("wrong", pw_hash, salt)

def test_password_salt_uniqueness():
    _, salt1 = hash_password("same")
    _, salt2 = hash_password("same")
    assert salt1 != salt2
```

---

## 📁 Project Structure

```
nextunnel/
├── nextunnel.py                    # Main application (single file)
├── install.sh                      # Installer script
├── README.md                       # English documentation
├── README.fa.md                    # Persian documentation
├── CHANGELOG.md                    # Version history
├── CONTRIBUTING.md                 # This file
├── SECURITY.md                     # Security policy
├── LICENSE                         # MIT License
├── CODE_OF_CONDUCT.md              # Community guidelines
├── .gitignore                      # Git ignore rules
├── .editorconfig                   # Editor settings
├── .github/
│   ├── workflows/
│   │   ├── release.yml             # Auto-release on tag
│   │   └── lint.yml                # Lint on PR
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   ├── feature_request.md
│   │   └── config.yml
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── FUNDING.yml
├── docs/
│   ├── screenshots/
│   └── examples/
└── tests/                          # (future)
    ├── test_auth.py
    ├── test_tunnels.py
    └── test_api.py
```

### Key Files to Know

| File | Purpose |
|------|---------|
| `nextunnel.py` | Entire application — backend + frontend in one file |
| `install.sh` | Installation automation for Linux |
| `README.md` | Main user documentation |
| `CHANGELOG.md` | Version history (update on every change!) |

### Understanding `nextunnel.py`

The file is organized in this order:

1. **Header & imports** — shebang, docstring, imports
2. **CONFIG** — global configuration dict
3. **Security utilities** — password hashing, tokens
4. **Database** — schema, migrations, helpers
5. **First-run setup** — admin user creation
6. **Sessions** — creation, validation, cleanup
7. **Rate limiting** — login attempt tracking
8. **Update checker** — GitHub API integration
9. **System detection** — OS, IP, x-ui, monitoring
10. **Tunnel generators** — one function per protocol
11. **Tunnel CRUD** — create, read, update, delete
12. **Process management** — start, stop, health check
13. **Tools** — installation scripts
14. **ISP profiles** — built-in and custom
15. **Dashboard stats** — aggregation
16. **I18N** — backend messages
17. **HTML** — the entire frontend (CSS + JS)
18. **HTTP Handler** — request routing
19. **Server** — main entry point

---

## 💬 Community

### Where to Get Help

- 📖 **Read the docs** — [README.md](README.md) / [README.fa.md](README.fa.md)
- 🔍 **Search issues** — [existing issues](https://github.com/metiwilson/nextunnel/issues)
- 💬 **Discussions** — [GitHub Discussions](https://github.com/metiwilson/nextunnel/discussions)
- 🐛 **Bug reports** — [open an issue](https://github.com/metiwilson/nextunnel/issues/new)

### Communication Guidelines

- **Be patient** — Maintainers are volunteers
- **Be specific** — "It doesn't work" doesn't help
- **Be respectful** — We're all here to help each other
- **Be concise** — Long messages are harder to respond to
- **Search first** — Your question may already be answered

### Response Times

| Channel | Typical Response |
|---------|------------------|
| GitHub Issues | 3-7 days |
| Pull Requests | 3-7 days |
| Discussions | Best effort |

---

## 🌟 Recognition

Every contribution matters! Here's how we recognize your work:

### Contributors Page

All contributors are listed on the [GitHub contributors page](https://github.com/metiwilson/nextunnel/graphs/contributors).

### CHANGELOG Credits

Significant contributions are credited in `CHANGELOG.md` with a link to the PR.

### Special Thanks

Top contributors may be featured in the README's acknowledgments section.

### Types of Contributions Recognized

- 💻 Code
- 📖 Documentation
- 🌐 Translations
- 🎨 Design
- 🐛 Bug reports
- 💡 Feature ideas
- 📣 Spreading the word
- ⭐ Starring the repo!

---

## ❓ Questions?

Still unsure about something?

1. **Read the [FAQ](README.md#-faq)** in the README
2. **Search [existing issues](https://github.com/metiwilson/nextunnel/issues)**
3. **Open a [discussion](https://github.com/metiwilson/nextunnel/discussions)**
4. **Open an issue** with the `question` label

We're happy to help! Don't be shy — asking questions is a great way to learn and contribute.

---

## 🙏 Thank You

**Thank you for taking the time to contribute to NexTunnel!**

Whether you're fixing a typo, reporting a bug, adding a feature, or translating the UI, your contribution makes the project better for everyone.

<div align="center">

**Happy coding! 🚀**

[🏠 Repository](https://github.com/metiwilson/nextunnel) · [🐛 Issues](https://github.com/metiwilson/nextunnel/issues) · [💬 Discussions](https://github.com/metiwilson/nextunnel/discussions) · [📄 License](LICENSE)

Made with ❤️ by the NexTunnel community

</div>
