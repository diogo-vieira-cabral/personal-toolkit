
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
- [Configuration](config.yaml)
- [Scraper Logic](scraper.py)

#### Project Structure

olx-job-monitor/
│
├── scraper.py
├── scorer.py
├── main.py
├── config.yaml
│
├── data/
├── logs/
└── docs/
    └── working_notes.md