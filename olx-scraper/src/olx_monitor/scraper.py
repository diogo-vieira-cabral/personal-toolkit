import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from datetime import datetime
import pandas as pd

from scorer import calculate_score

seen_urls = set()

df = pd.DataFrame(columns=["timestamp", "title", "url", "score"])


def scan_ad_page(url):

    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        return soup.get_text(" ")

    except:
        return ""


def search_olx(keywords, scoring_rules, alert_score):

    global df

    for keyword in keywords:
        encoded_keyword = quote(keyword)

        url = f"https://www.olx.pt/emprego/q-{encoded_keyword}/"

        print("Searching:", keyword)

        try:
            r = requests.get(url)
            soup = BeautifulSoup(r.text, "html.parser")

        except:
            print("Failed loading page")
            continue

        links = soup.find_all("a", href=True)

        for link in links:
            href = link["href"]

            if "/d/anuncio/" not in href:
                continue

            if href in seen_urls:
                continue

            seen_urls.add(href)

            title = link.get_text(strip=True)

            page_text = scan_ad_page(href)

            combined_text = f"{title} {href} {page_text}"

            score = calculate_score(combined_text, scoring_rules)

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            new_row = {
                "timestamp": timestamp,
                "title": title,
                "url": href,
                "score": score,
            }

            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

            if score >= alert_score:
                print("\n🚨 MATCH FOUND")
                print("Title:", title)
                print("Score:", score)
                print("URL:", href)

    df.to_excel("data/jobs.xlsx", index=False)
