# Known Issues Register

Last updated 2026-03-06.

## OPEN — Saved-card checkout failure (INC-4471)

Since the 2026-03-05 release, checkout fails for customers paying with a saved
card. Cards entered fresh at checkout are unaffected.

- **Workaround:** ask the customer to re-enter their card details rather than
  selecting a saved card.
- **Impact:** approximately 8% of transactions.
- **Fee waivers:** this incident qualifies for a restocking-fee waiver on any
  affected return.

## OPEN — CSV export truncation (INC-4468)

Exports containing more than 1,000 records silently drop the final row.

- **Workaround:** export in batches under 1,000 records.

## RESOLVED — Report latency (INC-4455)

Reports took 40+ seconds to load between 2026-02-20 and 2026-02-28. Resolved
by a query index change on 2026-02-28. No customer action needed.
