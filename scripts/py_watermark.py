"""Compute watermark probe (CEO order O-20260924-1136 section 4, T2 line item).

Objective utilization time-series for the O-1136 violation criterion:
  a runnable CPU-dense batch exists (backtest/factor/screen/build) AND machine
  py CPU sustained <70% of total capacity for 15min+ -> round report must name
  the violation (with cause and fix) OR prove the legal-idle whitelist
  (board fully closed + bandit queue empty + no runnable batch).

This probe records FACTS ONLY (deterministic, zero judgment):
  - machine CPU total + py CPU share (two-snapshot delta, compute_audit idiom)
  - hottest proc in CORE units -> local_batch_running (>=0.5 core sustained)
  - runnable-work inventory: open fleet tickets (ids), bandit open candidates,
    capability facts (Money02 bars present / core48 daily panel present)
Verdict (frozen at first run, do not tune by results):
  loaded_ok              max py CPU in window >= 70% (not sustained-low)
  py_low_with_work_cands py CPU <70% sustained >=15min AND work candidates
  py_low_board_clear     py CPU <70% sustained AND zero candidates (idle facts)
  insufficient_history   window span <15min or <2 samples (bootstrap)
Adjudication (violation vs legal idle) stays with the round report: the probe
cannot know lane ownership / by-design single-core builds / network-only lanes.

Writes: one append line per S6 run to results/watermark.jsonl (machine-local,
gitignored, 24h prune) - minimal write surface, fleet/audit probe paradigm.
Exit codes: 0 = normal (any verdict), 2 = sampling machinery failure.
Subcommands: probe (default) | selftest (offline unit tests)
"""
import glob
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERIES = os.path.join(ROOT, "results", "watermark.jsonl")
BANDIT = os.path.join(ROOT, "results", "bandit_queue.json")
TASKS_DIR = os.path.join(ROOT, "fleet", "tasks")
BARS_DIR = os.path.join(ROOT, "Money02", "data", "bars")
DAILY_DIR = os.path.join(ROOT, "data", "daily")

SAMPLE_WINDOW_S = 3.0
LOW_PY_LINE = 70.0        # O-1136: py CPU <70% of machine capacity
SUSTAIN_MIN = 15.0        # ... sustained 15min+ -> violation candidate
# _load_series retention MUST exceed SUSTAIN_MIN: with the filter equal to
# the test span, the oldest sample is dropped the moment its age reaches the
# span, so span_obs < SUSTAIN_MIN always held and the verdict face stayed
# permanently "insufficient_history" at the 10-min loop cadence (observed
# every round R94-R117; selftest fed _window_verdict synthetics directly and
# never exercised the production _load_series+_window_verdict pairing).
RETENTION_MIN = 2 * SUSTAIN_MIN
PRUNE_KEEP_MIN = 1440.0   # keep trailing 24h of the local series
LOCAL_BATCH_CORES = 0.5   # hottest proc eating >=0.5 core = local batch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compute_audit import cpu_total, core_count, python_procs  # reuse, no rewrite


def _delta_stats(p1, p2, elapsed, cores):
    """Pure math: two {pid: cpu_seconds} snapshots -> load facts.

    p1/p2 map pid -> cumulative CPU seconds; elapsed in seconds.
    """
    deltas = {}
    for pid, cpu2 in p2.items():
        cpu1 = p1.get(pid, cpu2)  # proc born inside window: delta 0 (conservative)
        deltas[pid] = max(0.0, cpu2 - cpu1)
    total_delta = sum(deltas.values())
    py_cpu_pct = min(100.0, total_delta / max(elapsed * cores, 1e-9) * 100.0)
    top_cores = (max(deltas.values()) / elapsed) if deltas else 0.0
    return {
        "py_cpu_pct": round(py_cpu_pct, 1),
        "py_procs": len(p2),
        "top_proc_cores": round(top_cores, 2),
        "local_batch_running": top_cores >= LOCAL_BATCH_CORES,
    }


