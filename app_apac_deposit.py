"""
app_apac_deposit.py

Streamlit dashboard for comparing APAC deposit products.
"""

from __future__ import annotations

import streamlit as st

import data_apac_deposit as data_lib

st.set_page_config("APAC Deposit Comparator", page_icon="💰", layout="wide")

st.title("💰 APAC Deposit‑Product Comparator")

st.markdown(
    """
Find the latest headline interest rates for major fixed‑ and easy‑access deposits
in Singapore 🇸🇬, Japan 🇯🇵 and Hong Kong 🇭🇰.  
Use *Refresh now* to scrape the provider sites live.
"""
)

# Sidebar refresh button & filters
force = st.sidebar.button("🔄 Refresh now")
with st.spinner("Loading data …"):
    df, cached = data_lib.get_data(force_refresh=force)

badge_text = "Live data ✔︎" if force or not cached else "Up‑to‑date ✔︎"
badge_color = "#10B981" if force or not cached else "#06AED5"
st.markdown(
    f"<span style='background-color:{badge_color}; "
    f"color:white; padding:3px 8px; border-radius:6px;'>{badge_text}</span>",
    unsafe_allow_html=True,
)

markets = st.sidebar.multiselect("Market", sorted(df.market.unique()), default=list(df.market.unique()))
types = st.sidebar.multiselect("Provider type", sorted(df.provider_type.unique()), default=list(df.provider_type.unique()))
access = st.sidebar.multiselect("Access type", sorted(df.access_type.unique()), default=list(df.access_type.unique()))

mask = df.market.isin(markets) & df.provider_type.isin(types) & df.access_type.isin(access)
view = df.loc[mask].sort_values(["market", "interest_rate_pct"], ascending=[True, False])

st.dataframe(
    view[
        [
            "provider",
            "product_name",
            "market",
            "provider_type",
            "access_type",
            "interest_rate_pct",
            "tenure",
            "early_withdrawal_penalty",
            "url",
            "last_scraped",
        ]
    ],
    use_container_width=True,
    height=600,
)

st.subheader("📈 Top 10 headline rates")
st.bar_chart(
    view.sort_values("interest_rate_pct", ascending=False).head(10).set_index("provider")["interest_rate_pct"]
)

st.caption("Rates scraped from provider public pages. Verify details before committing funds.")
