# Odoo Demo Architect

**Turn a discovery call into a complete, working Odoo demo — and the documents to sell it — with an AI agent doing the build.**

> Powered by **[Claude Code](https://claude.com/claude-code)** (the agent) + **[Knowcap](https://knowcap.ai)** (the memory). Claude does the research, build, code, and testing; Knowcap — queried over its MCP — feeds the agent the *truth of what the client actually said* in the discovery call. The agent is only as good as its memory: Knowcap is the memory.

A Claude Code skill. Point it at a discovery call (in Knowcap) and a reachable Odoo instance; it mines the client's pains, researches what Odoo does natively vs. what needs building, stands up a **live database** (modules + realistic data + the 1–2 "hero" features that win the deal), **tests** that those features actually fire, and generates three sales documents: a **run-of-show**, a **one-pager** for the decision-maker, and a **one-page step-by-step demo script**.

Built from a real engagement where this produced a full Odoo 19 Enterprise demo — credit-limit hard-block with manager override, weight-based fleet load-building, localized data, three sales docs — ready for a CEO meeting, with the founder barely touching the keyboard.

---

## The stack
- **Claude Code** — the agent that reads the call, researches native-vs-custom, builds the database, writes + ships the custom code, and tests every hero feature.
- **Knowcap** — the meeting-intelligence layer. The agent calls the **Knowcap MCP** (`get_source_transcriptions`, `search_memories`) to pull the discovery transcript and the client's pains in their own words. No transcript hunting, no "remind me what they said." → [knowcap.ai](https://knowcap.ai)

## What you get
- A **live Odoo demo DB** tailored to the client (any Odoo: Online, self-hosted, or Odoo.sh).
- **Working hero features**, no-code where possible, custom module only when necessary.
- A **verification log** proving each hero fired (real numbers).
- Three **self-contained HTML docs** (brand-themed): run-of-show, one-pager, 1-page script.

## Install
```bash
# clone into your Claude Code skills folder
git clone https://github.com/Smetools/odoo-demo-architect ~/.claude/skills/odoo-demo-architect
```
Or drop the folder anywhere Claude Code loads skills. Then just ask Claude: *"build an Odoo demo for <client> from our discovery call."*

## Prerequisites
- **Claude Code.**
- **Knowcap** (recommended) with its **MCP** connected — so the agent can pull the discovery transcript + extracted pains directly. → [knowcap.ai](https://knowcap.ai). (No Knowcap? Paste a transcript or notes instead.)
- A reachable **Odoo instance + API key** (Settings → My Profile → Account Security → New API Key).
  - On **Odoo.sh**: create the project + enter any partner trial code first (web-only), then come back with the DB URL + API key.
- Optional: the **Perplexity MCP** for the native-vs-custom research step (web search works too).

## Quickstart
1. Put your Odoo creds in env vars (or `scripts/creds.json`):
   `ODOO_URL`, `ODOO_DB`, `ODOO_LOGIN`, `ODOO_KEY`.
2. Verify the connection: `python scripts/odoo_connect.py` → prints `server_version`.
3. Copy `demo_config.example.json` → `scripts/demo_config.json`, fill it from the discovery call.
4. Ask Claude to run the pipeline (see `SKILL.md`).

## How it works (pipeline)
1. **Mine the discovery — via Knowcap.** Pull the meeting transcript over the Knowcap MCP; extract pains in the client's words + the 1–2 heroes.
2. **Research native-vs-custom** for each hero, for the client's exact Odoo version.
3. **Connect** to Odoo over XML-RPC; confirm the version.
4. **Install** the scope's modules.
5. **Load realistic data** (idempotent; currency before invoices; pre-stage so heroes fire live).
6. **Build heroes** — no-code first, custom module as fallback.
7. **Test every hero** on a throwaway record; keep demo objects pristine.
8. **Generate the docs** from the brand templates.
9. **Hand off** — login, cheat-sheet, verification log, doc links.

Full procedure in [`SKILL.md`](SKILL.md).

## Read this before touching Odoo 19
Several core fields were renamed in v19 (`res.users.group_ids`, `res.groups` lost `category_id`, etc.), credit limit is **warning-only** natively, and fleet load-by-weight needs `stock_fleet`. All the footguns are in [`reference/odoo19-field-gotchas.md`](reference/odoo19-field-gotchas.md) so you don't relearn them the hard way.

## Files
```
SKILL.md                        the procedure (what the agent follows)
scripts/odoo_connect.py         XML-RPC connector + helpers
scripts/build_demo.py           config-driven data + hero builder (template)
demo_config.example.json        per-client config shape
reference/odoo19-field-gotchas.md  version-specific fields + footguns
templates/                      brand.css + the three doc templates
```

## License
MIT. Use it, fork it, sell with it.

## Credit
Built by **[SMEtools](https://www.smetools.io)** — Odoo implementation + AI automation.
Runs on **[Claude Code](https://claude.com/claude-code)** + **[Knowcap](https://knowcap.ai)**.
