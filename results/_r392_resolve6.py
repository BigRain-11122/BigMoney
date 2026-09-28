"""r393 resolve #6: second-rebase stop #4 (commit e21cb5e7, my round-392) -- 10 files.

Skill: bigmoney-conflict-resolve (recipes r188/R208/R209/R216/r312 + manual
UNKNOWN classed per SKILL.md). Stage semantics: :2:=ours=upstream(origin),
:3:=theirs=my round-392 commit.
  PREREG_TEMPLATE.md   same-law double-draft (O-1712 G-ANCHOR-FACE): keep
                       mine (2-bullet form, includes 面错配-非数据腐坏
                       diagnostic + frozen-file-fix clause) and fold
                       origin's concrete example into bullet 1 -- zero loss.
  T-109 ticket         CLAIM COLLISION: bm-a claimed 17:10 (earlier, origin
                       side) vs bm-b 17:16:30 (later, mine) -> per fleet
                       README claim protocol (commit-time order, later
                       yields): bm-a keeps claim; my progress_r392_bmb note
                       kept verbatim as handoff + yield_r393_bmb annotation.
  market_clock twins   same-day idempotent regen -> take-new by probe, .md
                       follows its json twin side.
  compute_audit.json   rolling-ledger union + latest take-new (r188/R208).
  regime_state.json    history/transitions union + state take-new (R208).
  scorecard_v1/strategy_scorecard/token_usage/update_status
                       snapshot take-new (R208/R216).
"""
import json
import re
import subprocess


def blob_bytes(stage, path):
    return subprocess.run(["git", "show", f":{stage}:{path}"],
                          capture_output=True).stdout


def blob_json(stage, path):
    return json.loads(blob_bytes(stage, path))


TS_SHAPE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")


