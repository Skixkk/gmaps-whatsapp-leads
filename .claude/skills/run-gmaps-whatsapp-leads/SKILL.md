---
name: run-gmaps-whatsapp-leads
description: Run the lead-gen pipeline — scrape Google Maps (SerpAPI → CSV), send WhatsApp messages (PyWhatKit), and run the smoke test suite.
---

# run-gmaps-whatsapp-leads

Python-based lead generation pipeline: scrape Google Maps business data via SerpAPI, export to CSV, then send automated WhatsApp messages via PyWhatKit.

**Driver:** `.claude/skills/run-gmaps-whatsapp-leads/smoke_test.py`

All paths below are relative to the project root `gmaps-whatsapp-leads/`.

## Prerequisites

- Python 3.12 (recommended)
- Dependencies: `pip install -r requirements.txt`
- **SerpAPI key**: copy `get-data/.env.example` → `get-data/.env` and set `API_KEY`

## Run the smoke test (agent path)

```bash
cd gmaps-whatsapp-leads
python .claude/skills/run-gmaps-whatsapp-leads/smoke_test.py
```

This verifies without API keys or GUI:
- All `.py` files parse without SyntaxError
- `GoogleMapSearcher` class structure and method signatures
- `generate_location_label()` filename helper
- Mock CSV export (creates a temp CSV with correct columns/encoding)
- Module structure of non-GUI scripts

GUI-dependent modules (`send-msg/*` with `pywhatkit`) are syntax-checked but not imported (they trigger Windows GUI init and hang headless). SerpApi-search needs an API key for full import.

## Run individual data-collection scripts

```bash
# Google Maps → CSV (interactive — prompts for keyword, location, pagination)
python get-data/google_map_to_path_csv.py

# Google web search → CSV (edit query in the script first)
python get-data/SerpApi-search.py

# Open Google Maps + WhatsApp Web in browser (manual login)
python web-search/webbrowser-open-web.py
```

## Run WhatsApp send scripts (human path, needs GUI)

The `send-msg/` scripts use **PyWhatKit** which automates WhatsApp Web. Run from the `send-msg/` directory:

```bash
cd send-msg
python send-msg-csv.py          # Batch-send from contacts.csv
python scheduled-times.py       # Hardcoded numbers
python send_to_group.py         # Send to group by ID
python send-image.py            # Send image to contact
```

## Commands at a glance

| Action | Command |
|--------|---------|
| Smoke test | `python .claude/skills/run-gmaps-whatsapp-leads/smoke_test.py` |
| Maps → CSV | `python get-data/google_map_to_path_csv.py` |
| Web search → CSV | `python get-data/SerpApi-search.py` |
| Batch WhatsApp | `cd send-msg && python send-msg-csv.py` |

## Gotchas

- **Hyphenated directories**: `get-data/`, `send-msg/`, `web-search/` contain hyphens, which are invalid in Python identifiers. The smoke test uses `importlib.util.spec_from_file_location` to load them instead of `import`.
- **Windows GBK encoding**: The smoke test uses `[PASS]`/`[FAIL]` text rather than Unicode checkmarks to avoid `gbk` codec errors on Chinese Windows.
- **PyWhatKit hangs headless**: The `pywhatkit`/`pyautogui` stack triggers Windows GUI init on import. The smoke test skips these modules at runtime and only syntax-checks them.
- **utf-8-sig encoding**: All CSV exports use `utf-8-sig` (BOM) for Excel compatibility with Chinese characters. Raw reads without specifying encoding may produce garbled text.
- **`dist/` is gitignored**: Output CSVs go into `get-data/dist/data/YYYY-MM/` and are not tracked.
