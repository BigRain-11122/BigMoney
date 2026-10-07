# -*- coding: utf-8 -*-
"""r685 bm-c: compute_audit.json rebase-conflict resolver (diff3 two-law merge).
latest -> newer-wins by ts; history -> append-only union (base prefix verify).
"""
import json, hashlib, sys, io

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

def load(s):
    return json.load(open(r"%s\results\_r685bmc_ca_stage%d.json" % (REPO, s), encoding="utf-8"))

b, o, t = load(1), load(2), load(3)

def h(e):
    return hashlib.md5(json.dumps(e, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()

bh, oh, th = [h(e) for e in b["history"]], [h(e) for e in o["history"]], [h(e) for e in t["history"]]

# 1) base-prefix verification (append-only assumption check)
prefix_ok = True
for i in range(len(bh)):
    if oh[i] != bh[i] or th[i] != bh[i]:
        prefix_ok = False
        print("PREFIX_MISMATCH_AT=%d" % i)
        break
print("BASE_PREFIX_OK=%s (base=%d ours=%d theirs=%d)" % (prefix_ok, len(bh), len(oh), len(th)))

# 2) extras
o_extra = [e for e, x in zip(o["history"], oh) if x not in set(bh)]
t_extra = [e for e, x in zip(t["history"], th) if x not in set(bh)]
print("OURS_EXTRA=%d THEIRS_EXTRA=%d" % (len(o_extra), len(t_extra)))

merged_hist = b["history"] + o_extra + t_extra
# stable sort by ts (append face is chronology-ordered)
merged_hist = sorted(merged_hist, key=lambda e: e.get("ts", ""))
# dup guard: same md5 consecutive = suspicious
seen = set(); dup = 0
for e in merged_hist:
    k = h(e)
    if k in seen: dup += 1
    seen.add(k)
print("MERGED_HIST=%d DUP=%d" % (len(merged_hist), dup))

# 3) latest newer-wins by ts
lt, lo = b["latest"].get("ts",""), o["latest"].get("ts","")
lts = t["latest"].get("ts","")
newer = max([(lt,b),(lo,o),(lts,t)], key=lambda x: x[0])[1]
print("LATEST_NEWER_WINS: base=%s ours=%s theirs=%s -> pick=%s" % (lt, lo, lts, newer.get("ts")))

merged = {"latest": newer, "history": merged_hist}

# 4) EOL + ascii-escape style detection from working tree raw bytes
raw = open(r"%s\results\compute_audit.json" % REPO, "rb").read()
crlf = raw.count(b"\r\n")
lf = raw.count(b"\n") - crlf
has_raw_cjk = any(ch > 127 for ch in raw[:60000])
print("EOL: crlf=%d lf=%d raw_cjk=%s" % (crlf, lf, has_raw_cjk))

txt = json.dumps(merged, indent=1, ensure_ascii=not has_raw_cjk)
eol = "\r\n" if crlf > lf else "\n"
data = txt.replace("\n", eol).encode("utf-8")
out = r"%s\results\compute_audit.json" % REPO
open(out, "wb").write(data)
print("WROTE bytes=%d" % len(data))

# 5) re-parse validation
json.load(open(out, encoding="utf-8"))
print("REPARSE_OK")
print("HIST_SORTED=%s" % all(merged_hist[i].get("ts","") <= merged_hist[i+1].get("ts","") for i in range(len(merged_hist)-1)))