def wallclock_max(obj, best=""):
    if isinstance(obj, dict):
        for v in obj.values():
            best = wallclock_max(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = wallclock_max(v, best)
    elif isinstance(obj, str) and TS_SHAPE.match(obj):
        best = max(best, obj)
    return best


# ---- 1. PREREG_TEMPLATE.md: mine + origin example into bullet 1 -----------
P = "research/PREREG_TEMPLATE.md"
ours, mine = blob_bytes(2, P), blob_bytes(3, P)
m = re.search(r"（示例：`[^`]*`）", ours.decode("utf-8"))
assert m, "origin example span not found"
example = m.group(0)
mtxt = mine.decode("utf-8")
assert mtxt.count("数据锚面定义四元组") == 1, "bullet-1 not unique in mine"
assert "探针-锚同面断言" in mtxt, "bullet-2 missing in mine"
merged = mtxt.replace(
    "④预热窗；**无",
    "④预热窗" + example + "；**无", 1)
assert merged != mtxt and merged.count(example) == 1, "example fold-in failed"
open(P, "w", encoding="utf-8", newline="").write(merged)
print(f"PREREG_TEMPLATE: mine({len(mine)}B) + origin example "
      f"({len(example)} chars) -> {len(merged.encode('utf-8'))}B")

# ---- 2. T-109 ticket: earlier claim (bm-a) wins, later (bm-b) yields -------
P = "fleet/tasks/T-2026-09-28-109-P0.json"
A, B = blob_json(2, P), blob_json(3, P)
assert A["status"] == "claimed" and "bm-a" in A.get("claimed_by", ""), \
    "origin side is not bm-a's claim"
assert B["status"] == "claimed" and "bm-b" in B.get("claimed_by", ""), \
    "mine is not bm-b's claim"
assert (A.get("claimed_at") or "") <= (B.get("claimed_at") or ""), \
    "claim-time order violated (bm-a not earlier?)"
merged_t = dict(A)                      # bm-a claim-bearing side wins
merged_t["progress_r392_bmb"] = B.get("progress_r392_bmb", "")
merged_t["yield_r393_bmb"] = (
    "claim collision resolved per fleet README (commit-time order, later "
    "yields): bm-a claimed 17:10 (earlier), bm-b claimed 17:16:30 (later) "
    "-> bm-b yields T-109 to bm-a. bm-b s1 artifacts handed over: "
    "scripts/sentiment_axes_derive.py (selftest 17/17 green) + pool entry "
    "SENTIMENT-AXES-FULLHIST-P1=ready; four-face inventory in "
    "progress_r392_bmb. Zero-loss merge: bm-a claim fields + bm-b progress.")
json.loads(json.dumps(merged_t))
open(P, "w", encoding="utf-8").write(json.dumps(
    merged_t, ensure_ascii=False, indent=2))
print(f"T-109: bm-a claim wins (17:10 <= 17:16:30), bm-b yields; "
      f"progress_r392_bmb kept ({len(merged_t['progress_r392_bmb'])}B)")

# ---- 3. market_clock twins: take-new, md follows json twin side -----------
P = "results/market_clock/call_latest.json"
ta, tb = wallclock_max(blob_json(2, P)), wallclock_max(blob_json(3, P))
side = 2 if tb <= ta else 3
open(P, "wb").write(blob_bytes(side, P))
open("results/market_clock/CALL-2026-09-28.md", "wb").write(
    blob_bytes(side, "results/market_clock/CALL-2026-09-28.md"))
print(f"market_clock twins: take side {':2:ours' if side == 2 else ':3:theirs'}"
      f" (probe {ta} vs {tb})")

# ---- 4. compute_audit.json: rolling-ledger union -------------------------
P = "results/compute_audit.json"
A, B = blob_json(2, P), blob_json(3, P)
seen, union = set(), []
for row in A.get("history", []) + B.get("history", []):
    k = json.dumps(row, sort_keys=True, ensure_ascii=False)
    if k not in seen:
        seen.add(k)
        union.append(row)
union.sort(key=lambda r: r.get("ts", ""))
la = (A.get("latest") or {}).get("ts") or ""
lb = (B.get("latest") or {}).get("ts") or ""
latest = (A if lb <= la else B).get("latest")
merged = {"history": union, "latest": latest}
json.loads(json.dumps(merged))
open(P, "w", encoding="utf-8").write(json.dumps(
    merged, ensure_ascii=False, indent=1))
print(f"compute_audit: union {len(A['history'])}+{len(B['history'])} -> "
      f"{len(union)}; latest take-new {max(la, lb)}")

# ---- 5. regime_state.json: ledger union + state take-new ------------------
P = "results/regime_state.json"
A, B = blob_json(2, P), blob_json(3, P)
merged = {}
for key in ("history", "transitions"):
    if key in A or key in B:
        ha, hb = A.get(key, []), B.get(key, [])
        s2, u2 = set(), []
        for row in ha + hb:
            k = json.dumps(row, sort_keys=True, ensure_ascii=False)
            if k not in s2:
                s2.add(k)
                u2.append(row)
        u2.sort(key=lambda r: r.get("ts", r.get("date", "")))
        merged[key] = u2
state_side = A if wallclock_max(B) <= wallclock_max(A) else B
for k, v in state_side.items():
    if k not in merged:
        merged[k] = v
json.loads(json.dumps(merged))
open(P, "w", encoding="utf-8").write(json.dumps(
    merged, ensure_ascii=False, indent=1))
print("regime_state: union ledgers + state take-new "
      f"{'ours' if state_side is A else 'theirs'}")

# ---- 6. snapshots: take-new ----------------------------------------------
for P in ["results/scorecard_v1.json", "results/strategy_scorecard.json",
          "results/token_usage.json", "results/update_status.json"]:
    a, b = blob_json(2, P), blob_json(3, P)
    ta, tb = wallclock_max(a), wallclock_max(b)
    pick = a if tb <= ta else b
    open(P, "w", encoding="utf-8").write(json.dumps(
        pick, ensure_ascii=False, indent=1))
    print(f"{P}: take-new {'ours' if pick is a else 'theirs'} "
          f"(probe {ta or '-'} vs {tb or '-'})")
print("resolve6 done")
