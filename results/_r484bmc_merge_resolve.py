"""r484 bm-c merge-window resolver (canon recipe: r440 newer-wins / r675
block-union / r456+r466 token per-key w/ fallback / r657 add-isolation /
r644 marker-content check). Fail-closed on any unexpected probe result."""
import json
import os
import subprocess

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
OUTLOG = os.path.join(REPO, "results", "_r484bmc_merge_resolve_out.txt")
lines = []


def show(ref, path):
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True,
                       cwd=REPO, creationflags=CNW)
    if r.returncode != 0:
        raise SystemExit(f"RESOLVER-FAIL: git show {ref}:{path} rc={r.returncode}")
    return r.stdout


def face_ts(raw):
    """Best-effort top-level freshness field for S6 regenerable faces."""
    try:
        d = json.loads(raw)
    except Exception:
        return None
    for k in ("ts", "generated", "updated", "written_at", "as_of"):
        v = d.get(k)
        if isinstance(v, str) and ":" in v:
            return v
    return None


# ---- UU face sets ----
S6_OURS_CANDIDATES = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/daily_scorecard.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-30.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/update_status.json",
]
TOKEN_FACE = "results/token_usage.json"
CODELY = "CODELY.md"

# ---- 1. S6 regenerable faces: per-face newer-wins (r440) ----
ours_wins, theirs_wins = [], []
for p in S6_OURS_CANDIDATES:
    o, t = show("HEAD", p), show("MERGE_HEAD", p)
    o_ts, t_ts = face_ts(o), face_ts(t)
    if o_ts and t_ts:
        if o_ts >= t_ts:
            ours_wins.append(p)
        else:
            theirs_wins.append(p)
            lines.append(f"FACE_THEIRS_NEWER {p} ours={o_ts} theirs={t_ts}")
    else:
        # ts-less face (js / md / nested-ts): systematic 13-min chain offset
        # evidence (regime/update_status probes) -> ours (fail-closed probe
        # asserted on at least 2 ts faces below)
        ours_wins.append(p)
        lines.append(f"FACE_TSLESS_DEFAULT_OURS {p}")
# probe floor: at least 2 ts-comparable faces must BOTH be ours-newer,
# else the systematic-offset premise is falsified -> fail closed
ts_faces = [p for p in S6_OURS_CANDIDATES
            if face_ts(show("HEAD", p)) and face_ts(show("MERGE_HEAD", p))]
ours_ts_wins = [p for p in ts_faces if face_ts(show("HEAD", p)) >= face_ts(show("MERGE_HEAD", p))]
assert len(ts_faces) >= 2 and len(ours_ts_wins) == len(ts_faces), \
    f"RESOLVER-FAIL: newer-wins premise falsified ({len(ours_ts_wins)}/{len(ts_faces)})"
for p in ours_wins:
    raw = show("HEAD", p)
    with open(os.path.join(REPO, p.replace("/", os.sep)), "wb") as f:
        f.write(raw)
for p in theirs_wins:
    raw = show("MERGE_HEAD", p)
    with open(os.path.join(REPO, p.replace("/", os.sep)), "wb") as f:
        f.write(raw)
lines.append(f"S6 faces: ours={len(ours_wins)} theirs={len(theirs_wins)}")

# ---- 2. token_usage.json: per-key union (r456) w/ r466 fallback ----
o_raw, t_raw = show("HEAD", TOKEN_FACE), show("MERGE_HEAD", TOKEN_FACE)
o, t = json.loads(o_raw), json.loads(t_raw)
o_m, t_m = o.get("machines", {}), t.get("machines", {})
side_pick = 0
union_m = {}
for k in sorted(set(o_m) | set(t_m)):
    ov, tv = o_m.get(k), t_m.get(k)
    if ov == tv:
        union_m[k] = ov
    elif k not in t_m:
        union_m[k] = ov; side_pick += 1
    elif k not in o_m:
        union_m[k] = tv; side_pick += 1
    else:
        # both present, differ: freshness per value ts if available
        o_ts = ov.get("ts") if isinstance(ov, dict) else None
        t_ts = tv.get("ts") if isinstance(tv, dict) else None
        if o_ts and t_ts:
            union_m[k] = ov if o_ts >= t_ts else tv
            side_pick += 1
        else:
            union_m[k] = ov if str(ov) >= str(tv) else tv
            side_pick += 1
o_gen, t_gen = o.get("generated"), t.get("generated")
if side_pick == 0:
    # r466 fallback: whole-face freshness (generated ts)
    assert o_gen and t_gen, "RESOLVER-FAIL: token faces identical keys, no generated ts"
    winner = o if o_gen >= t_gen else t
    lines.append(f"token: per-key zero side-pick -> whole-face freshness "
                 f"ours={o_gen} theirs={t_gen} -> {'ours' if o_gen >= t_gen else 'theirs'}")
else:
    winner = o if o_gen >= t_gen else t
    winner = dict(winner)
    winner["machines"] = union_m
    lines.append(f"token: per-key union side_pick={side_pick}")
with open(os.path.join(REPO, "results", "token_usage.json"), "wb") as f:
    f.write(json.dumps(winner, ensure_ascii=False, indent=1).encode("utf-8"))
json.load(open(os.path.join(REPO, "results", "token_usage.json"), encoding="utf-8"))

# ---- 3. CODELY.md block-union (r675 recipe + r479 containment filter) ----
o_raw, t_raw = show("HEAD", CODELY), show("MERGE_HEAD", CODELY)
o_txt, t_txt = o_raw.decode("utf-8"), t_raw.decode("utf-8")
o_lines = o_txt.splitlines()
missing = [ln for ln in o_lines if ln.strip() and ln not in t_txt]
# r479 containment: a "missing" line that is a substring of theirs -> dropped
# (origin carries the same entry in a normalized variant); true-new only
true_new = [ln for ln in missing if ln not in t_txt]
assert len(true_new) == 1 and "r484 bm-c" in true_new[0], \
    f"RESOLVER-FAIL: CODELY true-new != 1 ({len(true_new)})"
base = t_txt if t_txt.endswith("\n") else t_txt + "\n"
union = base + true_new[0] + "\n"
# assertions: theirs full text preserved as prefix; my entry exactly once;
# zero conflict markers at line starts (r644/r657)
assert union.startswith(t_txt.rstrip("\n") + "\n") or union.startswith(t_txt), \
    "RESOLVER-FAIL: CODELY theirs-prefix identity broken"
assert union.count(true_new[0]) == 1
assert not any(ln.startswith(("<<<<<<<", "=======", ">>>>>>>"))
               for ln in union.splitlines())
with open(os.path.join(REPO, "CODELY.md"), "wb") as f:
    f.write(union.encode("utf-8"))
lines.append(f"CODELY union: theirs-preserved + {len(true_new)} true-new line, "
             f"marker-scan clean, result_lines={len(union.splitlines())}")

with open(OUTLOG, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(lines))
print("RESOLVE_DONE_WROTE", OUTLOG)
