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
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.http import get_json, write_output, fail_stub  # noqa: E402

SEARCH = "https://projects.propublica.org/nonprofits/api/v2/search.json"
ORG = "https://projects.propublica.org/nonprofits/api/v2/organizations/{ein}.json"

# A name search for a college routinely ranks a CONDUIT vehicle above the college
# itself - e.g. "McDaniel College" matches "Madeleine W Geiman Charitable Trust
# FBO McDaniel College" (Orlando FL, ~$17k revenue) before "Mc Daniel College Inc"
# (Westminster MD). Those trusts/estates give TO the institution; they are not it,
# and pinning the wrong EIN silently poisons every financial figure downstream.
CONDUIT_RE = re.compile(
    r"\b(fbo|f\s?b\s?o|trust|estate|scholarship|bequest|annuity|"
    r"charitable remainder|unitrust|crut|clat)\b")


def _norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


# Squash to letters/digits only, and drop corporate suffixes, before comparing.
# The IRS files spacing and suffixes unpredictably: the query "McDaniel College"
# must still match the registered name "Mc Daniel College Inc".
_SUFFIX_RE = re.compile(r"\b(inc|incorporated|corp|corporation|the|of)\b")


def _squash(s):
    return re.sub(r"[^a-z0-9]", "", _SUFFIX_RE.sub(" ", _norm(s)))


def _variants(name):
    """Alternate spellings the IRS/ProPublica index may file the org under.

    Searching "McDaniel College" returns ONLY two trusts FBO the college and two
    honor societies - the college itself is indexed as "Mc Daniel College Inc" and
    never comes back. Searching "Mc Daniel College" returns it exactly. Saint/St.
    is the same class of problem. So try the obvious respellings before giving up.
    """
    seen, out = set(), []

    def add(v):
        v = re.sub(r"\s+", " ", v or "").strip()
        if v and v.lower() not in seen:
            seen.add(v.lower())
            out.append(v)

    add(name)
    add(re.sub(r"\b(Mc|Mac)([A-Z])", r"\1 \2", name))       # McDaniel -> Mc Daniel
    add(re.sub(r"\b(Mc|Mac)\s+([A-Za-z])", r"\1\2", name))  # Mc Daniel -> McDaniel
    add(re.sub(r"\bSt\.?\s+", "Saint ", name))              # St Mary's -> Saint Mary's
    add(re.sub(r"\bSaint\s+", "St ", name))                 # Saint Mary's -> St Mary's
    return out


def _score(org, qsq, state):
    """Rank a search hit against the squashed query. Higher is better."""
    name = _norm(org.get("name"))
    nsq = _squash(org.get("name"))
    score = 0
    if nsq == qsq:
        score += 100
    elif nsq.startswith(qsq):
        score += 60
    elif qsq in nsq:
        score += 40
    # A conduit vehicle named after the institution is not the institution
    # (unless the caller actually searched for a trust).
    if CONDUIT_RE.search(name) and not CONDUIT_RE.search(qsq):
        score -= 80
    if state:
        score += 25 if (org.get("state") or "").upper() == state.upper() else -25
    return score


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", help="organization name to search")
    ap.add_argument("--ein", help="EIN if known (digits only)")
    ap.add_argument("--state", help="two-letter state code; disambiguates a name "
                                    "search and flags an out-of-state match")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    if not args.name and not args.ein:
        fail_stub(args.out, "propublica", "provide --name or --ein")

    ein = args.ein
    candidates = []
    warnings = []

    if not ein:
        qsq = _squash(args.name)
        best = ranked = None
        first_try = None
        used_query = args.name
        search_error = None
        for q in _variants(args.name):
            try:
                sr = get_json(SEARCH, params={"q": q})
            except Exception as e:  # noqa: BLE001
                # The API 404s a query with no hits. Keep trying the respellings -
                # the original spelling failing is exactly when a variant saves us.
                search_error = e
                continue
            orgs = sr.get("organizations", [])
            if not orgs:
                continue
            r = sorted(orgs, key=lambda o: _score(o, qsq, args.state), reverse=True)
            if first_try is None:
                first_try = (q, r)
            if _score(r[0], qsq, args.state) >= 40:
                best, ranked, used_query = r[0], r, q
                break
        if best is None and first_try is not None:
            used_query, ranked = first_try
            best = ranked[0]
        if best is None:
            fail_stub(args.out, "propublica",
                      f"no nonprofit match for '{args.name}' (tried: "
                      f"{', '.join(_variants(args.name))})"
                      + (f"; last search error: {search_error}" if search_error else ""))

        candidates = [{
            "ein": o.get("ein"),
            "name": o.get("name"),
            "state": o.get("state"),
            "ntee": o.get("ntee_code"),
            "score": _score(o, qsq, args.state),
        } for o in ranked[:10]]
        top = _score(best, qsq, args.state)

        # Refuse to silently pin a wrong EIN. Every downstream financial figure
        # keys off this, so a bad pick is worse than an honest gap: write the
        # stub with candidates and let the flow tag [verify] or rerun with --ein.
        if top < 40:
            listing = "; ".join(
                f"{c['name']} (EIN {c['ein']}, {c['state']}, score {c['score']})"
                for c in candidates[:5]) or "none"
            fail_stub(args.out, "propublica",
                      f"no confident match for '{args.name}' (tried: "
                      f"{', '.join(_variants(args.name))}). Best hits were not the "
                      f"institution: {listing}. Rerun with --ein, or web-browse the "
                      f"990 and tag [verify].")

        ein = best.get("ein")
        if used_query.lower() != args.name.lower():
            warnings.append(
                f"matched under the respelling '{used_query}' (the IRS files this "
                f"org as '{best.get('name')}'); '{args.name}' alone did not return it.")
        if CONDUIT_RE.search(_norm(best.get("name"))) and not CONDUIT_RE.search(qsq):
            warnings.append(
                f"'{best.get('name')}' looks like a trust/estate that BENEFITS the "
                f"institution rather than the institution itself. Rerun with the "
                f"institution's own --ein from candidates[].")
        if args.state and (best.get("state") or "").upper() != args.state.upper():
            warnings.append(
                f"state mismatch: picked an org in {best.get('state')} but --state "
                f"is {args.state.upper()}.")

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
        "warnings": warnings,
        "recent_filings": recent,
        "note": "If selected_ein is wrong, rerun with --ein from candidates[]. "
                "A name search can match a trust/estate named FBO the institution "
                "instead of the institution - check warnings[].",
    })
    print(f"Wrote {path} (EIN {ein}, {len(recent)} filings)")
    for w in warnings:
        print(f"  WARNING: {w}", file=sys.stderr)


if __name__ == "__main__":
    main()