def _scan_tickets(tasks_dir=TASKS_DIR):
    """Open (unclaimed) ticket ids - all priorities; signature = the ticket itself."""
    ids = []
    for p in sorted(glob.glob(os.path.join(tasks_dir, "T-*.json"))):
        try:
            with open(p, encoding="utf-8") as f:
                d = json.load(f)
            if d.get("status") == "open":
                ids.append(d.get("id") or os.path.basename(p)[:-5])
        except Exception:
            pass
    return ids


def _bandit_open(path=BANDIT):
    """Count engineering candidates with status 'open' (non-gated)."""
    try:
        with open(path, encoding="utf-8") as f:
            cands = json.load(f).get("engineering_candidates", [])
        return sum(1 for c in cands if c.get("status") == "open")
    except Exception:
        return 0


def _capability_facts(bars_dir=BARS_DIR, daily_dir=DAILY_DIR):
    return {
        "bars_present": os.path.isdir(bars_dir),
        "daily_panel": len(glob.glob(os.path.join(daily_dir, "*.csv"))) > 0,
    }


def _append_series(path, record, now, keep_min=PRUNE_KEEP_MIN):
    """Append one line, prune older than keep_min. Atomic tmp+replace."""
    lines = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            lines = [ln for ln in f.read().splitlines() if ln.strip()]
    kept = []
    for ln in lines:
        try:
            if now - float(json.loads(ln).get("epoch", 0)) <= keep_min * 60:
                kept.append(ln)
        except Exception:
            pass  # drop corrupt lines rather than crash the chain
    kept.append(json.dumps(record, ensure_ascii=False))
    tmp = path + ".tmp"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(tmp, "w", encoding="utf-8") as f:
        f.write("\n".join(kept) + "\n")
    os.replace(tmp, path)
    return len(kept)


def _load_series(path, now, span_min=SUSTAIN_MIN):
    """Return samples within the trailing span_min window (epoch + py_cpu_pct)."""
    out = []
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as f:
        for ln in f.read().splitlines():
            try:
                d = json.loads(ln)
                if now - float(d.get("epoch", 0)) <= span_min * 60:
                    out.append((float(d.get("epoch", 0)),
                                float(d.get("py_cpu_pct", 0.0))))
            except Exception:
                pass
    return out


def _window_verdict(samples, work_cands, line=LOW_PY_LINE, span_min=SUSTAIN_MIN):
    """Frozen verdict from trailing samples. samples = [(epoch, py_cpu_pct)]."""
    if len(samples) < 2:
        return "insufficient_history", {"n": len(samples), "span_min": 0.0}
    span_min_obs = (max(e for e, _ in samples) - min(e for e, _ in samples)) / 60.0
    if span_min_obs < span_min:
        return "insufficient_history", {"n": len(samples),
                                        "span_min": round(span_min_obs, 1)}
    max_py = max(v for _, v in samples)
    avg_py = sum(v for _, v in samples) / len(samples)
    facts = {"n": len(samples), "span_min": round(span_min_obs, 1),
             "avg_py_cpu_pct": round(avg_py, 1), "max_py_cpu_pct": round(max_py, 1)}
    if max_py >= line:
        return "loaded_ok", facts
    if work_cands:
        return "py_low_with_work_cands", facts
    return "py_low_board_clear", facts


