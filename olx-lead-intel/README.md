# olx-lead-intel

A lightweight Python pipeline that monitors OLX job listings, scores them against configurable signals, and surfaces high-value leads — without manual scrolling.

---

## Why this exists

Most automation freelancers find clients by scrolling job boards manually.
This tool inverts that — it runs in the background, scores listings against configurable signals, and surfaces leads worth pursuing.

It's also the first stage of a larger pipeline: structured lead data feeding into a workflow that infers client pain points and maps them to automation opportunities.

Built to solve a real problem while learning data engineering by doing.

---gg

## What it does

- Scans OLX employment listings by keyword
- Scores each ad using a configurable weighted ruleset
- Tracks seen URLs across runs — no duplicates
- Runs on a 30-minute schedule
- Appends results to CSV for analysis

---

## Project structure
```text
olx-lead-intel/
│
├── data/                       # exported leads (CSV)
├── docs/
│   └── working_notes.md        # development notes
├── logs/
│   └── monitor.log             # runtime logs
│
├── config.yml                  # keywords, scoring rules, schedule
│
├── scraper.py                  # fetch + parse OLX listings
├── scorer.py                   # keyword scoring engine
├── main.py                     # entry point + run loop
├── requirements.txt
└── README.md
```

---

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Usage

Edit `config.yml` to set your keywords, scoring weights, and alert threshold.
Then run:
```bash
python main.py
```

Results append to `data/jobs.csv`. Logs write to `logs/monitor.log`.

---

## Notes

- Only collects public listing URLs — no personal data stored
- Respects site load with randomised request delays
- [Configuration reference](config.yml)
- [Development notes](docs/working_notes.md)