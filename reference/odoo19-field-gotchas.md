# Odoo 19 (Enterprise) — field names & footguns

Hard-won notes from a real v19 demo build over XML-RPC. Check these before you waste a build cycle. Always confirm the major version first: `common.version()["server_version"]`.

## Renamed core fields (these break v17/v18 code)
| Concept | v17/18 | **v19** |
|---|---|---|
| User's groups | `groups_id` | **`group_ids`** |
| Group's app category | `category_id` on `res.groups` | **removed** — use `privilege_id` (model `res.groups.privilege`), or just omit |
| (so in security XML) | `<field name="groups_id" ...>` | `<field name="group_ids" ...>` |

A custom module that sets `category_id` on `res.groups` or `groups_id` on `res.users` will fail to install on v19 with `Invalid field ... / Cannot ...`. Drop the category or use `privilege_id`.

## fields_get returns null attributes over XML-RPC (some v19 builds)
`fields_get([], {"attributes": ["string","type"]})` may return each field with `string=None`. The **keys (technical names) are still correct** — match on keys, not labels. (`fields_named()` in `odoo_connect.py` does this.)

## Product model (v19)
- Goods that track stock: `type="consu"` **plus** `is_storable=True` (the old `type="product"` is gone).
- Weight: `product.template.weight` (kg by default).

## Credit limit (Accounting)
- Native behaviour is **WARNING ONLY** — it does NOT block SO confirmation. A hard block needs a Studio approval rule or a custom `action_confirm` override.
- Enable: `res.config.settings.account_use_credit_limit = True` (+ `account_default_credit_limit`). Apply via `create` then `execute`.
- Per-customer: `res.partner.use_partner_credit_limit = True`, `credit_limit = <amount>`. **These are non-stored** — you cannot `search` on `use_partner_credit_limit` (Postgres "not stored" error); read it per-record instead.
- `res.partner.credit` = current Total Receivable (computed from posted AR moves). Pre-stage it by posting an unpaid customer invoice.

## Fleet load-by-weight / Dispatch (v19) — IS native, but gated
- Native `fleet` alone = vehicle cost/maintenance; **no capacity fields**.
- Install **`stock_fleet`** ("Stock Transport"). It adds the dispatch fields to `stock.picking.batch`: `vehicle_id`, `vehicle_category_id`, `vehicle_weight_capacity`, `used_weight_percentage`, `estimated_shipping_weight`, `has_dispatch_management`.
- Capacity lives on **`fleet.vehicle.model.category`** → fields `weight_capacity`, `volume_capacity`. Create a category with capacity, assign it to the vehicle (`fleet.vehicle.category_id`), then a batch with that vehicle computes `used_weight_percentage`.
- Demo flow: confirm SOs → deliveries → create `stock.picking.batch` with `vehicle_id` + `picking_ids` → read `used_weight_percentage`.

## Currency
- New databases ship most currencies **inactive**. Find with `search([["name","=","EGP"]], context={"active_test": False})`, set `active=True`, then `res.company.currency_id`.
- Change company currency **BEFORE** posting any invoices/journal entries — Odoo blocks the switch once entries exist.

## Stock seeding (so deliveries go Ready)
- Create `stock.quant` with `inventory_quantity` and `context={"inventory_mode": True}`, then call `action_apply_inventory` with the same context. The apply may warn harmlessly if already applied; check by reserving (`stock.picking.action_assign` → state `assigned`).

## XML-RPC helper footgun
- `execute_kw(..., method, args, kwargs)`: a **context dict must go in kwargs**, never as a positional arg. `search(domain, {"active_test":False})` sends the dict as `offset` → `psycopg2 can't adapt type 'dict'`. Pass `context=` as a keyword (see `x()` in `odoo_connect.py`).

## Module install over XML-RPC
- `x("ir.module.module","button_immediate_install",[ids])`. Heavy — let it run minutes. On a failed XML-data load it rolls back cleanly (module stays uninstalled); fix and retry.
- After deploying a custom module to git (Odoo.sh), wait for the rebuild, then `x("ir.module.module","update_list")` and search for it before installing.
