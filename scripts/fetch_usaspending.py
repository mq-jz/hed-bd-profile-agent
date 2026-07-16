#!/usr/bin/env python3
"""Fetch federal prime awards for a recipient from USA Spending.

USA Spending API is public, no key required.
Endpoint: https://api.usaspending.gov/api/v2/search/spending_by_award/

Usage:
  python scripts/fetch_usaspending.py --name "Cleveland Clinic" \
      --out 02-federal-funding/raw --min 1000000 --years 5

Writes <out>/usaspending.json with a normalized award list.

[VERIFY] Endpoint shape and award_type_codes are correct as of this writing,
but USA Spending revises its schema periodically. If results look wrong, check
https://api.usaspending.gov/docs/endpoints and adjust the `filters` block.
"""
import argparse
import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.http import post_json, write_output, fail_stub  # noqa: E402

API = "https://api.usaspending.gov/api/v2/search/spending_by_award/"

# Contracts + grants. See USA Spending award type code reference. The API
# rejects requests mixing type groups ("must only contain types from one
# group"), so we query each group separately and merge.
AWARD_TYPE_GROUPS = {
    "contracts": ["A", "B", "C", "D"],
    "grants": ["02", "03", "04", "05"],
}


def fiscal_year_start(years_back):
    today = datetime.date.today()
    fy = today.year if today.month < 10 else today.year + 1
    start_fy = fy - years_back
    # federal FY starts Oct 1 of the prior calendar year
    return f"{start_fy - 1}-10-01"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True, help="recipient name to search")
    ap.add_argument("--out", required=True, help="output directory")
    ap.add_argument("--min", type=int, default=1_000_000, help="min award amount")
    ap.add_argument("--years", type=int, default=5, help="lookback in fiscal years")
    args = ap.parse_args()

    results = []
    for group_codes in AWARD_TYPE_GROUPS.values():
        payload = {
            "filters": {
                "recipient_search_text": [args.name],
                "award_type_codes": group_codes,
                "time_period": [{
                    "start_date": fiscal_year_start(args.years),
                    "end_date": datetime.date.today().isoformat(),
                }],
                "award_amounts": [{"lower_bound": args.min}],
            },
            "fields": [
                "Award ID", "Recipient Name", "Awarding Agency",
                "Awarding Sub Agency", "Award Amount", "Description",
                "Period of Performance Start Date", "Award Type",
            ],
            "sort": "Award Amount",
            "order": "desc",
            "limit": 100,
            "page": 1,
        }
        try:
            resp = post_json(API, payload)
        except Exception as e:  # noqa: BLE001
            fail_stub(args.out, "usaspending", f"{type(e).__name__}: {e}")
        results.extend(resp.get("results", []))

    results.sort(key=lambda r: r.get("Award Amount") or 0, reverse=True)
    results = results[:100]
    awards = [{
        "agency": r.get("Awarding Agency"),
        "sub_agency": r.get("Awarding Sub Agency"),
        "description": r.get("Description"),
        "amount": r.get("Award Amount"),
        "start_date": r.get("Period of Performance Start Date"),
        "award_type": r.get("Award Type"),
        "award_id": r.get("Award ID"),
    } for r in results]

    path = write_output(args.out, "usaspending", {
        "query": args.name,
        "min_amount": args.min,
        "count": len(awards),
        "awards": awards,
    })
    print(f"Wrote {path} ({len(awards)} awards)")


if __name__ == "__main__":
    main()