def probe():
    now = time.time()
    cores = core_count()
    p1 = {pid: cpu_s for pid, _name, cpu_s, _age in python_procs()}
    time.sleep(SAMPLE_WINDOW_S)
    p2 = {pid: cpu_s for pid, _name, cpu_s, _age in python_procs()}
    samp = _delta_stats(p1, p2, SAMPLE_WINDOW_S, cores)
    cpu_tot = cpu_total()
    if cpu_tot is None and samp is None:
        print("watermark probe: sampling machinery failure", file=sys.stderr)
        return 2
    ticket_ids = _scan_tickets()
    bandit_open = _bandit_open()
    caps = _capability_facts()
    record = {
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "epoch": round(now, 0),
        "machine": _machine_id(),
        "cpu_total_pct": cpu_tot,
        "cores": cores,
        "py_cpu_pct": samp["py_cpu_pct"],
        "py_procs": samp["py_procs"],
        "top_proc_cores": samp["top_proc_cores"],
        "local_batch_running": samp["local_batch_running"],
        "open_tickets": len(ticket_ids),
        "open_ticket_ids": ticket_ids,
        "bandit_open": bandit_open,
        "bars_present": caps["bars_present"],
        "daily_panel": caps["daily_panel"],
    }
    n_kept = _append_series(SERIES, record, now)
    samples = _load_series(SERIES, now, span_min=RETENTION_MIN)
    work_cands = (len(ticket_ids) > 0 or bandit_open > 0
                  or samp["local_batch_running"])
    verdict, facts = _window_verdict(samples, work_cands)
    out = dict(record)
    out["series_kept"] = n_kept
    out["window"] = facts
    out["verdict"] = verdict
    print(json.dumps(out, ensure_ascii=False))
    return 0


def _machine_id():
    try:
        with open(os.path.join(ROOT, "fleet", "machine.json"),
                  encoding="utf-8-sig") as f:
            return json.load(f).get("machine_id", "?")
    except Exception:
        return "?"


