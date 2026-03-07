import yaml
import time
import logging
from datetime import datetime
from pathlib import Path

from scraper import search_olx

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("logs/monitor.log"), logging.StreamHandler()],
)
log = logging.getLogger(__name__)

# ── Ensure folders exist ───────────────────────────────────────────────────────
# Path().mkdir() creates the folder if it doesn't exist yet.
# exist_ok=True means it won't crash if the folder is already there.
Path("data").mkdir(exist_ok=True)
Path("logs").mkdir(exist_ok=True)

# ── Load config ────────────────────────────────────────────────────────────────
with open("config.yml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

search_keywords = config["search"]["keywords"]
scoring_rules = config["scoring"]["rules"]
alert_score = config["alerts"]["min_score"]
interval_seconds = config["schedule"]["interval_minutes"] * 60


# ── Export results ─────────────────────────────────────────────────────────────
def save_results(df):
    """
    Appends new results to the master CSV.

    Why CSV instead of Excel here?
    - CSV can be appended to without loading the whole file
    - Excel requires reading → modifying → rewriting the entire file each time
    - CSV also loads directly into PostgreSQL later — one less conversion step
    """
    if df.empty:
        log.info("No new listings found this cycle.")
        return

    output_path = Path("data/jobs.csv")

    # header=True only on first write, so we don't repeat column names
    write_header = not output_path.exists()

    df.to_csv(
        output_path,
        mode="a",  # append, never overwrite
        index=False,
        header=write_header,
        encoding="utf-8",
    )

    log.info(f"Saved {len(df)} new listing(s) to {output_path}")


# ── Main loop ──────────────────────────────────────────────────────────────────
def run():
    cycle = 0

    while True:
        cycle += 1
        log.info(f"=== Cycle {cycle} started ===")

        try:
            df = search_olx(
                keywords=search_keywords,
                scoring_rules=scoring_rules,
                alert_score=alert_score,
            )
            save_results(df)

        except Exception as e:
            # Notice: we DO use a broad except here — but we LOG it.
            # The difference: we know it failed, we see why, and the
            # loop continues instead of the whole script dying.
            log.error(f"Cycle {cycle} failed: {e}", exc_info=True)

        log.info(
            f"=== Cycle {cycle} complete. Sleeping {interval_seconds // 60}m ===\n"
        )
        time.sleep(interval_seconds)


if __name__ == "__main__":
    run()
