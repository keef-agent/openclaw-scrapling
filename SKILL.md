---
name: scrapling
description: Cloudflare-bypassing web scraper for OpenClaw agents. Falls back gracefully to urllib. Use when web_fetch returns 403/empty on protected sites.
version: 1.0.0
author: keef-agent
---

# scrapling

Bypass Cloudflare and scrape any website. 774x faster than BeautifulSoup. Zero selector maintenance.

Wraps [Scrapling](https://github.com/D4Vinci/Scrapling) with graceful urllib fallback — if stealth fetch fails, it tries a normal fetch automatically. If that also fails, it exits with an error you can act on.

## Install

```bash
pip install scrapling[all]
playwright install chromium
```

Run once. After that, any call to `scrapling-fetch.py` just works.

## Script

`scripts/scrapling-fetch.py` — call it from any agent, cron, or shell.

### Basic usage

```bash
# Full page text
python3 scripts/scrapling-fetch.py "https://example.com" --text-only

# Limit output length
python3 scripts/scrapling-fetch.py "https://example.com" --text-only --max-chars 3000

# Extract a specific element
python3 scripts/scrapling-fetch.py "https://example.com" --selector "article.main" --text-only

# Get raw HTML
python3 scripts/scrapling-fetch.py "https://example.com" --html
```

### Arguments

| Arg | Default | Description |
|---|---|---|
| `url` | required | URL to fetch |
| `--text-only` | off | Strip HTML, return plain text |
| `--html` | off | Return raw HTML (overrides --text-only) |
| `--selector` | none | CSS selector to target a specific element |
| `--max-chars` | 5000 | Truncate output to N chars |

## When to use

**Use `web_fetch` first.** It's faster and has no browser overhead.

**Switch to scrapling when:**
- `web_fetch` returns a Cloudflare challenge page
- Response body is empty or suspiciously short
- You get a 403 or 429 from a protected site
- The target is Medium, Substack, paywalled news, or any JS-heavy page

## Integration pattern

Add this to any cron or agent prompt that needs reliable web access:

```
If web_fetch returns a Cloudflare block, empty body, or 403, fall back to:
  python3 /path/to/skills/scrapling/scripts/scrapling-fetch.py "<url>" --text-only --max-chars 3000
```

Or in shell:

```bash
CONTENT=$(python3 scripts/scrapling-fetch.py "$URL" --text-only --max-chars 5000)
if [ $? -ne 0 ]; then
  echo "Both fetch methods failed for $URL" >&2
  exit 1
fi
echo "$CONTENT"
```

## Fallback chain

1. **StealthyFetcher** (Playwright, Cloudflare bypass) — first attempt
2. **urllib** (basic HTTP with browser user-agent) — if stealth fails
3. **Exit 1 + error to stderr** — if both fail

You always get output or a clear error. No silent failures.

## Notes

- First run may take a few seconds (browser launch). Subsequent calls are fast.
- `--selector` uses CSS selectors — same syntax as `document.querySelector`.
- Scrapling's auto-matching means selectors survive minor site redesigns.
- If you only have `scrapling` without `[all]`, StealthyFetcher won't be available — it falls back to urllib automatically.
