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
  * Mid-rebase/mid-merge guard (r201): .git/rebase-merge|rebase-apply|
    MERGE_HEAD present -> honest no-op, no state write, no launch
    (live case: 20:00 tick fired on a conflicted tree, read the marker
    file, fresh-fallback wiped 49 launches -> 1 and launched unclaimed
    during the session-dead rebase window, r159/r199 face).
  * Corrupt-state refusal (r201): an EXISTING autofill_state.json that
    fails to parse aborts the tick (exit 2) instead of silently saving
    a fresh {"launches": []} over it.
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
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POOL = os.path.join(ROOT, "results", "runnable_pool.json")
STATE = os.path.join(ROOT, "results", "autofill_state.json")
LOG = os.path.join(ROOT, "logs", "autofill.log")
MACHINES = os.path.join(ROOT, "fleet", "machines")
MACHINE_JSON = os.path.join(ROOT, "fleet", "machine.json")
_GIT_DIR = os.path.join(ROOT, ".git")

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
    """Age (minutes) of a machine's heartbeat last_seen; None if absent.

    r163 bm-a: production heartbeat files carry the ISO format with UTC
    offset (T-04 F5 clock_read era, e.g. 2026-09-25T13:29:04+08:00); the
    legacy strptime silently returned None for EVERY production read,
    leaving the takeover gate heartbeat-blind (13:40:01 deep-dC live-fire:
    owner_since 43min alone opened a "legal" takeover on a live owner).
    Parse both formats; tz-aware values compared against aware-now."""
    path = os.path.join(MACHINES, machine_id + ".json")
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            ls = str(json.load(fh).get("last_seen"))
        if "T" in ls:                # ISO w/ offset (production format)
            dt = datetime.fromisoformat(ls)
            now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
        else:                        # legacy "%Y-%m-%d %H:%M:%S"
            dt = datetime.strptime(ls, "%Y-%m-%d %H:%M:%S")
            now = datetime.now()
        return (now - dt).total_seconds() / 60.0
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


class _CorruptState(Exception):
    """Existing autofill_state.json fails to parse (r201: refuse, never wipe)."""


def _load_state():
    if os.path.exists(STATE):
        try:
            with open(STATE, encoding="utf-8") as fh:
                return json.load(fh)
        except Exception as ex:
            # r201: a parse-failed EXISTING file must never fall back to a
            # fresh state -- the next _save_state would wipe the launch
            # history (live case: mid-rebase marker file, 49 launches -> 1).
            raise _CorruptState(str(ex))
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
            if sh.get("status") == "done":
                # done shards never re-fire (r180: entry left "ready" +
                # done shard wedged the picker into no-op relaunches)
                continue
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
    for probe in ("rebase-merge", "rebase-apply", "MERGE_HEAD"):
        if os.path.exists(os.path.join(_GIT_DIR, probe)):
            _log(f"tick no-op: git mid-operation ({probe}) -- conflicted "
                 f"tree, no state write, no launch")
            print(f"no-op: git mid-operation ({probe})")
            return 0
    rec = {"ts": _now(), "machine": _machine_id()}
    try:
        py = _py_cpu_pct()
    except Exception as ex:
        _log(f"tick ABORT sampler fault: {ex}")
        return 2
    rec["py_cpu_pct"] = py
    try:
        state = _load_state()
    except _CorruptState as ex:
        _log(f"tick ABORT corrupt autofill_state (refuse wipe, r201): {ex}")
        print(f"ABORT corrupt autofill_state.json: {ex}")
        return 2
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
    try:
        s = _load_state()
    except _CorruptState as ex:
        print(f"corrupt autofill_state.json: {ex}")
        sys.exit(2)
    print(json.dumps(s.get("last_tick", {}), ensure_ascii=False, indent=1))
    print(f"launches total: {len(s.get('launches', []))}")


