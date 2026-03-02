# Basic Usage Examples

## 1. Scraping a Cloudflare-protected page

The most common use case. Some sites return empty content or a JS challenge page when `web_fetch` hits them.

```bash
python3 scripts/scrapling-fetch.py "https://medium.com/@someauthor/some-article" --text-only --max-chars 5000
```

Output goes to stdout. Errors go to stderr. Exit code 0 = success, 1 = all methods failed.

**In an agent prompt:**
```
Fetch this article: https://medium.com/@someauthor/some-article
If web_fetch returns empty or a Cloudflare page, run:
  python3 /path/to/skills/scrapling/scripts/scrapling-fetch.py "https://medium.com/@someauthor/some-article" --text-only --max-chars 5000
```

---

## 2. Extracting specific content with a CSS selector

Use `--selector` to grab just the content you need instead of the whole page.

```bash
# Get only the main article text
python3 scripts/scrapling-fetch.py "https://techcrunch.com/2025/01/01/some-article/" \
  --selector "article.article-content" \
  --text-only \
  --max-chars 3000

# Get pricing table from a SaaS page
python3 scripts/scrapling-fetch.py "https://someproduct.com/pricing" \
  --selector ".pricing-table" \
  --text-only

# Get all heading text from a page
python3 scripts/scrapling-fetch.py "https://example.com" \
  --selector "h1, h2, h3" \
  --text-only
```

Scrapling's auto-matching means selectors survive minor site redesigns — unlike BeautifulSoup or raw CSS parsing.

---

## 3. Using as web_fetch fallback in a cron job

This is the main pattern for cron agents that need reliable web access.

**Shell script fallback:**

```bash
#!/bin/bash
URL="https://example.com/data"
SKILL_DIR="$(dirname "$0")/../skills/scrapling"

# Try web_fetch equivalent first (fast)
CONTENT=$(curl -sL "$URL" --max-time 10)

# Check if Cloudflare blocked it
if echo "$CONTENT" | grep -qi "cloudflare\|just a moment\|checking your browser"; then
  echo "Cloudflare detected, switching to scrapling..." >&2
  CONTENT=$(python3 "$SKILL_DIR/scripts/scrapling-fetch.py" "$URL" --text-only --max-chars 5000)
  if [ $? -ne 0 ]; then
    echo "ERROR: All fetch methods failed for $URL" >&2
    exit 1
  fi
fi

echo "$CONTENT"
```

**In an OpenClaw cron prompt:**

```
## Fetch Instructions
1. Try web_fetch first for speed.
2. If the response is empty, contains "Just a moment", or is under 200 chars, it's probably a Cloudflare block.
3. Fall back to:
   python3 ~/.openclaw/workspace/skills/scrapling/scripts/scrapling-fetch.py "<url>" --text-only --max-chars 5000
4. If scrapling also fails (exit code 1), log the error and skip this URL.
```

---

## 4. Getting raw HTML for further processing

Sometimes you need the full HTML to parse yourself.

```bash
# Save HTML to file
python3 scripts/scrapling-fetch.py "https://example.com" --html > /tmp/page.html

# Pipe to another tool
python3 scripts/scrapling-fetch.py "https://example.com" --html | python3 -c "
import sys
from html.parser import HTMLParser
# ... your parsing logic
"
```

---

## 5. Checking exit code for error handling

```bash
python3 scripts/scrapling-fetch.py "https://protected-site.com" --text-only --max-chars 3000
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  echo "Fetch succeeded"
else
  echo "All fetch methods failed — check stderr for details"
fi
```

Errors are always on stderr. Content is always on stdout. They never mix.
