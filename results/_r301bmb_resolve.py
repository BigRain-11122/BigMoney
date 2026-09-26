# -*- coding: utf-8 -*-
"""r301 bm-b S7 push-rejection rebase batch resolve (canonical recipes
r188/R208/R209/R216/r140/r185; classifier 11 GREEN + 16 UNKNOWN hand-qualified).

Collision: bm-a r296 pair (95f4e95d FUSION_GRID_P1 runner+pool-ready entry,
5868496e wrap) landed same window as bm-b r301. ours(stage2)=bm-a 05:42-44
chain batch, theirs(stage3)=bm-b 05:43-45 chain batch -- both S6 chains
re-derived the shared regen faces from equivalent trees.

Per-file qualification (fail-closed, no blind take):
  UNION (zero-loss, two-machine samples):
  - compute_audit.json  rolling-ledger: history rows from BOTH machines
    (bm-a cores-32 sample 05:42:08 + bm-b cores-16 sample 05:43:15);
    exact-row dedupe, ts ASC; latest take-new by ts.
  - x2_watch_log.jsonl  append-log: ours +6 lines (05:42:56-58) and
    theirs +6 lines (05:43:51-56) both legitimate watch records ->
    base order + ts-ordered union tail.

  TAKE-STAGE2 (upstream bm-a, post-integration faces per r298 precedent):
  - dashboard_status.js / dashboard_status.json  ours carries the
    FUSION-GRID-P1 pool-ready face (pool_ready 1, ready_ids FUSION-GRID-P1,
    post 95f4e95d integration); theirs predates the pool entry landing on
    bm-b's tree. Both transient display faces re-derived next round.

  TAKE-NEW by ts (pure runtime-metadata drift; content equivalence proven
  by recursive strip-whitelist equality assertion before take):
  - docs/daily_report/REPORT-2026-09-27.json/.md  (generated_at 05:44:03 >
    05:43:10; counts face commits_24h 445/446 aggregation instant)
  - daily_scorecard.json / scorecard_v1.json / strategy_scorecard.json
    (as_of/generated + elapsed_sec runtime metadata only)
  - fundamental_b_layer_filter.json / futures/heat/lhb_update_status.json
    (updated/last_attempt only)
  - paper/*_paper.json x6  (updated/as_of only -- anchor integrity gate:
    stripped-equality proves zero anchor drift, refresh stamps only)
  - paper_export/{export-2026-09-24,latest}.json (state_updated faces only)
  - prospect_paper/_summary.json / prospect_promotion/_summary.json (generated)
  - regime_state.json (updated only; no new transitions either side)
  - t35_open_fill_verify.json (ts only)
  - token_usage.json (R216: meter re-derives whole doc, newest wins;
    *_est/_bytes leaf drift only)
  - update_status.json (updated/now only)

Gates: parse-verify after write, marker sweep all 27, stripped-equality
assertion for every take-new json, union row-count == |A union B|.
"""
import difflib
import io
import json
import re
import subprocess

TAKE_NEW = [
    "docs/daily_report/REPORT-2026-09-27.json",
    "docs/daily_report/REPORT-2026-09-27.md",
    "results/daily_scorecard.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-24.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/token_usage.json",
    "results/update_status.json",
]
TAKE_STAGE2 = [
    "results/dashboard_status.js",
    "results/dashboard_status.json",
]
UNION_LEDGER = "results/compute_audit.json"
UNION_JSONL = "results/x2_watch_log.jsonl"

STRIP_EXACT = {
    "ts", "updated", "generated", "as_of", "generated_at", "now",
    "last_attempt", "elapsed_sec", "state_updated",
    "generated_from_state_updated", "commits_24h",
    "result_jsons_landed_24h", "prev_generated", "delta_prev",
    "delta_vs_prev",
    # embedded compute_audit sample telemetry (daily_report rd subtree)
    "py_cpu_pct", "verdict", "flags", "cpu_total_pct", "cores", "py_procs",
    "gpu_util_pct", "gpu_mem_used_mb", "zombies", "rogue_apps",
    "load_state", "pool_starvation_candidate", "pool_starvation_detail",
    "result_stale_min", "fleet_open_tasks", "single_core_hog_candidate",
    "single_core_hog_detail", "gpu", "pool_ready_count",
}
STRIP_SUFFIX = ("_est", "_bytes")


def blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)],
                       capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("blob fail stage %d %s" % (stage, path))
    return r.stdout


def strip_meta(node):
    if isinstance(node, dict):
        return {k: strip_meta(v) for k, v in sorted(node.items())
                if k not in STRIP_EXACT and not k.endswith(STRIP_SUFFIX)}
    if isinstance(node, list):
        return [strip_meta(x) for x in node]
    return node


def find_ts(d):
    for k in ("generated_at", "generated", "updated", "ts", "as_of"):
        if isinstance(d, dict) and k in d and isinstance(d[k], str):
            return k, d[k]
    # fallback: recursive max over ts-like leaves (per-card as_of faces)
    KEYS = ("updated", "generated", "generated_at", "ts", "as_of",
            "state_updated", "generated_from_state_updated",
            "last_update", "last_attempt", "now")
    best = {}
    def _walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k in KEYS and isinstance(v, str):
                    if v > best.get("v", ""):
                        best.update(k=k, v=v)
                else:
                    _walk(v)
        elif isinstance(node, list):
            for x in node:
                _walk(x)
    _walk(d)
    if best:
        return best["k"], best["v"]
    raise RuntimeError("no ts key found: %r" % (list(d)[:8],))


