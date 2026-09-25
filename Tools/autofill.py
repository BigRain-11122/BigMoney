"""Tools/autofill.py -- C8 auto-fill leg (O-20260924-2100 s2.2, T-36).

Deterministic, zero-LLM fill: the pool (results/runnable_pool.json) is
the ONLY runnable face; when a machine's python CPU sits below 70% while
a ready, lane-legal shard is on the pool, this script launches the
shard's runner detached at BelowNormal priority -- no round, no MSG, no
human in the loop (O-2100: fill latency ready->running <= 10 min).

Contract:
  * NEVER edits the pool (single-writer = round control plane). Running
    state lives in results/autofill_state.json + the runner's own
    checkpoint files.
  * No double-run: skips any entry whose runner is already alive
    (process scan by runner path), and any shard owned by another
    machine with a fresh heartbeat.
  * Stale takeover (O-2100 s2.4): shard owner heartbeat
    (fleet/machines/<id>.json last_seen) stale > 20 min -> shard is
    takeable (checkpoint resume makes takeover safe; concurrent appends
    are guarded by the runner-side final compaction keep-last).
  * Lane guard (F-08/R31/R65): entry.lane_owner null/ANY = any machine;
    named = that machine only.
  * Silent law: logs to logs/autofill.log only.

Exit codes: 0 = normal (incl. honest no-op), 2 = mechanism fault
(pool unreadable / sampler failure) -- report honestly, never mask.
selftest = offline decision matrix, no real launches.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POOL = os.path.join(ROOT, "results", "runnable_pool.json")
STATE = os.path.join(ROOT, "results", "autofill_state.json")
LOG = os.path.join(ROOT, "logs", "autofill.log")
MACHINES = os.path.join(ROOT, "fleet", "machines")
MACHINE_JSON = os.path.join(ROOT, "fleet", "machine.json")

LOW_PY_LINE = 70.0        # O-1136: py CPU < 70% of machine capacity
SAMPLE_S = 2.0            # instantaneous py-CPU sample window
STALE_MIN = 20.0          # O-2100 s2.4: shard-owner heartbeat staleness
FILL_TARGET_MIN = 10.0    # O-2100 s2.2 hard target
DETACHED = (0x00000008 | 0x00000200)   # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _log(msg):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a", encoding="ascii", errors="replace") as fh:
        fh.write(f"{_now()} {msg}\n")


def _machine_id():
    try:
        with open(MACHINE_JSON, encoding="utf-8") as fh:
            return json.load(fh).get("machine_id", "")
    except Exception:
        return ""


def _py_cpu_pct(window=SAMPLE_S):
    """Instantaneous python-process CPU load as % of machine capacity."""
    import psutil
    procs = [p for p in psutil.process_iter(["name"])
             if (p.info["name"] or "").lower().startswith("python")]
    s1 = {p.pid: sum(p.cpu_times()[:2]) for p in procs}
    time.sleep(window)
    delta = 0.0
    cores = psutil.cpu_count() or 1
    for p in psutil.process_iter(["name"]):
        if (p.info["name"] or "").lower().startswith("python"):
            try:
                prev = s1.get(p.pid)
                if prev is not None:
                    delta += sum(p.cpu_times()[:2]) - prev
            except Exception:
                pass
    return round(100.0 * delta / (window * cores), 1)


def _hb_age_min(machine_id):
    """Age (minutes) of a machine's heartbeat last_seen; None if absent."""
    path = os.path.join(MACHINES, machine_id + ".json")
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            ls = json.load(fh).get("last_seen")
        return (datetime.now() - datetime.strptime(
            ls, "%Y-%m-%d %H:%M:%S")).total_seconds() / 60.0
    except Exception:
        return None


