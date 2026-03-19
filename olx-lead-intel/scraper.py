from playwright.sync_api import sync_playwright
from datetime import datetime
import pandas as pd
import logging
import json
import os
import random
import time
import re

from scorer import calculate_score

log = logging.getLogger(__name__)

SEEN_URLS_FILE = "data/seen_urls.json"

# ── User agent pool ────────────────────────────────────────────────────────────
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
]

# ── OLX category URL slugs ─────────────────────────────────────────────────────
CATEGORY_URLS = {
    "administrativo-e-secretariado": "https://www.olx.pt/emprego/administrativo-e-secretariado/",
    "it-e-telecomunicacoes": "https://www.olx.pt/emprego/it-e-telecomunicacoes/",
    "comercial": "https://www.olx.pt/emprego/comercial/",
}


def load_seen_urls() -> set:
    if os.path.exists(SEEN_URLS_FILE):
        with open(SEEN_URLS_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_seen_urls(seen: set) -> None:
    with open(SEEN_URLS_FILE, "w") as f:
        json.dump(list(seen), f)


def human_pause(min_s: float = 4.0, max_s: float = 12.0) -> None:
    time.sleep(random.uniform(min_s, max_s))


def passes_tier1(title: str, snippet: str, gate_keywords: list) -> bool:
    combined = f"{title} {snippet}".lower()
    for keyword in gate_keywords:
        pattern = r"\b" + re.escape(keyword.lower()) + r"\b"
        if re.search(pattern, combined):
            return True
    return False


def get_company_tag(page) -> str:
    try:
        selectors = [
            "[data-testid='ad-contact-company']",
            ".css-1q7ubt8",
            "[data-cy='seller-company-name']",
        ]
        for selector in selectors:
            el = page.query_selector(selector)
            if el:
                return el.inner_text().strip()
    except Exception:
        pass
    return ""


def build_empty_row(title: str, url: str, category: str, timestamp: str) -> dict:
    return {
        "timestamp": timestamp,
        "title": title,
        "url": url,
        "category": category,
        "company_tag": "",
        "score": 0,
        "categories_matched": "",
        "keywords_matched": "",
        "tier1_passed": False,
        "company_registered": "",
        "company_sector": "",
        "company_size_band": "",
        "racius_url": "",
        "enrichment_score_delta": "",
        "company_website": "",
        "contact_name": "",
        "contact_title": "",
        "contact_email": "",
        "contact_source": "",
        "contact_confidence": "",
        "outreach_sent": "",
        "outreach_date": "",
        "response_received": "",
        "response_date": "",
        "notes": "",
    }


# ── Debug helpers ──────────────────────────────────────────────────────────────

def save_debug_snapshot(page, label: str) -> None:
    """
    Saves a screenshot + full HTML dump to logs/ for inspection.
    label should be a short slug like 'administrativo-p1' or 'keyword-analista'.
    Files written:
        logs/debug_<label>.png   — what Playwright actually rendered
        logs/debug_<label>.html  — raw DOM at that moment
    """
    os.makedirs("logs", exist_ok=True)
    safe_label = label.replace(" ", "_").replace("/", "-")[:60]

    screenshot_path = f"logs/debug_{safe_label}.png"
    html_path = f"logs/debug_{safe_label}.html"

    try:
        page.screenshot(path=screenshot_path, full_page=True)
        log.info(f"[DEBUG] Screenshot saved → {screenshot_path}")
    except Exception as e:
        log.warning(f"[DEBUG] Screenshot failed for '{label}': {e}")

    try:
        html = page.content()
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
        log.info(f"[DEBUG] HTML dump saved → {html_path}")
    except Exception as e:
        log.warning(f"[DEBUG] HTML dump failed for '{label}': {e}")


def inspect_links(page, label: str) -> list:
    """
    Tries multiple selectors and logs what each finds.
    Returns the best non-empty result, or empty list.
    This helps identify if the selector is stale after an OLX markup change.
    """
    selectors_to_try = [
        "a[href*='/anuncio/emprego/']",      # Original selector
        "a[href*='/anuncio/']",              # Broader — catches all ad types
        "[data-cy='listing-ad-title']",      # OLX data-cy pattern
        "[data-testid='listing-thumb']",     # Alternative testid
        "article a",                         # Generic article link
        ".css-rc5s2u a",                     # OLX listing card class (may be stale)
    ]

    best_links = []
    for selector in selectors_to_try:
        try:
            found = page.query_selector_all(selector)
            log.info(f"[DEBUG] [{label}] selector '{selector}' → {len(found)} element(s)")
            if found and len(found) > len(best_links):
                best_links = found
        except Exception as e:
            log.warning(f"[DEBUG] [{label}] selector '{selector}' error: {e}")

    return best_links


def wait_for_listings(page, timeout_ms: int = 15000) -> bool:
    """
    Waits for any known listing selector to appear in the DOM.
    Returns True if something loaded, False if timed out.
    """
    selectors_to_wait = [
        "a[href*='/anuncio/emprego/']",
        "a[href*='/anuncio/']",
        "[data-cy='listing-ad-title']",
        "article a",
    ]
    for selector in selectors_to_wait:
        try:
            page.wait_for_selector(selector, timeout=timeout_ms)
            log.info(f"[DEBUG] Listings appeared via selector: '{selector}'")
            return True
        except Exception:
            continue

    log.warning("[DEBUG] wait_for_listings: no selector matched within timeout")
    return False


# ── Main scrape function ───────────────────────────────────────────────────────

def scrape_targets(
    targets: list,
    mode: str,
    scoring_rules: dict,
    scoring_config: dict,
    tier1_keywords: list,
    alert_score: int,
    telegram_threshold: int,
    pages_per_category: int,
) -> pd.DataFrame:

    seen_urls = load_seen_urls()
    rows = []

    targets_shuffled = targets.copy()
    random.shuffle(targets_shuffled)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            locale="pt-PT",
            viewport={"width": 1280, "height": 800},
        )

        page = context.new_page()

        for target in targets_shuffled:

            if mode == "category":
                base_url = CATEGORY_URLS.get(target)
                if not base_url:
                    log.warning(f"No URL mapping for category '{target}' — skipping")
                    continue
                urls_to_scrape = [
                    base_url if p_num == 1 else f"{base_url}?page={p_num}"
                    for p_num in range(1, pages_per_category + 1)
                ]
                category_label = target
            else:
                urls_to_scrape = [
                    f"https://www.olx.pt/emprego/q-{target.replace(' ', '-')}/"
                ]
                category_label = "keyword"

            log.info(f"Scraping target: '{target}' ({len(urls_to_scrape)} page(s))")

            for page_num, page_url in enumerate(urls_to_scrape, start=1):
                debug_label = f"{target}-p{page_num}"

                try:
                    log.info(f"[DEBUG] Loading: {page_url}")
                    page.goto(page_url, wait_until="domcontentloaded", timeout=30000)

                    # Wait for actual listing elements rather than relying on networkidle
                    listings_found = wait_for_listings(page, timeout_ms=12000)

                    # Always snapshot the first page of each target for inspection
                    if page_num == 1:
                        save_debug_snapshot(page, debug_label)

                    if not listings_found:
                        log.warning(
                            f"[DEBUG] No listings detected on '{page_url}' — "
                            f"check logs/debug_{debug_label}.png"
                        )
                        # Still try inspect_links so we know what IS in the DOM
                        inspect_links(page, debug_label)
                        continue

                    # Try all selectors and pick the best one
                    links = inspect_links(page, debug_label)
                    log.info(f"'{target}' page {page_url}: {len(links)} listings found")

                    new_count = 0

                    for link in links:
                        href = link.get_attribute("href")
                        if not href:
                            continue
                        if not href.startswith("http"):
                            href = "https://www.olx.pt" + href
                        if href in seen_urls:
                            continue

                        seen_urls.add(href)
                        title = link.inner_text().strip()
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        row = build_empty_row(title, href, category_label, timestamp)

                        if not passes_tier1(title, "", tier1_keywords):
                            log.debug(f"Tier 1 failed — skipping: {title}")
                            continue

                        row["tier1_passed"] = True
                        new_count += 1

                        human_pause(1.5, 4.0)
                        page_text = ""
                        company_tag = ""

                        try:
                            ad_page = context.new_page()
                            ad_page.goto(href, wait_until="domcontentloaded", timeout=20000)
                            page_text = ad_page.inner_text("body")
                            company_tag = get_company_tag(ad_page)
                            ad_page.close()
                        except Exception as e:
                            log.warning(f"Could not load ad page {href}: {e}")

                        row["company_tag"] = company_tag

                        combined_text = f"{title} {page_text}"
                        score, breakdown, keywords_matched = calculate_score(
                            combined_text, scoring_config
                        )

                        row["score"] = score
                        row["categories_matched"] = str(breakdown)
                        row["keywords_matched"] = ", ".join(keywords_matched)

                        if score >= alert_score:
                            rows.append(row)

                            if score >= telegram_threshold:
                                log.info(
                                    f"🚨 TELEGRAM ALERT — score={score} | "
                                    f"{title} | {href}"
                                )
                            else:
                                log.info(
                                    f"✅ MATCH — score={score} | {title} | {href}"
                                )

                        human_pause()

                    log.info(f"'{target}': {new_count} new listings passed Tier 1")
                    human_pause(3.0, 8.0)

                except Exception as e:
                    log.error(f"Failed on '{target}' page {page_url}: {e}")
                    # Save snapshot even on error so you can see what happened
                    try:
                        save_debug_snapshot(page, f"{debug_label}-ERROR")
                    except Exception:
                        pass
                    continue

        browser.close()

    save_seen_urls(seen_urls)
    return pd.DataFrame(rows)


# ── Public interface ───────────────────────────────────────────────────────────
def search_olx(
    targets: list,
    mode: str,
    scoring_rules: dict,
    scoring_config: dict,
    tier1_keywords: list,
    alert_score: int,
    telegram_threshold: int,
    pages_per_category: int = 4,
) -> pd.DataFrame:
    return scrape_targets(
        targets=targets,
        mode=mode,
        scoring_rules=scoring_rules,
        scoring_config=scoring_config,
        tier1_keywords=tier1_keywords,
        alert_score=alert_score,
        telegram_threshold=telegram_threshold,
        pages_per_category=pages_per_category,
    )
