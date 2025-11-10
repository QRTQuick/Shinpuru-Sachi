# Shinpuru-Sachi — Terminal Browser

**Shinpuru-Sachi** is a lightweight terminal browser (also called a terminal search tool) designed for creators, coders, and power users. It allows you to search the web from your terminal, fetch results quickly, and optionally receive desktop notifications.  

Developed by **Chisom Life Eke**, founder of **Quick Red Tech**.  

---

## Features

- **Terminal-based search**  
  Perform web searches directly from your terminal using DuckDuckGo.

- **Instant top results**  
  Quickly view the top search result with a title, snippet, and URL.  

- **Optional desktop notifications**  
  Receive native notifications for top search results (requires `plyer`).

- **Fallback HTML scraping**  
  If DuckDuckGo’s JSON API fails or returns no results, Sachi scrapes HTML to provide fallback results.  

- **Open results in browser**  
  Optionally open the top search result directly in your default web browser.  

- **Cross-platform support**  
  Works on Windows, Linux, and macOS with Python 3.x.  

- **Customizable max results**  
  Control the number of results displayed (default is 3).  

- **Lightweight & minimal dependencies**  
  Only requires `requests`, `beautifulsoup4`, and optionally `plyer` for notifications.  

- **Honest limitations**  
  - The tool relies on DuckDuckGo and may occasionally fail if the API or HTML structure changes.  
  - Desktop notifications are optional and may not work on all platforms.  
  - It is primarily a terminal search tool and does not replace full web browsers.  

---

## Installation

1. Clone or download the repository:

```bash
git clone https://github.com/QRTQuick/Shinpuru-Sachi.git
cd Shinpuru-Sachi