# -*- coding: utf-8 -*-
# r1039 bm-c: D-19 row diff from pinned watermarks (watermarks read from state file programmatically).
import json, hashlib, subprocess, sys, io, os

GROUP = r"K:\Fluxgroup\FluxGroup"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
st = json.loads(io.open(os.path.join(ROOT, "state-bm-c.json"), encoding="utf-8").read())
wm_ord = st["last_orders_sha"]          # content-bytes sha1 (blob sha) of orders.md
wm_dec = st["last_decisions_sha"]       # raw-blob sha256 of decisions.md

def g(*args):
    return subprocess.run(["git", "-C", GROUP] + list(args), capture_output=True).stdout

g("fetch", "origin")

new_ord = g("show", "origin/main:docs/orders.md")
new_dec = g("show", "origin/main:docs/decisions.md")
sha1_new_ord = hashlib.sha1(new_ord).hexdigest()
sha256_new_dec = hashlib.sha256(new_dec.replace(b"\r\n", b"\n")).hexdigest()  # probe method = LF-normalized sha256

def find_old(path, match):
    commits = g("log", "origin/main", "--format=%H", "-n", "400", "--", path).decode().split()
    for c in commits:
        b = g("show", "%s:%s" % (c, path))
        if match(b):
            return b, c
    return None, None

old_ord, c_ord = find_old("docs/orders.md", lambda b: hashlib.sha1(b).hexdigest() == wm_ord)
assert old_ord is not None, "old ORD version not found in history"
old_dec, c_dec = find_old("docs/decisions.md", lambda b: hashlib.sha256(b.replace(b"\r\n", b"\n")).hexdigest() == wm_dec)
assert old_dec is not None, "old DEC version not found in history"
print("old ORD at", c_ord[:9], "/ old DEC at", c_dec[:9])

def rows(b):
    return [ln.strip() for ln in b.decode("utf-8", "replace").splitlines() if ln.startswith("|")]

old_os, old_ds = set(rows(old_ord)), set(rows(old_dec))
new_ord_rows = [r for r in rows(new_ord) if r not in old_os]
new_dec_rows = [r for r in rows(new_dec) if r not in old_ds]

rep = io.open(os.path.join(ROOT, "results", "_r1039bmc_d19_rows.md"), "w", encoding="utf-8", newline="\n")
rep.write("# r1039 D-19 diff (ORD %s -> %s / DEC %s -> %s)\n\n" % (wm_ord[:12], sha1_new_ord[:12], wm_dec[:12], sha256_new_dec[:12]))
rep.write("## ORD new rows (%d)\n" % len(new_ord_rows))
for r in new_ord_rows:
    rep.write("ORD| %s\n" % r)
rep.write("\n## DEC new rows (%d)\n" % len(new_dec_rows))
for r in new_dec_rows:
    rep.write("DEC| %s\n" % r)
rep.close()

facts = {
    "wm_ord": wm_ord, "wm_dec": wm_dec,
    "new_ord_sha1": sha1_new_ord, "new_dec_sha256": sha256_new_dec,
    "ord_rows_new": len(new_ord_rows), "dec_rows_new": len(new_dec_rows),
    "probe_match_ord": sha1_new_ord == "33ea18b586ad65b1093b8b65520709fe9fa2621d",
    "probe_match_dec": sha256_new_dec == "ec6b91647416271402686f8b9800486feb03eefab3fc4cffbcbebd913416726e",
}
io.open(os.path.join(ROOT, "results", "_r1039bmc_d19_facts.json"), "w", encoding="utf-8").write(json.dumps(facts, ensure_ascii=False, indent=1))
print(json.dumps(facts, ensure_ascii=False))
