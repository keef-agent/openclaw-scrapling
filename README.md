# openclaw-scrapling

> OpenClaw skill: Cloudflare-bypassing web scraper using [Scrapling](https://github.com/D4Vinci/Scrapling). Drop-in replacement for `web_fetch` on protected sites.

![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-skill-5865F2?style=flat-square)
![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue?style=flat-square)
![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square)

---

## What this does

`web_fetch` is great until it isn't. Cloudflare, bot detection, JS-heavy sites — they all silently return nothing or a challenge page. You won't even know it failed until you read the empty output.

This skill wraps Scrapling's `StealthyFetcher` (headless Playwright with fingerprint spoofing) in a simple CLI script. Your agent calls one command, gets page content back. If stealth fetch fails, it falls back to urllib automatically. If that also fails, it exits 1 with a clear error.

**Fallback chain:**
1. `StealthyFetcher` (Playwright, full Cloudflare bypass)
2. `Fetcher` (scrapling HTTP client, stealthy headers)
3. `urllib` (basic HTTP, browser user-agent)
4. Exit 1 + error message

No silent failures. No guessing why you got empty content.

---

## Install

```bash
pip install scrapling[all]
playwright install chromium
```

That's it. Run once, then `scrapling-fetch.py` just works.

---

## Usage

```bash
# Full page text
python3 scripts/scrapling-fetch.py "https://example.com" --text-only

# Limit output
python3 scripts/scrapling-fetch.py "https://example.com" --text-only --max-chars 3000

# Target a specific element
python3 scripts/scrapling-fetch.py "https://example.com" --selector "article.post-content" --text-only

# Raw HTML
python3 scripts/scrapling-fetch.py "https://example.com" --html
```

### Arguments

| Arg | Description |
|---|---|
| `url` | URL to fetch (required) |
| `--text-only` | Strip HTML, return plain text |
| `--html` | Return raw HTML |
| `--selector CSS` | CSS selector to target a specific element |
| `--max-chars N` | Truncate to N chars (default: 5000) |

---

## Why this exists

[@dr_cintas put it better than I can](https://x.com/dr_cintas/status/2028544202380845507):

> "OpenClaw just got an unfair advantage over every other AI agent. It can now use Scrapling to scrape any website without getting blocked by Cloudflare. You don't need to maintain selectors when websites update their structure. 774x faster than BeautifulSoup. Zero bot detection."

That tweet prompted me to package this as a proper OpenClaw skill so anyone can drop it in and go.

---

## When to use it

**Use `web_fetch` first.** It's faster, lighter, no browser overhead.

**Switch to scrapling when:**
- `web_fetch` returns a Cloudflare challenge page
- Response body is empty or suspiciously short  
- You get 403/429 from a protected site
- Target is Medium, Substack, paywalled news, or any JS-rendered page

---

## OpenClaw integration

Drop the skill into your OpenClaw workspace:

```bash
# Clone into your skills directory
git clone https://github.com/keef-agent/openclaw-scrapling.git ~/.openclaw/workspace/skills/scrapling
```

OpenClaw will pick up the skill via `SKILL.md` automatically.

Add to any cron or agent prompt:

```
If web_fetch returns a Cloudflare block or empty body, fall back to:
  python3 ~/.openclaw/workspace/skills/scrapling/scripts/scrapling-fetch.py "<url>" --text-only --max-chars 3000
```

---

## The library behind this

This skill wraps [Scrapling](https://github.com/D4Vinci/Scrapling) by [@D4Vinci](https://github.com/D4Vinci). It's genuinely impressive — auto-matching selectors that survive site redesigns, built-in fingerprint spoofing, async support. This skill is just a thin CLI wrapper to make it easy to call from agents.

Go star the original repo.

---

## License

MIT. Do whatever you want with it.
