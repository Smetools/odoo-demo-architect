"""Generic Odoo XML-RPC connector for odoo-demo-architect.

Reads credentials from environment variables (or a creds.json next to this file):
  ODOO_URL    e.g. https://my-instance.odoo.com   (no trailing slash)
  ODOO_DB     database name
  ODOO_LOGIN  user login (often an email; "admin" on Odoo.sh trials)
  ODOO_KEY    an API key (Settings > My Profile > Account Security > New API Key)

Usage:
    from odoo_connect import x, common, UID, URL, DB
    UID                      # authenticated user id
    common.version()         # confirm server_version BEFORE building (field names vary by version)
    x("res.partner", "search_read", [["customer_rank", ">", 0]], fields=["name"])

The x() helper passes keyword args straight into execute_kw's kwargs, so pass
Odoo kwargs natively:  x(model, "search", domain, limit=5, context={"active_test": False})
Do NOT pass a context dict positionally — that becomes `offset` and Postgres errors.
"""
import os, json, ssl, xmlrpc.client

_here = os.path.dirname(os.path.abspath(__file__))

def _cfg(key, default=None):
    v = os.environ.get(key)
    if v:
        return v
    path = os.path.join(_here, "creds.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f).get(key, default)
    return default

URL   = (_cfg("ODOO_URL")   or "").rstrip("/")
DB    =  _cfg("ODOO_DB")
LOGIN =  _cfg("ODOO_LOGIN") or "admin"
KEY   =  _cfg("ODOO_KEY")

if not (URL and DB and KEY):
    raise SystemExit("Set ODOO_URL, ODOO_DB, ODOO_KEY (and optionally ODOO_LOGIN) "
                     "as env vars or in creds.json next to this script.")

_ctx = ssl.create_default_context()
common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common", context=_ctx, allow_none=True)
UID = common.authenticate(DB, LOGIN, KEY, {})
if not UID:
    raise SystemExit("Authentication failed — check DB / LOGIN / API key.")
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object", context=_ctx, allow_none=True)


def x(model, method, *args, **kwargs):
    """execute_kw wrapper. Positional args -> Odoo positional params;
    keyword args (limit, fields, context, ...) -> Odoo kwargs."""
    return models.execute_kw(DB, UID, KEY, model, method, list(args), kwargs)


def get_or_create(model, domain, vals, label=None):
    """Idempotent create: update if a record matches `domain`, else create."""
    ids = x(model, "search", domain, limit=1)
    if ids:
        x(model, "write", ids, vals)
        return ids[0]
    return x(model, "create", vals)


def fields_named(model, *needles):
    """Return field technical names on `model` whose name/label contains any needle.
    NOTE: on some Odoo 19 builds fields_get attribute VALUES return null over XML-RPC,
    so match on the technical KEYS, which are always reliable."""
    keys = list(x(model, "fields_get", [], {}).keys())
    nl = [n.lower() for n in needles]
    return sorted(k for k in keys if any(n in k.lower() for n in nl))


if __name__ == "__main__":
    print("server_version:", common.version().get("server_version"))
    print("uid:", UID, "url:", URL, "db:", DB)
