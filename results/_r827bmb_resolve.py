"""r827 bm-b rebase resolver: 15 UU faces vs bm-a r949 same-window push race.

Recipes per bigmoney-conflict-resolve SKILL + classify_conflicts.py:
- 12 snapshot faces: take-new by embedded ts (all verified: mine 09:39-09:41 >
  origin 09:27-09:33); md twins follow their json twin direction (regex
  cross-check when extractable).
- compute_audit.json (rolling-ledger r188/R208): history union by ts
  (same-ts content tie -> origin side, rebase HEAD r140 law), latest take-new.
- regime_state.json (rolling-ledger R208): history union by asof, transitions
  union by row identity, scalar state face take-new by 'updated'.
- state/queue/explore.md: row-level union -- E6 row from origin (r949 done),
  E7 row from mine (r827 done), both consumption records appended in event
  order (r949 then r827); LF-normalized write-back.
Every json json.loads-validated + union line-count assertions before write.
"""
import json
import re
import subprocess
import sys

def blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)],
                       capture_output=True)
    return r.stdout.decode("utf-8", errors="replace")

def stage_bytes(path):
    return subprocess.run(["git", "show", ":%d:%s" % (2, path)], capture_output=True).stdout

O, M = 2, 3  # rebase semantics: 2 = ours = origin/bm-a tip (HEAD), 3 = theirs = my commit
receipt = {"round": "r827", "faces": {}, "notes": []}

TS_KEYS = ["generated_at", "generated", "ts", "updated", "scanned_at", "time"]

def get_ts(j):
    for k in TS_KEYS:
        if isinstance(j, dict) and isinstance(j.get(k), str):
            return k, j[k]
    return None, None

def md_ts(text):
    m = re.findall(r"20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}", text)
    return m[0] if m else None

SNAPSHOTS = [
    "docs/daily_report/REPORT-2026-10-10.json",
    "docs/daily_report/REPORT-2026-10-10.md",
    "docs/live_usage/LIVE-2026-10-10.json",
    "docs/live_usage/LIVE-2026-10-10.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/token_usage.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/update_status.json",
    "results/fundamental_b_layer_filter.json",
]

# 1) snapshots: take-new (mine), ts-asserted
for p in SNAPSHOTS:
    bo, bm = blob(O, p), blob(M, p)
    if p.endswith(".json"):
        jo, jm = json.loads(bo), json.loads(bm)
        ko, to = get_ts(jo)
        km, tm = get_ts(jm)
        assert tm and to and tm >= to, (p, to, tm)
        chosen, side = bm, "mine"
        receipt["faces"][p] = {"recipe": "snapshot-take-new", "ts_o": to, "ts_m": tm, "took": side}
        json.loads(chosen)  # parse-validate
    else:
        to, tm = md_ts(bo), md_ts(bm)
        assert tm and to and tm >= to, (p, to, tm)
        receipt["faces"][p] = {"recipe": "snapshot-take-new(md)", "ts_o": to, "ts_m": tm, "took": "mine"}
        chosen = bm
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(chosen)

# 2) compute_audit.json: history union by ts + latest take-new
p = "results/compute_audit.json"
jo, jm = json.loads(blob(O, p)), json.loads(blob(M, p))
ho = {r["ts"]: r for r in jo["history"]}
hm = {r["ts"]: r for r in jm["history"]}
union = dict(ho)
for ts, row in hm.items():
    if ts in union:
        if json.dumps(union[ts], sort_keys=True) != json.dumps(row, sort_keys=True):
            union[ts] = ho[ts]  # same-ts content tie -> origin (r140)
            receipt["notes"].append("compute_audit same-ts tie kept origin @%s" % ts)
    else:
        union[ts] = row
history = sorted(union.values(), key=lambda r: r["ts"])
lo, lm = jo["latest"], jm["latest"]
latest = lm if lm["ts"] >= lo["ts"] else lo
assert len(history) == len(set(list(ho) + list(hm))), "union count != |A u B|"
assert len(history) >= max(len(ho), len(hm)), "union shrink"
out = {"latest": latest, "history": history}
json.loads(json.dumps(out))
with open(p, "w", encoding="utf-8", newline="\n") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
receipt["faces"][p] = {"recipe": "ledger-union", "hist_o": len(ho), "hist_m": len(hm),
                       "hist_union": len(history), "latest_took": "mine" if latest is lm else "origin"}

