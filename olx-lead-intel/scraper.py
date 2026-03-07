from playwright.sync_api import sync_playwright
from datetime import datetime
import pandas as pd
import logging
import json
import os
import random
import time

from scorer import calculate_score

log = logging.getLogger(__name__)

SEEN_URLS_FILE = "data/seen_urls.json"


def load_seen_urls() -> set:
    if os.path.exists(SEEN_URLS_FILE):
        with open(SEEN_URLS_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_seen_urls(seen: set) -> None:
    with open(SEEN_URLS_FILE, "w") as f:
        json.dump(list(seen), f)


def human_pause(min_s: float = 2.0, max_s: float = 5.0) -> None:
    time.sleep(random.uniform(min_s, max_s))


def search_olx(keywords: list, scoring_rules: dict, alert_score: int) -> pd.DataFrame:

    seen_urls = load_seen_urls()
    rows = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            locale="pt-PT",
            viewport={"width": 1280, "height": 800},
        )

        page = context.new_page()

        for keyword in keywords:
            url = f"https://www.olx.pt/emprego/q-{keyword.replace(' ', '-')}/"
            log.info(f"Searching: '{keyword}'")

            try:
                page.goto(url, wait_until="networkidle", timeout=30000)
                human_pause()

                # grab all listing links
                links = page.query_selector_all("a[href*='/anuncio/emprego/']")
                log.info(f"'{keyword}': {len(links)} listings found on page")

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
                    new_count += 1

                    title = link.inner_text().strip()

                    # visit individual ad page
                    human_pause(1.5, 4.0)
                    try:
                        ad_page = context.new_page()
                        ad_page.goto(href, wait_until="networkidle", timeout=20000)
                        page_text = ad_page.inner_text("body")
                        ad_page.close()
                    except Exception as e:
                        log.warning(f"Could not load ad page {href}: {e}")
                        page_text = ""

                    combined_text = f"{title} {href} {page_text}"
                    score = calculate_score(combined_text, scoring_rules)
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    rows.append(
                        {
                            "timestamp": timestamp,
                            "title": title,
                            "url": href,
                            "score": score,
                        }
                    )

                    if score >= alert_score:
                        log.info(f"🚨 MATCH — score={score} | {title} | {href}")

                    human_pause()

                log.info(f"'{keyword}': {new_count} new listings added")
                human_pause(3.0, 8.0)

            except Exception as e:
                log.error(f"Failed on keyword '{keyword}': {e}")
                continue

        browser.close()

    save_seen_urls(seen_urls)
    return pd.DataFrame(rows)
