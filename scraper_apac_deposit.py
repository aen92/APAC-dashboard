"""
scraper_apac_deposit.py

Light‑weight web‑scraper for deposit‑rate pages used by the APAC Deposit Comparator.
"""

import re
from datetime import datetime, timezone
from typing import Optional

import pandas as pd
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}
TIMEOUT = 20


def _extract_first_percent(text: str) -> Optional[float]:
    """Return the first '12.34%' style number in text."""
    m = re.search(r"(\d+(?:\.\d+)?)\s*%", text)
    return float(m.group(1)) if m else None


# ---------- Provider‑specific extractors ---------- #
def scrape_dbs(url: str) -> Optional[float]:
    """DBS SG fixed‑deposit table."""
    soup = BeautifulSoup(requests.get(url, headers=HEADERS, timeout=TIMEOUT).text, "lxml")
    return _extract_first_percent(soup.get_text(" ", strip=True))


def scrape_ocbc(url: str) -> Optional[float]:
    """OCBC SG fixed‑deposit table."""
    soup = BeautifulSoup(requests.get(url, headers=HEADERS, timeout=TIMEOUT).text, "lxml")
    return _extract_first_percent(soup.get_text(" ", strip=True))


# Map provider ➞ scraper
SCRAPE_MAP = {
    "DBS": scrape_dbs,
    "OCBC": scrape_ocbc,
    # Add more custom provider functions here if needed
}


# ---------- Generic fallback ---------- #
def generic_scrape(url: str) -> Optional[float]:
    """If no custom extractor exists, grab first percentage in page."""
    soup = BeautifulSoup(requests.get(url, headers=HEADERS, timeout=TIMEOUT).text, "lxml")
    return _extract_first_percent(soup.get_text(" ", strip=True))


# ---------- Public API ---------- #
def scrape_one(provider: str, url: str) -> Optional[float]:
    """Return latest interest‑rate percentage (float) or None."""
    func = SCRAPE_MAP.get(provider, generic_scrape)
    try:
        return func(url)
    except Exception as exc:  # noqa: BLE001
        print(f"[WARN] {provider} scrape failed: {exc}")
        return None


def scrape_all(sources_df: pd.DataFrame) -> pd.DataFrame:
    """Enrich the sources list with fresh rates & timestamp."""
    rows = []
    now_utc = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for _, row in sources_df.iterrows():
        pct = scrape_one(row.provider, row.url)
        rows.append({**row, "interest_rate_pct": pct, "last_scraped": now_utc})
    return pd.DataFrame(rows)
