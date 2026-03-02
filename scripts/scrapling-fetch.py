#!/usr/bin/env python3
"""
Cloudflare-bypassing web fetcher built on Scrapling, with urllib fallback.

Usage:
  python3 scrapling-fetch.py <url> [options]

Options:
  --text-only       Strip HTML tags, return plain text
  --html            Return raw HTML (overrides --text-only)
  --selector CSS    Target a specific CSS element
  --max-chars N     Truncate output to N characters (default: 5000)

Exit codes:
  0  Success
  1  All fetch methods failed

Examples:
  python3 scrapling-fetch.py "https://example.com" --text-only
  python3 scrapling-fetch.py "https://example.com" --selector "article" --text-only --max-chars 3000
  python3 scrapling-fetch.py "https://example.com" --html
"""

import sys
import argparse
import urllib.request


def fallback_fetch(url):
    """Plain urllib fetch — no stealth, but better than nothing."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.read().decode("utf-8", errors="replace"), "html"
    except Exception as e:
        raise RuntimeError(f"urllib fallback failed: {e}")


def scrapling_fetch(url, selector=None, text_only=False, want_html=False):
    """
    Attempt Scrapling StealthyFetcher first, fall back to urllib on failure.
    Returns (content: str, mode: str) where mode is 'stealth' or 'fallback'.
    """
    # --- Try StealthyFetcher (Cloudflare bypass) ---
    try:
        from scrapling.fetchers import StealthyFetcher
        page = StealthyFetcher.fetch(url, headless=True, network_idle=True)

        if selector:
            els = page.css(selector)
            if els:
                if want_html:
                    return "\n".join(el.html_content for el in els), "stealth"
                return "\n".join(el.text for el in els), "stealth"
            return f"WARN: selector '{selector}' matched 0 elements", "stealth"

        if want_html:
            return page.html_content, "stealth"
        if text_only:
            return page.get_all_text(), "stealth"
        return page.html_content, "stealth"

    except ImportError:
        print("WARN: scrapling not installed — falling back to urllib", file=sys.stderr)
    except Exception as e:
        print(f"WARN: StealthyFetcher failed ({e}) — falling back to urllib", file=sys.stderr)

    # --- Try basic Fetcher (no stealth, but uses scrapling parsing) ---
    try:
        from scrapling.fetchers import Fetcher
        page = Fetcher().get(url, stealthy_headers=True)

        if selector:
            els = page.css(selector)
            if els:
                if want_html:
                    return "\n".join(el.html_content for el in els), "fetcher"
                return "\n".join(el.text for el in els), "fetcher"
            return f"WARN: selector '{selector}' matched 0 elements", "fetcher"

        if want_html:
            return page.html_content, "fetcher"
        if text_only:
            return page.get_all_text(), "fetcher"
        return page.html_content, "fetcher"

    except Exception as e:
        print(f"WARN: Fetcher failed ({e}) — falling back to urllib", file=sys.stderr)

    # --- urllib fallback ---
    raw_html, mode = fallback_fetch(url)
    if selector or text_only:
        # Best-effort text extraction without scrapling
        import re
        text = re.sub(r"<[^>]+>", " ", raw_html)
        text = re.sub(r"\s+", " ", text).strip()
        return text, "urllib"
    return raw_html, "urllib"


def main():
    parser = argparse.ArgumentParser(
        description="Fetch a URL with Cloudflare bypass via Scrapling, urllib fallback."
    )
    parser.add_argument("url", help="URL to fetch")
    parser.add_argument(
        "--text-only",
        action="store_true",
        help="Return plain text (strips HTML)"
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="Return raw HTML (overrides --text-only)"
    )
    parser.add_argument(
        "--selector",
        default=None,
        help="CSS selector to target a specific element"
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=5000,
        help="Truncate output to N characters (default: 5000)"
    )
    args = parser.parse_args()

    try:
        content, mode = scrapling_fetch(
            args.url,
            selector=args.selector,
            text_only=args.text_only,
            want_html=args.html,
        )
        print(f"# fetched via: {mode}", file=sys.stderr)
        print(content[:args.max_chars])
        sys.exit(0)
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: unexpected failure: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