def selftest():
    import shutil
    import tempfile
    ok = [True]

    def check(name, cond):
        if not cond:
            ok[0] = False
            print("FAIL:", name)
        else:
            print("PASS:", name)

    # 1) delta math: 2 cores busy of 16 over 3s -> 12.5% machine, batch detected
    p1 = {10: 100.0, 11: 50.0}
    p2 = {10: 103.0, 11: 54.0}  # deltas 3s and 4s over 3s window
    st = _delta_stats(p1, p2, 3.0, 16)
    check("delta py_cpu_pct", abs(st["py_cpu_pct"] - (7.0 / 48.0 * 100)) < 0.05)
    check("delta top cores", abs(st["top_proc_cores"] - (4.0 / 3.0)) < 0.05)
    check("batch detected (>=0.5 core)", st["local_batch_running"])
    # idle case
    st0 = _delta_stats({10: 5.0}, {10: 5.05}, 3.0, 16)
    check("no batch when tiny delta", not st0["local_batch_running"])
    # newborn proc conservative
    stn = _delta_stats({}, {99: 42.0}, 3.0, 16)
    check("newborn proc delta 0", stn["py_cpu_pct"] == 0.0
          and not stn["local_batch_running"])

    # 2) window verdict branches on synthetic samples
    t0 = 1000.0
    s_load = [(t0, 80.0), (t0 + 300, 75.0), (t0 + 950, 82.0)]
    v, f = _window_verdict(s_load, True)
    check("loaded_ok on high max", v == "loaded_ok" and f["n"] == 3)
    s_low = [(t0, 5.0), (t0 + 300, 4.0), (t0 + 950, 6.0)]
    v, f = _window_verdict(s_low, True)
    check("py_low_with_work_cands", v == "py_low_with_work_cands"
          and abs(f["span_min"] - 15.8) < 0.1)
    v, _ = _window_verdict(s_low, False)
    check("py_low_board_clear", v == "py_low_board_clear")
    v, f = _window_verdict([(t0, 5.0), (t0 + 120, 5.0)], True)
    check("insufficient span", v == "insufficient_history")
    v, _ = _window_verdict([(t0, 5.0)], True)
    check("insufficient n", v == "insufficient_history")
    # one spike inside window breaks "sustained low"
    s_spike = [(t0, 5.0), (t0 + 300, 75.0), (t0 + 950, 5.0)]
    v, _ = _window_verdict(s_spike, True)
    check("spike breaks sustained-low", v == "loaded_ok")

    # 2b) production pairing: _load_series retention must leave enough
    # history for the span test (filter==test span left the verdict face
    # structurally unreachable at the ~10-11min loop cadence)
    tmpd2 = tempfile.mkdtemp()
    try:
        path2 = os.path.join(tmpd2, "watermark.jsonl")
        now2 = 200000.0
        for age_min in (33.0, 22.0, 11.0, 0.0):   # realistic probe cadence
            with open(path2, "a", encoding="utf-8") as f:
                f.write(json.dumps({"epoch": now2 - age_min * 60,
                                    "py_cpu_pct": 3.0}) + "\n")
        v_bug, f_bug = _window_verdict(_load_series(path2, now2), False)
        check("old span-equal filter dead (n<3 or span<15)",
              v_bug == "insufficient_history")
        kept = _load_series(path2, now2, span_min=RETENTION_MIN)
        v_new, f_new = _window_verdict(kept, False)
        check("retention 2x -> board_clear fires",
              v_new == "py_low_board_clear" and f_new["n"] == 3
              and f_new["span_min"] >= 15.0)
        v_new2, _ = _window_verdict(kept, True)
        check("retention 2x -> work_cands fires",
              v_new2 == "py_low_with_work_cands")
    finally:
        shutil.rmtree(tmpd2, ignore_errors=True)

    # 3) series append + prune + reload roundtrip in temp dir
    tmpd = tempfile.mkdtemp()
    try:
        path = os.path.join(tmpd, "watermark.jsonl")
        now = 100000.0
        old = {"epoch": now - 20000 * 60, "py_cpu_pct": 1.0}   # >24h old
        new1 = {"epoch": now - 20 * 60, "py_cpu_pct": 3.0}
        new2 = {"epoch": now, "py_cpu_pct": 4.0}
        n = _append_series(path, old, now)
        n = _append_series(path, new1, now)
        n = _append_series(path, new2, now)
        check("prune drops >24h", n == 2)
        with open(path, encoding="utf-8") as f:
            lines = [json.loads(x) for x in f.read().splitlines()]
        check("series survives roundtrip", len(lines) == 2
              and lines[0]["py_cpu_pct"] == 3.0)
        # corrupt line dropped, not fatal
        with open(path, "a", encoding="utf-8") as f:
            f.write("{corrupt\n")
        n = _append_series(path, {"epoch": now + 60, "py_cpu_pct": 2.0}, now + 60)
        check("corrupt line dropped", n == 3)
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)

    # 4) ticket scan + bandit count on synthetic fixtures
    tmpd = tempfile.mkdtemp()
    try:
        td = os.path.join(tmpd, "tasks")
        os.makedirs(td)
        for tid, st_ in (("T-1", "open"), ("T-2", "claimed"), ("T-3", "open")):
            with open(os.path.join(td, tid + ".json"), "w",
                      encoding="utf-8") as f:
                json.dump({"id": tid, "status": st_}, f)
        check("ticket scan open only", _scan_tickets(td) == ["T-1", "T-3"])
        with open(os.path.join(td, "bad.json"), "w", encoding="utf-8") as f:
            f.write("{broken")
        check("ticket scan tolerates corrupt", _scan_tickets(td) == ["T-1", "T-3"])
        bp = os.path.join(tmpd, "bandit.json")
        with open(bp, "w", encoding="utf-8") as f:
            json.dump({"engineering_candidates": [
                {"name": "a", "status": "open"},
                {"name": "b", "status": "gated-P1"},
                {"name": "c", "status": "open"},
            ]}, f)
        check("bandit open count", _bandit_open(bp) == 2)
        check("bandit missing file -> 0", _bandit_open(
            os.path.join(tmpd, "nope.json")) == 0)
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)

    print("selftest:", "ALL PASS" if ok[0] else "FAIL")
    return 0 if ok[0] else 1


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "probe"
    if arg == "selftest":
        return selftest()
    if arg == "probe":
        return probe()
    print("usage: py_watermark.py [probe|selftest]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
