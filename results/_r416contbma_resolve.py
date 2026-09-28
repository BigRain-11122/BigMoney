"""r416-cont bm-a push-storm conflict resolver (bigmoney-conflict-resolve skill canon).

Rival window: bm-b dead-r412 closeout (a0dea7fdf 06:23:52) + bm-c r201 batch-87
lineage + autofill ticks (f452727d8/7510dab28). merge_lane_views resolve already
handled 7 ALL_FACES members; this script resolves the remainder:
  - snapshot deep-ts take-new (R208/R350 deep probe, staged blobs not worktree)
  - twin-regen-md coupling (json probe decides side; md copied byte-wise same side; r327/r329)
  - js-wrapper-snapshot side coupling with json winner (R209)
  - append-log multiset union ts-sorted (r188/r217 + batch-83 multiset law)
  - memory-union CODELY.md (base prefix + both suffixes; batch-number collision:
    bm-c r201 batch-87 first on origin -> mine renumbers to 88 per batch-71 law;
    duplicate 84/85/86 pointer face -> origin's richer pointer kept, mine dropped)
  - archive append union (base + origin section + mine section, zero-loss)
  - prep_state.json AA take stage2 (semantic diff = .generated ts only; runner
    byte-identical 159743B both sides = cross-machine determinism proven;
    bm-b landed first 06:23:52 + in-flight bm-b screen burn consumes that face)
"""
import json, re, subprocess, sys, collections

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def stage(n, path):
    r = subprocess.run(["git", "show", f":{n}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"stage read fail {n}:{path}: {r.stderr.decode()[:200]}")
    return r.stdout


def probe_ts(obj, best=None, path=""):
    """R350 deep probe: recursive, key-EXCLUDE forbidden, wall-clock needs time-of-day."""
    if best is None:
        best = [""]
    if isinstance(obj, dict):
        for k, v in obj.items():
            probe_ts(v, best, path + "." + str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            probe_ts(v, best, f"{path}[{i}]")
    elif isinstance(obj, str):
        m = re.match(r"^(20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})", obj)
        if m and obj > best[0]:
            best[0] = obj
    return best[0]


def take_new(path):
    b2, b3 = stage(2, path), stage(3, path)
    try:
        t2, t3 = probe_ts(json.loads(b2.decode("utf-8"))), probe_ts(json.loads(b3.decode("utf-8")))
    except Exception as e:
        print(f"  {path}: JSON parse issue ({e}); falling back to origin side")
        open(path, "wb").write(b2); return "origin(fallback)"
    win = "origin" if t2 >= t3 else "local"
    # same-second tie -> HEAD(=origin during rebase replay) per r140
    open(path, "wb").write(b2 if win == "origin" else b3)
    json.loads(open(path, "rb").read().decode("utf-8"))  # parse-verify written face
    print(f"  {path}: {win} (origin ts {t2!r} vs local ts {t3!r})")
    return win


def twin(pair_json, pair_md):
    b2j, b3j = stage(2, pair_json), stage(3, pair_json)
    t2, t3 = probe_ts(json.loads(b2j.decode("utf-8"))), probe_ts(json.loads(b3j.decode("utf-8")))
    win = "origin" if t2 >= t3 else "local"
    open(pair_json, "wb").write(b2j if win == "origin" else b3j)
    json.loads(open(pair_json, "rb").read().decode("utf-8"))
    open(pair_md, "wb").write(stage(2, pair_md) if win == "origin" else stage(3, pair_md))
    print(f"  twin {pair_json}+md: {win} (ts {t2!r} vs {t3!r})")
    return win


print("== snapshots deep-ts take-new ==")
snaps = [
    "results/fundamental_b_layer_filter.json",
    "results/daily_scorecard.json",
    "results/dashboard_status.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-28.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
]
dash_json_winner = None
for p in snaps:
    w = take_new(p)
    if p == "results/dashboard_status.json":
        dash_json_winner = w

print("== twins (json probe -> md byte-copy same side) ==")
twin("docs/daily_report/REPORT-2026-09-29.json", "docs/daily_report/REPORT-2026-09-29.md")
twin("docs/live_usage/LIVE-2026-09-29.json", "docs/live_usage/LIVE-2026-09-29.md")
twin("docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md")

print("== dashboard_status.js wrapper couples with json winner ==")
b = stage(2, "results/dashboard_status.js") if dash_json_winner == "origin" else stage(3, "results/dashboard_status.js")
open("results/dashboard_status.js", "wb").write(b)
print(f"  dashboard_status.js: {dash_json_winner} side bytes")

print("== x2_watch_log.jsonl multiset union (ts-sorted) ==")
b1 = stage(1, "results/x2_watch_log.jsonl").decode("utf-8").splitlines()
b2 = stage(2, "results/x2_watch_log.jsonl").decode("utf-8").splitlines()
b3 = stage(3, "results/x2_watch_log.jsonl").decode("utf-8").splitlines()
c = collections.Counter()
for src in (b2, b3):
    c.update(l for l in src if l.strip())
base_set = set(l for l in b1 if l.strip())
missing = [l for l in base_set if c[l] < 1]
assert not missing, f"base rows lost: {missing[:2]}"
rows = []
for l, n in c.items():
    rows.extend([l] * n)


def ts_of(l):
    m = re.search(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}", l)
    return m.group(0) if m else ""


rows.sort(key=ts_of)
open("results/x2_watch_log.jsonl", "w", encoding="utf-8", newline="\n").write("\n".join(rows) + "\n")
for l in rows[-2:]:
    json.loads(l)
print(f"  union rows={len(rows)} (origin {len([l for l in b2 if l.strip()])} + local {len([l for l in b3 if l.strip()])}, multiset preserved)")

print("== prep_state.json AA -> stage2 (bm-b first-landed; semantic diff = .generated only) ==")
open("results/trial_labor_w6/prep_state.json", "wb").write(stage(2, "results/trial_labor_w6/prep_state.json"))
json.loads(open("results/trial_labor_w6/prep_state.json", "rb").read().decode("utf-8"))
print("  stage2 written + parse-ok")

print("== CODELY.md memory-union (batch collision: mine 87->88) ==")
b2 = stage(2, "CODELY.md").decode("utf-8").splitlines()
b3 = stage(3, "CODELY.md").decode("utf-8").splitlines()
base = stage(1, "CODELY.md").decode("utf-8").splitlines()
# common prefix of both sides must cover the base head
n = 0
while n < len(b2) and n < len(b3) and n < len(base) and b2[n] == b3[n] == base[n]:
    n += 1
assert n >= len(base) - 3, f"prefix divergence too early at {n} (base {len(base)})"
suf2, suf3 = b2[n:], b3[n:]
assert any("坑律八十七批" in l for l in suf2), "origin batch-87 missing"
ptr2 = [l for l in suf2 if l.startswith("冷层指针")]
ptr3 = [l for l in suf3 if l.startswith("冷层指针")]
assert len(ptr2) == 1 and len(ptr3) == 1, "pointer face shape unexpected"
b87 = [l for l in suf2 if l.startswith("- [")][0]
mine_new = [l for l in suf3 if l.startswith("- [")][0]
assert "坑律八十七批" in mine_new
mine88 = mine_new.replace("坑律八十七批", "坑律八十八批", 1)
assert "坑律八十八批" in mine88
merged = b2[:n] + [ptr2[0], b87, mine88]
open("CODELY.md", "w", encoding="utf-8", newline="\n").write("\n".join(merged) + "\n")
import os
print(f"  prefix={n} + origin-pointer + origin-b87 + local-b88(renumbered); size={os.path.getsize('CODELY.md')}B")
print(f"  dropped: local pointer line (subsumed by origin richer pointer); logged in report addendum")

print("== archive 202609.md append union (base + origin section + local section) ==")
a2 = stage(2, "research/memory-archive/202609.md").decode("utf-8").splitlines()
a3 = stage(3, "research/memory-archive/202609.md").decode("utf-8").splitlines()
ab = stage(1, "research/memory-archive/202609.md").decode("utf-8").splitlines()
assert a2[:len(ab)] == ab and a3[:len(ab)] == ab, "archive base prefix drift"
merged = a2 + ["", "(bm-a r416-cont 同窗独立整编节·与上节同窗双机各自迁移实录·零丢失并集)",] + a3[len(ab):]
open("research/memory-archive/202609.md", "w", encoding="utf-8", newline="\n").write("\n".join(merged) + "\n")
print(f"  archive union lines={len(merged)} (origin {len(a2)} + local suffix {len(a3)-len(ab)})")

print("RESOLVER DONE")
