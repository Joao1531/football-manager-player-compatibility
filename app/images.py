"""
Best-effort player/manager photo lookup via the Wikipedia REST summary API.

Wikipedia/Wikimedia Commons only hosts images with a compatible reuse
license, so this is safe to display (with attribution) in a research demo.
Lookups are best-effort: many lower-profile players do not have a Wikipedia
page, or the name is ambiguous (shared with a non-footballer) -- in either
case this returns None and the caller shows a placeholder instead of
guessing or fabricating an image.
"""

from __future__ import annotations

import requests
import streamlit as st

WIKI_SUMMARY = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
# Wikipedia's API requires a descriptive User-Agent (robot policy) or it
# returns 403 with no data -- not an auth/network problem, just missing header.
_HEADERS = {"User-Agent": "MIAD-FinalProject-CompatibilityExplorer/1.0 (research demo, non-commercial)"}

# Verified exact Wikipedia article titles for the three managers.
MANAGER_WIKI_TITLES = {
    "Pep Guardiola": "Pep Guardiola",
    "Jürgen Klopp": "Jürgen Klopp",
    "Roberto De Zerbi": "Roberto De Zerbi",
}

_FOOTBALL_HINTS = ("footbal", "soccer", "midfielder", "forward", "defender", "goalkeeper", "winger", "manager", "coach")


@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def _fetch_summary(title: str) -> dict | None:
    try:
        r = requests.get(WIKI_SUMMARY.format(title=title.replace(" ", "_")), timeout=4, headers=_HEADERS)
        if r.status_code == 200:
            return r.json()
    except requests.RequestException:
        pass
    return None


@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def lookup_photo(name: str) -> tuple[str | None, str | None]:
    """Returns (image_url, wikipedia_page_url) or (None, None) if not found
    or the match looks unrelated to football."""
    for candidate in (name, f"{name} (footballer)"):
        data = _fetch_summary(candidate)
        if not data or data.get("type") == "disambiguation":
            continue
        desc = (data.get("description") or "").lower()
        extract = (data.get("extract") or "").lower()
        looks_football = any(h in desc for h in _FOOTBALL_HINTS) or any(h in extract[:200] for h in _FOOTBALL_HINTS)
        thumb = (data.get("thumbnail") or {}).get("source")
        if thumb and (looks_football or candidate != name):
            page_url = (data.get("content_urls") or {}).get("desktop", {}).get("page")
            return thumb, page_url
    return None, None


def render_photo(name: str, width: int = 120, caption_suffix: str = "") -> None:
    """Streamlit widget: shows the looked-up photo, or a placeholder box."""
    import streamlit as st  # local import keeps this module importable without a Streamlit context in tests

    url, page_url = lookup_photo(name)
    if url:
        st.image(url, width=width, caption=f"Photo: Wikipedia{caption_suffix}")
    else:
        st.markdown(
            f"""<div style="width:{width}px;height:{width}px;border-radius:8px;background:#30333a;
            display:flex;align-items:center;justify-content:center;font-size:{width//3}px;">👤</div>""",
            unsafe_allow_html=True,
        )
        st.caption("No photo found")