# 3) regime_state.json: history union by asof + transitions union + scalars take-new
p = "results/regime_state.json"
jo, jm = json.loads(blob(O, p)), json.loads(blob(M, p))
uo = {r.get("asof"): r for r in jo.get("history", [])}
um = {r.get("asof"): r for r in jm.get("history", [])}
u = dict(uo)
for a, row in um.items():
    if a in u and json.dumps(u[a], sort_keys=True) != json.dumps(row, sort_keys=True):
        receipt["notes"].append("regime_state same-asof divergence kept origin @%s" % a)
    else:
        u[a] = row
history = sorted(u.values(), key=lambda r: str(r.get("asof")))
to_l = jo.get("transitions", [])
tm_l = jm.get("transitions", [])
seen = {json.dumps(x, sort_keys=True) for x in to_l}
trans = list(to_l) + [x for x in tm_l if json.dumps(x, sort_keys=True) not in seen and not seen.add(json.dumps(x, sort_keys=True))]
base = jm if jm["updated"] >= jo["updated"] else jo
out = dict(base)
out["history"] = history
out["transitions"] = trans
json.loads(json.dumps(out))
with open(p, "w", encoding="utf-8", newline="\n") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
receipt["faces"][p] = {"recipe": "ledger-union+state-take-new",
                       "hist_union": len(history), "trans_union": len(trans),
                       "scalars_took": "mine" if base is jm else "origin"}

# 4) explore.md: row-level union
# NOTE (heal): origin side carries a DEFECT -- E6 row duplicated (stale 'open'
# line 11 + r949-done line 12, bm-a's edit inserted without replacing). Heal per
# one-row-per-item queue law: keep the r949 done row, drop the stale open row.
# bm-a's done content + consumption record preserved verbatim (zero loss of
# their work; only the stale duplicate is dropped). Logged in receipt.
p = "state/queue/explore.md"
o_txt, m_txt = blob(O, p), blob(M, p)
o_lines = o_txt.split("\n")
m_lines = [l.rstrip("\r") for l in m_txt.split("\n")]
e6_o_all = [l for l in o_lines if l.startswith("| E6 ")]
e6_o = [l for l in e6_o_all if "r949" in l]
assert len(e6_o) == 1, ("origin E6 done row not unique", len(e6_o))
stale_e6 = [l for l in e6_o_all if "r949" not in l]
receipt["notes"].append("explore.md HEAL: dropped %d stale duplicate E6 open row(s) from origin side "
                        "(kept r949 done row verbatim)" % len(stale_e6))
e7_m = [l for l in m_lines if l.startswith("| E7 ")]
assert len(e7_m) == 1, (len(e7_m))
assert "r827" in e7_m[0], "mine E7 row lacks r827 marker"
rec_m = [l for l in m_lines if l.startswith("> r827 ")]
assert len(rec_m) == 1
out_lines = []
for l in o_lines:
    ls = l.rstrip("\r")
    if ls in stale_e6:
        continue  # heal: skip stale duplicate
    if ls.startswith("| E7 "):
        out_lines.append(e7_m[0])
    else:
        out_lines.append(ls)
if out_lines and out_lines[-1] == "":
    out_lines.pop()
out_lines.append(rec_m[0])
union_txt = "\n".join(out_lines) + "\n"
assert union_txt.count("| E6 |") == 1 and union_txt.count("| E7 |") == 1
assert "r949" in union_txt and "r827" in union_txt
assert union_txt.count("> r949 ") == 1 and union_txt.count("> r827 ") == 1
with open(p, "w", encoding="utf-8", newline="\n") as f:
    f.write(union_txt)
receipt["faces"][p] = {"recipe": "row-union(E6<-origin done row, stale dup healed, E7<-mine, both records)",
                      "e6_side": "origin", "e7_side": "mine", "stale_dup_dropped": len(stale_e6)}

import io
with io.open("results/_r827bmb_resolve_receipt.json", "w", encoding="utf-8") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("resolver done:", len(receipt["faces"]), "faces;", receipt["notes"] or "no tie notes")
