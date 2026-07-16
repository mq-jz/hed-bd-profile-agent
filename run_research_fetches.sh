#!/usr/bin/env bash
# Warm the raw/ folders for the research flows by running every mechanical fetch
# in parallel. Run AFTER intake is approved - it reads identity facts from
# 00-intake/output/intake.md is NOT automatic; pass them as arguments here.
#
# Usage:
#   ./run_research_fetches.sh "Rhode Island School of Design" RI [EIN]
#
# Args:
#   $1  institution name (as it appears in College Scorecard / ProPublica)
#   $2  two-letter state code (for the congressional delegation / CDS)
#   $3  optional EIN (digits only) to pin the exact ProPublica 990 record
#
# Each fetch writes plain JSON (or an _error stub) into the owning flow's raw/.
# Missing API keys never crash the run - the stub is written and the flow agent
# tags [verify]. Re-run any single fetch by copying its line below.
set -u
NAME="${1:?institution name required}"
STATE="${2:?two-letter state code required}"
EIN="${3:-}"
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "Fetching raw data for: $NAME ($STATE)"

# institutional-profile: College Scorecard (facts, selectivity, student body)
python scripts/fetch_scorecard.py --name "$NAME" \
  --out research/institutional-profile/raw &

# financials: ProPublica 990 (endowment proxy, revenue, expenses, net assets)
if [ -n "$EIN" ]; then
  python scripts/fetch_propublica.py --ein "$EIN" \
    --out research/financials/raw &
else
  # --state disambiguates the name search; a bare name can match a trust "FBO
  # <College>" or a same-named college in another state. Pass the EIN when known.
  python scripts/fetch_propublica.py --name "$NAME" --state "$STATE" \
    --out research/financials/raw &
fi

# federal-funding: USA Spending prime awards to the institution
python scripts/fetch_usaspending.py --name "$NAME" --min 0 --years 10 \
  --out research/federal-funding/raw &

# federal-funding (CDS): current congressional delegation for the state
python scripts/fetch_congress.py --state "$STATE" \
  --out research/federal-funding/raw &

wait
echo "Done. Inspect each research/<flow>/raw/*.json before running the flows."
echo "Note: HERD (NSF), foundation funding (Candid), Carnegie peer set, and"
echo "lobbying disclosures have no free API here - those flows web-browse and"
echo "tag [verify]. See reference/sources.md."
