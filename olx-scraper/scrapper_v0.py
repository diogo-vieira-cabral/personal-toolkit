import requests
import pandas as pd
import time
from datetime import datetime
from urllib.parse import quote


def scrape_olx_jobs(keywords, max_pages=3):
    """
    This function searches OLX job listings using their internal API.

    PARAMETERS
    ----------
    keywords : list
        Words we want to search for (e.g. 'contabilidade', 'excel')

    max_pages : int
        Number of result pages to scan for each keyword
    """

    # list that will store every lead we find
    all_leads = []

    # HTTP headers make our request look like a real browser
    # It doesn’t bypass strong protection, but it avoids simple bot filters.
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}

    # scoring rules
    # key = keyword we want to detect
    # value = number of points we add if it appears
    scoring_rules = {
        "excel": 6,
        "contabilidade": 3,
        "dados": 7,
        "administrativo": 4,
        "assistente": 3,
        "urgente": 4,
        "pro-activo": 5,
        "proativo": 5,
        "remoto": 6,
        "home office": 6,
        "proactiva": 5,
        "pro-ativa": 5,
    }

    # words that strongly suggest an employer posting the ad
    employer_signals = [
        "empresa",
        "escritório",
        "gabinete",
        "procura-se",
        "recrutamos",
        "contrata",
        "contrata-se",
    ]

    # loop through every search keyword
    for keyword in keywords:
        print(f"\n🔎 Searching OLX for: {keyword}")

        # encode keyword for safe use inside URL
        encoded_keyword = quote(keyword)

        # go through result pages
        for page in range(1, max_pages + 1):
            # OLX API endpoint
            # category_id=25 filters to EMPREGO
            url = (
                f"https://www.olx.pt/api/v1/offers/"
                f"?query={encoded_keyword}"
                f"&category_id=25"
                f"&page={page}"
            )

            try:
                # send request to OLX server
                response = requests.get(url, headers=headers, timeout=15)

                # if request failed, skip page
                if response.status_code != 200:
                    print("❌ Request failed:", response.status_code)
                    continue

                # convert response JSON into Python dictionary
                data = response.json()

                # the actual ads are inside "data"
                offers = data.get("data", [])

                print(f"📦 Found {len(offers)} ads")

                # process each ad
                for offer in offers:
                    # extract title of the ad
                    title = offer.get("title", "").strip()

                    # skip empty titles
                    if not title:
                        continue

                    # convert to lowercase for easier matching
                    title_lower = title.lower()

                    # -------------------------
                    # SCORE CALCULATION
                    # -------------------------

                    score = 0

                    # check every scoring keyword
                    for word, points in scoring_rules.items():
                        # if keyword appears in title
                        if word in title_lower:
                            # add its points
                            score += points

                            # print debug message
                            print(f"   +{points} for keyword '{word}'")

                    # check employer signals
                    for word in employer_signals:
                        if word in title_lower:
                            score += 4

                            print(f"   +4 employer signal '{word}'")

                    # ignore weak leads
                    if score < 3:
                        continue

                    # -------------------------
                    # LOCATION EXTRACTION
                    # -------------------------

                    location = None

                    if offer.get("location"):
                        location = offer["location"].get("city", {}).get("name")

                    # -------------------------
                    # CREATE LEAD OBJECT
                    # -------------------------

                    lead = {
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "keyword": keyword,
                        "title": title,
                        "location": location,
                        "score": score,
                        "url": offer.get("url"),
                    }

                    all_leads.append(lead)

                    # HIGH SIGNAL ALERT
                    if score >= 15:
                        print(f"🚨 HIGH SIGNAL: {title} | {location}")

            except Exception as e:
                print("❌ Error:", e)

    # convert collected leads to dataframe
    df = pd.DataFrame(all_leads)

    # remove duplicate titles
    if not df.empty:
        df = df.drop_duplicates(subset=["title"])

    return df


def run_monitor():
    """
    This function runs the scraper and saves the results.
    """

    keywords = ["contabilidade", "administrativo", "assistente", "excel"]

    # run scraper
    df = scrape_olx_jobs(keywords, max_pages=3)

    # if leads exist, save them
    if not df.empty:
        filename = f"olx_jobs_{datetime.now().strftime('%Y-%m-%d')}.csv"

        df.to_csv(filename, index=False)

        print(f"\n💾 Saved {len(df)} leads to {filename}")

    else:
        print("\nNo leads found")


# -------------------------
# MAIN LOOP
# -------------------------

while True:
    print("\n=======================")
    print("OLX JOB MONITOR START")
    print("=======================")

    run_monitor()

    print("\n⏳ Waiting 3 hours...")

    # 10800 seconds = 3 hours
    time.sleep(10800)
