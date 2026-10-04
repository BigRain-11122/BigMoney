"""r681 bm-a S0.5 probe: orders diff (double-scan) + D-19 decisions watermark (per-key caliber).
All output to UTF-8 file, zero console CJK (pit-encoding)."""
import json, subprocess, hashlib, sys, os, datetime

OUT = []

def log(s):
    OUT.append(s)

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"

def git(args, cwd=REPO):
    r = subprocess.run(["git"] + args, cwd=cwd, capture_output=True)
    return r.returncode, r.stdout, r.stderr

# ---------- 1. orders diff (same-caliber both sides: full filenames with .md) ----------
rc, so, se = git(["ls-tree", "--name-only", "origin/main", "fleet/orders/"])
# same-caliber both sides: basename form (r477 law)
orders_remote = set(os.path.basename(x.strip()) for x in so.decode("utf-8", "replace").splitlines() if x.strip().endswith(".md"))
orders_remote.discard("README.md")
try:
    with open(os.path.join(REPO, "fleet", "machines", "bm-a.json"), "rb") as f:
        hb = json.loads(f.read().decode("utf-8", "replace"))
    ack = set(hb.get("orders_ack", []))
except Exception as e:
    ack = set()
    log("HEARTBEAT_READ_ERR " + repr(e))
unacked = sorted(orders_remote - ack)
extra = sorted(ack - orders_remote)
log("ORDERS_REMOTE=%d ACK=%d UNACKED=%d" % (len(orders_remote), len(ack), len(unacked)))
for u in unacked:
    log("  UNACKED: " + u)
log("ACK_EXTRA(sample, harmless): " + ",".join(extra[:3]) + ("..." if len(extra) > 3 else ""))

# ---------- 2. D-19 decisions watermark (group tree: origin/main raw bytes sha256) ----------
GROUP_CANDIDATES = [r"K:\Fluxgroup\FluxGroup", r"C:\Users\sjs20\Desktop\FluxGroup"]
grp = None
for c in GROUP_CANDIDATES:
    if os.path.isdir(c) and os.path.isdir(os.path.join(c, ".git")):
        grp = c
        break
log("GROUP_TREE=" + str(grp))
if grp:
    rc1, _, _ = git(["fetch", "origin"], cwd=grp)
    rc2, dec, ede = git(["show", "origin/main:docs/decisions.md"], cwd=grp)
    rc3, ords, eords = git(["show", "origin/main:docs/orders.md"], cwd=grp)
    if rc2 == 0:
        dec_sha = hashlib.sha256(dec).hexdigest()
        log("DECISIONS_SHA256=" + dec_sha)
        with open(os.path.join(REPO, "state-bm-a.json"), "rb") as f:
            st = json.loads(f.read().decode("utf-8", "replace"))
        prev = st.get("last_decisions_sha", "")
        log("STATE_SHA256=" + prev)
        log("MATCH" if prev == dec_sha else "CHANGED")
        if prev != dec_sha:
            dec_txt = dec.decode("utf-8", "replace")
            lines = dec_txt.splitlines()
            log("DEC_LINES_TOTAL=%d" % len(lines))
            # tail 80 lines for consumption scan (BigMoney-relevant rows)
            for ln in lines[-80:]:
                if any(k in ln for k in ["BigMoney", "bigmoney", "quant", "bm-a", "bm-a", "BigMoney"]):
                    log("  DEC_ROW: " + ln[:200])
        # CEO pending physical-orders section: rows mentioning BigMoney/quant
        if rc3 == 0:
            ords_txt = ords.decode("utf-8", "replace")
            for ln in ords_txt.splitlines():
                if any(k in ln for k in ["BigMoney", "bigmoney", "quant"]):
                    log("  CEO_ORDERS_ROW: " + ln[:200])
    else:
        log("DECISIONS_SHOW_ERR " + ede.decode("utf-8", "replace")[:200])
else:
    log("GROUP_TREE_ABSENT_FALLBACK_SPARSE_CLONE")

with open(os.path.join(REPO, "results", "_r681bma_s05_probe.txt"), "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(OUT))
print("PROBE_DONE lines=%d" % len(OUT))
