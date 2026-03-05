import yaml
import time
from datetime import datetime

from scraper import search_olx

# ========================
# LOAD CONFIG FILE
# ========================

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

search_keywords = config["search"]["keywords"]
scoring_rules = config["scoring"]["rules"]
alert_score = config["alerts"]["min_score"]
interval = config["schedule"]["interval_minutes"] * 60


# ========================
# MAIN LOOP
# ========================

while True:
    print("\n=======================")
    print("Starting scan:", datetime.now())
    print("=======================\n")

    search_olx(
        keywords=search_keywords, scoring_rules=scoring_rules, alert_score=alert_score
    )

    print(f"\nSleeping {interval / 60} minutes\n")

    time.sleep(interval)