def _since_age_min(shard):
    """Age (minutes) of a shard's owner_since claim-stamp; None if absent.

    r178 bm-b: owner_since is a control-plane proof of life (the pre-claim
    commit push). A machine mid-LONG-round only writes its heartbeat at
    round end (S7), so heartbeat age alone misreads a live owner as
    stale (12:40 deep-dA false-takeover live-fire) and causes same-tick
    dual burns."""
    s = shard.get("owner_since")
    if not s:
        return None
    try:
        return (datetime.now() - datetime.strptime(
            s, "%Y-%m-%d %H:%M:%S")).total_seconds() / 60.0
    except Exception:
        return None


def _owner_age_min(owner, shard):
    """Effective owner freshness = freshest of heartbeat / claim-stamp."""
    ages = [a for a in (_hb_age_min(owner), _since_age_min(shard))
            if a is not None]
    return min(ages) if ages else None


def _runner_alive(runner_rel):
    """True if a python process is already running this entry's runner."""
    import psutil
    needle = runner_rel.replace("/", "\\").lower()
    for p in psutil.process_iter(["name", "cmdline"]):
        try:
            if (p.info["name"] or "").lower().startswith("python"):
                cmd = " ".join(p.info["cmdline"] or []).lower()
                if needle in cmd.replace("/", "\\"):
                    return True
        except Exception:
            continue
    return False