def marker_sweep(path, raw):
    bad = [l for l in raw.decode("utf-8", "replace").splitlines()
           if l.startswith(("<<<<<<<", "=======", ">>>>>>>"))]
    assert not bad, (path, bad[:2])
    return len(raw)


report = []


def take_new(path):
    o_raw, t_raw = blob(2, path), blob(3, path)
    if path.endswith(".json"):
        o = json.loads(o_raw.decode("utf-8-sig"))
        t = json.loads(t_raw.decode("utf-8-sig"))
        so, st = strip_meta(o), strip_meta(t)
        assert so == st, "content drift beyond meta whitelist: %s" % path
        ko, vo = find_ts(o)
        kt, vt = find_ts(t)
        assert ko == kt, "ts key mismatch %s: %s vs %s" % (path, ko, kt)
        side = t_raw if vt > vo else o_raw          # tie -> ours (r140)
        pick = "theirs(%s)" % vt if vt > vo else "ours(%s)" % vo
    else:
        # .md twin of the strip-checked .json -- hand-qualified take-new
        mo = re.search(r"生成 (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})",
                       o_raw.decode("utf-8", "replace"))
        mt = re.search(r"生成 (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})",
                       t_raw.decode("utf-8", "replace"))
        assert mo and mt, "md gen-ts not found %s" % path
        vo, vt = mo.group(1), mt.group(1)
        side = t_raw if vt > vo else o_raw
        pick = "theirs(%s)" % vt if vt > vo else "ours(%s)" % vo
    n = marker_sweep(path, side)
    with io.open(path, "wb") as f:
        f.write(side)
    if path.endswith(".json"):
        json.load(io.open(path, encoding="utf-8-sig"))
    report.append("take-new %-52s %s %dB" % (path, pick, n))


def take_stage2(path):
    raw = blob(2, path)
    n = marker_sweep(path, raw)
    with io.open(path, "wb") as f:
        f.write(raw)
    if path.endswith(".json"):
        json.load(io.open(path, encoding="utf-8-sig"))
    report.append("take-stage2 %-51s upstream-bm-a %dB" % (path, n))


def union_ledger(path):
    o_raw, t_raw, base_raw = blob(2, path), blob(3, path), blob(1, path)
    o = json.loads(o_raw.decode("utf-8-sig"))
    t = json.loads(t_raw.decode("utf-8-sig"))
    assert set(o) == set(t), "top-key drift %s" % path
    um = {}
    for r in o.get("history", []) + t.get("history", []):
        um.setdefault(json.dumps(r, sort_keys=True, ensure_ascii=False), r)
    merged = sorted(um.values(), key=lambda r: str(r.get("ts", "")))  # ASC
    lo, lt = (o.get("latest") or {}), (t.get("latest") or {})
    latest = lt if str(lt.get("ts", "")) > str(lo.get("ts", "")) else lo  # tie->ours
    out = dict(o)
    out["history"] = merged
    out["latest"] = latest
    nl = "\r\n" if b"\r\n" in base_raw else "\n"
    payload = json.dumps(out, ensure_ascii=False, indent=2)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(payload.replace("\n", nl))
    chk = json.loads(io.open(path, encoding="utf-8-sig").read())
    assert len(chk["history"]) == len(um) == len(set(
        json.dumps(r, sort_keys=True, ensure_ascii=False)
        for r in chk["history"])), "union zero-loss gate"
    assert chk["history"] == merged
    report.append("union-ledger %s history %d|%d -> %d rows, latest=%s" % (
        path, len(o.get("history", [])), len(t.get("history", [])),
        len(merged), latest.get("ts")))


def union_jsonl(path):
    o_raw, t_raw, base_raw = blob(2, path), blob(3, path), blob(1, path)
    nl = "\r\n" if b"\r\n" in base_raw else "\n"
    split = (lambda b: b.decode("utf-8", "replace").replace("\r\n", "\n")
             .split("\n"))
    base_l = [l for l in split(base_raw) if l.strip()]
    o_l = [l for l in split(o_raw) if l.strip()]
    t_l = [l for l in split(t_raw) if l.strip()]
    base_set = set(base_l)
    extra = [l for l in (o_l + t_l) if l not in base_set]
    extra = sorted({l for l in extra},
                   key=lambda l: str(json.loads(l).get("ts", "")))
    out_l = base_l + extra
    assert set(out_l) == set(o_l) | set(t_l), "jsonl union zero-loss gate"
    assert len(out_l) == len(set(out_l))
    for l in out_l:
        json.loads(l)
    with io.open(path, "wb") as f:
        f.write(nl.join(out_l).encode("utf-8") + nl.encode("utf-8"))
    report.append("union-jsonl %s lines %d|%d base=%d -> %d (extra=%d)" % (
        path, len(o_l), len(t_l), len(base_l), len(out_l), len(extra)))


for p in TAKE_NEW:
    take_new(p)
for p in TAKE_STAGE2:
    take_stage2(p)
union_ledger(UNION_LEDGER)
union_jsonl(UNION_JSONL)

all_paths = TAKE_NEW + TAKE_STAGE2 + [UNION_LEDGER, UNION_JSONL]
assert len(all_paths) == 27, len(all_paths)
for p in all_paths:                      # final marker sweep on written files
    marker_sweep(p, io.open(p, "rb").read())
print("== r301 resolve: 27/27 written, all gates PASS ==")
for r in report:
    print("  " + r.encode("gbk", "replace").decode("gbk"))
subprocess.run(["git", "add"] + all_paths, check=True)
print("git add 27 paths done")
