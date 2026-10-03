"""r654 bm-b S0.5: orders double-scan (same-caliber set compare, r646 law) +
D-19 group decisions/orders raw-blob hash check (content-addressing law:
git show origin/main bytes only - r660 law). K: absent per D-20261004-02③
fallback = temporary sparse clone (r631 bm-b recipe). Template: results/_r449bmc_s05_scan.py."""
import hashlib
import json
import os
import re
import shutil
import subprocess

RB = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
TMP = os.path.join(os.environ.get("TEMP", r"C:\Windows\Temp"), "_r654bmb_grsparse")
CREATE = 0x08000000


def git(repo, *a):
    p = subprocess.run(["git", "-C", repo] + list(a), capture_output=True,
                       creationflags=CREATE)
    return p.returncode, (p.stdout or b""), (p.stderr or b"")


# ---------- 1) orders double-scan ----------
rc, out, _ = git(RB, "ls-tree", "-r", "--name-only", "HEAD", "fleet/orders/")
assert rc == 0, "ls-tree rc=%d" % rc
orders = sorted(os.path.basename(ln) for ln in out.decode("utf-8", "replace").splitlines()
                if "fleet/orders/" in ln and re.match(r"^O-.*\.md$", os.path.basename(ln)))
hb = json.loads(open(os.path.join(RB, "fleet", "machines", "bm-b.json"), "rb").read().decode("utf-8"))
acked = sorted(set(x for x in hb.get("orders_ack", []) if x.startswith("O-")))
o_set, a_set = set(orders), set(acked)
unacked = [o for o in orders if o not in a_set]
ghost = [a for a in acked if a not in o_set]
print("ORDERS-SCAN tree=%d ack=%d unacked=%d ghost-ack=%d" % (len(orders), len(acked), len(unacked), len(ghost)))
for u in unacked:
    print("UNACKED:", u)

# ---------- 2) D-19 group decisions.md via sparse clone (K: absent fallback) ----------
if os.path.isdir(TMP):
    shutil.rmtree(TMP, ignore_errors=True)
rc, out, err = subprocess.run(
    ["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse",
     "https://github.com/BigRain-11122/FluxGroup.git", TMP],
    capture_output=True, creationflags=CREATE).returncode, None, None
assert rc == 0, "sparse clone rc=%d" % rc
git(TMP, "sparse-checkout", "set", "--skip-checks", "docs/decisions.md")
rc, out, err = git(TMP, "show", "origin/main:docs/decisions.md")
assert rc == 0, "decisions show rc=%d %s" % (rc, err[:200])
d_sha = hashlib.sha256(out).hexdigest().upper()
st = json.loads(open(os.path.join(RB, "state.json"), "rb").read().decode("utf-8"))
d_prev = st.get("last_decisions_sha", "")
print("D19-DECISIONS sha=%s prev=%s match=%s" % (d_sha[:16], d_prev[:16], d_sha == d_prev))
if d_sha != d_prev:
    open(os.path.join(RB, "results", "_r654bmb_d19_decisions.md"), "wb").write(out)
    txt = out.decode("utf-8", "replace")
    for ln in txt.splitlines():
        if ("BigMoney" in ln or "quant" in ln or "bm-b" in ln) and ln.strip().startswith(("-", "*", "|", ">", "#") or ln.strip()[:1].isdigit()):
            print("D19-LINE:", ln.strip()[:300])

# ---------- 3) group orders.md (raw-blob SHA-256) ----------
rc, out, err = git(TMP, "show", "origin/main:docs/orders.md")
assert rc == 0, "orders show rc=%d %s" % (rc, err[:200])
o_sha = hashlib.sha256(out).hexdigest().upper()
o_prev = st.get("last_orders_sha", "")
print("D19-GORDERS sha=%s prev=%s match=%s" % (o_sha[:16], o_prev[:16], o_sha == o_prev))
if o_sha != o_prev:
    open(os.path.join(RB, "results", "_r654bmb_d19_orders.md"), "wb").write(out)
    txt = out.decode("utf-8", "replace")
    for ln in txt.splitlines():
        if ("BigMoney" in ln or "quant" in ln or "bm-b" in ln) and ln.strip().startswith(("-", "*", "|", ">", "#") or ln.strip()[:1].isdigit()):
            print("GORDER-LINE:", ln.strip()[:300])

shutil.rmtree(TMP, ignore_errors=True)

# ---------- 4) inbox visibility (S7 processing later) ----------
inbox_dir = os.path.join(RB, "fleet", "inbox")
msgs = []
if os.path.isdir(inbox_dir):
    for f in sorted(os.listdir(inbox_dir)):
        if f.lower().endswith(".md") or f.lower().endswith(".json"):
            msgs.append(f)
print("INBOX-UNPROCESSED n=%d %s" % (len(msgs), msgs))
