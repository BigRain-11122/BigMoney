# -*- coding: utf-8 -*-
# r236 bm-c rebase resolver: 17 UU vs bm-a r443/r444 same-window regen family
# (same-day idempotent snapshot faces, r439bmb twin law corpus).
# Probe law r100/R350: key normalize (strip _/-) BEFORE prefix match, value must
# be timestamp-shaped ^20\d{2}- AND carry time-of-day ([T ]HH:MM) to feed
# max-compare; NO key-exclusion lists; probe STAGED blobs (:2:/:3:), never the
# working tree; same-second tie -> :2 side (= upstream in rebase, r140).
# Stage semantics in rebase: :2 = upstream (HEAD/origin side, bm-a here),
# :3 = the replayed commit (my bm-c side).
import json
import re
import subprocess

def stage(stage_no, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage_no, path)],
                       capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout

TS_RE = re.compile(r"^20\d{2}-")
TOD_RE = re.compile(r"[T ]\d{2}:\d{2}")

def deep_ts(obj, best=("", "")):
    """Hardened deep probe: max wall-clock ts value anywhere in the tree."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = re.sub(r"[_\-]", "", str(k)).lower()
            if isinstance(v, str) and TS_RE.match(v) and TOD_RE.search(v) \
               and any(nk.startswith(p) for p in
                       ("generated", "updated", "ts", "asof", "now",
                        "written", "donets", "closets", "checked")):
                if v > best[0]:
                    best = (v, k)
            best = deep_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = deep_ts(v, best)
    return best

def jload(b):
    return json.loads(b.decode("utf-8-sig"))

def resolve_snapshot(path, prefer=None):
    """take-new whole doc by hardened deep-ts probe; tie -> :2 (upstream)."""
    b2, b3 = stage(2, path), stage(3, path)
    if b2 is None:
        pick, side = b3, "ours-bmc"
    elif b3 is None:
        pick, side = b2, "theirs-upstream"
    else:
        t2 = deep_ts(jload(b2))[0]
        t3 = deep_ts(jload(b3))[0]
        if t3 > t2:
            pick, side = b3, "ours-bmc"
        elif t2 > t3:
            pick, side = b2, "theirs-upstream"
        else:
            pick, side = b2, "tie-head-upstream"
    if prefer is not None and side != prefer and not side.startswith("tie"):
        # twin law override: twins MUST take the SAME side
        pick = stage(3, path) if prefer == "ours-bmc" else stage(2, path)
        side = "twin-override-" + prefer
    with open(path, "wb") as f:
        f.write(pick)
    json.loads(open(path, "rb").read().decode("utf-8-sig"))  # verify parse
    print("%-52s -> %s" % (path, side))
    return side

def resolve_union_ledger(path, ledger_keys):
    """rolling-ledger: union list rows (dedup by exact row identity, keep
    both sides' distinct rows, sort by ts asc), snapshot fields take-new."""
    b2, b3 = stage(2, path), stage(3, path)
    d2, d3 = jload(b2), jload(b3)
    t2, t3 = deep_ts(d2)[0], deep_ts(d3)[0]
    base = d3 if t3 > t2 else d2           # newer snapshot fields
    side = "ours-bmc" if t3 > t2 else ("theirs-upstream" if t2 > t3 else "tie-upstream")
    for k in ledger_keys:
        if not isinstance(d2.get(k), list) or not isinstance(d3.get(k), list):
            continue
        rows = []
        seen = set()
        for row in list(d2[k]) + list(d3[k]):
            key = json.dumps(row, sort_keys=True, ensure_ascii=False)
            if key in seen:
                continue
            seen.add(key)
            rows.append(row)
        rows.sort(key=lambda r: str(r.get("ts", r.get("date", ""))))
        base[k] = rows
    with open(path, "w", encoding="utf-8", newline="") as f:
        json.dump(base, f, ensure_ascii=False, indent=1)
    json.loads(open(path, "rb").read().decode("utf-8-sig"))  # verify parse
    print("%-52s -> %s (union %s)" % (path, side, ledger_keys))
    return side

def resolve_bytes_twin(path, side):
    """take whole bytes from the SAME side as the json twin decided."""
    pick = stage(3, path) if side == "ours-bmc" else stage(2, path)
    with open(path, "wb") as f:
        f.write(pick)
    print("%-52s -> twin-bytes %s" % (path, side))

# --- 1. json snapshots (probe independently) ---
s_report = resolve_snapshot("docs/daily_report/REPORT-2026-09-29.json")
s_dash = resolve_snapshot("results/dashboard_status.json")
resolve_snapshot("results/fundamental_b_layer_filter.json")
resolve_snapshot("results/futures_update_status.json")
resolve_snapshot("results/lhb_update_status.json")
s_sc1 = resolve_snapshot("results/scorecard_v1.json")
s_sc2 = resolve_snapshot("results/strategy_scorecard.json")
resolve_snapshot("results/token_usage.json")
resolve_snapshot("results/update_status.json")

# --- 2. LIVE-2026-09-29.json: same-day idempotent regen snapshot
#     (ceo_live_usage daily face, 当日原地再生幂等) -> take-new by
#     generated ts; all four twins take the SAME side (r98/r99/r100 twin law).
s_live = resolve_snapshot("docs/live_usage/LIVE-2026-09-29.json")

# --- 3. md twins follow their json twin side ---
resolve_bytes_twin("docs/daily_report/REPORT-2026-09-29.md",
                   "ours-bmc" if s_report == "ours-bmc" else "theirs-upstream")
resolve_bytes_twin("docs/live_usage/LIVE-2026-09-29.md",
                   "ours-bmc" if s_live == "ours-bmc" else "theirs-upstream")
resolve_bytes_twin("docs/live_usage/LIVE-latest.json",
                   "ours-bmc" if s_live == "ours-bmc" else "theirs-upstream")
resolve_bytes_twin("docs/live_usage/LIVE-latest.md",
                   "ours-bmc" if s_live == "ours-bmc" else "theirs-upstream")

# --- 4. js wrapper takes same side as its json twin (R209 whole-bytes) ---
resolve_bytes_twin("results/dashboard_status.js",
                   "ours-bmc" if s_dash == "ours-bmc" else "theirs-upstream")

# --- 5. rolling-ledgers: union + take-new fields ---
resolve_union_ledger("results/compute_audit.json", ["history"])
resolve_union_ledger("results/regime_state.json", ["history", "transitions"])

print("RESOLVE_DONE")
