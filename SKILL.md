---
name: odoo-demo-architect
description: Build a complete, client-tailored Odoo demo from a discovery call. Mines the client's pains, researches native-vs-custom for each hero feature, stands up a LIVE Odoo database (modules + realistic data + working hero features) over XML-RPC, tests it, and generates the sales docs (run-of-show, one-pager, step-by-step script). Use when prepping an Odoo sales demo, POC, or proof-of-value before a client meeting. Triggers: "build an Odoo demo", "demo DB for <client>", "Odoo proof of concept", "stand up a demo before the meeting".
---

# Odoo Demo Architect

Turn a discovery call into a polished, working Odoo demo + the documents to sell it — end to end, with minimal human steering. Built from a real engagement that won on first showing.

## What it produces
1. A **live Odoo database** with the client's modules installed, realistic industry data, and the 1–2 "hero" features that map to their pain — actually working, not slideware.
2. Three **sales documents** (brand-themed, self-contained HTML): a **run-of-show**, a **one-pager** for the decision-maker, and a **1-page step-by-step demo script**.
3. A **verification log** proving each hero feature fired (e.g. "credit block raised at 56,379 > 50,000; override confirmed").

## Inputs you need before starting
- **Discovery material** — a call transcript, recording, or notes describing the client's business + pains. (If using Knowcap, pull the transcript first.)
- **Agreed scope** — which Odoo areas are in Phase 1 (Sales, Inventory, Accounting, Fleet, etc.).
- **A reachable Odoo instance + credentials** — `URL`, `DB`, `login`, and an **API key** (Settings → My Profile → Account Security → New API Key). Works on Odoo Online, self-hosted, or Odoo.sh.
  - *Odoo.sh note:* create the project + enter any partner trial code FIRST (web UI only — no API for project creation). Then proceed here once the DB is up and you have an API key.

## The pipeline (run in order)

### 1. Mine the discovery
From the transcript/notes, extract and write down:
- The **business shape** (entities, what they sell, who they sell to). Watch for "it's a group" that is really ONE company in Odoo — confirm chart-of-accounts/P&L/warehouse are shared.
- The **top 3–5 pains in the client's own words** (quote them). These become the demo beats.
- The **1–2 hero features** — the differentiators that justify the spend. Everything else is supporting flow.

### 2. Research native-vs-custom (don't assume)
For EACH hero feature, verify whether Odoo does it natively, no-code, or needs custom code — for the client's **exact Odoo version**. Use the Perplexity MCP (`perplexity_ask`) or web search. Ask precisely, e.g. *"In Odoo <ver>, is there a native hard-block (not warning) on SO confirmation over credit limit?"* Capture the verdict + citations. This step repeatedly overturns assumptions (e.g. credit limit is **warning-only** natively; v19 fleet dispatch IS native but only via `stock_fleet`).

### 3. Connect (XML-RPC)
Use `scripts/odoo_connect.py`. Authenticate, print `server_version` to confirm the major version (field names differ across versions — see `reference/odoo19-field-gotchas.md`). All build steps go through the `x(model, method, *args, **kwargs)` helper.

### 4. Install modules for the scope
`button_immediate_install` on the `ir.module.module` ids. Common set: `sale_management`, `stock`, `account_accountant`, `stock_delivery`, `stock_picking_batch`, `fleet`, `web_studio`, `base_automation`, `contacts`. For fleet load-by-weight on v19 also install `stock_fleet` (Stock Transport — adds vehicle capacity + batch dispatch). Module installs are heavy; allow several minutes.

### 5. Generate + load realistic demo data
Industry-appropriate, minimal but believable. Drive it from a `demo_config.json` (see `demo_config.example.json`) and `scripts/build_demo.py`. Rules:
- **Get-or-create by name** so re-runs are idempotent.
- Set the right **currency** first (activate it with `context={'active_test': False}`, set on `res.company`) — BEFORE posting any invoices (currency can't change once journal entries exist).
- Give products a **weight** if fleet is in scope. Give customers **credit limits** (`use_partner_credit_limit=True`, `credit_limit=...`) if credit is in scope.
- **Pre-stage state** to make heroes fire live: e.g. post an unpaid invoice to put a customer's receivable JUST under their limit, so a live order tips them over. Keep one demo quotation in **draft** for the live click.
- Seed stock with `inventory_mode` context so deliveries can reserve (go Ready).

### 6. Build the hero features — no-code first, module as fallback
- **Prefer no-code:** server actions / automated rules (`base.automation`) / Studio. Portable to any Odoo, no deploy.
- **Custom module only if needed:** generate a minimal module, push to the instance's git (Odoo.sh) or hand it to the user to deploy, then install + test. Keep modules tiny and version-correct.
- Example hero (credit hard-block + manager override): override `sale.order.action_confirm` to raise `UserError` when `partner.credit + amount_total > credit_limit` unless the user is in an approver group; add an "Override" button gated to that group. (No-code equivalent: a Studio approval rule on the Confirm button + a stored "over limit" flag.)

### 7. Test every hero over XML-RPC
On a THROWAWAY record: trigger the action, assert the block fires, assert the override path works, then delete the throwaway. Leave the real demo objects pristine. Print a verification log with the actual numbers.

### 8. Generate the sales docs
From `templates/` (genericized, brand-themed), produce three self-contained HTML files, filling in the client's data:
- **run-of-show** — beats with exact click-paths + what to say.
- **one-pager** — before/after, what's automated, investment, the path to go-live; branded for the *selling* company; decision-maker audience.
- **demo-script-1pager** — 7-ish numbered steps (Do + Say), prints on one A4.

### 9. Hand off
Output: the login, the pre-loaded data cheat-sheet, the verification log, and links to the three docs. Remind the user to rehearse once and keep the demo quotation in draft.

## Guardrails
- **Never invent that a feature works — test it.** Step 7 is mandatory; a demo hero that fails live loses the deal.
- **Research before building** (step 2). Version assumptions are the #1 source of wasted effort.
- **Don't hard-code the client.** Everything client-specific lives in `demo_config.json`.
- **Currency before invoices. Weight before fleet. Pre-stage before the live click.** Order matters.
- Read `reference/odoo19-field-gotchas.md` before touching Odoo 19 — several core fields were renamed.

## Files
- `scripts/odoo_connect.py` — XML-RPC connector + `x()` helper (correct context-kwarg passing).
- `scripts/build_demo.py` — config-driven data + hero builder (template to adapt per engagement).
- `demo_config.example.json` — the shape of a per-client config.
- `reference/odoo19-field-gotchas.md` — version-specific field names + footguns learned the hard way.
- `templates/` — the three doc templates (brand-themed, `{{placeholder}}` driven).
