# APAC Deposit‑Product Comparator (Unique‑Named Build)

This repo contains a Streamlit dashboard that scrapes and compares headline
deposit rates across Singapore, Japan and Hong Kong.

## Files

| File | Purpose |
|------|---------|
| **app_apac_deposit.py** | Streamlit UI entry‑point |
| **data_apac_deposit.py** | Data orchestration & caching |
| **scraper_apac_deposit.py** | Per‑site and generic scraper functions |
| **requirements_apac_deposit.txt** | Python dependencies |
| **README_apac_deposit.md** | This documentation |

## Local dev

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements_apac_deposit.txt
streamlit run app_apac_deposit.py
```

## Deploy on Streamlit Cloud

When creating a new app, set the *Main file* to `app_apac_deposit.py`.

Enjoy!
