#!/usr/bin/env python3
"""Fetch institution facts from the U.S. Dept of Education College Scorecard.

Endpoint: https://api.data.gov/ed/collegescorecard/v1/schools
Needs a data.gov API key (DATA_GOV_API_KEY). DEMO_KEY works for light testing
but is heavily rate-limited; register free at https://api.data.gov/signup/.

Usage:
  python scripts/fetch_scorecard.py --name "Bowie State University" \
      --out 00-intake/output/raw

Writes <out>/scorecard.json with the matched school's key facts for the
profile: Carnegie classification, control, enrollment, location, MSI
designations, religious affiliation, selectivity (admission rate), retention and
completion rates, federal/Pell aid rates, and student demographics.

Used by BOTH the intake flow (identity match -> id/control/Carnegie) and the
institutional-profile research flow (Student Body, Selectivity, Designation).

[VERIFY] Carnegie basic codes are numeric; map to R1/R2 vs non-R1/R2 with the
current ACE crosswalk. Scorecard demographic/retention fields can be null for
small or specialized institutions; the research agent fills gaps from IPEDS Data
Feedback / institutional fact books and tags [verify].
"""
import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.http import get_json, write_output, fail_stub  # noqa: E402

API = "https://api.data.gov/ed/collegescorecard/v1/schools"

FIELDS = ",".join([
    "id", "school.name", "school.city", "school.state", "school.zip",
    "school.school_url", "school.ownership",
    "school.carnegie_basic", "school.carnegie_undergrad",
    "school.religious_affiliation",
    "latest.student.size", "latest.student.grad_students",
    # selectivity + outcomes
    "latest.admissions.admission_rate.overall",
    "latest.student.retention_rate.four_year.full_time",
    "latest.completion.completion_rate_4yr_150nt",
    # aid
    "latest.aid.pell_grant_rate", "latest.aid.federal_loan_rate",
    # student-to-faculty + demographics
    "latest.student.demographics.student_faculty_ratio",
    "latest.student.demographics.women", "latest.student.demographics.men",
    "latest.student.demographics.race_ethnicity.white",
    "latest.student.demographics.race_ethnicity.black",
    "latest.student.demographics.race_ethnicity.hispanic",
    "latest.student.demographics.race_ethnicity.asian",
    "latest.student.demographics.race_ethnicity.aian",
    "latest.student.demographics.race_ethnicity.nhpi",
    "latest.student.demographics.race_ethnicity.two_or_more",
    "latest.student.demographics.race_ethnicity.non_resident_alien",
    "latest.student.demographics.race_ethnicity.unknown",
    # MSI designations
    "school.minority_serving.historically_black",
    "school.minority_serving.hispanic",
    "school.minority_serving.tribal",
    "school.minority_serving.aanapii",
    "school.minority_serving.predominantly_black",
    "school.minority_serving.annh",
])

OWNERSHIP = {1: "public", 2: "private nonprofit", 3: "private for-profit"}

# Scorecard religious_affiliation is a numeric code; -2/-1/null mean "not
# religiously affiliated / not reported". The agent maps a present code to the
# denomination via the Scorecard data dictionary and tags [verify].


def _pct(v):
    """Scorecard rates are 0-1 floats; render as a rounded percent or None."""
    return round(v * 100, 1) if isinstance(v, (int, float)) else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True, help="institution name to match")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    key = os.environ.get("DATA_GOV_API_KEY") or "DEMO_KEY"

    try:
        resp = get_json(API, params={
            "school.name": args.name,
            "fields": FIELDS,
            "per_page": 5,
            "api_key": key,
        })
    except Exception as e:  # noqa: BLE001
        fail_stub(args.out, "scorecard", f"{type(e).__name__}: {e}")

    results = resp.get("results", []) if isinstance(resp, dict) else []
    if not results:
        fail_stub(args.out, "scorecard",
                  f"no College Scorecard match for '{args.name}'")

    schools = []
    for r in results:
        msi = {
            "hbcu": r.get("school.minority_serving.historically_black"),
            "hsi": r.get("school.minority_serving.hispanic"),
            "tcu": r.get("school.minority_serving.tribal"),
            "aanapisi": r.get("school.minority_serving.aanapii"),
            "pbi": r.get("school.minority_serving.predominantly_black"),
            "annh": r.get("school.minority_serving.annh"),
        }
        demo = {
            "women_pct": _pct(r.get("latest.student.demographics.women")),
            "men_pct": _pct(r.get("latest.student.demographics.men")),
            "white_pct": _pct(r.get("latest.student.demographics.race_ethnicity.white")),
            "black_pct": _pct(r.get("latest.student.demographics.race_ethnicity.black")),
            "hispanic_pct": _pct(r.get("latest.student.demographics.race_ethnicity.hispanic")),
            "asian_pct": _pct(r.get("latest.student.demographics.race_ethnicity.asian")),
            "aian_pct": _pct(r.get("latest.student.demographics.race_ethnicity.aian")),
            "nhpi_pct": _pct(r.get("latest.student.demographics.race_ethnicity.nhpi")),
            "two_or_more_pct": _pct(r.get("latest.student.demographics.race_ethnicity.two_or_more")),
            "nonresident_pct": _pct(r.get("latest.student.demographics.race_ethnicity.non_resident_alien")),
            "unknown_pct": _pct(r.get("latest.student.demographics.race_ethnicity.unknown")),
        }
        schools.append({
            "id": r.get("id"),
            "name": r.get("school.name"),
            "city": r.get("school.city"),
            "state": r.get("school.state"),
            "zip": r.get("school.zip"),
            "url": r.get("school.school_url"),
            "control": OWNERSHIP.get(r.get("school.ownership"),
                                     r.get("school.ownership")),
            "carnegie_basic": r.get("school.carnegie_basic"),
            "carnegie_undergrad": r.get("school.carnegie_undergrad"),
            "religious_affiliation_code": r.get("school.religious_affiliation"),
            "enrollment": r.get("latest.student.size"),
            "grad_students": r.get("latest.student.grad_students"),
            "selectivity": {
                "admission_rate_pct": _pct(r.get("latest.admissions.admission_rate.overall")),
                "retention_rate_pct": _pct(r.get("latest.student.retention_rate.four_year.full_time")),
                "graduation_rate_pct": _pct(r.get("latest.completion.completion_rate_4yr_150nt")),
            },
            "aid": {
                "pell_grant_rate_pct": _pct(r.get("latest.aid.pell_grant_rate")),
                "federal_loan_rate_pct": _pct(r.get("latest.aid.federal_loan_rate")),
            },
            "student_faculty_ratio": r.get("latest.student.demographics.student_faculty_ratio"),
            "demographics_pct": {k: v for k, v in demo.items() if v is not None},
            "designations": {k: v for k, v in msi.items() if v},
        })

    path = write_output(args.out, "scorecard", {
        "query": args.name,
        "count": len(schools),
        "schools": schools,
        "_note": "carnegie_basic is a numeric code; confirm NOT R1/R2 via the "
                 "ACE crosswalk. ownership 1=public 2=private-nonprofit. "
                 "Percent fields are already x100 (e.g. 41.0 = 41%). Nulls were "
                 "not reported to Scorecard; fill from IPEDS and tag [verify].",
    })
    print(f"Wrote {path} ({len(schools)} matches)")


if __name__ == "__main__":
    main()
