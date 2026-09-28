"""Tools/resident_dispatcher.py -- T-108 D2 resident dispatcher (O-20260928-1630).

EXECUTION-LAYER V2, face D2: a 30s light pre-check cycle that closes the
ignition gap between pool-ready and burn-start. The 10-min autofill task
(C8 baseline, O-2100 <=10min SLA) stays untouched; this dispatcher ADDS a
fast lane so a lane-compatible ready shard is claimed <=60s after it is
visible on the local pool face (O-1630 sec.3 acceptance; the audit v2.4
10-min SLA line tightens together with it in T-107 slice-2).

Design (recorded in-ticket r174, v0.1):
  * REUSE law: the dispatcher never re-implements claim/launch/fuse/
    keepalive machinery -- it invokes the EXISTING autofill tick engine
    (Tools/autofill.py tick) only when a lane-compatible ready entry is
    visible; the tick keeps every gate it owns (py<70 fill line, r199
    launch-claim, r282 rebase-retry, r290 self-commit, O-0947 crash
    fuse, r201 mid-op refusal). Zero new science faces.
  * LIGHT pre-check: local pool read + cached-origin pool read via
    `git show origin/main:...` (ZERO network -- cached refs only).
    ZERO writes when idle (event-only logging: invocations + faults).
  * Guards (D-20260928-02 family): .git/index.lock + rebase/merge
    markers -> the cycle skips silently (git write rights belong to
    the round session; the tick self-guards the same markers anyway).
  * Spacing: never stack a tick onto a just-finished tick of ANY host
    (>=15s vs autofill_state last_tick; ignition worst case
    30s detect + 15s spacing + ~15s tick <= 60s target).
  * Churn gate: after a no-op-family tick verdict, re-invocation locks
    until the pool face (mtime) or origin face (content sha) CHANGES --
    new work unlocks immediately (face-change = ignition path), a fused
    or busy-but-unchanged pool does not spin the tick. py_loaded holds
    retry every PY_RETRY_S (load recovery re-check).
  * Ladder adoption slice (r179): a takeable-less cycle with the lane
    ready count below the supply floor dispatches the EXISTING
    Tools/fill_ladder.py generator (T-107 slice-2 machinery) so the
    starvation face heals itself with zero round-session dependency;
    spacing-locked at LADDER_MIN_S; all ladder laws stay ladder-owned.
  * Host: schtasks 1-min repetition (register_dispatcher_task.ps1,
    IgnoreNew single-instance) -> this process runs 2 inner cycles
    ~30s apart then exits; no daemon lifecycle to babysit.
  * Faces: results/dispatcher_log.jsonl (gitignored append log) +
    results/dispatcher_state.<mid>.json (machine-suffixed tracked
    lane face, D-03(1) naming law, event-written only).

Exit codes (house contract): 0 = normal (incl. honest idle no-op),
2 = mechanism fault (pool unreadable / tick unreadable outcome) --
report honestly, never mask. selftest = offline decision matrix, no
real launches, no real git ops (r117 hermetic law).
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
import autofill as af            # REUSE law: engine machinery, not rewritten
import fill_ladder as flx        # REUSE law: supply-floor counter + floor

POOL = af.POOL                   # results/runnable_pool.json (single pool face)
LOG = os.path.join(ROOT, "results", "dispatcher_log.jsonl")
STATE_SHARED = os.path.join(ROOT, "results", "dispatcher_state.json")

CYCLE_S = 30.0                   # 2 inner cycles per 1-min task fire
ABS_SPACING_S = 15.0             # min age of the last tick (any host) before
                                 # the dispatcher may stack another one
PY_RETRY_S = 300.0               # py_loaded hold: re-check window
LADDER_MIN_S = 300.0             # r179 adoption slice: ladder spacing -- a
                                 # fully gated-out floor breach still re-probes
                                 # at 5-min cadence, never every cycle
NOOP_LOCK_FAMILY = {             # churn gate: lock until a face changes
    "pool_empty_or_busy", "pool_absent", "fuse_refused_crash_loop",
    "claim_lost_yield", "unreadable",
}


class _PoolUnreadable(Exception):
    """Local pool face exists but fails to parse (house r201 family:
    refuse, never guess)."""


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _log(msg):
    af._log(f"dispatcher: {msg}")     # rides logs/autofill.log (ascii-safe)


def _state_path():
    # D-03(1) naming law: results/dispatcher_state.<mid>.json
    return af._lane_path_for(STATE_SHARED)


def _load_disp_state():
    p = _state_path()
    if p and os.path.exists(p):
        try:
            with open(p, encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            pass                       # corrupt tracked face -> fresh boot
    return {"lane_machine": af._machine_id(), "last_event": None,
            "counters": {}}


def _save_disp_state(st):
    p = _state_path()
    if p is None:
        return                          # r98: identity unreadable -> no write
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(st, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, p)


def _event(kind, **fields):
    """Event-only logging (design law): invocations + faults, never idle
    cycles. Appends the gitignored jsonl and refreshes the tracked
    machine-suffixed state face atomically."""
    rec = {"ts": _now(), "kind": kind, "machine": af._machine_id()}
    rec.update(fields)
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a", encoding="ascii", errors="replace") as fh:
        fh.write(json.dumps(rec, ensure_ascii=True) + "\n")
    st = _load_disp_state()
    st["lane_machine"] = af._machine_id()
    st["last_event"] = rec
    st["counters"][kind] = int(st["counters"].get(kind, 0)) + 1
    _save_disp_state(st)
    return rec


def _mid_op():
    """Git-quiescence probe (D-20260928-02 family): index.lock (round
    session mid-add/commit) plus the autofill r201 marker triple."""
    if os.path.exists(os.path.join(af._GIT_DIR, "index.lock")):
        return "index.lock"
    return af._mid_op()


def _pool_face():
    """(mtime, pool) of the local pool face; (None, None) = absent ->
    honest idle. Parse fault raises _PoolUnreadable (never guess)."""
    try:
        mtime = os.path.getmtime(POOL)
    except OSError:
        return None, None
    try:
        with open(POOL, encoding="utf-8") as fh:
            return mtime, json.load(fh)
    except Exception as ex:
        raise _PoolUnreadable(str(ex))


def _origin_face():
    """(sha16, pool) of origin's pool face via CACHED refs (git show --
    zero network, zero writes). (None, None) = no origin face (no
    remote / not yet fetched) -> honest degrade, local face only."""
    try:
        rel = os.path.relpath(POOL, ROOT).replace("\\", "/")
    except ValueError:
        rel = os.path.basename(POOL)
    r = subprocess.run(["git", "show", f"origin/main:{rel}"],
                       cwd=ROOT, capture_output=True)
    if r.returncode != 0:
        return None, None
    sha = hashlib.sha256(r.stdout).hexdigest()[:16]
    try:
        return sha, json.loads(r.stdout.decode("utf-8"))
    except Exception:
        return sha, None


def _takeable(pool, myid):
    """Conservative visibility scan (the tick re-adjudicates at full
    depth -- fuse, runner-alive, claim races stay tick-owned). Mirrors
    the tick's picker laws: ready + runner (r301) + workers_plan
    (O-2130) + lane guard (R31) + done-shard skip (r180) + fresh-owner
    skip / stale-owner takeover (O-2100 s2.4)."""
    if not isinstance(pool, dict):
        return None
    for e in pool.get("entries", []):
        if e.get("status") != "ready" or not e.get("runner"):
            continue
        lo = e.get("lane_owner")
        if lo not in (None, "", "ANY", myid):
            continue
        if not e.get("workers_plan"):
            continue
        for sh in e.get("shards", []):
            if sh.get("status") == "done":
                continue
            ow = sh.get("owner")
            if ow and ow != myid:
                age = af._owner_age_min(ow, sh)
                if age is not None and age < af.STALE_MIN:
                    continue
            return {"entry": e.get("id"), "shard": sh.get("key")}
    return None


def _af_last_tick_age_s():
    """Age (seconds) of the freshest autofill tick record on this
    machine's state lane (ANY host of that lane = this machine's
    ticks); None = unreadable/absent (treated as no spacing info)."""
    try:
        st = af._load_state()
        ts = (st.get("last_tick") or {}).get("ts")
        if not ts:
            return None
        return (datetime.now()
                - datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                ).total_seconds()
    except Exception:
        return None


def _read_tick_verdict():
    """Post-invocation verdict read from the autofill state lane (the
    tick always records last_tick; stdout JSON is not guaranteed on
    every path). Unreadable -> 'unreadable' (churn-lock family)."""
    try:
        st = af._load_state()
        return (st.get("last_tick") or {}).get("verdict") or "unreadable"
    except Exception:
        return "unreadable"


def _invoke_tick():
    """Fire the EXISTING autofill tick engine (subprocess, synchronous).
    Returns (exit_code, verdict)."""
    try:
        p = subprocess.run(
            [sys.executable, os.path.join(TOOLS, "autofill.py"), "tick"],
            cwd=ROOT, capture_output=True, timeout=240)
        rc = p.returncode
    except Exception as ex:
        _log(f"tick invocation fault: {ex}")
        return 2, "unreadable"
    return rc, _read_tick_verdict()


def _ready_below_floor(pool, myid):
    """Supply-floor probe (O-1614 sec.1): lane-compatible ready count
    below the ladder floor -- REUSE law: fill_ladder's pure counter,
    never re-implemented here."""
    return flx._compatible_ready_count(pool, myid) < flx.FLOOR_DEFAULT


def _invoke_ladder():
    """r179 adoption slice: fire the EXISTING fill_ladder generator
    (subprocess, synchronous). Every ladder-owned law stays put: enqueue
    gates, honest no-op (zero writes when floor is satisfied or every
    gate refuses), double-file pool writes, idempotent append-only."""
    try:
        p = subprocess.run(
            [sys.executable, os.path.join(TOOLS, "fill_ladder.py")],
            cwd=ROOT, capture_output=True, timeout=120)
        return p.returncode
    except Exception as ex:
        _log(f"ladder invocation fault: {ex}")
        return 2


def _ts_age_s(ts):
    try:
        return (datetime.now()
                - datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                ).total_seconds()
    except Exception:
        return None


def _eligible(last_event, pool_mtime, origin_sha):
    """Churn gate + spacing decision. Face-change (new pool bytes or new
    origin content since the last invocation) = immediate ignition;
    no-op-family verdicts lock until a face changes; py_loaded holds
    retry every PY_RETRY_S (load-recovery re-check)."""
    af_age = _af_last_tick_age_s()
    if af_age is not None and af_age < ABS_SPACING_S:
        return "spacing"
    if last_event is None:
        return "invoke"
    if (pool_mtime != last_event.get("pool_mtime")
            or origin_sha != last_event.get("origin_sha")):
        return "invoke"                       # new work = ignition path
    v = last_event.get("verdict")
    if v == "py_loaded":
        age = _ts_age_s(last_event.get("ts") or "")
        if age is None or age > PY_RETRY_S:
            return "invoke"
        return "py_hold"
    if v in NOOP_LOCK_FAMILY:
        return "gate"
    return "invoke"


def cycle():
    """One 30s-cycle decision. Returns the action string; raises
    _PoolUnreadable on a corrupt local pool face (caller reports exit 2).
    ZERO writes on idle / guard / gate skips (design law)."""
    mid = _mid_op()
    if mid is not None:
        _log(f"cycle skip: git mid-operation ({mid}) -> yield git window")
        return "git_yield"
    pool_mtime, pool = _pool_face()
    if pool is None:
        return "idle"                          # absent pool = honest idle
    myid = af._machine_id()
    cand = _takeable(pool, myid)
    origin_sha = None
    origin_only = False
    if cand is None:
        # cached-origin face (zero network): catch ready work that a
        # round pull has not landed locally yet; the tick itself stays
        # local-face honest (no-op until the pull arrives).
        origin_sha, opool = _origin_face()
        if opool is not None:
            cand = _takeable(opool, myid)
            origin_only = cand is not None
    if cand is None:
        # r179 adoption slice (T-108 D2 x T-107 slice-2 wiring): the
        # supply side closes its own loop -- no takeable candidate AND
        # the lane-compatible ready count below the floor (O-1614
        # sec.1) -> dispatch the fill ladder. Spacing-locked via the
        # tracked state face so a fully gated-out breach (all catalog
        # entries refused) re-probes at LADDER_MIN_S cadence instead
        # of spawning a subprocess every cycle. Pool-absent stays a
        # plain idle (the ladder reads the same absent face itself).
        if _ready_below_floor(pool, myid):
            st = _load_disp_state()
            age = _ts_age_s(st.get("ladder_last_ts") or "")
            if age is None or age > LADDER_MIN_S:
                st["ladder_last_ts"] = _now()
                _save_disp_state(st)
                rc = _invoke_ladder()
                _event("ladder", exit_code=rc)
                _log(f"fill ladder invoked rc={rc}")
                return "ladder"
        return "idle"
    st = _load_disp_state()
    act = _eligible(st.get("last_event"), pool_mtime, origin_sha)
    if act != "invoke":
        return act
    rc, verdict = _invoke_tick()
    _event("invoke", exit_code=rc, verdict=verdict,
           entry=cand.get("entry"), shard=cand.get("shard"),
           origin_only=origin_only, pool_mtime=pool_mtime,
           origin_sha=origin_sha)
    _log(f"tick invoked: entry={cand.get('entry')} shard="
         f"{cand.get('shard')} rc={rc} verdict={verdict} "
         f"origin_only={origin_only}")
    return "invoked"


def run(cycles=2):
    fault = False
    for i in range(cycles):
        try:
            cycle()
        except _PoolUnreadable as ex:
            _event("fault", reason=f"pool_unreadable: {ex}")
            _log(f"FAULT pool unreadable: {ex}")
            fault = True
            break
        if i < cycles - 1:
            time.sleep(CYCLE_S)
    return 2 if fault else 0


def status():
    st = _load_disp_state()
    print(json.dumps(st, ensure_ascii=False, indent=1))
    return 0


def selftest():
    """Hermetic offline decision matrix (r117: no real git ops, no real
    launches, no production-path writes)."""
    import tempfile
    global POOL, LOG, STATE_SHARED
    ok_all = True

    def ok(name, cond):
        nonlocal ok_all
        ok_all &= bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")

    print("T-108 D2 resident dispatcher selftest:")
    with tempfile.TemporaryDirectory() as tmp:
        POOL = os.path.join(tmp, "runnable_pool.json")
        LOG = os.path.join(tmp, "dispatcher_log.jsonl")
        STATE_SHARED = os.path.join(tmp, "dispatcher_state.json")
        # hermetic pairings: af helpers read fixtures, never production
        af.MACHINES = os.path.join(tmp, "machines")
        os.makedirs(af.MACHINES, exist_ok=True)
        af._GIT_DIR = os.path.join(tmp, "fake_git")
        os.makedirs(af._GIT_DIR, exist_ok=True)
        invocations = []
        verdict_q = []
        gate_q = {"af_age": None}
        origin_q = {"face": (None, None)}
        ladder_calls = []

        def _fake_invoke():
            invocations.append(dict(gate_q.get("cand") or {}))
            return 0, verdict_q.pop(0) if verdict_q else "pool_empty_or_busy"

        def _fake_af_age():
            return gate_q["af_age"]

        def _fake_origin():
            return origin_q["face"]

        def _fake_ladder():
            ladder_calls.append(1)
            return 0

        global _invoke_tick, _af_last_tick_age_s, _origin_face, _invoke_ladder
        _invoke_tick, _af_last_tick_age_s, _origin_face = \
            _fake_invoke, _fake_af_age, _fake_origin
        _invoke_ladder = _fake_ladder
        _sp = _state_path()

        def _pool_write(entries):
            with open(POOL, "w", encoding="utf-8") as fh:
                json.dump({"entries": entries}, fh)

        entry = {"id": "E1", "status": "ready",
                 "runner": "scripts/fake_runner.py", "lane_owner": None,
                 "priority": 1, "workers_plan": {"workers": 8},
                 "shards": [{"key": "s0", "status": "ready",
                             "owner": None}]}

        # D1 idle: empty pool -> ZERO tick invocations; r179 adoption
        # slice: starved pool dispatches the ladder instead (the old
        # zero-write idle contract moves to D15e's floor-satisfied face)
        invocations.clear()
        _pool_write([])
        act = cycle()
        st = _load_disp_state()
        ok("D1 starved empty pool -> no tick invoke, ladder dispatched",
           act == "ladder" and not invocations and len(ladder_calls) == 1
           and st["last_event"]["kind"] == "ladder"
           and st.get("ladder_last_ts") and os.path.exists(LOG))
        # D2 takeable candidate -> invoke + event faces written
        invocations.clear()
        _pool_write([dict(entry)])
        act = cycle()
        st = _load_disp_state()
        ok("D2 candidate -> invoke, event written (tracked lane face)",
           act == "invoked" and len(invocations) == 1
           and st["last_event"]["kind"] == "invoke"
           and st["last_event"]["verdict"] == "pool_empty_or_busy"
           and os.path.exists(LOG))
        # D3 lane guard: rival lane -> idle
        invocations.clear()
        _pool_write([dict(entry, lane_owner="bm-z")])
        act = cycle()
        ok("D3 lane-guard rival -> idle", act == "idle" and not invocations)
        # D4 missing workers_plan (O-2130) -> idle
        e4 = dict(entry)
        e4.pop("workers_plan")
        _pool_write([e4])
        act = cycle()
        ok("D4 no workers_plan -> idle (O-2130)", act == "idle"
           and not invocations)
        # D5 all shards done (r180) -> idle
        _pool_write([dict(entry, shards=[{"key": "s0", "status": "done",
                                          "owner": None}])])
        act = cycle()
        ok("D5 done-shard only -> idle", act == "idle" and not invocations)
        # D6a fresh rival owner -> idle; D6b stale rival -> invoke
        myid = af._machine_id()        # runtime identity (portable fixture)
        with open(os.path.join(af.MACHINES, "bm-z.json"), "w",
                  encoding="utf-8") as fh:
            json.dump({"last_seen": datetime.now().astimezone().isoformat(
                timespec="seconds")}, fh)
        _pool_write([dict(entry, shards=[{"key": "s0", "status": "ready",
                                          "owner": "bm-z"}])])
        act = cycle()
        ok("D6a fresh rival owner -> idle (no false takeover)",
           act == "idle" and not invocations)
        with open(os.path.join(af.MACHINES, "bm-z.json"), "w",
                  encoding="utf-8") as fh:
            json.dump({"last_seen": (datetime.now()
                                     - timedelta(minutes=30)).astimezone()
                      .isoformat(timespec="seconds")}, fh)
        act = cycle()
        ok("D6b stale rival owner -> invoke (takeover visibility)",
           act == "invoked" and len(invocations) == 1)
        # D6c own owner -> invoke (crash-fuse visibility stays tick-owned)
        invocations.clear()
        _pool_write([dict(entry, shards=[{"key": "s0", "status": "ready",
                                          "owner": myid}])])
        act = cycle()
        ok("D6c own-owned shard -> invoke (tick re-adjudicates fuse)",
           act == "invoked" and len(invocations) == 1)
        # D7 git-quiescence guards: index.lock + rebase marker -> skip
        invocations.clear()
        lock = os.path.join(af._GIT_DIR, "index.lock")
        with open(lock, "w") as fh:
            fh.write("")
        _pool_write([dict(entry)])
        act = cycle()
        ok("D7a index.lock -> git_yield, zero invoke",
           act == "git_yield" and not invocations)
        os.remove(lock)
        os.makedirs(os.path.join(af._GIT_DIR, "rebase-merge"))
        act = cycle()
        ok("D7b rebase marker -> git_yield, zero invoke",
           act == "git_yield" and not invocations)
        os.rmdir(os.path.join(af._GIT_DIR, "rebase-merge"))
        # D8 spacing: fresh tick (<15s) -> spacing skip
        invocations.clear()
        gate_q["af_age"] = 5.0
        _pool_write([dict(entry)])
        act = cycle()
        ok("D8 fresh tick 5s -> spacing skip", act == "spacing"
           and not invocations)
        gate_q["af_age"] = None
        # D9 churn gate: face-change unlock / no-op lock / py_hold window
        invocations.clear()
        _pool_write([dict(entry)])       # face change -> eligible baseline
        verdict_q.append("pool_empty_or_busy")
        cycle()                          # baseline invoke on these faces
        act = cycle()                    # same faces, no-op verdict
        ok("D9a unchanged face + no-op -> gate lock",
           act == "gate" and len(invocations) == 1)
        _pool_write([dict(entry)])       # mtime bump = face change
        act = cycle()
        ok("D9b pool face change -> unlock invoke",
           act == "invoked" and len(invocations) == 2)
        invocations.clear()
        verdict_q.append("py_loaded")
        _pool_write([dict(entry)])       # face change -> eligible baseline
        act = cycle()                    # py_loaded baseline invoke
        ok("D9c-1 py_loaded baseline -> invoke", act == "invoked"
           and len(invocations) == 1)
        act = cycle()                    # same faces, py_loaded fresh
        ok("D9c py_loaded fresh -> py_hold", act == "py_hold"
           and len(invocations) == 1)
        # D10 origin-only candidate: local lacks it, cached origin has it
        invocations.clear()
        _pool_write([])
        origin_q["face"] = ("ab", {"entries": [dict(entry)]})
        act = cycle()
        st = _load_disp_state()
        ok("D10 origin-only candidate -> invoke, origin_only marked",
           act == "invoked" and len(invocations) == 1
           and st["last_event"]["origin_only"] is True)
        act = cycle()                 # same origin sha -> gate lock
        ok("D10b unchanged origin face -> gate lock",
           act == "gate" and len(invocations) == 1)
        origin_q["face"] = ("cd", {"entries": [dict(entry)]})
        act = cycle()
        ok("D10c origin face change -> unlock invoke",
           act == "invoked" and len(invocations) == 2)
        origin_q["face"] = (None, None)
        # D11 corrupt pool -> _PoolUnreadable (refuse, never guess)
        with open(POOL, "w", encoding="utf-8") as fh:
            fh.write("{ not json")
        try:
            cycle()
            raised = False
        except _PoolUnreadable:
            raised = True
        ok("D11 corrupt pool -> _PoolUnreadable raised", raised)
        # D12 pool absent -> idle
        os.remove(POOL)
        act = cycle()
        ok("D12 pool absent -> honest idle", act == "idle")
        # D13 unreadable verdict joins the churn-lock family
        invocations.clear()
        _pool_write([dict(entry)])
        verdict_q.append("unreadable")
        cycle()
        act = cycle()
        ok("D13 unreadable verdict -> churn-lock on unchanged face",
           act == "gate" and len(invocations) == 1)
        # D14 takeable determinism (pure-function double run)
        _pool_write([dict(entry, id="E2")])
        t1 = _takeable(json.load(open(POOL, encoding="utf-8")), "bm-c")
        t2 = _takeable(json.load(open(POOL, encoding="utf-8")), "bm-c")
        ok("D14 takeable deterministic", t1 == t2 and t1["entry"] == "E2")
        # D15 ladder adoption slice (r179): spacing + floor-satisfied laws
        # D15a empty pool -> ladder dispatched, ts recorded (D1 pair;
        # ts reset here simulates a fresh-boot state -- D1's dispatch
        # above left a fresh spacing lock)
        ladder_calls.clear()
        st = _load_disp_state()
        st["ladder_last_ts"] = None
        _save_disp_state(st)
        _pool_write([])
        act = cycle()
        st = _load_disp_state()
        ok("D15a starved pool -> ladder dispatch + ts record",
           act == "ladder" and len(ladder_calls) == 1
           and st.get("ladder_last_ts"))
        # D15b fresh ladder ts -> spacing lock (no re-spawn every cycle)
        act = cycle()
        ok("D15b fresh ladder ts -> spacing lock",
           act == "idle" and len(ladder_calls) == 1)
        # D15c aged ladder ts -> re-dispatch past LADDER_MIN_S
        st = _load_disp_state()
        st["ladder_last_ts"] = (datetime.now()
                               - timedelta(seconds=LADDER_MIN_S + 100)
                               ).strftime("%Y-%m-%d %H:%M:%S")
        _save_disp_state(st)
        act = cycle()
        ok("D15c ladder ts aged -> re-dispatch",
           act == "ladder" and len(ladder_calls) == 2)
        # D15d floor satisfied + takeable -> tick path, never the ladder
        ladder_calls.clear()
        invocations.clear()
        _pool_write([dict(entry, id="R%d" % i) for i in range(3)])
        act = cycle()
        ok("D15d floor satisfied + takeable -> tick path, no ladder",
           act == "invoked" and len(invocations) == 1 and not ladder_calls)
        # D15e floor satisfied (3 ready, shards done = unclaimable) ->
        # plain idle, ZERO writes (the D1 zero-write contract lives here)
        _sp_existed = os.path.exists(_sp)
        ladder_calls.clear()
        _pool_write([dict(entry, id="R%d" % i,
                           shards=[{"key": "s0", "status": "done",
                                    "owner": None}]) for i in range(3)])
        act = cycle()
        ok("D15e floor satisfied -> idle, no ladder, no writes",
           act == "idle" and not ladder_calls)
        # D15f rival-lane ready entries do not count toward MY floor
        # (ts reset = fresh-boot breed again)
        ladder_calls.clear()
        st = _load_disp_state()
        st["ladder_last_ts"] = None
        _save_disp_state(st)
        _pool_write([dict(entry, id="V%d" % i, lane_owner="bm-z")
                     for i in range(3)])
        act = cycle()
        ok("D15f rival-lane ready-only pool -> floor breach -> ladder",
           act == "ladder" and len(ladder_calls) == 1)
    print("dispatcher selftest:", "PASS" if ok_all else "FAIL")
    return 0 if ok_all else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "status", "selftest"])
    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    if a.cmd == "status":
        return status()
    return run()


if __name__ == "__main__":
    sys.exit(main())
