# -*- coding: utf-8 -*-
"""r307 bm-b mid-round fold resolve (canonical recipes
r188/R208/R209/R216/r140/r185/r203/r215/r245/r223; classifier 12 GREEN + 16 UNKNOWN
hand-qualified frozen from r306 batch1 same-file-set precedent; strip-equality
assert = live fail-closed re-qualification of every take-new file).

Collision: bm-a r301 wrap (ecafdcc2, committed 07:23:55) landed during r307
bm-b S6 chain window -> stash(r307-pres6-fold) -> pull --rebase fast-forward
758bf157..ecafdcc2 -> stash pop 28 UU. ours(stage2)=bm-a ecafdcc2 S6 faces,
theirs(stage3)=bm-b r307 S6 faces (chain 07:23:56-07:26).

Per-file qualification (fail-closed, no blind take):
  TAKE-NEW by ts, strip-whitelist equality asserted first (23):
    REPORT-2026-09-27.json/.md, daily_scorecard, fundamental_b_layer_filter,
    futures/heat/lhb_update_status, paper x6, export-2026-09-24+latest,
    prospect x2, regime_state, scorecard_v1, strategy_scorecard,
    t35_open_fill_verify, token_usage, update_status
  TAKE-STAGE3 (this-machine snapshot, whole bytes; both sides carry the
  pool-ready integration face since 758bf157 (sectldr-0of1 owner=bm-a
  07:20:04), residual delta = machine telemetry only; re-derived next
  round either way):
    dashboard_status.json / dashboard_status.js (R209 wrapper preserved)
  UNION rolling-ledger: compute_audit.json (history rows from BOTH machines
  -- bm-a cores-32 ecafdcc2 chain + bm-b cores-16 07:23:56; exact-row dedupe
  ts ASC; latest take-new)
  UNION append-log: x2_watch_log.jsonl (base order + ts-sorted extras both sides)
  MIXED dict+ledger: autofill_state.json (r302/r306 template: launches full-identity
  union -> ts desc cap50 -> ASC write-back; last_tick inner-ts compare, tie ->
  HEAD/ours; CRLF mirror base; parse gate + isinstance dict)

Gates: marker sweep all 28, parse-verify after write, strip-equality for
every take-new json, union row-count == |A union B|, cap-drops-oldest-only.
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
TAKE_STAGE3 = [
    "results/dashboard_status.js",
    "results/dashboard_status.json",
]
UNION_LEDGER = "results/compute_audit.json"
UNION_JSONL = "results/x2_watch_log.jsonl"
MIXED = "results/autofill_state.json"

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
    # r307 qualification (_r307bmb_deepdiff.py, batch2 whitelist-extension
    # precedent): runtime advisory + measurement faces that re-derive on
    # every producer run --
    #  - guard/regime_guard: live.paper REGIME_GUARD env-request face (bm-a
    #    tick ran with env=enforce -> mode=enforce/active_from=2026-10-01;
    #    bm-b no-env -> shadow) -- re-derives each live_paper, both honest
    #  - batch_in_flight / watermark_verdict: pool launch + py_watermark
    #    probe advisories at report build instant (re-derive each S6 run)
    #  - machines/per_round_context/total_report_tokens_est: token meter
    #    measurement snapshot (R216 whole-doc re-derive each run)
    "guard", "regime_guard", "batch_in_flight", "watermark_verdict",
    "machines", "per_round_context", "total_report_tokens_est",
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


def take_stage3(path):
    raw = blob(3, path)
    n = marker_sweep(path, raw)
    with io.open(path, "wb") as f:
        f.write(raw)
    if path.endswith(".json"):
        json.load(io.open(path, encoding="utf-8-sig"))
    report.append("take-stage3 %-51s this-machine(bm-b) %dB" % (path, n))


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


def resolve_mixed(path):
    o_raw, t_raw, base_raw = blob(2, path), blob(3, path), blob(1, path)
    o = json.loads(o_raw.decode("utf-8-sig"))
    t = json.loads(t_raw.decode("utf-8-sig"))
    ol, tl = o.get("launches", []), t.get("launches", [])
    um = {}
    for r in ol + tl:
        key = json.dumps(r, sort_keys=True, ensure_ascii=False)
        um.setdefault(key, r)
    union_all = sorted(um.values(), key=lambda r: str(r.get("ts", "")), reverse=True)
    dropped = union_all[50:]
    merged_launches = sorted(union_all[:50], key=lambda r: str(r.get("ts", "")))  # ASC (r245)
    print("launches union %d|%d -> union=%d cap50=%d dropped_oldest=%d" % (
        len(ol), len(tl), len(union_all), len(merged_launches), len(dropped)))
    if dropped:
        print("dropped ts range (must be oldest): %s .. %s" % (
            dropped[-1].get("ts"), dropped[0].get("ts")))
        assert str(dropped[0].get("ts", "")) <= str(merged_launches[0].get("ts", "")), \
            "cap must drop oldest only"
    ka = {json.dumps(r, sort_keys=True, ensure_ascii=False) for r in merged_launches}
    ba = {json.dumps(r, sort_keys=True, ensure_ascii=False) for r in ol + tl}
    assert ka <= ba, "kept entries must all come from union"
    merged = dict(o)
    lo, lt = o.get("last_tick"), t.get("last_tick")
    if isinstance(lo, dict) and isinstance(lt, dict):
        to, tt = str(lo.get("ts", "")), str(lt.get("ts", ""))
        if tt > to:
            merged["last_tick"] = lt
            pick = "theirs(bm-b %s > ours %s)" % (tt, to)
        elif tt == to:
            merged["last_tick"] = lo
            pick = "tie->HEAD(ours) %s" % (to)
        else:
            merged["last_tick"] = lo
            pick = "ours(HEAD %s >= theirs %s)" % (to, tt)
    else:
        pick = "last_tick non-dict faces -> keep ours"
    print("last_tick:", pick)
    merged["launches"] = merged_launches
    crlf = b"\r\n" in base_raw
    nl = "\r\n" if crlf else "\n"
    payload = json.dumps(merged, ensure_ascii=False, indent=1)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(payload.replace("\n", nl))
    chk = json.loads(io.open(path, encoding="utf-8-sig").read())
    assert isinstance(chk.get("last_tick"), dict), "last_tick must stay dict"
    assert chk["launches"] == merged_launches
    marker_sweep(path, io.open(path, "rb").read())
    report.append("mixed %s launches %d|%d -> %d, last_tick=%s" % (
        path, len(ol), len(tl), len(merged_launches), pick))


for p in TAKE_NEW:
    take_new(p)
for p in TAKE_STAGE3:
    take_stage3(p)
union_ledger(UNION_LEDGER)
union_jsonl(UNION_JSONL)
resolve_mixed(MIXED)

all_paths = TAKE_NEW + TAKE_STAGE3 + [UNION_LEDGER, UNION_JSONL, MIXED]
assert len(all_paths) == 28, len(all_paths)
for p in all_paths:                      # final marker sweep on written files
    marker_sweep(p, io.open(p, "rb").read())
print("== r307 resolve: 28/28 written, all gates PASS ==")
for r in report:
    print("  " + r.encode("gbk", "replace").decode("gbk"))
subprocess.run(["git", "add"] + all_paths, check=True)
print("git add 28 paths done")
