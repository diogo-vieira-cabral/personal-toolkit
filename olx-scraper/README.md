
# OLX Job monitor

Python automation tool for detecting high-signal OLX job listings.

Features:
- scans OLX employment listings
- scores ads based on keywords
- tracks new ads only
- runs about every 30 minutes
- exports results to CSV

### Why I built this

This tool automates **discovery for client acquisition**.

It cuts through the noise and highlights listings that **match specific signals, removing the need to manually scroll and validate through hundreds of ads.**

The tool only collects **public listing URLs** and does **not retrieve or store personal data at scale**.


#### Project Notes

- [working_notes](docs/working_notes.md)
- [Configuration](config.yml)
- [Scraper Logic](src/olx_monitor/scraper.py)

#### Project Structure

```text
olx-scraper/
│
├── .venv/                      # Python virtual environment
├── data/                       # exported job leads
├── docs/
│   └── working_notes.md        # development notes
│
├── logs/
│   └── monitor.log             # scraper runtime logs
│
├── src/
│   └── olx_monitor/
│       ├── scraper.py          # OLX scraping logic
│       └── scorer.py           # keyword scoring system
│
├── .gitignore
├── config.yml                  # search keywords + scoring rules
├── main.py                     # main runner / scheduler
├── requirements.txt
└── README.md
```