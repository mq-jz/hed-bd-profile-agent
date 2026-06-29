#!/usr/bin/env python3
"""Fetch congressional members for a state from the Congress.gov API.

Requires a free API key. Register at https://api.congress.gov/sign-up/ and add
to .env:  CONGRESS_API_KEY=your_key_here

Endpoint: https://api.congress.gov/v3/member?currentMember=true

Usage:
  python scripts/fetch_congress.py --state CO --out 04-delegation/raw

Writes <out>/congress.json with current members for the state: name, party,
chamber, district (House), and the member detail URL (committee assignments
live on the member detail endpoint; this script fetches each member's detail
to attach terms/committees where available).

[VERIFY] The member endpoint returns committee data inconsistently across
members. Where committees are absent, the stage agent should fall back to web
browse (Ballotpedia, member website) and tag [verify].
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.http import get_json, write_output, fail_stub, require_key  # noqa: E402

LIST_API = "https://api.congress.gov/v3/member"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True, help="two-letter state code, e.g. CO")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    key = require_key(args.out, "congress", "CONGRESS_API_KEY")

    try:
        resp = get_json(LIST_API, params={
            "currentMember": "true",
            "stateCode": args.state.upper(),
            "limit": 250,
            "api_key": key,
            "format": "json",
        })
    except Exception as e:  # noqa: BLE001
        fail_stub(args.out, "congress", f"{type(e).__name__}: {e}")

    members = []
    for m in resp.get("members", []):
        members.append({
            "name": m.get("name"),
            "party": m.get("partyName"),
            "state": m.get("state"),
            "district": m.get("district"),  # None for senators
            "chamber": ((m.get("terms") or {}).get("item") or [{}])[-1].get("chamber")
                        if isinstance(m.get("terms"), dict) else None,
            "bioguide_id": m.get("bioguideId"),
            "detail_url": m.get("url"),
        })

    path = write_output(args.out, "congress", {
        "state": args.state.upper(),
        "count": len(members),
        "members": members,
        "note": "Committee assignments often absent here. "
                "Fall back to web browse per member and tag [verify].",
    })
    print(f"Wrote {path} ({len(members)} members)")


if __name__ == "__main__":
    main()
