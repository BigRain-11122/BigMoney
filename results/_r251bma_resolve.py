# r251 bm-a rebase-replay UU resolver (13th family run) -- classifier-informed
# recipes; :2 = origin/bm-b side, :3 = bm-a (replayed commit) side.
# r242 law: ts keys PROBED from both blobs (ts/updated/generated/as_of/
# last_attempt families), real values only, NO None-tie default -> UNKNOWN
# manual verdict instead. r245 law: launches cap kept ts-ASCENDING on
# write-back. Zero-loss unions; parse-verify before add (r185).
import json
import subprocess

def blob(side, path):
    r = subprocess.run(["git", "show", f":{side}:{path}"], capture_output=True)
    return r.stdout

def jload(b):
    return json.loads(b.decode("utf-8-sig"))

def probe_ts(d):
    for k in ("ts", "updated", "updated_at", "generated", "generated_at",
              "as_of", "last_attempt", "status_ts", "written_at"):
        v = d.get(k)
        if isinstance(v, str) and v:
            return k, v
    return None, None

resolved, unknown = [], []

def take_new_json(path, extra_union_keys=()):
    b2, b3 = blob(2, path), blob(3, path)
    d2, d3 = jload(b2), jload(b3)
    k2, v2 = probe_ts(d2)
    k3, v3 = probe_ts(d3)
    if v2 is None and v3 is None:
        unknown.append(path)
        return
    winner = 3 if (v3 or "") >= (v2 or "") else 2
    out = dict(d3) if winner == 3 else dict(d2)
    for key in extra_union_keys:                       # zero-loss union legs
        if isinstance(d2.get(key), list) and isinstance(d3.get(key), list):
            seen, merged = set(), []
            for row in d2[key] + d3[key]:
                sig = json.dumps(row, sort_keys=True, ensure_ascii=False)
                if sig not in seen:
                    seen.add(sig)
                    merged.append(row)
            out[key] = sorted(merged, key=lambda r: str(r.get("ts", "")))
    data = json.dumps(out, ensure_ascii=False, indent=1)
    json.loads(data)
    open(path, "w", encoding="utf-8", newline="\n").write(data + "\n")
    resolved.append((path, f"take-:{winner} by {k2 or k3} {v2} vs {v3}"))

# ---- snapshots (probe-derived take-new)
for p in ("results/dashboard_status.json",
          "results/fundamental_b_layer_filter.json",
          "results/futures_update_status.json",
          "results/heat_update_status.json",
          "results/lhb_update_status.json",
          "results/token_usage.json",
          "results/update_status.json",
          "results/prospect_promotion/_summary.json"):
    take_new_json(p)

# ---- rolling ledgers: union + take-new state fields
take_new_json("results/compute_audit.json", extra_union_keys=("history",))
take_new_json("results/regime_state.json",
              extra_union_keys=("history", "transitions"))

# ---- daily report pair (r242 precedent: json twin generated_at anchor,
#      md twin same side whole bytes)
j2, j3 = jload(blob(2, "docs/daily_report/REPORT-2026-09-26.json")), \
         jload(blob(3, "docs/daily_report/REPORT-2026-09-26.json"))
g2, g3 = probe_ts(j2), probe_ts(j3)
side = 3 if (g3[1] or "") >= (g2[1] or "") else 2
open("docs/daily_report/REPORT-2026-09-26.json", "wb").write(
    blob(side, "docs/daily_report/REPORT-2026-09-26.json"))
open("docs/daily_report/REPORT-2026-09-26.md", "wb").write(
    blob(side, "docs/daily_report/REPORT-2026-09-26.md"))
json.loads(open("docs/daily_report/REPORT-2026-09-26.json",
                encoding="utf-8-sig").read())
resolved.append(("docs/daily_report/REPORT-2026-09-26.{json,md}",
                 f"take-:{side} by {g2[0] or g3[0]} {g2[1]} vs {g3[1]}"))

# ---- dashboard_status.js (js-wrapper-snapshot): json twin generated_at
#      anchor above picks the side; re-emit whole bytes of that side
open("results/dashboard_status.js", "wb").write(
    blob(side, "results/dashboard_status.js"))
assert b"window.DASH_DATA" in open("results/dashboard_status.js", "rb").read()
resolved.append(("results/dashboard_status.js",
                 f"take-:{side} whole bytes (json-twin anchored, wrapper "
                 "preserved)"))

# ---- CODELY.md line union (memory-union)
l2 = blob(2, "CODELY.md").decode("utf-8").splitlines()
l3 = blob(3, "CODELY.md").decode("utf-8").splitlines()
seen, merged = set(), []
for ln in l2 + l3:
    s = ln.strip()
    if s and s in seen:
        continue
    if s:
        seen.add(s)
    merged.append(ln)
open("CODELY.md", "w", encoding="utf-8", newline="\n").write(
    "\n".join(merged) + "\n")
resolved.append(("CODELY.md", f"line union {len(l2)}+{len(l3)} -> "
               f"{len(merged)}"))

# ---- autofill_state.json (auto-merged M by git; verify launches order law)
af = json.loads(open("results/autofill_state.json", encoding="utf-8-sig").read())
ls = af.get("launches", [])
assert all(ls[i]["ts"] <= ls[i + 1]["ts"] for i in range(len(ls) - 1)), \
    "launches must be ts-ascending (r245 law)"
assert isinstance(af.get("last_tick"), dict), "last_tick must stay dict"
resolved.append(("results/autofill_state.json (verify-only)",
                 f"launches ts-ascending {len(ls)} OK, last_tick dict OK"))

# ---- runnable_pool.json (auto-merged): my entries intact post-replay
pool = json.loads(open("results/runnable_pool.json",
                       encoding="utf-8-sig").read())
ids = {e["id"] for e in pool["entries"]}
assert "CN-DIV-LOWVOL-ROT-P1" in ids and "T80-AGGR-FULLPOOL-BATTERY" in ids
resolved.append(("results/runnable_pool.json (verify-only)",
                 f"{len(ids)} entries, both ready lanes intact"))

print(json.dumps({"resolved": resolved, "unknown": unknown},
                 ensure_ascii=False, indent=1))
assert not unknown, "UNKNOWN leftovers must be resolved by hand"