def _load_state():
    if os.path.exists(STATE):
        try:
            with open(STATE, encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            pass
    return {"launches": []}


def _save_state(s):
    tmp = STATE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(s, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, STATE)


def _pick(pool, myid):
    """Highest-priority ready, lane-legal, not-running entry + shard."""
    entries = [e for e in pool.get("entries", [])
               if e.get("status") == "ready" and e.get("runner")]
    entries.sort(key=lambda e: e.get("priority", 99))
    for e in entries:
        lo = e.get("lane_owner")
        if lo not in (None, "", "ANY", myid):
            _log(f"skip {e['id']}: lane owner {lo} != {myid}")
            continue
        if not e.get("workers_plan"):
            # O-20260924-2130 s1.1: ready batch registration MUST carry a
            # multi-core plan; single-core long burns are a violation.
            _log(f"skip {e['id']}: no workers_plan (O-2130 multi-core law)")
            continue
        if _runner_alive(e["runner"]):
            _log(f"skip {e['id']}: runner already alive (no double-run)")
            continue
        for sh in e.get("shards", []):
            ow = sh.get("owner")
            if ow and ow != myid:
                age = _owner_age_min(ow, sh)
                if age is not None and age < STALE_MIN:
                    _log(f"skip {e['id']}/{sh['key']}: owner {ow} "
                         f"fresh ({age:.0f}min)")
                    continue
                _log(f"takeover {e['id']}/{sh['key']}: owner {ow} "
                     f"stale/absent ({age}min) -> takeable")
            return e, sh
        _log(f"skip {e['id']}: no takeable shard")
    return None, None


def tick(dry=False):
    rec = {"ts": _now(), "machine": _machine_id()}
    try:
        py = _py_cpu_pct()
    except Exception as ex:
        _log(f"tick ABORT sampler fault: {ex}")
        return 2
    rec["py_cpu_pct"] = py
    state = _load_state()
    if py >= LOW_PY_LINE:
        rec["verdict"] = "py_loaded"
        state["last_tick"] = rec
        _save_state(state)
        _log(f"tick py={py}% >= {LOW_PY_LINE} -> loaded, no fill")
        return 0
    try:
        with open(POOL, encoding="utf-8") as fh:
            pool = json.load(fh)
    except FileNotFoundError:
        rec["verdict"] = "pool_absent"
        state["last_tick"] = rec
        _save_state(state)
        _log("tick pool absent -> honest no-op")
        return 0
    except Exception as ex:
        _log(f"tick ABORT pool unreadable: {ex}")
        return 2
    e, sh = _pick(pool, rec["machine"])
    if not e:
        rec["verdict"] = "pool_empty_or_busy"
        state["last_tick"] = rec
        _save_state(state)
        _log(f"tick py={py}% pool has no takeable shard -> no-op")
        return 0
    cmd = [sys.executable, os.path.join(ROOT, e["runner"])] + \
        list(e.get("runner_args", []))
    try:
        ent = datetime.strptime(e.get("entered_at", rec["ts"]),
                                "%Y-%m-%d %H:%M:%S")
        latency = round((datetime.now() - ent).total_seconds() / 60.0, 1)
    except Exception:
        latency = None
    if dry:
        rec.update({"verdict": "dry_launch", "entry": e["id"],
                    "shard": sh.get("key"), "cmd": cmd,
                    "fill_latency_min": latency})
        state["last_tick"] = rec
        _save_state(state)
        print(json.dumps(rec, ensure_ascii=False))
        return 0
    os.makedirs(os.path.join(ROOT, "logs"), exist_ok=True)
    out = os.path.join(ROOT, "logs", f"autofill_{e['id']}.log")
    with open(out, "a", encoding="utf-8") as lf:
        p = subprocess.Popen(cmd, cwd=ROOT, stdout=lf,
                             stderr=subprocess.STDOUT,
                             creationflags=DETACHED, close_fds=True)
    try:
        import psutil
        psutil.Process(p.pid).nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    except Exception:
        pass
    rec.update({"verdict": "launched", "entry": e["id"],
                "shard": sh.get("key"), "pid": p.pid,
                "fill_latency_min": latency,
                "target_met": (latency is None
                               or latency <= FILL_TARGET_MIN)})
    state["launches"].append(rec)
    state["launches"] = state["launches"][-50:]
    state["last_tick"] = rec
    _save_state(state)
    _log(f"C8 LAUNCH {e['id']}/{sh.get('key')} pid={p.pid} "
         f"py={py}% latency={latency}min target_met={rec['target_met']}")
    print(json.dumps(rec, ensure_ascii=False))
    return 0


def status():
    s = _load_state()
    print(json.dumps(s.get("last_tick", {}), ensure_ascii=False, indent=1))
    print(f"launches total: {len(s.get('launches', []))}")


def selftest():
    import tempfile
    global POOL, STATE, MACHINES, LOG, _py_cpu_pct, _runner_alive
    ok_all = True

    def ok(name, cond):
        nonlocal ok_all
        ok_all &= bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")

    print("C8 autofill selftest:")
    with tempfile.TemporaryDirectory() as tmp:
        POOL = os.path.join(tmp, "runnable_pool.json")
        STATE = os.path.join(tmp, "autofill_state.json")
        LOG = os.path.join(tmp, "autofill.log")
        MACHINES = os.path.join(tmp, "machines")
        os.makedirs(MACHINES)
        entry = {"id": "E1", "status": "ready",
                 "runner": "scripts/fake_runner.py",
                 "runner_args": ["run"], "lane_owner": None,
                 "priority": 1, "entered_at": "2026-09-24 20:00:00",
                 "workers_plan": {"workers": 12, "priority": "BelowNormal"},
                 "shards": [{"key": "s0", "status": "ready",
                             "owner": None}]}
        # S1 py-loaded -> no fill
        def hi(w=SAMPLE_S):
            return 88.8
        orig = _py_cpu_pct
        _py_cpu_pct = hi
        with open(POOL, "w", encoding="utf-8") as fh:
            json.dump({"entries": [dict(entry)]}, fh)
        rc = tick(dry=True)
        st = _load_state()["last_tick"]
        ok("S1 py_loaded no fill", rc == 0 and st["verdict"] == "py_loaded")
        # S2 py-low + empty pool -> honest no-op
        _py_cpu_pct = lambda w=SAMPLE_S: 5.0
        with open(POOL, "w", encoding="utf-8") as fh:
            json.dump({"entries": []}, fh)
        rc = tick(dry=True)
        ok("S2 pool empty no-op", rc == 0
           and _load_state()["last_tick"]["verdict"] == "pool_empty_or_busy")
        # S3 lane guard: named owner != me -> skip
        with open(POOL, "w", encoding="utf-8") as fh:
            json.dump({"entries": [dict(entry, lane_owner="bm-z")]}, fh)
        rc = tick(dry=True)
        ok("S3 lane guard skip",
           _load_state()["last_tick"]["verdict"] == "pool_empty_or_busy")
        # S4 already-running guard
        with open(POOL, "w", encoding="utf-8") as fh:
            json.dump({"entries": [dict(entry)]}, fh)
        _runner_alive_orig = _runner_alive
        _runner_alive = lambda r: True
        rc = tick(dry=True)
        ok("S4 no double-run (runner alive -> skip)",
           _load_state()["last_tick"]["verdict"] == "pool_empty_or_busy")
        _runner_alive = _runner_alive_orig
        # S5 stale takeover: owner hb stale -> dry launch with latency
        with open(os.path.join(MACHINES, "bm-z.json"), "w",
                  encoding="utf-8") as fh:
            json.dump({"last_seen": "2026-09-24 18:00:00"}, fh)
        ent2 = dict(entry, shards=[{"key": "s0", "status": "ready",
                                    "owner": "bm-z"}])
        with open(POOL, "w", encoding="utf-8") as fh:
            json.dump({"entries": [ent2]}, fh)
        rc = tick(dry=True)
        st = _load_state()["last_tick"]
        ok("S5 stale takeover dry-launch", rc == 0
           and st["verdict"] == "dry_launch" and st["entry"] == "E1"
           and st["fill_latency_min"] is not None)
        # S6 fresh owner -> skip
        with open(os.path.join(MACHINES, "bm-z.json"), "w",
                  encoding="utf-8") as fh:
            json.dump({"last_seen": _now()}, fh)
        rc = tick(dry=True)
        ok("S6 fresh owner skip",
           _load_state()["last_tick"]["verdict"] == "pool_empty_or_busy")
        # S9 owner_since freshness (r178): hb stale but claim-stamp fresh
        # -> skip (no false takeover of a live long-round owner)
        with open(os.path.join(MACHINES, "bm-z.json"), "w",
                  encoding="utf-8") as fh:
            json.dump({"last_seen": "2026-09-24 18:00:00"}, fh)
        ent3 = dict(entry, shards=[{"key": "s0", "status": "ready",
                                    "owner": "bm-z",
                                    "owner_since": _now()}])
        with open(POOL, "w", encoding="utf-8") as fh:
            json.dump({"entries": [ent3]}, fh)
        rc = tick(dry=True)
        ok("S9 owner_since fresh -> skip (no false takeover)",
           _load_state()["last_tick"]["verdict"] == "pool_empty_or_busy")
        # S10 both stale -> takeover still legal (dead-owner regression)
        ent4 = dict(entry, shards=[{"key": "s0", "status": "ready",
                                    "owner": "bm-z",
                                    "owner_since": "2026-09-24 18:00:00"}])
        with open(POOL, "w", encoding="utf-8") as fh:
            json.dump({"entries": [ent4]}, fh)
        rc = tick(dry=True)
        ok("S10 both-stale takeover (dead-owner regression)",
           _load_state()["last_tick"]["verdict"] == "dry_launch")
        # S8 O-2130 multi-core law: no workers_plan -> skip
        nowp = dict(entry, shards=[{"key": "s0", "status": "ready",
                                    "owner": None}])
        nowp.pop("workers_plan")
        with open(POOL, "w", encoding="utf-8") as fh:
            json.dump({"entries": [nowp]}, fh)
        rc = tick(dry=True)
        ok("S8 no workers_plan -> skip (O-2130)",
           _load_state()["last_tick"]["verdict"] == "pool_empty_or_busy")
        _py_cpu_pct = orig
    # S7 sampler sanity on the real machine (pure read)
    py = _py_cpu_pct(window=0.5)
    ok("S7 live py sample in [0,100]", 0.0 <= py <= 100.0)
    print("SELFTEST", "ALL PASS" if ok_all else "FAIL")
    return 0 if ok_all else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", default="tick",
                    choices=["tick", "status", "selftest"])
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    if a.cmd == "tick":
        sys.exit(tick(dry=a.dry))
    if a.cmd == "status":
        status()
        sys.exit(0)
    sys.exit(selftest())


if __name__ == "__main__":
    main()
