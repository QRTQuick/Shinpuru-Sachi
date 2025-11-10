#!/usr/bin/env python3
"""
sachi.py — terminal search -> desktop notification

Usage examples:
  python sachi.py -S "who owns gpt"
  ./sachi.py --search "who owns gpt"
"""

import argparse
import sys
import webbrowser
import textwrap
import platform
import html
from urllib.parse import quote_plus

try:
    import requests
    from bs4 import BeautifulSoup
except Exception:
    print("Missing required packages. Install with:\n  pip install requests beautifulsoup4 plyer", file=sys.stderr)
    sys.exit(1)

# Notification backends:
try:
    from plyer import notification
    PLYER_AVAILABLE = True
except Exception:
    PLYER_AVAILABLE = False

# Tkinter for expanded view if needed
try:
    import tkinter as tk
    from tkinter.scrolledtext import ScrolledText
    TK_AVAILABLE = True
except Exception:
    TK_AVAILABLE = False

DUCKDUCKGO_SEARCH = "https://html.duckduckgo.com/html/?q={query}"


def fetch_duckduckgo(query, max_results=3, timeout=8):
    """
    Fetch DuckDuckGo HTML search and return list of dicts:
    [{'title':..., 'snippet':..., 'url':...}, ...]
    """
    url = DUCKDUCKGO_SEARCH.format(query=quote_plus(query))
    headers = {
        "User-Agent": "sachi-terminal-browser/1.0 (+https://example.local)"
    }
    resp = requests.post(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    results = []
    # DuckDuckGo's html output uses "result" or "result__body" classes.
    for r in soup.select(".result"):
        a = r.select_one("a.result__a")
        if not a:
            a = r.find("a")
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
    # Fallback: try parsing links if above fails
    if not results:
        for a in soup.select("a"):
            href = a.get("href")
            text = a.get_text(strip=True)
            if href and text:
                results.append({"title": text, "snippet": "", "url": href})
                if len(results) >= max_results:
                    break
    return results


def notify_simple(title, message, timeout=8):
    """
    Cross-platform simple notification using plyer if available.
    """
    if PLYER_AVAILABLE:
        try:
            notification.notify(
                title=title,
                message=message,
                timeout=timeout
            )
            return True
        except Exception:
            pass
    # plyer not available or failed
    return False


def show_expanded(result):
    """
    Show a small Tk window with title, snippet, and Open button.
    """
    if not TK_AVAILABLE:
        # fallback: open browser
        webbrowser.open(result["url"])
        return

    root = tk.Tk()
    root.title(result.get("title", "Sachi search result"))
    root.geometry("640x360")
    root.minsize(400, 200)

    frame = tk.Frame(root, padx=8, pady=8)
    frame.pack(fill="both", expand=True)

    title_lbl = tk.Label(frame, text=result.get("title", ""), font=("Segoe UI", 12, "bold"), wraplength=600, justify="left")
    title_lbl.pack(anchor="w", pady=(0, 6))

    url_lbl = tk.Label(frame, text=result.get("url", ""), font=("Segoe UI", 9), fg="blue", cursor="hand2", wraplength=600, justify="left")
    url_lbl.pack(anchor="w")
    def open_url(_=None):
        webbrowser.open(result["url"])
    url_lbl.bind("<Button-1>", open_url)

    st = ScrolledText(frame, wrap="word", height=10)
    st.insert("1.0", result.get("snippet", ""))
    st.configure(state="disabled")
    st.pack(fill="both", expand=True, pady=(8, 8))

    btn_frame = tk.Frame(frame)
    btn_frame.pack(fill="x")
    open_btn = tk.Button(btn_frame, text="Open in browser", command=open_url)
    open_btn.pack(side="right")

    root.mainloop()


def main():
    parser = argparse.ArgumentParser(prog="Sachi", description="Terminal search that shows desktop notifications.")
    parser.add_argument("-S", "--search", help="Search query (wrap in quotes)")
    parser.add_argument("--open", action="store_true", help="Open top result in browser instead of notification")
    parser.add_argument("--no-notify", action="store_true", help="Do not attempt system notification (use Tk window / open).")
    parser.add_argument("--max", type=int, default=1, help="How many results to fetch (default 1)")
    args = parser.parse_args()

    if not args.search:
        parser.print_help()
        sys.exit(1)

    query = args.search.strip()
    try:
        results = fetch_duckduckgo(query, max_results=args.max)
    except Exception as e:
        # network or parsing error: fallback to opening a real browser search page
        fallback_url = "https://duckduckgo.com/?q=" + quote_plus(query)
        print(f"[Sachi] Failed to fetch search results ({e}). Opening browser fallback...")
        webbrowser.open(fallback_url)
        sys.exit(0)

    if not results:
        print("[Sachi] No results found; opening browser search page.")
        webbrowser.open("https://duckduckgo.com/?q=" + quote_plus(query))
        sys.exit(0)

    top = results[0]
    title = top.get("title", "Search result")
    snippet = top.get("snippet", "").strip()
    url = top.get("url")

    # Build message (short)
    short = textwrap.shorten(snippet if snippet else url, width=200, placeholder="...")

    # If user asked to open directly
    if args.open:
        webbrowser.open(url)
        sys.exit(0)

    # Try to notify
    notified = False
    if not args.no_notify:
        notified = notify_simple(title, short)
    if notified:
        # Also print to stdout for terminal feedback
        print(f"[Sachi] Notified: {title}\n{short}\n{url}")
    else:
        # If notification not available, show small window or open browser
        print("[Sachi] System notification not available or failed — showing expanded view.")
        # Use expanded Tk view with open button
        show_expanded({"title": title, "snippet": snippet or short, "url": url})


if __name__ == "__main__":
    main()