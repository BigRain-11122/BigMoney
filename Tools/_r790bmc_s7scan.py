# -*- coding: utf-8 -*-
"""r790 bm-c S7 closing scan (double-scan law): group-tree DEC/ORD raw-blob
hashes vs state watermarks (SHA-256/SHA-1 ALGORITHM PIN r537, hex-case
normalized r711), fleet orders ack diff (basename-with-.md canon), inbox
unread scan. NO repo git writes here (closing scan is read-only; the S0
script owns the pull leg). Facts -> results/_r790bmc_s7_facts.json."""
import subprocess, hashlib, json, glob, os, re

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
GROUP = r"K:\Fluxgroup\FluxGroup"
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

def git_out(cwd, args):
    p = subprocess.run(["git", "-C", cwd] + args, capture_output=True, creationflags=CNW)
    return p.returncode, p.stdout, p.stderr

facts = {"round": 790, "scan": "closing"}
rc, _, err = git_out(GROUP, ["fetch", "origin"])
facts["group_fetch_rc"] = rc
rc, dec_bytes, _ = git_out(GROUP, ["show", "origin/main:docs/decisions.md"])
facts["dec_sha"] = hashlib.sha256(dec_bytes).hexdigest().upper()
rc, ord_bytes, _ = git_out(GROUP, ["show", "origin/main:docs/orders.md"])
facts["ord_sha"] = hashlib.sha1(ord_bytes).hexdigest().upper()
with open(os.path.join(REPO, "state-bm-c.json"), encoding="utf-8") as fh:
    state = json.load(fh)
facts["prev_dec_sha"] = state.get("last_decisions_sha", "")
facts["prev_ord_sha"] = state.get("last_orders_sha", "")
facts["dec_delta"] = facts["dec_sha"].upper() != facts["prev_dec_sha"].upper()
facts["ord_delta"] = facts["ord_sha"].upper() != facts["prev_ord_sha"].upper()
if facts["dec_delta"]:
    rc, dlog, _ = git_out(GROUP, ["log", "-8", "--oneline", "origin/main", "--", "docs/decisions.md"])
    with open(os.path.join(REPO, "results", "_r790bmc_dec_log.txt", ), "w", encoding="utf-8") as fh:
        fh.write(dlog.decode("utf-8", "replace"))
    with open(os.path.join(REPO, "results", "_r790bmc_dec_blob.md"), "wb") as fh:
        fh.write(dec_bytes)
if facts["ord_delta"]:
    with open(os.path.join(REPO, "results", "_r790bmc_ord_blob.md"), "wb") as fh:
        fh.write(ord_bytes)

order_files = sorted(glob.glob(os.path.join(REPO, "fleet", "orders", "O-*.md")))
facts["fleet_orders_total"] = len(order_files)
with open(os.path.join(REPO, "fleet", "machines", "bm-c.json"), encoding="utf-8") as fh:
    hb = json.load(fh)
ack = set(hb.get("orders_ack", []))
facts["unacked"] = [os.path.basename(f) for f in order_files
                    if os.path.basename(f) not in ack]

unread = []
for f in sorted(glob.glob(os.path.join(REPO, "fleet", "inbox", "*.md"))):
    try:
        txt = open(f, encoding="utf-8", errors="replace").read()
    except Exception:
        unread.append(os.path.basename(f))
        continue
    if re.search(r"(?im)(bm-c|all)", txt[:800]):
        unread.append(os.path.basename(f))
facts["inbox_unread"] = unread
facts["shape_assert"] = bool(re.fullmatch(r"[0-9A-F]{64}", facts["dec_sha"])
                             and re.fullmatch(r"[0-9A-F]{40}", facts["ord_sha"]))
out = os.path.join(REPO, "results", "_r790bmc_s7_facts.json")
with open(out, "w", encoding="utf-8") as fh:
    json.dump(facts, fh, indent=1)
print(json.dumps({k: facts[k] for k in ("dec_sha", "ord_sha", "dec_delta", "ord_delta",
                                        "unacked", "inbox_unread", "fleet_orders_total",
                                        "shape_assert", "group_fetch_rc")}, indent=1))
