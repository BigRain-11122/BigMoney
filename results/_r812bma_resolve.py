# -*- coding: utf-8 -*-
"""r812 bm-a push-storm UU resolver (31 faces) per bigmoney-conflict-resolve skill.
Stage mapping in REBASE: :2: = origin side (new base), :3: = local side (replay commit) -- r351.
ALL_FACES -> merge_lane_views.py resolve (canon). Twins -> json deep-ts take-newer + md same side.
Host-guard faces -> take :3: (bm-a host r378). Snapshots -> deep-ts take-new. x2 -> line union."""
import json, subprocess, io, re, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def stage(n, path):
    r = subprocess.run(["git", "show", f":{n}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"stage {n} {path}: {r.returncode}")
    return r.stdout


def write(path, data):
    io.open(path, "wb").write(data)


def jload(b):
    return json.loads(b.decode("utf-8-sig"))


def deep_ts(obj):
    best = [None]
    def rec(o):
        if isinstance(o, dict):
            for k, v in o.items():
                kk = k.replace("_", "").replace("-", "").lower()
                if isinstance(v, str) and re.match(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}", v) \
                        and kk in ("generatedat", "generated", "updated", "ts", "scants", "generatedts", "date"):
                    if best[0] is None or v > best[0][0]:
                        best[0] = (v, k)
                rec(v)
        elif isinstance(o, list):
            for it in o:
                rec(it)
    rec(obj)
    return best[0]


report = []
# 1. ALL_FACES canon union
for f in ["results/compute_audit.json", "results/regime_state.json",
          "results/token_usage.json", "results/update_status.json",
          "results/lhb_update_status.json", "results/futures_update_status.json"]:
    r = subprocess.run([sys.executable, "scripts/merge_lane_views.py", "resolve", f],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    report.append((f, "laneviews-union", r.returncode, ""))
# 2. twins
for jp, mp in [("docs/daily_report/REPORT-2026-10-07.json", "docs/daily_report/REPORT-2026-10-07.md"),
               ("docs/live_usage/LIVE-2026-10-07.json", "docs/live_usage/LIVE-2026-10-07.md"),
               ("docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md")]:
    t2, t3 = deep_ts(jload(stage(2, jp))), deep_ts(jload(stage(3, jp)))
    side = 3 if (t3 and (not t2 or t3[0] >= t2[0])) else 2
    write(jp, stage(side, jp)); write(mp, stage(side, mp))
    report.append((jp, f"twin take :{side}:", 0, t3[0] if side == 3 and t3 else (t2[0] if t2 else "MISS")))
# 3. host-guard
for f in ["results/scorecard_v1.json", "results/strategy_scorecard.json",
          "results/dashboard_status.json", "results/dashboard_status.js"]:
    write(f, stage(3, f)); report.append((f, "host-guard :3:", 0, ""))
# 4. take-new snapshots
for f in ["results/fundamental_b_layer_filter.json", "results/_attrition_guard_scan.json",
          "results/t35_open_fill_verify.json", "results/daily_scorecard.json",
          "results/paper/COMPOSITE-CE-01_paper.json", "results/paper/COMPOSITE-CE-02_paper.json",
          "results/paper/DROUGHT-CE-01_paper.json", "results/paper/ENGULF-CE-01_paper.json",
          "results/paper/NEEDLE-DE-01_paper.json", "results/paper/VOLATILITY-CE-01_paper.json",
          "results/prospect_paper/_summary.json", "results/prospect_promotion/_summary.json",
          "results/paper_export/export-2026-09-30.json", "results/paper_export/latest.json"]:
    t2, t3 = deep_ts(jload(stage(2, f))), deep_ts(jload(stage(3, f)))
    side = 3 if (t3 and (not t2 or t3[0] >= t2[0])) else 2
    write(f, stage(side, f))
    report.append((f, f"take-new :{side}:", 0, t3[0] if side == 3 and t3 else (t2[0] if t2 else "MISS")))
# 5. x2 line union
f = "results/x2_watch_log.jsonl"
l2 = stage(2, f).decode("utf-8", "replace").splitlines()
l3 = stage(3, f).decode("utf-8", "replace").splitlines()
seen, out = set(), []
for ln in l2 + l3:
    if ln not in seen:
        seen.add(ln); out.append(ln)
write(f, ("\n".join(out) + ("\n" if out else "")).encode("utf-8"))
report.append((f, f"line union |{len(l2)}|+|{len(l3)}| -> {len(out)}", 0, ""))

bad = []
for f, _, _, _ in report:
    try:
        json.loads(io.open(f, encoding="utf-8-sig").read())
    except Exception as e:
        bad.append((f, str(e)[:60]))
print("parse gate:", "ALL PASS" if not bad else f"FAIL {bad}")
for t in report:
    print("  %s: %s rc=%s %s" % t)
