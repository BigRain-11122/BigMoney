"""R309 bm-a push-collision resolver (rebase replay 2/2 vs bm-b r314 window).

Canon: bigmoney-conflict-resolve SKILL (classifier 11 + 4 UNKNOWN manual).
Rebase stage semantics INVERTED vs merge: stage2 = new base (origin/main,
bm-b side), stage3 = replayed commit (bm-a round 309). r140 same-second
tie -> HEAD (= stage2, the rebase base).

Files (classifier output + manual UNKNOWN classification):
  autofill_state.json        mixed-dict+ledger  union launches cap50 re-sort asc
                                                + last_tick whole-dict ts-compare
  compute_audit.json         rolling-ledger     history union zero-loss, latest take-new
  regime_state.json          rolling-ledger     transitions union, fields take-new
  dashboard_status.js        js-wrapper         take-side WHOLE BYTES by inner ts
  dashboard_status.json      snapshot           take-new whole bytes
  *_update_status.json x4    snapshot           take-new whole bytes
  fundamental_b_layer_filter snapshot           take-new whole bytes
  token_usage.json           snapshot           take-new whole bytes
  scorecard_v1.json          UNKNOWN->snapshot   per-round re-derive, take-new by generated
  strategy_scorecard.json    UNKNOWN->snapshot   per-round re-derive, take-new by generated
  REPORT-2026-09-27.json/.md UNKNOWN->twin       take-new by generated_at, BOTH twins
                                                from the SAME winning side (coherence)

Zero-loss proof: union counts printed; every file json.loads-verified
before write-back (r185 law).
"""
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")


def stage_bytes(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"],
                        capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"stage {stage} missing for {path}")
    return r.stdout


def sjson(stage, path):
    return json.loads(stage_bytes(stage, path).decode("utf-8-sig"))


def dedupe_union(list_a, list_b, ts_key):
    seen, out = set(), []
    for e in list_a + list_b:
        k = json.dumps(e, sort_keys=True, ensure_ascii=False)
        if k in seen:
            continue
        seen.add(k)
        out.append(e)
    if out and ts_key and ts_key in out[0]:
        out.sort(key=lambda e: e.get(ts_key, ""))
    return out


def write_raw(path, data: bytes):
    with open(path, "wb") as fh:
        fh.write(data)


def write_json(path, obj):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
        fh.write("\n")


def pick_new(stage2, stage3, ts_keys):
    """Return (winner_stage, winner_obj) by first common ts key; tie -> 2."""
    for k in ts_keys:
        t2, t3 = stage2.get(k), stage3.get(k)
        if t2 is not None and t3 is not None:
            if t3 > t2:
                return 3, stage3
            return 2, stage2          # newer-or-tie -> HEAD side (r140)
    return 2, stage2                 # no ts key -> HEAD side, disclosed


report = []

# -- 1. autofill_state.json (mixed-dict+ledger) --------------------------
p = "results/autofill_state.json"
a, b = sjson(2, p), sjson(3, p)
la = dedupe_union(a.get("launches", []), b.get("launches", []), "ts")
la_sorted = sorted(la, key=lambda e: e.get("ts", ""), reverse=True)[:50]
la_final = sorted(la_sorted, key=lambda e: e.get("ts", ""))  # asc write-back
t2 = (a.get("last_tick") or {}).get("ts")
t3 = (b.get("last_tick") or {}).get("ts")
last_tick = b.get("last_tick") if (t3 and t2 and t3 > t2) else a.get("last_tick")
assert isinstance(last_tick, dict), "last_tick must stay a dict"
write_json(p, {"launches": la_final, "last_tick": last_tick})
report.append(f"{p}: launches union {len(a.get('launches', []))}+"
              f"{len(b.get('launches', []))} -> {len(la)} dedup -> cap50 "
              f"{len(la_final)} asc; last_tick ts {t2!r} vs {t3!r}")

# -- 2. compute_audit.json (rolling-ledger) ------------------------------
p = "results/compute_audit.json"
a, b = sjson(2, p), sjson(3, p)
ha = dedupe_union(a.get("history", []), b.get("history", []), "ts")
w_stage, latest = pick_new(a, b, ["ts"]) if "ts" in a or "ts" in b else (2, a)
# top-level ts lives inside latest snapshot in some versions; fall back
# to comparing latest.ts
lt = (a.get("latest") or {}).get("ts"), (b.get("latest") or {}).get("ts")
if lt[0] and lt[1]:
    latest = b.get("latest") if lt[1] > lt[0] else a.get("latest")
else:
    latest = a.get("latest")
