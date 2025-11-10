#!/usr/bin/env python3
"""
sachi.py — terminal search -> terminal output (optional desktop notification)

Usage examples:
  python sachi.py -S "who owns gpt"
  ./sachi.py --search "who owns gpt"
"""

import argparse
import sys
import webbrowser
import textwrap
import html
from urllib.parse import quote_plus

# --- External dependencies ---
try:
    import requests
    from bs4 import BeautifulSoup
except Exception:
    print("Missing required packages. Install with:\n  pip install requests beautifulsoup4 plyer", file=sys.stderr)
    sys.exit(1)

# --- Desktop notification backend ---
try:
    from plyer import notification
    PLYER_AVAILABLE = True
except Exception:
    PLYER_AVAILABLE = False

DUCKDUCKGO_JSON_API = "https://api.duckduckgo.com/?q={query}&format=json&no_redirect=1&skip_disambig=1"
DUCKDUCKGO_HTML = "https://html.duckduckgo.com/html/?q={query}"

# ------------------ Fetch functions ------------------ #
def fetch_json_api(query, max_results=3, timeout=8):
    """Try DuckDuckGo JSON API."""
    url = DUCKDUCKGO_JSON_API.format(query=quote_plus(query))
    headers = {"User-Agent": "Sachi-terminal-browser/1.0"}
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()

    results = []

    if data.get("AbstractText"):
        results.append({
            "title": data.get("Heading", "DuckDuckGo"),
            "snippet": data.get("AbstractText"),
            "url": data.get("AbstractURL") or f"https://duckduckgo.com/?q={quote_plus(query)}"
        })

    related = data.get("RelatedTopics", [])
    for item in related:
        if "Topics" in item:
            for t in item["Topics"]:
                if len(results) >= max_results:
                    break
                results.append({
                    "title": t.get("Text", ""),
                    "snippet": "",
                    "url": t.get("FirstURL", "")
                })
        else:
            if len(results) >= max_results:
                break
            results.append({
                "title": item.get("Text", ""),
                "snippet": "",
                "url": item.get("FirstURL", "")
            })
        if len(results) >= max_results:
            break

    return results[:max_results]


def fetch_html_scrape(query, max_results=3, timeout=8):
    """Fallback: HTML scraping for full results."""
    url = DUCKDUCKGO_HTML.format(query=quote_plus(query))
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    resp = requests.post(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    results = []
    for r in soup.select(".result"):
        a = r.select_one("a.result__a") or r.find("a")
        title = a.get_text(strip=True) if a else None
        href = a.get("href") if a else None
        snippet_tag = r.select_one(".result__snippet")
        snippet = snippet_tag.get_text(" ", strip=True) if snippet_tag else ""
        if title and href:
            results.append({
                "title": html.unescape(title),
                "snippet": html.unescape(snippet),
                "url": href
            })
        if len(results) >= max_results:
            break

    # fallback generic links
    if not results:
        for a in soup.select("a"):
            href = a.get("href")
            text = a.get_text(strip=True)
            if href and text:
                results.append({"title": text, "snippet": "", "url": href})
                if len(results) >= max_results:
                    break

    return results[:max_results]

# ------------------ Notification ------------------ #
def notify_simple(title, message, timeout=8):
    if PLYER_AVAILABLE:
        try:
            notification.notify(title=title, message=message, timeout=timeout)
            return True
        except Exception:
            pass
    return False

# ------------------ Main ------------------ #
def main():
    parser = argparse.ArgumentParser(
        prog="Sachi",
        description="Terminal search that prints results (optional notification)."
    )
    parser.add_argument("-S", "--search", help="Search query (wrap in quotes)")
    parser.add_argument("--open", action="store_true", help="Open top result in browser")
    parser.add_argument("--no-notify", action="store_true", help="Do not attempt notification")
    parser.add_argument("--max", type=int, default=3, help="How many results to fetch")
    args = parser.parse_args()

    if not args.search:
        parser.print_help()
        sys.exit(1)

    query = args.search.strip()
    results = []

    # Try JSON API first
    try:
        results = fetch_json_api(query, max_results=args.max)
    except Exception:
        pass

    # If no JSON results, fallback to HTML scraping
    if not results:
        try:
            results = fetch_html_scrape(query, max_results=args.max)
        except Exception as e:
            fallback_url = f"https://duckduckgo.com/?q={quote_plus(query)}"
            print(f"[Sachi] Failed to fetch results ({e}). Opening browser fallback...")
            webbrowser.open(fallback_url)
            sys.exit(0)

    if not results:
        print("[Sachi] No results found; opening browser search page.")
        webbrowser.open(f"https://duckduckgo.com/?q={quote_plus(query)}")
        sys.exit(0)

    # --- Top result displayed in compact Notified style ---
    top = results[0]
    title = top.get("title", "")
    snippet = top.get("snippet", "").strip()
    url = top.get("url", "")
    print(f"\n[Sachi] Notified: {title}")
    if snippet:
        print(snippet)
    print(url)

    if not args.no_notify:
        notify_simple(title, snippet or url)

    # --- Print all results in full below ---
    for i, res in enumerate(results, 1):
        print(f"\n[Sachi] Result #{i}")
        print(f"Title  : {res.get('title', '')}")
        print(f"Snippet: {res.get('snippet', '')}")
        print(f"URL    : {res.get('url', '')}")
        print("-" * 80)

    # --- Open top result in browser if requested ---
    if args.open:
        webbrowser.open(url)

if __name__ == "__main__":
    main()