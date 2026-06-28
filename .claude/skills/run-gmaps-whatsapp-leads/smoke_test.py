#!/usr/bin/env python3
"""
smoke_test.py — Verify the gmaps-whatsapp-leads project is importable and functional.
Runs without API keys — uses mock data for CSV export, checks imports parse correctly.

GUI-dependent scripts (send-msg/* using pywhatkit) are checked via compile()
only, since pywhatkit/pyautogui trigger Windows GUI init and hang headless.
"""

import os
import sys
import csv
import tempfile
import importlib.util

# ---------- helpers ----------
PASS = FAIL = SKIP = 0

def check(desc, ok):
    global PASS, FAIL
    if ok:
        print(f"  [PASS] {desc}")
        PASS += 1
    else:
        print(f"  [FAIL] {desc}")
        FAIL += 1

def skip(desc):
    global SKIP
    print(f"  [SKIP] {desc}")
    SKIP += 1

def section(title):
    print(f"\n{'='*60}\n  {title}\n{'='*60}")

def compile_check(desc, filepath):
    """Check that a .py file at least parses without SyntaxError."""
    try:
        with open(filepath, encoding="utf-8") as f:
            compile(f.read(), filepath, "exec")
        check(desc, True)
    except SyntaxError as e:
        check(desc, False)
        print(f"         {e}")

def safe_import(name, filepath):
    """Import a module by filepath; return None on failure."""
    try:
        spec = importlib.util.spec_from_file_location(name, filepath)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception as e:
        return None  # caller decides pass/skip

# ---------- root ----------
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, _PROJECT_ROOT)

# ===================== PART 1: Syntax-only checks (GUI scripts) =====================
section("Syntax check — all .py files parse")

SCRIPT_FILES = [
    ("web-search/webbrowser-open-web.py",     "web-search", "webbrowser-open-web.py"),
    ("get-data/google_map_to_path_csv.py",     "get-data",   "google_map_to_path_csv.py"),
    ("get-data/SerpApi-search.py",             "get-data",   "SerpApi-search.py"),
    ("send-msg/scheduled-times.py",            "send-msg",   "scheduled-times.py"),
    ("send-msg/send-msg-csv.py",               "send-msg",   "send-msg-csv.py"),
    ("send-msg/send_to_group.py",              "send-msg",   "send_to_group.py"),
    ("send-msg/send-image.py",                 "send-msg",   "send-image.py"),
]
for label, subdir, fn in SCRIPT_FILES:
    compile_check(label, os.path.join(_PROJECT_ROOT, subdir, fn))

# ===================== PART 2: Non-GUI imports =====================
section("Import — non-GUI modules")

# google_map_to_path_csv (no GUI dependency)
gmap_mod = safe_import("gmap_mod", os.path.join(_PROJECT_ROOT, "get-data", "google_map_to_path_csv.py"))
if gmap_mod:
    check("import google_map_to_path_csv.py", True)
else:
    check("import google_map_to_path_csv.py", False)
    sys.exit(1)  # this one must work — rest depends on it

# SerpApi-search (no GUI dep, but needs API key at top-level)
serp_mod = safe_import("serp_mod", os.path.join(_PROJECT_ROOT, "get-data", "SerpApi-search.py"))
if serp_mod:
    check("import SerpApi-search.py", True)
else:
    skip("SerpApi-search.py (needs API_KEY env var)")

# web-search/webbrowser-open-web (pure stdlib)
wb_mod = safe_import("wb_mod", os.path.join(_PROJECT_ROOT, "web-search", "webbrowser-open-web.py"))
check("import webbrowser-open-web.py", wb_mod is not None)

# GUI-dependent modules (pywhatkit) — checked syntax only above
skip("send-msg/*.py (GUI-dependent — syntax checked but import skipped headless)")

# ===================== PART 3: GoogleMapSearcher introspection =====================
section("GoogleMapSearcher class introspection")

GoogleMapSearcher = gmap_mod.GoogleMapSearcher
generate_location_label = gmap_mod.generate_location_label

check("GoogleMapSearcher class exists", True)

expected_fields = [
    "position", "title", "place_id", "rating", "reviews_count",
    "price_level", "extracted_price", "business_type", "address", "country",
    "open_state", "latitude", "longitude", "phone", "website", "user_review"
]
check(f"CSV_FIELDS has {len(expected_fields)} columns",
      GoogleMapSearcher.CSV_FIELDS == expected_fields)

# method signatures
import inspect
sig_search = inspect.signature(GoogleMapSearcher.search)
sig_export = inspect.signature(GoogleMapSearcher.export_to_csv)
check("search() has 'query' param",           'query' in sig_search.parameters)
check("search() has 'location_ll' param",     'location_ll' in sig_search.parameters)
check("search() start param optional",
      sig_search.parameters['start'].default is not inspect.Parameter.empty)
check("export_to_csv() base_dir param optional",
      sig_export.parameters['base_dir'].default is not inspect.Parameter.empty)

# ===================== PART 4: generate_location_label() =====================
section("generate_location_label()")

check("label with name: 'Los_Angeles'",
      generate_location_label("@33.9818,-118.2479,15z", "Los Angeles") == "Los_Angeles")
check("label w/o name uses lat/lng",
      generate_location_label("@33.9818,-118.2479,15z", "") == "33.9818_-118.2479")

# ===================== PART 5: CSV export mock =====================
section("CSV export (mock data, no API key)")

mock_results = [{
    "position": 1,
    "title": "Test Business",
    "place_id": "12345",
    "rating": 4.5,
    "reviews": 100,
    "price": "$$",
    "extracted_price": "20-30",
    "type": "Restaurant",
    "address": "123 Main St",
    "country": "US",
    "open_state": "OPEN",
    "gps_coordinates": {"latitude": 33.98, "longitude": -118.25},
    "phone": "+1234567890",
    "website": "https://example.com",
    "user_review": '"Great place!"',
}]

searcher = object.__new__(GoogleMapSearcher)
searcher.local_results = mock_results

with tempfile.TemporaryDirectory() as tmpdir:
    exported = searcher.export_to_csv(
        keyword="test-business", start_value=0,
        location_label="test-area", base_dir=tmpdir,
    )
    check("CSV file created", os.path.isfile(exported))

    with open(exported, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    check("CSV has 1 row",          len(rows) == 1)
    check("CSV 'title' column",     rows[0].get("title") == "Test Business")
    check("CSV 'phone' column",     rows[0].get("phone") == "+1234567890")
    check("CSV 'latitude' column",  rows[0].get("latitude") == "33.98")
    check("CSV 'longitude' column", rows[0].get("longitude") == "-118.25")
    check("CSV 'user_review' (stripped quotes)", rows[0].get("user_review") == "Great place!")
    check("CSV has all 16 fields",  len(rows[0]) == len(expected_fields))

# ===================== PART 6: SerpApi-search module =====================
section("SerpApi-search module structure")

if serp_mod:
    check("export_fields list length 6", len(serp_mod.export_fields) == 6)
    check("exports 'position'",          "position" in serp_mod.export_fields)
    check("exports 'snippet'",           "snippet" in serp_mod.export_fields)
else:
    skip("SerpApi-search checks (module not loaded)")

# ===================== SUMMARY =====================
print(f"\n{'='*60}")
print(f"  RESULTS: {PASS} passed, {FAIL} failed, {SKIP} skipped")
print(f"{'='*60}")

if FAIL:
    sys.exit(1)
