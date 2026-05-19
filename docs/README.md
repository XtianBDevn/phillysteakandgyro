# Philly Steak & Gyros — Engagement Docs

This folder contains all client-facing and internal docs for the Philly Steak & Gyros website engagement. All four docs will be mirrored to Notion once auth is complete.

## Index

| # | Doc | Audience | Purpose |
|---|---|---|---|
| 01 | [Audit](01-audit.md) | Internal + Client | What's broken on the live site, measured |
| 02 | [Punch-list](02-punch-list.md) | Client / Wix editor | Step-by-step fix-in-place instructions |
| 03 | [Wix mobile hotfix](03-wix-mobile-hotfix.md) | Wix editor | Copy-paste Custom Code snippet for iPhone 11 + cross-browser |
| 04 | [GBP checklist](04-gbp-checklist.md) | Client / Owner | Google Business Profile audit + weekly cadence |
| 05 | [Proposal](05-proposal.md) | Client | Three-tier engagement scope + pricing |

## Local working copy

A clean, mobile-first static rebuild lives at `../local-site/`:

```
local-site/
├── index.html       ← homepage with all 7 Day-One fixes baked in
├── menu.html        ← menu with per-item delivery deep-links
├── css/site.css     ← mobile-first stylesheet
├── js/site.js       ← tiny nav-toggle script, no framework
└── pages/*.original.html ← preserved mirrors of the live Wix output
```

Serve with `python3 -m http.server 4321 --directory local-site` and open `http://127.0.0.1:4321/`.

## Open questions for the client

1. Confirm Instagram handle (placeholder `@phillysteakgyros`).
2. Confirm exact delivery deep-link URLs (Grubhub supports `?search=`; DoorDash and Uber Eats vary).
3. Decide on direct-ordering provider (Tier 2).
4. Confirm appetite for migrating off Wix (Tier 3).
