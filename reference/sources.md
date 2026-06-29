# Sources

Sources by research flow. Each flow reads only its own rows. Use the seeded
`raw/*.json` fetch first, then web-browse to fill and confirm. Always confirm a
fact before stating it; tag gaps `[verify]`.

## institutional-profile flow
Owns: About, Carnegie Classification, Mutual Peers, Memberships, Selectivity,
EPSCoR, Religious Affiliation, Designation, Student Body.

- College Scorecard (facts, control, Carnegie code, MSI, selectivity, retention/
  graduation, demographics) - seeded by `fetch_scorecard.py`:
  https://collegescorecard.ed.gov/data/
- IPEDS Data Feedback Report / institution fact book (enrollment detail,
  student-faculty ratio, demographics where Scorecard is null):
  https://nces.ed.gov/ipeds/
- Carnegie Classifications lookup (basic class, size/setting, R-status):
  https://carnegieclassifications.acenet.edu/
- Chronicle of Higher Education peer tool (mutual peers visualizer):
  https://www.chronicle.com/ (search "mutual peers")
- NSF EPSCoR eligible jurisdictions (is the state EPSCoR-eligible):
  https://www.nsf.gov/od/oia/programs/epscor/
- Institution website / accreditor (NECHE, AICAD, etc.) for memberships and
  religious affiliation.

## financials flow
Owns: Endowment and Financials, Foundation Funding, HERD.

- ProPublica Nonprofit Explorer (revenue, expenses, net assets, 990 PDFs) -
  seeded by `fetch_propublica.py`: https://projects.propublica.org/nonprofits/
- NACUBO-TIAA endowment study (endowment market value, FY):
  https://www.nacubo.org/ (endowment study press release / tables)
- NSF HERD survey (Higher Education R&D expenditures + rank) - no simple free
  API; use the NCSES data tool and tag [verify]:
  https://ncsesdata.nsf.gov/profiles/site?method=rankingBySource&ds=herd
- Candid / Foundation Directory (private foundation grant history; subscription,
  manual export to raw/, tag [verify] where blocked):
  https://fconline.foundationcenter.org/
- Foundation 990s via ProPublica for what a funder actually gave (precedent).

## federal-funding flow
Owns: Federal Funding (+ future-opportunity ideas), CDS, Lobbying Disclosures.

- USA Spending prime awards to the institution - seeded by
  `fetch_usaspending.py`: https://www.usaspending.gov/
- NSF Award Search (research awards detail): https://www.nsf.gov/awardsearch/
- grants.gov (open/forecasted programs, for future-opportunity ideas):
  https://www.grants.gov/search-grants
- Congress.gov delegation (Senators + House member for the state) - seeded by
  `fetch_congress.py`: https://www.congress.gov/
- House Community Project Funding + Senate CDS disclosures (earmarks requested/
  secured): https://appropriations.house.gov/ and
  https://www.appropriations.senate.gov/
- Senate LDA database / OpenSecrets (federal lobbying registrations):
  https://lda.senate.gov/ and https://www.opensecrets.org/

## leadership flow
Owns: Key Leaders, Sponsored Programs.

- Institution leadership / "about" pages, office of the president/provost.
- Sponsored programs / research office staff directory.
- LinkedIn (prior experience, education) and institution press releases.
- The intake names the point of contact and any leaders already known.

## strategy-news flow
Owns: Strategic Plan, Mission/Vision/Values, Centers and Institutes, Academic
Programs, Recent News.

- Institution strategic plan page (or news of a plan in development).
- Mission/vision/values page.
- Centers & institutes index; academic catalog / programs A-Z.
- Institution newsroom + recent press (prefer funding/research/leadership news).
