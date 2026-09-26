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
  * Crash-loop token fuse (O-20260926-0947 s2, T-77 slice-2): a runner
    that died without landing its shard (own launch record, runner not
    alive, shard still not done past FUSE_CONFIRM_MIN) is CONFIRMED into
    results/crash_fuse.json keyed by runner+args+launch-time code hash;
    relaunch of the SAME hash is REFUSED (fix-first -- each crash-relaunch
    cycle burns loop-session API tokens, r175/r198 families). Editing the
    runner (hash change) auto-clears the fuse; refusals are counted and
    visible. Corrupt existing fuse file = refuse-wipe abort (r201 law).
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
FUSE = os.path.join(ROOT, "results", "crash_fuse.json")
LOG = os.path.join(ROOT, "logs", "autofill.log")
MACHINES = os.path.join(ROOT, "fleet", "machines")
MACHINE_JSON = os.path.join(ROOT, "fleet", "machine.json")
_GIT_DIR = os.path.join(ROOT, ".git")

LOW_PY_LINE = 70.0        # O-1136: py CPU < 70% of machine capacity
SAMPLE_S = 2.0            # instantaneous py-CPU sample window
STALE_MIN = 20.0          # O-2100 s2.4: shard-owner heartbeat staleness
FILL_TARGET_MIN = 10.0    # O-2100 s2.2 hard target
FUSE_CONFIRM_MIN = 25.0   # O-0947: crash confirm window -- > one flip
                          # window (r224 landed->flip lag) + margin, so a
                          # SUCCESSFUL-but-unflipped run is never counted
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


class _CorruptFuse(Exception):
    """Existing crash_fuse.json fails to parse (r201 law: refuse, no wipe)."""


def _load_fuse():
    if os.path.exists(FUSE):
        try:
            with open(FUSE, encoding="utf-8") as fh:
                return json.load(fh)
        except Exception as ex:
            raise _CorruptFuse(str(ex))
    return {"sigs": {}}


def _save_fuse(f):
    tmp = FUSE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(f, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, FUSE)


def _sha16(path):
    """Launch-time code version stamp: sha256[:16] of the runner file
    bytes (None if absent). Same hash after a crash = same version =
    fix-first refusal; any edit auto-clears the fuse."""
    import hashlib
    try:
        with open(path, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()[:16]
    except OSError:
        return None


def _sig(e):
    """Crash-fuse signature: runner + args (ticket wording: same
    runner+args+version)."""
    return (e.get("runner", "") + "|"
            + ",".join(str(a) for a in e.get("runner_args", [])))


def _confirm_crashes(state, pool, myid, fuse):
    """O-0947 slice-2: confirm own-machine launches whose runner died
    without landing (shard still not done past FUSE_CONFIRM_MIN) into
    the shared fuse registry. Only the launching machine can verify its
    own runner liveness, so confirmation is per-machine; the registry
    itself is shared (all machines respect it at the launch gate).
    Returns True if the registry changed (caller saves)."""
    dirty = False
    sigs = fuse.setdefault("sigs", {})
    for rec in state.get("launches", []):
        if (rec.get("machine") != myid
                or rec.get("verdict") != "launched"
                or rec.get("crash_counted")):
            continue
        ent = shard = None
        for en in pool.get("entries", []):
            if en.get("id") == rec.get("entry"):
                ent = en
                for s in en.get("shards", []):
                    if s.get("key") == rec.get("shard"):
                        shard = s
                        break
                break
        if ent is None:
            continue                      # entry retired -> nothing to do
        if shard is None or shard.get("status") == "done":
            rec["crash_counted"] = True   # landed -> never a crash
            continue
        try:
            age = (datetime.now() - datetime.strptime(
                rec["ts"], "%Y-%m-%d %H:%M:%S")).total_seconds() / 60.0
        except Exception:
            continue
        if age < FUSE_CONFIRM_MIN or _runner_alive(ent.get("runner", "")):
            continue
        sig = _sig(ent)
        reg = sigs.get(sig)
        if reg is None:
            reg = {"count": 0, "refusals": 0}
            sigs[sig] = reg
        reg.update({"code_sha256": rec.get("runner_sha256"),
                    "count": int(reg.get("count", 0)) + 1,
                    "last_crash_ts": _now(),
                    "entry": rec.get("entry"), "shard": rec.get("shard"),
                    "machine": myid})
        rec["crash_counted"] = True
        dirty = True
        _log(f"crash-fuse CONFIRM {sig} count={reg['count']} "
             f"(entry {rec.get('entry')} shard {rec.get('shard')} "
             f"launched {rec.get('ts')}: runner dead + shard not landed) "
             f"-- same-version relaunch refused (O-0947 fix-first)")
    return dirty


def _pick(pool, myid, skip=None):
    """Highest-priority ready, lane-legal, not-running entry + shard.
    skip (set of entry ids): candidates already refused by the caller
    this tick (O-0947 fuse) -- excluded so a fused head entry cannot
    starve later ready entries (r252 anti-starvation law)."""
    skip = skip or set()
    entries = [e for e in pool.get("entries", [])
               if e.get("status") == "ready" and e.get("runner")
               and e.get("id") not in skip]
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


def _git(args):
    """Central git runner (selftest stubs this for hermetic claim legs)."""
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True)
    return r.returncode, r.stderr.decode(errors="replace")[:200]


