# -*- coding: utf-8 -*-
"""r685 bm-c: compute_audit.json merge FIX2 - correct latest selection (dict['latest'] not top-level)."""
import json, hashlib

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
def load(s):
    return json.load(open(r"%s\results\_r685bmc_ca_stage%d.json" % (REPO, s), encoding="utf-8"))
def h(e):
    return hashlib.md5(json.dumps(e, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()

b, o, t = load(1), load(2), load(3)
bh_set = set(h(e) for e in b["history"])
o_extra = [e for e in o["history"] if h(e) not in bh_set]
t_extra = [e for e in t["history"] if h(e) not in bh_set]
merged_hist = sorted(b["history"] + o_extra + t_extra, key=lambda e: e.get("ts", ""))

# latest newer-wins by ts (FIX: compare latest dicts directly)
cands = [(b["latest"].get("ts",""), "base", b["latest"]),
         (o["latest"].get("ts",""), "ours", o["latest"]),
         (t["latest"].get("ts",""), "theirs", t["latest"])]
ts_w, src_w, dict_w = max(cands, key=lambda x: x[0])
print("LATEST_WINNER src=%s ts=%s" % (src_w, ts_w))
print("LATEST_KEYS=%s" % sorted(dict_w.keys())[:6])

merged = {"latest": dict_w, "history": merged_hist}
raw = open(r"%s\results\compute_audit.json" % REPO, "rb").read()
crlf = raw.count(b"\r\n"); lf = raw.count(b"\n") - crlf
txt = json.dumps(merged, indent=1, ensure_ascii=False)
eol = "\r\n" if crlf > lf else "\n"
data = txt.replace("\n", eol).encode("utf-8")
open(r"%s\results\compute_audit.json" % REPO, "wb").write(data)

# full validation suite
m2 = json.load(open(r"%s\results\compute_audit.json" % REPO, encoding="utf-8"))
assert sorted(m2.keys()) == ["history", "latest"], "top keys"
assert isinstance(m2["latest"].get("ts"), str), "latest.ts must be str"
assert "latest" not in m2["latest"], "no nested latest"
assert "history" not in m2["latest"], "no nested history"
assert len(m2["history"]) == 209, "hist len"
seen = set()
for e in m2["history"]:
    k = h(e); assert k not in seen, "dup"; seen.add(k)
ts_list = [e.get("ts","") for e in m2["history"]]
assert ts_list == sorted(ts_list), "sorted"
# both machines' new entries present
tss = set(ts_list)
assert "2026-10-07 14:29:26" in tss, "ours extra present"
assert "2026-10-07 15:08:08" in tss, "theirs extra present"
print("VALIDATION_ALL_PASS bytes=%d latest_ts=%s hist=%d" % (len(data), m2["latest"]["ts"], len(m2["history"])))