def selftest():
    import tempfile
    global POOL, STATE, MACHINES, LOG, _GIT_DIR, _py_cpu_pct, _runner_alive
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
        # (r163: production ISO format pairing -- fixtures must write
        # what production writes, R117 hermetic-production law)
        with open(os.path.join(MACHINES, "bm-z.json"), "w",
                  encoding="utf-8") as fh:
            json.dump({"last_seen": (datetime.now() - timedelta(
                minutes=30)).astimezone().isoformat(timespec="seconds")},
                fh)
        ent2 = dict(entry, shards=[{"key": "s0", "status": "ready",
                                    "owner": "bm-z"}])
        with open(POOL, "w", encoding="utf-8") as fh:
            json.dump({"entries": [ent2]}, fh)
        rc = tick(dry=True)
        st = _load_state()["last_tick"]
        ok("S5 stale takeover dry-launch", rc == 0
           and st["verdict"] == "dry_launch" and st["entry"] == "E1"
           and st["fill_latency_min"] is not None)
        # S6 fresh owner -> skip (r163: production ISO format pairing)
        with open(os.path.join(MACHINES, "bm-z.json"), "w",
                  encoding="utf-8") as fh:
            json.dump({"last_seen": datetime.now().astimezone().isoformat(
                timespec="seconds")}, fh)
        rc = tick(dry=True)
        ok("S6 fresh owner skip",
           _load_state()["last_tick"]["verdict"] == "pool_empty_or_busy")
        # S9 owner_since freshness (r178): hb stale but claim-stamp fresh
        # -> skip (no false takeover of a live long-round owner)
        # (r163: production ISO format pairing)
        with open(os.path.join(MACHINES, "bm-z.json"), "w",
                  encoding="utf-8") as fh:
            json.dump({"last_seen": (datetime.now() - timedelta(
                minutes=30)).astimezone().isoformat(timespec="seconds")},
                fh)
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
        # S11 done-shard guard (r180): ready entry + all shards done
        # -> no re-fire even when unowned (wedge regression)
        ent5 = dict(entry, shards=[{"key": "s0", "status": "done",
                                    "owner": None}])
        with open(POOL, "w", encoding="utf-8") as fh:
            json.dump({"entries": [ent5]}, fh)
        rc = tick(dry=True)
        ok("S11 done-shard skip (no re-fire)",
           _load_state()["last_tick"]["verdict"] == "pool_empty_or_busy")
        # S12 mixed shards: done shard skipped, ready sibling picked
        ent6 = dict(entry, shards=[{"key": "s0", "status": "done",
                                    "owner": None},
                                   {"key": "s1", "status": "ready",
                                    "owner": None}])
        with open(POOL, "w", encoding="utf-8") as fh:
            json.dump({"entries": [ent6]}, fh)
        rc = tick(dry=True)
        st = _load_state()["last_tick"]
        ok("S12 mixed shards -> picks ready sibling",
           st["verdict"] == "dry_launch" and st["shard"] == "s1")
        # S13 heartbeat format pairing (r163): production ISO last_seen
        # parses to a real age (legacy strptime returned None for every
        # production read = heartbeat-blind takeover gate); garbage ->
        # None; legacy format still parses (backward compat)
        with open(os.path.join(MACHINES, "bm-z.json"), "w",
                  encoding="utf-8") as fh:
            json.dump({"last_seen": (datetime.now() - timedelta(
                minutes=30)).astimezone().isoformat(timespec="seconds")},
                fh)
        age13 = _hb_age_min("bm-z")
        ok("S13 production ISO heartbeat parses (not None)",
           age13 is not None and 29.0 < age13 < 32.0)
        with open(os.path.join(MACHINES, "bm-z.json"), "w",
                  encoding="utf-8") as fh:
            json.dump({"last_seen": "2026-09-24 18:00:00"}, fh)
        age13b = _hb_age_min("bm-z")
        ok("S13b legacy heartbeat format still parses",
           age13b is not None and age13b > 1000.0)
        with open(os.path.join(MACHINES, "bm-z.json"), "w",
                  encoding="utf-8") as fh:
            json.dump({"last_seen": "not-a-timestamp"}, fh)
        ok("S13c garbage heartbeat -> None", _hb_age_min("bm-z") is None)
        # S14 mid-rebase guard (r201): conflicted tree -> honest no-op,
        # no state write, no launch (live case: tick fired on a mid-rebase
        # tree, fresh-fallback wiped the launches history, launched
        # unclaimed during the session-dead rebase window)
        _git_orig = _GIT_DIR
        _GIT_DIR = os.path.join(tmp, "fake_git")
        os.makedirs(os.path.join(_GIT_DIR, "rebase-merge"))
        with open(POOL, "w", encoding="utf-8") as fh:
            json.dump({"entries": [dict(entry)]}, fh)
        before = open(STATE, "rb").read()
        rc = tick(dry=True)
        after = open(STATE, "rb").read()
        logtail = open(LOG, encoding="ascii", errors="replace").read()
        ok("S14 mid-rebase guard no-op + zero state write",
           rc == 0 and before == after and "mid-operation" in logtail)
        os.rmdir(os.path.join(_GIT_DIR, "rebase-merge"))
        _GIT_DIR = _git_orig
        # S14b corrupt-state refusal (r201): marker-poisoned EXISTING
        # state file -> tick exit 2 + file byte-identical (anti-wipe)
        with open(STATE, "w", encoding="utf-8") as fh:
            fh.write('{"launches": [{"x": 1}]\n<<<<<<< ours\n}')
        before = open(STATE, "rb").read()
        rc = tick(dry=True)
        after = open(STATE, "rb").read()
        ok("S14b corrupt state -> exit 2 + no wipe",
           rc == 2 and before == after)
        # S14c absent state still fresh-starts (first-run compat)
        os.remove(STATE)
        rc = tick(dry=True)
        ok("S14c absent state -> fresh start (compat)",
           rc == 0 and _load_state()["last_tick"]["verdict"] == "dry_launch")
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
