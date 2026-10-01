# -*- coding: utf-8 -*-
# _r320bmc_s05_scan.py -- S0.5: orders diff-scan + D-19 decisions watermark + inbox unread (bm-c)
import subprocess, json, os, glob, hashlib, re

R = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
FG = r"K:\Fluxgroup\FluxGroup"
CRE = 8

def git(*a, cwd=R, check=True):
    p = subprocess.run(["git", "-C", cwd] + list(a), capture_output=True, creationflags=CRE)
    if check and p.returncode != 0:
        raise RuntimeError("git %s rc=%s: %s" % (" ".join(a), p.returncode, p.stderr.decode("utf-8", "replace")))
    return p.stdout

# --- 1) orders diff-scan (R13: full scan, no timestamp filter) ---
ack = set(json.load(open(R + r"\fleet\machines\bm-c.json", encoding="utf-8")).get("orders_ack", []))
orders = sorted(os.path.basename(p) for p in glob.glob(R + r"\fleet\orders\*.md"))
unacked = [o for o in orders if o not in ack]
print("ORDERS total=%d acked=%d unacked=%d" % (len(orders), len(ack & set(orders)), len(unacked)))
for o in unacked:
    print("--- UNACKED ORDER: %s ---" % o)
    txt = open(R + r"\fleet\orders" + os.sep + o, encoding="utf-8", errors="replace").read()
    print(txt[:1600])

# --- 2) D-19 decisions watermark (r292 raw-bytes law, r503 case-normalize) ---
subprocess.check_call(["git", "-C", FG, "fetch", "origin"], creationflags=CRE)
dec = subprocess.check_output(["git", "-C", FG, "show", "origin/main:docs/decisions.md"], creationflags=CRE)
sha = hashlib.sha256(dec).hexdigest().upper()
st = json.load(open(R + r"\state-bm-c.json", encoding="utf-8"))
prev = str(st.get("last_decisions_sha", "")).upper()
print("D-19 sha=%s prev=%s %s" % (sha[:16], prev[:16], "MATCH-unchanged" if sha == prev else "CHANGED"))
if sha != prev:
    txt = dec.decode("utf-8", errors="replace")
    lines = txt.splitlines()
    for i, ln in enumerate(lines):
        low = ln.lower()
        if ("bigmoney" in low or "quant" in low or "bm-c" in low or "bm_c" in low) and ln.strip().startswith(("-", "|", "*", "·")):
            print("DECISION-HIT L%d: %s" % (i + 1, ln.strip()[:240]))
    tail = [l for l in lines if l.strip()][-25:]
    print("--- decisions.md tail 25 ---")
    print("\n".join(tail))
    od = subprocess.run(["git", "-C", FG, "show", "origin/main:docs/orders.md"], capture_output=True, creationflags=CRE).stdout
    ot = od.decode("utf-8", errors="replace")
    m = re.search(r"(CEO[^\n]*物理件|物理件区)", ot)
    seg = ot[max(0, (m.start() if m else 0) - 200): (m.start() if m else 0) + 2200] if m else "(no physical-items section marker)"
    print("--- orders.md physical-items window ---")
    print(seg)

# --- 3) inbox unread for bm-c / ALL ---
proc = set(os.path.basename(p) for p in glob.glob(R + r"\fleet\inbox\processed\*"))
inbox = sorted(os.path.basename(p) for p in glob.glob(R + r"\fleet\inbox\*.md"))
unread = [m for m in inbox if m not in proc and ("bm-c" in m or "-all" in m.lower() or "ALL" in m)]
print("INBOX unread-for-bm-c=%d %s" % (len(unread), unread[:10]))
for m in unread[:6]:
    print("--- MSG: %s ---" % m)
    print(open(R + r"\fleet\inbox" + os.sep + m, encoding="utf-8", errors="replace").read()[:900])