def _claim_shard(sh, myid):
    """r199 launch-claim law (r202 live case: 20:30:01 tick fired SHARD-4
    with no pool owner-write -> structural unclaimed window every cycle).

    The LAUNCHER claims the shard before firing: fresh-read pool, rival
    fresh claim -> lost (False); write owner+owner_since, atomic save,
    git add+commit+push. Push lost after commit -> keep local commit
    (session S0 rebase reconciles), return False (yield this cycle, next
    tick re-claims own fresh claim and retries push). Pre-commit fault ->
    restore pre-claim bytes, return False. True = claimed, caller fires."""
    prev = None
    committed = False
    try:
        with open(POOL, encoding="utf-8") as fh:
            prev = fh.read()
        pool = json.loads(prev)
        hit = None
        for e in pool.get("entries", []):
            for s in e.get("shards", []):
                if s.get("key") == sh.get("key"):
                    hit = s
                    break
            if hit is not None:
                break
        if hit is None:
            _log(f"claim miss: shard {sh.get('key')} not in pool")
            return False
        ow = hit.get("owner")
        if ow and ow != myid:
            age = _owner_age_min(ow, hit)
            if age is not None and age < STALE_MIN:
                _log(f"claim lost: {sh.get('key')} owner {ow} fresh "
                     f"({age:.0f}min)")
                return False
        hit["owner"] = myid
        hit["owner_since"] = _now()
        tmp = POOL + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(pool, fh, ensure_ascii=False, indent=1)
        os.replace(tmp, POOL)
        for args in (("add", POOL),
                     ("commit", "-m",
                      f"autofill tick claim {sh.get('key')} owner={myid} "
                      f"(r199 launch-claim) [via {myid}]"),
                     ("push",)):
            rc, err = _git(args)
            if rc != 0:
                if args[0] == "push":
                    committed = True     # commit landed, push lost
                raise RuntimeError(err)
        _log(f"claim OK: {sh.get('key')} owner={myid} pushed")
        return True
    except Exception as ex:
        if not committed and prev is not None:
            try:
                with open(POOL, "w", encoding="utf-8") as fh:
                    fh.write(prev)       # restore pre-claim bytes
            except Exception:
                pass
        _log(f"claim fault ({ex}) -> yield (committed={committed})")
        return False


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
    try:
        fuse = _load_fuse()
    except _CorruptFuse as ex:
        _log(f"tick ABORT corrupt crash_fuse (refuse wipe, r201 law): {ex}")
        print(f"ABORT corrupt crash_fuse.json: {ex}")
        return 2
    if _confirm_crashes(state, pool, rec["machine"], fuse):
        _save_fuse(fuse)
    # O-0947 crash-loop token fuse: same runner+args+code-hash that has
    # a confirmed crash -> REFUSE relaunch (fix-first; each crash-retry
    # cycle burns loop-session API tokens, r175/r198 families). A code
    # edit (hash change) auto-clears -- the fix IS the unflag.
    # r252 anti-starvation: a fused HEAD entry must not block later
    # ready entries (live: T80 anchor-refusal fused at pool head made
    # every tick return without touching the next ready entry) --
    # refuse-and-skip, keep picking down the pool.
    skip, fuse_skipped, refused_head = set(), [], None
    e = sh = cur = sig = reg = None
    while True:
        cand_e, cand_sh = _pick(pool, rec["machine"], skip=skip)
        if not cand_e:
            break
        cur = _sha16(os.path.join(ROOT, cand_e["runner"]))
        sig = _sig(cand_e)
        reg = fuse.get("sigs", {}).get(sig)
        if reg and reg.get("code_sha256") == cur:
            reg["refusals"] = int(reg.get("refusals", 0)) + 1
            reg["last_refusal_ts"] = _now()
            _log(f"crash-fuse REFUSE relaunch {cand_e['id']}/"
                 f"{cand_sh.get('key')} sig={sig} "
                 f"crashes={reg.get('count')} "
                 f"refusals={reg['refusals']} (O-0947 fix-first: edit "
                 f"runner to clear) -> skip, try next entry")
            if refused_head is None:
                refused_head = {"entry": cand_e["id"],
                                "shard": cand_sh.get("key"),
                                "fuse_crashes": reg.get("count"),
                                "fuse_refusals": reg["refusals"]}
            fuse_skipped.append({"entry": cand_e["id"],
                                  "shard": cand_sh.get("key"),
                                  "sig": sig,
                                  "fuse_refusals": reg["refusals"]})
            skip.add(cand_e["id"])
            continue
        e, sh = cand_e, cand_sh
        break
    if fuse_skipped:
        _save_fuse(fuse)
    if not e:
        if refused_head:
            rec["verdict"] = "fuse_refused_crash_loop"
            rec.update(refused_head)
            rec["fuse_skipped"] = fuse_skipped
            state["last_tick"] = rec
            _save_state(state)
            print(json.dumps(rec, ensure_ascii=False))
            return 0
        rec["verdict"] = "pool_empty_or_busy"
        state["last_tick"] = rec
        _save_state(state)
        _log(f"tick py={py}% pool has no takeable shard -> no-op")
        return 0
    if refused_head:
        # head refused but a later entry launches: keep the refusal
        # trace visible on the tick record without polluting entry/shard
        rec["fuse_skipped"] = fuse_skipped
    if reg:
        del fuse["sigs"][sig]
        _save_fuse(fuse)
        _log(f"crash-fuse CLEARED {sig}: code changed since crash "
             f"(fix detected) -> launch allowed")
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
    if not _claim_shard(sh, rec["machine"]):
        rec["verdict"] = "claim_lost_yield"
        rec["entry"] = e["id"]
        rec["shard"] = sh.get("key")
        state["last_tick"] = rec
        _save_state(state)
        _log(f"tick yield {e['id']}/{sh.get('key')}: claim lost "
             f"(rival faster or git fault) -- no unclaimed launch")
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
                "runner_sha256": cur,
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
    global POOL, STATE, FUSE, MACHINES, LOG, _GIT_DIR, _py_cpu_pct, _runner_alive
    ok_all = True

    def ok(name, cond):
        nonlocal ok_all
        ok_all &= bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")

    print("C8 autofill selftest:")
    with tempfile.TemporaryDirectory() as tmp:
        POOL = os.path.join(tmp, "runnable_pool.json")
        STATE = os.path.join(tmp, "autofill_state.json")
        FUSE = os.path.join(tmp, "crash_fuse.json")
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
        # S15 launch-claim law (r199/r202): the LAUNCHER claims the shard
        # before firing. Live case: 20:30:01 tick fired SHARD-4 with no
        # pool owner-write -> structural unclaimed window every cycle.
        # Hermetic git stub (r117 hermetic-production pairing: no real
        # git ops from selftest).
        global _git
        _git_real = _git
        git_seq = []
        fail_at = {"stage": None}

        def _fake_git(args):
            git_seq.append(args[0])
            if fail_at["stage"] == args[0]:
                return 1, "fake git fault"
            return 0, ""

        _git = _fake_git

        def _pool_with(shard):
            with open(POOL, "w", encoding="utf-8") as fh:
                json.dump({"entries": [dict(entry, shards=[shard])]}, fh)

        # S15a unclaimed -> claim True, owner+since written, add/commit/push
        _pool_with({"key": "s0", "status": "ready", "owner": None})
        git_seq.clear()
        r15 = _claim_shard({"key": "s0"}, "bm-b")
        p15 = json.load(open(POOL, encoding="utf-8"))["entries"][0]["shards"][0]
        ok("S15a unclaimed -> claimed (owner+since written, git 3-step)",
           r15 is True and p15.get("owner") == "bm-b"
           and bool(p15.get("owner_since"))
           and git_seq == ["add", "commit", "push"])
        # S15b rival FRESH claim -> lost, pool untouched
        _pool_with({"key": "s0", "status": "ready", "owner": "bm-z",
                    "owner_since": _now()})
        r15b = _claim_shard({"key": "s0"}, "bm-b")
        p15b = json.load(open(POOL, encoding="utf-8"))["entries"][0]["shards"][0]
        ok("S15b rival fresh claim -> yield, no overwrite",
           r15b is False and p15b.get("owner") == "bm-z")
        # S15c rival STALE claim -> takeover, owner rewritten
        _pool_with({"key": "s0", "status": "ready", "owner": "bm-z",
                    "owner_since": "2026-09-24 18:00:00"})
        r15c = _claim_shard({"key": "s0"}, "bm-b")
        p15c = json.load(open(POOL, encoding="utf-8"))["entries"][0]["shards"][0]
        ok("S15c rival stale claim -> takeover rewrites owner",
           r15c is True and p15c.get("owner") == "bm-b")
        # S15d pre-commit git fault -> False + pre-claim bytes restored
        _pool_with({"key": "s0", "status": "ready", "owner": None})
        fail_at["stage"] = "add"
        r15d = _claim_shard({"key": "s0"}, "bm-b")
        p15d = json.load(open(POOL, encoding="utf-8"))["entries"][0]["shards"][0]
        fail_at["stage"] = None
        ok("S15d git add fault -> yield + pool restored (owner None)",
           r15d is False and p15d.get("owner") is None)
        # S15e push lost AFTER commit -> yield but claim bytes kept
        # (local commit reconciled by session S0 rebase; next tick retries)
        _pool_with({"key": "s0", "status": "ready", "owner": None})
        fail_at["stage"] = "push"
        r15e = _claim_shard({"key": "s0"}, "bm-b")
        p15e = json.load(open(POOL, encoding="utf-8"))["entries"][0]["shards"][0]
        fail_at["stage"] = None
        ok("S15e push lost post-commit -> yield, claim kept on disk",
           r15e is False and p15e.get("owner") == "bm-b")
        # S16 O-0947 crash-loop fuse: confirm pass -- own dead launch with
        # shard still un-landed past the confirm window counts ONCE into
        # the shared registry with its launch-time code hash; landed /
        # fresh / other-machine records never count (r224 flip-window
        # false-positive guard = FUSE_CONFIRM_MIN > one tick).
        st16 = {"launches": [
            {"ts": (datetime.now() - timedelta(minutes=30)).strftime(
                "%Y-%m-%d %H:%M:%S"), "machine": "bm-b",
             "verdict": "launched", "entry": "E1", "shard": "s0",
             "runner_sha256": "abc123"},
            {"ts": (datetime.now() - timedelta(minutes=30)).strftime(
                "%Y-%m-%d %H:%M:%S"), "machine": "bm-b",
             "verdict": "launched", "entry": "E1", "shard": "s1",
             "runner_sha256": "abc123"},
            {"ts": (datetime.now() - timedelta(minutes=3)).strftime(
                "%Y-%m-%d %H:%M:%S"), "machine": "bm-b",
             "verdict": "launched", "entry": "E1", "shard": "s0",
             "runner_sha256": "abc123"},
            {"ts": (datetime.now() - timedelta(minutes=30)).strftime(
                "%Y-%m-%d %H:%M:%S"), "machine": "bm-z",
             "verdict": "launched", "entry": "E1", "shard": "s0",
             "runner_sha256": "abc123"}]}
        pool16 = {"entries": [dict(entry, shards=[
            {"key": "s0", "status": "ready", "owner": None},
            {"key": "s1", "status": "done", "owner": None}])]}
        fu16 = {"sigs": {}}
        d16 = _confirm_crashes(st16, pool16, "bm-b", fu16)
        reg16 = fu16["sigs"].get("scripts/fake_runner.py|run")
        ok("S16 crash confirm: dead+unlanded counted once; landed marked; "
           "fresh/other-machine skipped",
           d16 and reg16 and reg16["count"] == 1
           and reg16["code_sha256"] == "abc123"
           and st16["launches"][0]["crash_counted"]
           and st16["launches"][1]["crash_counted"]
           and not st16["launches"][2].get("crash_counted")
           and not st16["launches"][3].get("crash_counted"))
        # S16b launch gate: same runner+args+version (hash) with a
        # confirmed crash -> relaunch REFUSED, refusal counter visible.
        with open(POOL, "w", encoding="utf-8") as fh:
            json.dump(pool16, fh)
        with open(FUSE, "w", encoding="utf-8") as fh:
            json.dump({"sigs": {"scripts/fake_runner.py|run": {
                "code_sha256": None, "count": 1, "refusals": 0}}}, fh)
        rc = tick(dry=True)
        st16b = _load_state()["last_tick"]
        fu16b = json.load(open(FUSE, encoding="utf-8"))
        ok("S16b same-version relaunch REFUSED (counter visible)",
           rc == 0 and st16b["verdict"] == "fuse_refused_crash_loop"
           and st16b.get("fuse_refusals") == 1
           and fu16b["sigs"]["scripts/fake_runner.py|run"]["refusals"] == 1)
        # S16c fix-first auto-clear: code hash differs from the crash
        # record -> fuse cleared, launch proceeds (the fix IS the unflag).
        with open(FUSE, "w", encoding="utf-8") as fh:
            json.dump({"sigs": {"scripts/fake_runner.py|run": {
                "code_sha256": "deadbeef0000", "count": 1,
                "refusals": 2}}}, fh)
        rc = tick(dry=True)
        st16c = _load_state()["last_tick"]
        fu16c = json.load(open(FUSE, encoding="utf-8"))
        ok("S16c code-change fix -> fuse auto-cleared, launch proceeds",
           rc == 0 and st16c["verdict"] == "dry_launch"
           and "scripts/fake_runner.py|run" not in fu16c["sigs"])
        # S16e r252 anti-starvation: a fused HEAD entry must not block a
        # later ready entry -- head refusal counted + skipped, next entry
        # picked instead (live: T80 fuse head starved the pool for every
        # tick until the skip-loop fix), refusal trace visible on record.
        pool16e = {"entries": [
            dict(entry),
            dict(entry, id="E2", runner="scripts/fake_runner2.py",
                 shards=[{"key": "s0", "status": "ready",
                           "owner": None}])]}
        with open(POOL, "w", encoding="utf-8") as fh:
            json.dump(pool16e, fh)
        with open(FUSE, "w", encoding="utf-8") as fh:
            json.dump({"sigs": {"scripts/fake_runner.py|run": {
                "code_sha256": None, "count": 1, "refusals": 0}}}, fh)
        rc = tick(dry=True)
        st16e = _load_state()["last_tick"]
        fu16e = json.load(open(FUSE, encoding="utf-8"))
        ok("S16e fused head skipped -> next entry launches (no starvation)",
           rc == 0 and st16e["verdict"] == "dry_launch"
           and st16e["entry"] == "E2"
           and fu16e["sigs"]["scripts/fake_runner.py|run"]["refusals"] == 1
           and st16e.get("fuse_skipped", [{}])[0].get("entry") == "E1")
        # S16d corrupt existing fuse file -> refuse-wipe abort (r201 law
        # mirrored for the new shared state file).
        with open(FUSE, "w", encoding="utf-8") as fh:
            fh.write('{"sigs": {}\n<<<<<<< ours\n}')
        before16d = open(FUSE, "rb").read()
        rc = tick(dry=True)
        after16d = open(FUSE, "rb").read()
        ok("S16d corrupt fuse -> exit 2 + no wipe",
           rc == 2 and before16d == after16d)
        os.remove(FUSE)
        _git = _git_real
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
