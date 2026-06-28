"""Config-driven Odoo demo data builder (template — adapt per engagement).

Reads demo_config.json (see demo_config.example.json) and creates:
  currency, products (with weight), customers (with credit limits),
  vehicle categories + vehicles (with capacity), a B2B pricelist,
  and pre-staged receivables (posted unpaid invoices) so heroes fire live.

Idempotent: get-or-create by name. Run order matters (currency before invoices).
Requires odoo_connect.py in the same folder + creds (env or creds.json).
"""
import json, os
from odoo_connect import x, get_or_create, URL, DB

CFG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "demo_config.json")
cfg = json.load(open(CFG, encoding="utf-8"))

# 1. currency (must run before invoices)
cur = cfg.get("currency")
if cur:
    ids = x("res.currency", "search", [["name", "=", cur]], context={"active_test": False})
    if not ids:
        ids = [x("res.currency", "create", {"name": cur, "rounding": 0.01})]
    x("res.currency", "write", ids, {"active": True})
    comp = x("res.company", "search", [], limit=1)[0]
    try:
        x("res.company", "write", [comp], {"currency_id": ids[0]})
    except Exception as e:
        print("  ! currency switch blocked (invoices exist?):", str(e)[:120])
    print("currency:", cur)

# 2. settings
s = x("res.config.settings", "create", {
    "account_use_credit_limit": bool(cfg.get("use_credit_limit", True)),
    "group_product_pricelist": True,
})
x("res.config.settings", "execute", [s])

# 3. products
prod = {}
for p in cfg.get("products", []):
    vals = {"name": p["name"], "list_price": p.get("price", 0.0),
            "weight": p.get("weight", 0.0), "type": "consu", "is_storable": True}
    try:
        prod[p["name"]] = get_or_create("product.template", [["name", "=", p["name"]]], vals)
    except Exception:
        vals.pop("is_storable", None)
        prod[p["name"]] = get_or_create("product.template", [["name", "=", p["name"]]], vals)
print("products:", len(prod))

# 4. vehicle categories + vehicles
brand = None
if cfg.get("vehicles"):
    brand = get_or_create("fleet.vehicle.model.brand", [["name", "=", "Demo Fleet"]], {"name": "Demo Fleet"})
for v in cfg.get("vehicles", []):
    cat = get_or_create("fleet.vehicle.model.category", [["name", "=", v["category"]]],
                        {"name": v["category"], "weight_capacity": v.get("capacity_kg", 0.0)})
    model = get_or_create("fleet.vehicle.model", [["name", "=", v["model"]]],
                         {"name": v["model"], "brand_id": brand, "category_id": cat})
    get_or_create("fleet.vehicle", [["license_plate", "=", v["plate"]]],
                  {"model_id": model, "license_plate": v["plate"], "category_id": cat})
print("vehicles:", len(cfg.get("vehicles", [])))

# 5. customers with credit limits
cust = {}
for c in cfg.get("customers", []):
    cust[c["name"]] = get_or_create("res.partner", [["name", "=", c["name"]]],
        {"name": c["name"], "is_company": True, "customer_rank": 1,
         "use_partner_credit_limit": True, "credit_limit": c.get("credit_limit", 0.0)})
print("customers:", len(cust))

# 6. B2B pricelist (optional global % discount)
pl_cfg = cfg.get("pricelist")
if pl_cfg:
    pl = get_or_create("product.pricelist", [["name", "=", pl_cfg["name"]]], {"name": pl_cfg["name"]})
    if pl_cfg.get("percent") and not x("product.pricelist.item", "search", [["pricelist_id", "=", pl]]):
        x("product.pricelist.item", "create", {"pricelist_id": pl, "applied_on": "3_global",
            "compute_price": "percentage", "percent_price": pl_cfg["percent"]})
    for cname in pl_cfg.get("assign_to", []):
        if cname in cust:
            x("res.partner", "write", [cust[cname]], {"property_product_pricelist": pl})

# 7. pre-stage receivables (post unpaid invoices)
def first_variant(tmpl_id):
    return x("product.product", "search", [["product_tmpl_id", "=", tmpl_id]], limit=1)[0]

any_prod = first_variant(next(iter(prod.values()))) if prod else None
for stage in cfg.get("prestage_receivables", []):
    cid = cust.get(stage["customer"])
    if not cid:
        continue
    mv = x("account.move", "create", {
        "move_type": "out_invoice", "partner_id": cid,
        "invoice_line_ids": [(0, 0, {"product_id": any_prod, "quantity": 1,
                                     "price_unit": stage["amount"], "tax_ids": [(6, 0, [])]})]})
    try:
        x("account.move", "action_post", [mv])
    except Exception as e:
        print("  ! post for", stage["customer"], str(e)[:100])

# 8. verify credit headroom
print("\n-- credit headroom --")
for c in cfg.get("customers", []):
    cid = cust[c["name"]]
    r = x("res.partner", "read", [cid], ["credit", "credit_limit"])[0]
    flag = "OVER" if r["credit"] > r["credit_limit"] else "ok"
    print(f"  {c['name']:30} owes={r['credit']:>12,.0f}  limit={r['credit_limit']:>12,.0f}  {flag}")
print("\nDONE. Instance:", URL, "DB:", DB)