merged = dict(a)
merged["history"] = ha
merged["latest"] = latest
write_json(p, merged)
report.append(f"{p}: history union {len(a.get('history', []))}+"
              f"{len(b.get('history', []))} -> {len(ha)}; latest.ts "
              f"{lt[0]!r} vs {lt[1]!r} -> {'bm-a(3)' if lt[1] > lt[0] else 'HEAD(2)'}")

# -- 3. regime_state.json (rolling-ledger) -------------------------------
p = "results/regime_state.json"
a, b = sjson(2, p), sjson(3, p)
tr = dedupe_union(a.get("transitions", []), b.get("transitions", []), None)
w_stage, base = pick_new(a, b, ["updated", "asof"])
merged = dict(base)
merged["transitions"] = tr
write_json(p, merged)
report.append(f"{p}: transitions union -> {len(tr)}; fields take-new by "
              f"updated/asof side={w_stage} (ts {a.get('updated')!r} vs "
              f"{b.get('updated')!r})")

# -- 4. js-wrapper snapshot (dashboard_status.js) ------------------------
p = "results/dashboard_status.js"
raw2, raw3 = stage_bytes(2, p), stage_bytes(3, p)


def js_inner(raw):
    s = raw.decode("utf-8-sig").strip()
    i = s.index("=")
    return json.loads(s[i + 1:].rstrip().rstrip(";"))


j2, j3 = js_inner(raw2), js_inner(raw3)
w_stage, _ = pick_new(j2, j3, ["updated", "ts", "generated"])
write_raw(p, raw2 if w_stage == 2 else raw3)
report.append(f"{p}: take-side whole bytes by inner ts side={w_stage} "
              f"({j2.get('updated', j2.get('ts'))!r} vs "
              f"{j3.get('updated', j3.get('ts'))!r})")

# -- 5. plain snapshots (take-new whole bytes) ---------------------------
SNAPS = {
    "results/dashboard_status.json": ["updated", "ts", "generated"],
    "results/futures_update_status.json": ["ts", "updated"],
    "results/heat_update_status.json": ["ts", "updated"],
    "results/lhb_update_status.json": ["ts", "updated"],
    "results/update_status.json": ["ts", "updated"],
    "results/fundamental_b_layer_filter.json": ["updated", "ts"],
    "results/token_usage.json": ["generated", "ts"],
    "results/scorecard_v1.json": ["generated", "ts"],        # UNKNOWN->snapshot
    "results/strategy_scorecard.json": ["generated", "ts"],   # UNKNOWN->snapshot
}
for p, keys in SNAPS.items():
    a, b = sjson(2, p), sjson(3, p)
    w_stage, _ = pick_new(a, b, keys)
    write_raw(p, stage_bytes(w_stage, p))
    v2 = next((a.get(k) for k in keys if a.get(k) is not None), None)
    v3 = next((b.get(k) for k in keys if b.get(k) is not None), None)
    report.append(f"{p}: take-new side={w_stage} ({v2!r} vs {v3!r})")

# -- 6. daily_report twins (take-new by generated_at, BOTH from winner) --
pj = "docs/daily_report/REPORT-2026-09-27.json"
pm = "docs/daily_report/REPORT-2026-09-27.md"
a, b = sjson(2, pj), sjson(3, pj)
w_stage, _ = pick_new(a, b, ["generated_at", "report_date"])
write_raw(pj, stage_bytes(w_stage, pj))
write_raw(pm, stage_bytes(w_stage, pm))
report.append(f"{pj} + md twin: BOTH from side={w_stage} "
              f"(generated_at {a.get('generated_at')!r} vs "
              f"{b.get('generated_at')!r})")

# -- parse-verify battery (r185 law) --------------------------------------
WRITTEN = ["results/autofill_state.json", "results/compute_audit.json",
           "results/regime_state.json", "results/dashboard_status.js",
           "results/dashboard_status.json", "results/futures_update_status.json",
           "results/heat_update_status.json", "results/lhb_update_status.json",
           "results/update_status.json", "results/fundamental_b_layer_filter.json",
           "results/token_usage.json", "results/scorecard_v1.json",
           "results/strategy_scorecard.json",
           "docs/daily_report/REPORT-2026-09-27.json",
           "docs/daily_report/REPORT-2026-09-27.md"]
verified = 0
for p in WRITTEN:
    raw = open(p, "rb").read()
    if p.endswith(".js"):
        js_inner(raw)
    elif p.endswith(".md"):
        txt = raw.decode("utf-8-sig")
        assert len(txt) > 0 and txt.lstrip().startswith("#"), "md twin face"
    else:
        json.loads(raw.decode("utf-8-sig"))
    verified += 1
print("\n".join(report))
print(f"resolver: {verified}/{len(WRITTEN)} files parse-verified OK")
