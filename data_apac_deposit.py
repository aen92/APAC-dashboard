"""
data_apac_deposit.py

Data orchestration layer for the APAC Deposit Comparator.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Tuple

import pandas as pd
from dateutil import tz

import scraper_apac_deposit as scraper

# -------- Config -------- #
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
CACHE_FILE = DATA_DIR / "deposit_products.csv"
HASH_FILE = DATA_DIR / ".last_hash"

LOCAL_TZ = tz.gettz("Europe/London")


def _product_sources() -> pd.DataFrame:
    """Static catalogue including qualitative attributes."""
    data = [
        # fmt: off
        ("DBS", "DBS Fixed Deposit", "Singapore", "Legacy Bank",
         "Fixed", False, None, "Interest forfeited", "1‑12 m", "https://www.dbs.com.sg/personal/rates-online/fixed-deposit-rate-singapore-dollar.page"),
        ("OCBC", "OCBC Fixed Deposit", "Singapore", "Legacy Bank",
         "Fixed", False, None, "Interest forfeited", "1‑12 m", "https://www.ocbc.com/business-banking/sgd-fixed-deposit-interest-rates"),
        ("UOB", "UOB Fixed Deposit", "Singapore", "Legacy Bank",
         "Fixed", False, None, "Interest forfeited", "1‑12 m", "https://www.uob.com.sg/personal/online-rates/singapore-dollar-time-fixed-deposit-rates.page"),
        ("Standard Chartered SG", "Standard Chartered SG Fixed Deposit", "Singapore", "Legacy Bank",
         "Fixed", False, None, "Interest forfeited", "1‑12 m", "https://www.sc.com/sg/save/time-deposits/singapore-dollar-time-deposit/"),
        ("Bank of China SG", "Bank of China SG Fixed Deposit", "Singapore", "Legacy Bank",
         "Fixed", False, None, "Interest forfeited", "1‑12 m", "https://www.bankofchina.com/sg/bocinfo/bi3/bi31/202504/t20250428_25337649.html"),
        # ... (add the remaining providers here exactly as needed) ...
        ("Mox Bank", "Mox Bank Savings", "Hong Kong", "Neo/Digital Bank",
         "Easy‑Access", False, None, "N/A", "None", "https://mox.com/features/smart-saving/"),
        # fmt: on
    ]
    cols = [
        "provider",
        "product_name",
        "market",
        "provider_type",
        "access_type",
        "fscs_covered",
        "ethical_rating",
        "early_withdrawal_penalty",
        "tenure",
        "url",
    ]
    return pd.DataFrame(data, columns=cols)


def _sha256_of_df(df: pd.DataFrame) -> str:
    """Deterministic hash of a DataFrame (ignore row order)."""
    recs = sorted(json.dumps(rec, sort_keys=True) for rec in df.to_dict(orient="records"))
    return hashlib.sha256("".join(recs).encode()).hexdigest()


def _load_cached() -> Tuple[pd.DataFrame, str] | Tuple[None, None]:
    if not CACHE_FILE.exists() or not HASH_FILE.exists():
        return None, None
    df = pd.read_csv(CACHE_FILE)
    with HASH_FILE.open("r") as fh:
        h = fh.read().strip()
    return df, h


def _save_cache(df: pd.DataFrame) -> None:
    df.to_csv(CACHE_FILE, index=False)
    with HASH_FILE.open("w") as fh:
        fh.write(_sha256_of_df(df))


def get_data(force_refresh: bool = False) -> Tuple[pd.DataFrame, bool]:
    """Return DataFrame and freshness boolean."""
    sources = _product_sources()

    if not force_refresh:
        cached_df, cached_hash = _load_cached()
        if cached_df is not None and _sha256_of_df(cached_df) == cached_hash:
            return cached_df, True  # Cache is fresh

    fresh_df = scraper.scrape_all(sources)
    _save_cache(fresh_df)
    return fresh_df, False
