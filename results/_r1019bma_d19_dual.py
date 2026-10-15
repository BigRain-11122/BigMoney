# -*- coding: utf-8 -*-
# r1019 bm-a (successor): D-19 dual watermark probe + company orders ack diff
import subprocess, hashlib, json, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")

GRP = r"C:\Users\sjs20\Desktop\FluxGroup"
REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"

def git(args, cwd):
    p = subprocess.run(["git"] + args, cwd=cwd, capture_output=True)
    return p.returncode, p.stdout, p.stderr

rc, _, err = git(["fetch", "origin"], GRP)
print("grp_fetch_rc", rc, err[:120].decode("utf-8", "replace") if err else "")

for name, key in (("decisions", "last_decisions_sha"), ("orders", "last_orders_sha")):
    rc, out, err = git(["show", "origin/main:docs/%s.md" % name], GRP)
    sha = hashlib.sha256(out).hexdigest() if rc == 0 else "ERR"
    state = json.loads(open(os.path.join(REPO, "state-bm-a.json"), "rb").read().decode("utf-8", "replace"))
    old = state.get(key)
    print(name, "sha", sha[:16], "old", (old or "")[:16], "MATCH" if sha == old else "CHANGED")
    if sha != old and rc == 0:
        text = out.decode("utf-8", "replace")
        rows = [ln for ln in text.splitlines() if re.search(r"[Bb]ig[Mm]oney|quant", ln) and ln.strip().startswith("|")]
        print("  bigmoney-mention rows in full doc:", len(rows))
        for ln in rows[-8:]:
            print("  ", ln[:180])

# company orders ack diff
hb = json.loads(open(os.path.join(REPO, "fleet", "machines", "bm-a.json"), "rb").read().decode("utf-8", "replace"))
ack = hb.get("orders_ack") or []
if isinstance(ack, str):
    ack = [ack]
acked = set(ack)
odir = os.path.join(REPO, "fleet", "orders")
files = sorted(f for f in os.listdir(odir) if f.startswith("O-") and f.endswith(".md"))
unacked = [f for f in files if f not in acked]
print("orders_files", len(files), "acked", len(acked), "unacked", unacked)
