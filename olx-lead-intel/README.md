# prospect-radar

This is a weighted signal detection pipeline that monitors Portuguese job boards in near real time as a prospecting tool.

---

## What it does

- Scrapes job board listings by job category (currently working on OLX)   
- Gates ads at scrape time — discards noise before scoring   
- Scores each ad using a configurable weighted ruleset   
- Penalizes unverifiable or ghost companies via enrichment lookup   
- Fires Telegram alerts for high-signal ads above threshold   
- Tracks seen URLs across runs — no duplicates   
- Outputs to CSV (SQLite planned)   

---

## Architecture — three tiers

**Tier 1 — Scraper gate**
Checks title and snippet before loading the full ad. If no qualifying keyword is present, the ad is discarded immediately — no full page load, no scoring.

**Tier 2 — Scoring engine**
Runs on full ad text. Weighted rules across categories with per-category caps to avoid diluted signals.   
Repeated keywords within a category score at diminishing value — confirms signal without inflating score.   
Co-occurrence bonuses reward high-value combinations.

**Tier 3 — Company enrichment**
Looks up company name on public registries. Confirmed registered company scores a bonus. Unverifiable or ghost companies are penalized. Penalization, not hard filtering.

---

## Scraper modes

Configurable in `config.example.yml`:

```yaml
sources:
  olx:
    mode: category        # or: keyword
    categories:
      - administrativo
      - informatica-telecomunicacoes
      - comercial
    pages_per_category: 4
    interval_minutes_min: 18
    interval_minutes_max: 35
```

`category` mode scrapes OLX category pages — broader catch, scoring filters.   
`keyword` mode uses OLX search — narrower, useful for targeted searches or other sources.   
Scoring runs identically in both modes.   

---

## Alerts

Telegram notification fires when a scored ad exceeds the configured threshold. High-signal ads surface within minutes of posting.

---

## Project structure

```text
prospect-radar/
│
├── data/                        # exported leads (CSV → SQLite planned)
├── logs/
│   └── monitor.log              # runtime logs
│
├── config.example.yml           # structure and scoring logic template (config.yml is gitignored)
│
├── scraper.py                   # fetch + parse OLX listings, Tier 1 gate
├── scorer.py                    # Tier 2 scoring engine
├── enrichment.py                # Tier 3 company lookup
├── alerts.py                    # Telegram notification handler
├── main.py                      # entry point + run loop
├── requirements.txt
├── DEVELOPMENT.md               # key decisions and reasoning
└── README.md
```

---

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp config.example.yml config.yml
# edit config.yml with your scoring rules and thresholds
```

---

## Usage

```bash
python main.py
```

Results append to `data/jobs.csv`. Logs write to `logs/monitor.log`.

---

## Notes

- Only collects public listing data — no personal data stored   
- Respects site load with randomised request delays and user-agent rotation   
- Enrichment uses free public lookups only   
- Scoring logic is not included in this repository — `config.example.yml` shows structure only   
- See [DEVELOPMENT.md](DEVELOPMENT.md) for design decisions and reasoning   
