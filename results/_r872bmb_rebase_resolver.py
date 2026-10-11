# -*- coding: utf-8 -*-
"""r872 bm-b rebase conflict resolver (round-face):
- 23 regenerated shared runtime faces -> ours-during-rebase base side is
  origin/bm-c r864; we take OUR COMMIT side (rebase --theirs) for uniform
  round evidence (all regenerate next round anyway).
- results/token_usage.json -> machine-keyed UNION (both machines' counters
  preserved, per-machine newer-ts wins within key).
- results/x2_watch_log.jsonl -> append-only row union (ours + theirs-not-in-ours).
Stage access: :2: = rebase ours (origin base), :3: = rebase theirs (my commit).
"""
import json
import subprocess

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"


def stage(path, n):
    r = subprocess.run(["git", "show", ":%d:%s" % (n, path)],
                       capture_output=True, cwd=ROOT)
    return r.stdout.decode("utf-8", errors="replace")


SIMPLE = [
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
    "results/paper_export/export-2026-10-09.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/update_status.json",
]

for p in SIMPLE:
    mine = stage(p, 3)
    assert mine.strip(), "empty stage-3 for %s" % p
    with open(ROOT + "\\" + p.replace("/", "\\"), "w", encoding="utf-8",
              newline="") as fh:
        fh.write(mine)
    print("took-my-side:", p)

# --- token_usage.json: machine-keyed union --------------------------------
p = "results/token_usage.json"
o, t = stage(p, 2), stage(p, 3)
jo, jt = json.loads(o), json.loads(t)
mo = jo.get("machines", {})
mt = jt.get("machines", {})
for k, v in mt.items():
    if k not in mo or str(v.get("ts", "")) >= str(mo[k].get("ts", "")):
        mo[k] = v
jo["machines"] = mo
for k, v in jt.items():
    if k != "machines" and k not in jo:
        jo[k] = v
with open(ROOT + "\\" + p.replace("/", "\\"), "w", encoding="utf-8") as fh:
    json.dump(jo, fh, ensure_ascii=False, indent=1)
print("union:", p, "machines:", sorted(mo.keys()))

# --- x2_watch_log.jsonl: row union ----------------------------------------
p = "results/x2_watch_log.jsonl"
o, t = stage(p, 2), stage(p, 3)
rows_o = [l for l in o.splitlines() if l.strip()]
seen = set(rows_o)
rows = rows_o + [l for l in t.splitlines() if l.strip() and l not in seen]
with open(ROOT + "\\" + p.replace("/", "\\"), "w", encoding="utf-8",
          newline="") as fh:
    fh.write("\n".join(rows) + ("\n" if rows else ""))
print("union:", p, "rows:", len(rows_o), "+", len(rows) - len(rows_o))
