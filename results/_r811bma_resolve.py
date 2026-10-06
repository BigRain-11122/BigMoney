# -*- coding: utf-8 -*-
"""r811 bm-a push-storm UU resolver (28 faces) per bigmoney-conflict-resolve skill.
Stage mapping in REBASE: :2: = origin side (new base), :3: = local side (replay commit) -- r351.
ALL_FACES members -> merge_lane_views.py resolve (canon, no hand-union).
Twins -> take-newer json by deep ts probe, md takes SAME side bytes (r327/r329).
Host-guard faces -> take :3: (bm-a host per r378, fresh re-derive) with ts probe log.
paper/*_paper + prospect summaries -> take-new by updated/generated deep probe.
fundamental_b_layer_filter -> take-new by updated ts.
_attrition_guard_scan -> take-new by ts.
x2_watch_log.jsonl -> line-level union zero loss.
"""
import json, subprocess, io, re, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def stage(n, path):
    r = subprocess.run(["git", "show", f":{n}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"stage {n} {path}: {r.returncode}")
    return r.stdout


def write(path, data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    io.open(path, "wb").write(data)


def deep_ts(obj, prefer=("generated_at", "generated", "updated", "ts", "scan_ts")):
    """Deep-scan nested layers for the newest wall-clock ts (r311/D-20261027 law)."""
    best = None
    def rec(o):
        nonlocal best
        if isinstance(o, dict):
            for k, v in o.items():
                kk = k.replace("_", "").replace("-", "").lower()
                if isinstance(v, str) and re.match(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}", v):
                    if kk in ("generatedat", "generated", "updated", "ts", "scants", "generatedts"):
                        if best is None or v > best[0]:
                            best = (v, k)
                rec(v)
        elif isinstance(o, list):
            for it in o:
                rec(it)
    rec(obj)
    return best


def jload(b):
    return json.loads(b.decode("utf-8-sig", errors="strict"))


report = []

# --- 1. ALL_FACES via canon resolver -----------------------------------------
for f in ["results/compute_audit.json", "results/regime_state.json",
          "results/token_usage.json", "results/update_status.json",
          "results/lhb_update_status.json", "results/futures_update_status.json"]:
    r = subprocess.run([sys.executable, "scripts/merge_lane_views.py", "resolve", f],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    report.append((f, "merge_lane_views resolve", r.returncode,
                   (r.stdout or "").strip().splitlines()[-1:] or [r.stderr.strip()[:80]]))

# --- 2. twins: json take-newer deep-probe, md same side ------------------------
for jp, mp in [("docs/daily_report/REPORT-2026-10-07.json", "docs/daily_report/REPORT-2026-10-07.md"),
               ("docs/live_usage/LIVE-2026-10-07.json", "docs/live_usage/LIVE-2026-10-07.md"),
               ("docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md")]:
    b2, b3 = stage(2, jp), stage(3, jp)
    j2, j3 = jload(b2), jload(b3)
    t2, t3 = deep_ts(j2), deep_ts(j3)
    if t3 and (not t2 or t3[0] >= t2[0]):
        side, jb, ts = 3, b3, t3
    else:
        side, jb, ts = 2, b2, t2
    write(jp, jb)
    write(mp, stage(side, mp))
    report.append((jp, f"twin take side :{side}: (ts {ts[0] if ts else 'MISS'} via {ts[1] if ts else '-'})", 0, ""))

# --- 3. host-guard faces: take :3: (bm-a host r378) ---------------------------
for f in ["results/scorecard_v1.json", "results/strategy_scorecard.json",
          "results/dashboard_status.json", "results/dashboard_status.js"]:
    b2, b3 = stage(2, f), stage(3, f)
    ts3 = None
    if not f.endswith(".js"):
        try:
            ts3 = deep_ts(jload(b3))
        except Exception:
            ts3 = None
    write(f, b3)
    report.append((f, f"host-guard take :3: (bm-a host r378; probe ts {ts3[0] if ts3 else 'n/a'})", 0, ""))

# --- 4. paper faces + prospect summaries: take-new by updated/generated -------
for f in ["results/paper/COMPOSITE-CE-01_paper.json", "results/paper/COMPOSITE-CE-02_paper.json",
          "results/paper/DROUGHT-CE-01_paper.json", "results/paper/ENGULF-CE-01_paper.json",
          "results/paper/NEEDLE-DE-01_paper.json", "results/paper/VOLATILITY-CE-01_paper.json",
          "results/prospect_paper/_summary.json", "results/prospect_promotion/_summary.json",
          "results/fundamental_b_layer_filter.json", "results/_attrition_guard_scan.json",
          "results/t35_open_fill_verify.json"]:
    b2, b3 = stage(2, f), stage(3, f)
    try:
        j2, j3 = jload(b2), jload(b3)
        t2, t3 = deep_ts(j2), deep_ts(j3)
        if t3 and (not t2 or t3[0] >= t2[0]):
            side, ts = 3, t3
        else:
            side, ts = 2, t2
        write(f, stage(side, f))
        report.append((f, f"take-new side :{side}: (ts {ts[0] if ts else 'MISS'})", 0, ""))
    except Exception as e:
        # not JSON or parse fail -> bytes take-new by mtime-ish probe impossible; fail loud
        report.append((f, "PARSE-FAIL fail-closed", 2, str(e)[:100]))
        raise

# --- 5. x2_watch_log.jsonl: line-level union ----------------------------------
f = "results/x2_watch_log.jsonl"
l2 = stage(2, f).decode("utf-8", "replace").splitlines()
l3 = stage(3, f).decode("utf-8", "replace").splitlines()
seen, out = set(), []
for ln in l2 + l3:
    if ln not in seen:
        seen.add(ln)
        out.append(ln)
write(f, "\n".join(out) + ("\n" if out else ""))
report.append((f, f"line union |{len(l2)}|+|{len(l3)}| -> {len(out)} rows", 0, ""))

# --- verify all JSON faces parse ----------------------------------------------
bad = []
for f in ["results/compute_audit.json", "results/regime_state.json", "results/token_usage.json",
          "results/update_status.json", "results/lhb_update_status.json", "results/futures_update_status.json",
          "docs/daily_report/REPORT-2026-10-07.json", "docs/live_usage/LIVE-2026-10-07.json",
          "docs/live_usage/LIVE-latest.json", "results/scorecard_v1.json", "results/strategy_scorecard.json",
          "results/dashboard_status.json", "results/fundamental_b_layer_filter.json",
          "results/_attrition_guard_scan.json",
          "results/paper/COMPOSITE-CE-01_paper.json", "results/prospect_paper/_summary.json",
          "results/prospect_promotion/_summary.json"]:
    try:
        json.loads(io.open(f, encoding="utf-8-sig").read())
    except Exception as e:
        bad.append((f, str(e)[:60]))
print("JSON parse gate:", "ALL PASS" if not bad else f"FAIL {bad}")

for f, act, rc, note in report:
    print(f"  {f}: {act}" + (f" rc={rc} {note}" if rc else ""))
