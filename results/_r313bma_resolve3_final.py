# -*- coding: utf-8 -*-
"""R313 resolver round 2 final: autofill_state union (r203/R208/r140/r245 laws) + token_usage take-new."""
import json, subprocess

def blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True)
    return r.stdout

# token_usage.json: take-new-theirs byte copy
b = blob(3, "results/token_usage.json")
json.loads(b.decode("utf-8"))
with open("results/token_usage.json", "wb") as f:
    f.write(b)
print("token_usage take-new-theirs (%dB, generated 10:40:20 > 10:36:36)" % len(b))

# autofill_state.json: mixed-dict+ledger union
pa = "results/autofill_state.json"
ba, bb = blob(2, pa), blob(3, pa)
da, db = json.loads(ba.decode("utf-8")), json.loads(bb.decode("utf-8"))
la, lb = da["launches"], db["launches"]
seen, union = set(), []
for row in la + lb:
    k = json.dumps(row, sort_keys=True, ensure_ascii=False)
    if k not in seen:
        seen.add(k)
        union.append(row)
union.sort(key=lambda r: r["ts"], reverse=True)   # newest first
union = union[:50]                                  # cap 50 = keep newest 50
union.sort(key=lambda r: r["ts"])                   # r245: write back in ts ASC (producer append order)
lt_a, lt_b = da["last_tick"], db["last_tick"]
assert isinstance(lt_a, dict) and isinstance(lt_b, dict)
last_tick = lt_a if lt_a.get("ts", "") >= lt_b.get("ts", "") else lt_b  # r140: tie -> ours(HEAD)
assert isinstance(last_tick, dict)
out = {"launches": union, "last_tick": last_tick}
nl = "\r\n" if b"\r\n" in ba[:1500] else "\n"
text = json.dumps(out, ensure_ascii=False, indent=1)
with open(pa, "w", encoding="utf-8", newline="") as f:  # newline='' + explicit \r\n = CRLF mirror
    f.write(text.replace("\n", nl))
# verify written bytes parse
with open(pa, "rb") as f:
    chk = json.loads(f.read().decode("utf-8"))
assert isinstance(chk["last_tick"], dict) and len(chk["launches"]) <= 50
ts_list = [r["ts"] for r in chk["launches"]]
assert ts_list == sorted(ts_list), "launches must be ts-ascending after write"
print("autofill_state union: %d+%d -> %d unique -> cap50 kept %d; last_tick ts=%s (side=%s)" % (
    len(la), len(lb), len(seen), len(union), last_tick["ts"], "ours" if last_tick is lt_a else "theirs"))

for p in [pa, "results/token_usage.json"]:
    r = subprocess.run(["git", "add", p], capture_output=True)
    print("add %s rc=%d" % (p, r.returncode))
print("ROUND2 RESOLVED")
