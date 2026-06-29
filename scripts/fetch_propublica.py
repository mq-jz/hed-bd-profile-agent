#!/usr/bin/env python3
"""Fetch nonprofit financials and 990 filings from ProPublica Nonprofit Explorer.

Public API, no key required.
Search:  https://projects.propublica.org/nonprofits/api/v2/search.json?q=NAME
Org:     https://projects.propublica.org/nonprofits/api/v2/organizations/EIN.json

Usage:
  python scripts/fetch_propublica.py --name "Cleveland Clinic" \
      --out 01-about/raw
  python scripts/fetch_propublica.py --ein 340714585 --out 01-about/raw

Writes <out>/propublica.json with org summary, employee count proxy, revenue,
and links to recent 990 filings.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.http import get_json, write_output, fail_stub  # noqa: E402

SEARCH = "https://projects.propublica.org/nonprofits/api/v2/search.json"
ORG = "https://projects.propublica.org/nonprofits/api/v2/organizations/{ein}.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", help="organization name to search")
    ap.add_argument("--ein", help="EIN if known (digits only)")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    if not args.name and not args.ein:
        fail_stub(args.out, "propublica", "provide --name or --ein")

    ein = args.ein
    candidates = []

    if not ein:
        try:
            sr = get_json(SEARCH, params={"q": args.name})
        except Exception as e:  # noqa: BLE001
            fail_stub(args.out, "propublica", f"search failed: {e}")
        orgs = sr.get("organizations", [])
        candidates = [{
            "ein": o.get("ein"),
            "name": o.get("name"),
            "state": o.get("state"),
            "ntee": o.get("ntee_code"),
        } for o in orgs[:10]]
        if not orgs:
            fail_stub(args.out, "propublica",
                      f"no nonprofit match for '{args.name}'")
        ein = orgs[0].get("ein")

    try:
        org = get_json(ORG.format(ein=ein))
    except Exception as e:  # noqa: BLE001
        fail_stub(args.out, "propublica", f"org fetch failed for EIN {ein}: {e}")

    o = org.get("organization", {})
    filings = org.get("filings_with_data", []) or []
    recent = [{
        "tax_year": f.get("tax_prd_yr"),
        "total_revenue": f.get("totrevenue"),
        "total_expenses": f.get("totfuncexpns"),
        "total_employees": f.get("noemplyeesw3cnt"),
        "pdf_url": f.get("pdf_url"),
    } for f in filings[:3]]

    path = write_output(args.out, "propublica", {
        "query": args.name or args.ein,
        "selected_ein": ein,
        "name": o.get("name"),
        "city": o.get("city"),
        "state": o.get("state"),
        "candidates": candidates,
        "recent_filings": recent,
        "note": "If selected_ein is wrong, rerun with --ein from candidates[]",
    })
    print(f"Wrote {path} (EIN {ein}, {len(recent)} filings)")


if __name__ == "__main__":
    main()
