# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

gmaps-whatsapp-leads — a lead generation and WhatsApp outreach tool. It scrapes Google Maps business data via SerpAPI, exports to CSV, then uses PyWhatKit to send automated WhatsApp messages to leads.

The workflow: **web search (browser)** → **data collection (SerpAPI → CSV)** → **WhatsApp outreach (PyWhatKit)**.

## Python Setup & Dependencies

```bash
# Environment (Python 3.12 recommended)
pip install virtualenv
virtualenv .venv && source .venv/bin/activate

# Install
pip install -r requirements.txt
```

Key dependencies: `serpapi`, `pandas`, `python-dotenv`, `pywhatkit`, `selenium`, `webdriver-manager`, `undetected-chromedriver`

## Environment Variables

Copy `get-data/.env.example` to `get-data/.env` and set your SerpAPI key:

```
API_KEY="your-serpapi-key"
```

## Data Collection Scripts

Each script reads `.env` from its own directory, so `.env` files go in `get-data/.env`, `send-msg/.env`, etc.

### Google Maps → CSV (`get-data/google_map_to_path_csv.py`)

Main script. Uses the `GoogleMapSearcher` class to query Google Maps via SerpAPI's `google_maps` engine and exports to CSV.

- **Class**: `GoogleMapSearcher` — wraps `serpapi.Client`, provides `search()` and `export_to_csv()`
- **CSV fields**: position, title, place_id, rating, reviews_count, price_level, extracted_price, business_type, address, country, open_state, latitude, longitude, phone, website, user_review
- **Output**: `dist/data/YYYY-MM/YYYY_MM_DD_HH_MM_SS_{keyword}_{start}_{location}.csv`
- Encoding is `utf-8-sig` (Excel-compatible for Chinese characters)

Usage: `python get-data/google_map_to_path_csv.py` — prompts for keyword, location name, and pagination offset.

### Google Web Search (`get-data/SerpApi-search.py`)

General web search (not Maps) via SerpAPI. Exports organic results to CSV. Uses env var `SERPAPI_API_KEY`.

### Browser Helper (`web-search/webbrowser-open-web.py`)

Opens Google Maps and WhatsApp Web in the default browser for manual login/coordination.

## WhatsApp Send Scripts

All scripts use **PyWhatKit** (`pywhatkit`) which automates WhatsApp Web in a browser. WhatsApp Web must be logged in first.

| Script | Purpose |
|--------|---------|
| `send-msg/scheduled-times.py` | Send scheduled messages to hardcoded numbers |
| `send-msg/send-msg-csv.py` | Batch-send from `contacts.csv` (columns: `name`, `phone_number`, `reminder_time`) |
| `send-msg/send_to_group.py` | Send message to a WhatsApp group by ID |
| `send-msg/send-image.py` | Send an image to a contact |

Run from the `send-msg/` directory: `python send-msg/send-msg-csv.py`

## CSV Conventions

- All exports use `utf-8-sig` encoding for Excel compatibility
- Output organized by month: `dist/data/YYYY-MM/`
- Field names are snake_case
- Missing values = empty string (not null/NaN)

## Architecture

```
gmaps-whatsapp-leads/
├── web-search/              # Browser launcher for manual logins
│   └── webbrowser-open-web.py
├── get-data/                # Data collection (SerpAPI)
│   ├── google_map_to_path_csv.py   # Google Maps search → CSV
│   ├── SerpApi-search.py           # Google web search → CSV
│   └── dist/data/                  # Output CSVs by month
├── send-msg/                # WhatsApp outreach (PyWhatKit)
│   ├── scheduled-times.py          # Individual scheduled sends
│   ├── send-msg-csv.py             # Batch send from CSV
│   ├── send_to_group.py            # Group messaging
│   ├── send-image.py               # Image sending
│   ├── dist/data/                  # Send-ready CSVs with name/phone/time
│   └── dist/output/                # Results (active/unable users)
└── .claude/
    └── skills/git-commit/          # Git commit skill definition
```

### Data Flow

1. **Scrape**: `GoogleMapSearcher.search()` queries SerpAPI → parses `local_results`
2. **Export**: `export_to_csv()` writes to `dist/data/YYYY-MM/` with timestamped filenames
3. **Transform**: CSV columns `title,phone` → `name,phone_number,reminder_time` for WhatsApp
4. **Send**: PyWhatKit opens WhatsApp Web, types message, schedules delivery

### Key Patterns

- Each module directory has its own `__init__.py` (package markers)
- Configuration via `.env` files per directory (never hardcoded keys)
- `dist/` dirs are gitignored — output data stays local
- `GoogleMapSearcher` enforces API key comes from `.env` only (no constructor arg)

## Git

Uses Angular commit convention with emoji:

```
<type>(<scope>): :emoji: <subject>
```

The project has a custom `.claude/skills/git-commit/SKILL.md` defining the commit format.
