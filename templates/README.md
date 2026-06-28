# Doc templates

Three self-contained HTML docs the skill produces in step 8. Inline `brand.css`
into each (one `<style>` block, no external deps except Google Fonts). Replace the
footer brand with the SELLING company. Fill `{{placeholders}}` from the engagement.

## 1. `run-of-show` (internal — the presenter drives from this)
Sections, in order:
- **Hero band**: client × your-company, date/time, audience, environment.
- **The one-line story** (lead): mirror the client's pain back as one sentence.
- **Status grid** (4 cards): what's built + tested (module live, fleet %, currency/data counts, staged quote).
- **Pain → demo beat** table (their words → the beat that kills it → status pill).
- **Run-of-show** rows: each beat = time, what to DO (exact click-path), what to SAY.
- **Pre-loaded data** cheat-sheet (customers/limits, products/weights, vehicles/capacity, ready objects).
- **Risks & tips** + a **close script** (dark card).

## 2. `one-pager` (external — leave-behind for the decision-maker)
- Hero band branded for YOUR company; audience = the economic buyer.
- **Today vs. with Odoo** before/after table.
- **What gets automated** (4 bullets, each tied to a pain).
- **Investment & timeline** grid (price, all-phases, duration, payment terms) — use the SOW's agreed figures/currency.
- **Path to go-live** step grid (demo = HERE).
- A dark "why Enterprise / why custom" card.

## 3. `demo-script-1pager` (internal — the one-page follow-along)
Compact, prints on one A4. A login strip, then a numbered table: `# | Do (click path) | Say`.
~7 steps: frame → clean order → ⭐hero block → ⭐override → fleet load → invoice → close.
Hero rows highlighted. Footer ref strip with the staged data. See
`demo-script-1pager.template.html`.

## Placeholders used
`{{CLIENT}}` `{{SELLER}}` `{{DATE_TIME}}` `{{AUDIENCE}}` `{{ODOO_URL}}` `{{ADMIN_LOGIN}}`
`{{PRICE}}` `{{ALL_PHASES}}` `{{DURATION}}` `{{PAYMENT_TERMS}}` and per-row step content.
