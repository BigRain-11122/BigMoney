"""Tools/autofill.py -- C8 auto-fill leg (O-20260924-2100 s2.2, T-36).

Deterministic, zero-LLM fill: the pool (results/runnable_pool.json) is
the ONLY runnable face; when a machine's python CPU sits below 70% while
a ready, lane-legal shard is on the pool, this script launches the
shard's runner detached at BelowNormal priority -- no round, no MSG, no
human in the loop (O-2100: fill latency ready->running <= 10 min).

Contract:
  * NEVER edits the pool (single-writer = round control plane). Running
    state lives in this machine's lane file
    results/autofill_state.<mid>.json (r381 lane-primary; the shared
    results/autofill_state.json is the frozen legacy base) + the
    runner's own checkpoint files.
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
  * Pool-behind-origin defer (r351): fetch + three-dot pool diff shows
    origin moved results/runnable_pool.json past HEAD -> claim/keepalive
    git write defers to the post-pull tick. A fresh disk read can still
    be TREE-blind (live: b5be80cd 00:52:51 keepalive committed a
    pre-fork pool model that never held bm-c's 00:41:57 entries ->
    session S7 paid a 3-wave replay tax + local blind-pool window);
    probe fault -> fail-open legacy flow.
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
  * Self-commit (r290): claim/keepalive git flows carry the tick's OWN
    runtime dirt (autofill_state/crash_fuse) in the same commit, so the
    r282 recovery rebase stays reachable in inter-round windows (r288
    live: keepalive push lost to a tick-dirtied tree -> claim stranded
    local -> remote takeover gate re-opened -> duplicate launch).
  * Abort-ownership (r344): the claim/keepalive rebase-retry NEVER
    aborts a rebase the tick did not start. Foreign rebase in flight ->
    skip pull+abort entirely and yield (live-fire 21:48:48: a 21:40
    tick's blind `rebase --abort` killed the session fold's in-flight
    rebase); a pull refused with "already a rebase" or a clean dirty-
    tree refusal aborts nothing; only a rebase OUR pull started and
    conflicted gets aborted (r282 semantics preserved for that case).
  * Silent law: logs to logs/autofill.log only.

    * submit (r301+r305 law family): control-plane helper asserting the
      registration contract TRIO at the entry point -- runner non-empty +
      on-disk, shards non-empty, workers_plan explicit (O-2130) -- because
      hand-submitted field omissions are silently dropped by _pick and
      starve the pool (r301 CN-SECTOR-LEADER missing shards, r305
      CN-MKTNEUTRAL missing workers_plan: two live strikes). Duplicate id
      refused; atomic append via os.replace; NO git ops -- the calling
      session commits (single-writer = round control plane); run between
      ticks (a same-second claim-write race is possible but the window is
      seconds and self-commit r290 keeps tick dirt recoverable).

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
# D-20260928-03(1) batch-1 writer retirement (r381): autofill_state is
# LANE-PRIMARY -- this machine's lane file (results/autofill_state.
# <mid>.json) is the sole live read+write surface and the shared file
# stays the FROZEN legacy base the merger (scripts/merge_lane_views.py)
# still reads as source #0.  Retires the last per-tick shared rewrite
# (the 608-write treadmill face; D-03 sec.3 replay metric).  POOL and
# FUSE keep the compat dual-track (pool: session edit scripts + mirror
# direction; fuse: the launch gate reads the lane-MERGED registry since
# r384 debt-table (1), the shared write stays for machines that have
# not pulled the merged gate yet -- withdrawal is its own slice).
_STATE_LANE_PRIMARY = True
# D-20260928-03(1) pool shared-write retirement (r388): claim/keepalive
# write the OWN lane as the authority record; the shared face becomes
# the merger-recipe union writeback (scripts/merge_lane_views.sync_face)
# -- the r348/r120 blind-overwrite swallow family and the r375
# pre-defer rewrite vector die by construction (a settle re-reads every
# source FRESH; a union cannot lose a source row). Precondition met
# r388: fleet pulled slice-5 (bm-b 462f202b / bm-c a1644a71 both
# rebased on c5d63fb8).
_POOL_LANE_PRIMARY = True
LOG = os.path.join(ROOT, "logs", "autofill.log")
MACHINES = os.path.join(ROOT, "fleet", "machines")
MACHINE_JSON = os.path.join(ROOT, "fleet", "machine.json")
_GIT_DIR = os.path.join(ROOT, ".git")

LOW_PY_LINE = 70.0        # O-1136: py CPU < 70% of machine capacity
SAMPLE_S = 2.0            # instantaneous py-CPU sample window
STALE_MIN = 20.0          # O-2100 s2.4: shard-owner heartbeat staleness
KEEPALIVE_MIN = 10.0      # r288 claim-keepalive cadence (well under
                          # STALE_MIN): refresh owner_since while the
                          # local runner burns so remote takeover gates
                          # never see a live owner as stale.
FILL_TARGET_MIN = 10.0    # O-2100 s2.2 hard target
FUSE_CONFIRM_MIN = 25.0   # O-0947: crash confirm window -- > one flip
                          # window (r224 landed->flip lag) + margin, so a
                          # SUCCESSFUL-but-unflipped run is never counted
FAST_CONFIRM_MIN = 5.0    # r177bm-c instant-exit fast-confirm window:
                          # runner dead + shard checkpoint face untouched
                          # since spawn = deterministic gate refusal
                          # (live-fire 18:22-18:31 W4-JUDGE P5C deep-panel
                          # absence on non-data hosts: one claim+launch+
                          # commit per minute for 25min before the fuse
                          # bit). Progress-bearing deaths keep the slow
                          # window (flip-lag false-positive guard intact).
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


def _mid_op():
    """r201 marker probe factored (r344 abort-ownership law): first
    mid-rebase/mid-merge marker present in .git, or None. The tick
    entry guard and the claim/keepalive abort-ownership checks share
    one truth -- never probe the marker triple in two places."""
    for probe in ("rebase-merge", "rebase-apply", "MERGE_HEAD"):
        if os.path.exists(os.path.join(_GIT_DIR, probe)):
            return probe
    return None


def _pool_origin_stale():
    """r351 pool-behind-origin probe (b5be80cd live-fire 00:52:51: the
    keepalive committed a pool model from a tree forked BEFORE bm-c's
    00:41:57 entries landed on origin -- the local face never held
    them, so the fresh read was still blind; the write was structurally
    incapable of carrying them, session S7 paid a 3-wave replay tax,
    and the local pool sat blind until reconciliation). Exit-code-only
    face rides the _git stub surface (hermetic selftest). Three-dot
    diff = origin's pool changes since the fork point, so local-ahead
    unpushed tick commits (r290 stranding face) do NOT trip the defer.
    True = origin moved the pool past HEAD -> claim/keepalive defer
    (both refreshes idempotent under their age gates; the fire gate
    stays push-success = origin-visible claim, r199 unchanged).
    False = pool even (other-file origin traffic replays clean, r282
    fill-latency intent preserved). None = probe fault -> fail-open
    legacy flow."""
    rc_f, _ = _git(("fetch", "-q", "origin", "main"))
    if rc_f != 0:
        return None
    # r142 bm-c drive-boundary law: relpath raises ValueError when POOL
    # is redirected outside ROOT's drive (selftest tmp on C: vs repo on
    # K:) -- the documented "probe fault -> None" contract was violated
    # by the escaping exception, faulting every hermetic claim leg on
    # drive-split machines (pre-existing S15a/c/e/f/g FAIL face, bm-c
    # only). Production POOL always sits under ROOT -> relpath works ->
    # zero behavior change; the basename fallback is inert under the
    # _git stub (the diff path arg only matters to real git).
    try:
        rel = os.path.relpath(POOL, ROOT)
    except ValueError:
        rel = os.path.basename(POOL)
    rc, _ = _git(("diff", "--quiet", "HEAD...origin/main", "--", rel))
    if rc == 1:
        return True
    if rc == 0:
        return False
    return None


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
    """True if a python process is already running this entry's runner.
    Null/empty runner -> False (live 2026-09-27: T34-PRESIGNAL-HALFSTEP
    pool entry carries explicit runner=null -- .get("runner", "") default
    never fires on null -- so the keepalive scan crashed on
    .replace() every tick 02:40-07:10, leaving the r288 claim-refresh
    line dead while a local burn runs)."""
    if not runner_rel:
        return False
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
    # D-20260928-03(1) batch-1 writer retirement (r381): lane-first --
    # the owning machine's lane is the authoritative live state; the
    # shared face is the frozen legacy base, kept only as the transition
    # fallback for a machine whose lane is absent (fresh clone / first
    # post-retirement tick); the next save persists back to the lane.
    lp = _lane_path_for(STATE) if _STATE_LANE_PRIMARY else None
    if _STATE_LANE_PRIMARY and lp is None:
        # r98: identity unreadable -> refuse the tick outright; a silent
        # shared-base read would strand a claim mid-tick when the strict
        # lane save hits the same missing identity.
        raise RuntimeError("state lane path unavailable: machine id "
                           "unreadable (r98) -- refuse tick")
    for path in ([lp] if lp is not None else []) + [STATE]:
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as fh:
                    return json.load(fh)
            except Exception as ex:
                # r201: a parse-failed EXISTING file must never fall back
                # to a fresh state -- the next _save_state would wipe the
                # launch history (live case: mid-rebase marker file,
                # 49 launches -> 1).
                raise _CorruptState(str(ex))
    return {"launches": []}


def _save_state(s):
    if _STATE_LANE_PRIMARY:
        # r381 retirement: the lane is the sole write surface (the
        # shared base stays frozen).  Native-strict on purpose: unlike
        # the dual-track lane mirror (_write_lane_file, fail-soft while
        # shared stayed authoritative), a lost AUTHORITATIVE save must
        # abort the tick (r201/r290 data-loss family), and the C8
        # watchdog makes the failure visible.
        lp = _lane_path_for(STATE)
        if lp is None:
            raise RuntimeError("state lane path unavailable: machine id "
                               "unreadable (r98) -- refuse state save")
        payload = dict(s)
        payload["lane_machine"] = _machine_id()
        tmp = lp + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=1)
        os.replace(tmp, lp)
        return
    tmp = STATE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(s, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, STATE)
    # D-20260928-03(1) batch-1: own lane alongside the shared state.
    _write_lane_file(STATE, s)


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
    # D-20260928-03(1) batch-2 closeout: own lane alongside the shared
    # fuse face (same dual-track as _save_state; 7/8 -> 8/8 wired).
    _write_lane_file(FUSE, f)


def _fuse_gate_view():
    """Merged lane view of the refusal registry for the launch gate
    (D-03(1) debt-table (1), r381 audit).  Factored out so selftests can
    simulate merge-path faults (S16g) without touching the fallback."""
    scripts_dir = os.path.join(ROOT, "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    import merge_lane_views as _mlv
    return _mlv.face_view("crash_fuse",
                          results_dir=os.path.dirname(FUSE))


def _load_fuse_gate():
    """Launch-gate + crash-confirm read of the refusal registry.

    The registry is CROSS-MACHINE: a crash confirmed on another machine
    may live only in that machine's lane file (the shared row can be
    lost to a push-storm resolve, r376 family), and a bare shared read
    would relaunch the same crashed version -- the exact revival the
    fuse exists to prevent.  So the gate reads the lane-merged view
    (r375 merge_crash_fuse: sigs key-union, same-key newer-event-wins).
    Corrupt SHARED file keeps the r201 refuse-tick abort (bare load
    first); any other merge-path fault degrades to the bare shared
    gate with an honest log -- pre-slice semantics, so the fleet's own
    heartbeat never widens its fault surface.  Single-source trees
    (selftest tmp, r117 law) merge == bare, existing legs unaffected.
    Saves stay dual-track: the union written back to the shared file
    absorbs lane-only sigs, which also protects machines that have not
    pulled this batch yet."""
    shared = _load_fuse()          # r201 corrupt -> _CorruptFuse -> abort
    try:
        merged = _fuse_gate_view()
    except Exception as ex:
        _log(f"crash-fuse merged-read unavailable -> bare shared gate "
             f"(pre-slice semantics, honest log): {ex}")
        return shared
    return merged if merged else shared


def _lane_path_for(shared_path):
    """D-20260928-03(1) batch-1 writer dual-track: this machine's lane
    file results/<face>.<machine>.json, derived from the writer's OWN
    path constant so selftest tmp redirections stay hermetic (r117
    law) and the name matches what scripts/merge_lane_views.py reads.
    None when identity is unreadable (r98: never guess)."""
    mid = _machine_id()
    if not mid or not shared_path.endswith(".json"):
        return None
    return shared_path[:-len(".json")] + f".{mid}.json"


def _write_lane_file(shared_path, data):
    """Own lane alongside the shared face (D-03(1) compat window: the
    shared file stays authoritative; a lane fault logs, never breaks
    the tick flow or its exit contract)."""
    lp = _lane_path_for(shared_path)
    if lp is None or not isinstance(data, dict):
        return
    payload = dict(data)
    payload["lane_machine"] = _machine_id()
    try:
        tmp = lp + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=1)
        os.replace(tmp, lp)
    except Exception as ex:
        _log(f"lane write fault {os.path.basename(lp)}: {ex} "
             f"(shared face stays authoritative)")


def _pool_lane_sync():
    """Re-mirror the pool lane from CURRENT shared bytes -- every
    byte-restore site must call this so the lane never holds a claim
    the shared file just rolled back (phantom-owner prevention).
    Dual-track era helper (pre-retirement); the lane-primary legs roll
    BOTH sides back byte-exact via _pool_rollback instead."""
    try:
        with open(POOL, encoding="utf-8") as fh:
            _write_lane_file(POOL, json.load(fh))
    except Exception as ex:
        _log(f"pool lane sync fault: {ex}")


def _read_pool_lane_bytes():
    """Pre-op snapshot of this machine's pool lane for the two-sided
    rollback (None = lane file absent pre-op). Byte-level so restores
    are exact."""
    lp = _lane_path_for(POOL)
    if lp is None or not os.path.exists(lp):
        return None
    with open(lp, "rb") as fh:
        return fh.read()


def _write_lane_file_strict(shared_path, data):
    """Lane-primary AUTHORITY write (D-03 pool shared-write retirement,
    r381 native-strict law): the lane is the claim's authoritative
    record, so a lost write must abort the leg (raise -> fault path),
    never fail-soft -- a dropped authority write would settle a union
    whose sources lack the claim, committing a shared face that reads
    unclaimed while the runner burns (r288 double-burn family)."""
    lp = _lane_path_for(shared_path)
    if lp is None or not isinstance(data, dict):
        raise RuntimeError("pool lane path unavailable (r98 identity "
                           "unreadable) -- refuse lane-primary write")
    payload = dict(data)
    payload["lane_machine"] = _machine_id()
    tmp = lp + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, lp)


def _pool_settle():
    """D-20260928-03(1) pool retirement: settle BOTH sides to the
    merger-recipe union (scripts/merge_lane_views.sync_face) -- shared
    becomes the union-writeback artifact, never a blind overwrite of a
    stale in-memory copy again (r348/r120 + r375 vectors). Fail-soft
    status: True = shared now holds the union (settled/unchanged/
    no_sources); False = union unavailable (corrupt source mid
    push-storm / merge fault) -> caller falls back to the
    pre-retirement direct write so the claim stays fleet-visible (r384
    fuse-gate fallback family: a lane-only island claim invites a
    rival STALE takeover)."""
    try:
        scripts_dir = os.path.join(ROOT, "scripts")
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        import merge_lane_views as _mlv
        res = _mlv.sync_face("runnable_pool",
                             results_dir=os.path.dirname(POOL))
        st = res.get("status")
        if st in ("settled", "unchanged", "no_sources"):
            return True
        _log(f"pool settle {st}: " + "; ".join(res.get("notes", [])[:2]))
        return False
    except Exception as ex:
        _log(f"pool settle fault: {ex}")
        return False


def _pool_rollback(prev, prev_lane):
    """Two-sided byte-restore for the pool claim/keepalive legs (D-03
    pool shared-write retirement). Restoring ONLY the shared face (the
    pre-retirement shape) leaves a live claim in the lane, and the next
    union settle would resurrect a phantom owner (r288 family -- the
    exact hazard the r381 audit flagged for this batch). Lane-primary:
    shared <- prev bytes AND lane <- pre-op lane bytes (a lane that did
    not exist pre-op is removed, not recreated). Dual-track (flag off):
    shared <- prev + lane re-mirrored from it (r378 phantom-owner law).
    Fail-soft on both sides (a rollback fault logs; the caller already
    yields)."""
    try:
        with open(POOL, "w", encoding="utf-8") as fh:
            fh.write(prev)
    except Exception as ex:
        _log(f"pool shared rollback fault: {ex}")
    if not _POOL_LANE_PRIMARY:
        _pool_lane_sync()
        return
    lp = _lane_path_for(POOL)
    if lp is None:
        return
    try:
        if prev_lane is None:
            if os.path.exists(lp):
                os.remove(lp)
        else:
            with open(lp, "wb") as fh:
                fh.write(prev_lane)
    except Exception as ex:
        _log(f"pool lane rollback fault: {ex}")


def _tick_owned_dirt():
    """r290 self-commit law: the tick's OWN runtime writes (autofill_
    state.json last_tick/launches, crash_fuse.json) are the dirt that
    makes every inter-round `pull --rebase` refuse -- so claim/keepalive
    git flows must carry them in the same commit, keeping the r282
    recovery rebase reachable in autonomous windows (live case: r288
    CN-TREND keepalive push lost to a tick-dirtied tree, claim stranded
    local, remote takeover gate re-opened -> double burn). Session-owned
    dirt (non-tick files) still yields per r282. Existence-filtered:
    absent files are never git-added.

    D-20260928-03(1) batch-1: the LANE files are tick-owned dirt too --
    the state lane is the PRIMARY surface post-r381 retirement, the
    pool lane is the claim/keepalive authority record post-r388 pool
    retirement, the fuse lane is a dual-track mirror -- they ride the
    same commit or every inter-round pull --rebase would refuse on
    them exactly the way the r290 live case refused on STATE."""
    dirt = [STATE, FUSE]
    for lp in (_lane_path_for(STATE), _lane_path_for(POOL),
               _lane_path_for(FUSE)):
        if lp is not None:
            dirt.append(lp)
    return [p for p in dirt if os.path.exists(p)]


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


def _ckpt_no_progress_since(sh, ts):
    """r177bm-c fast-confirm discriminator: True when the shard's
    checkpoint face shows ZERO progress since the given launch ts --
    checkpoint field absent from the shard dict (conservative False:
    keep the slow window), or the checkpoint file does not exist / was
    not touched after the launch. An instant deterministic exit
    (host-ineligible data gate) leaves the face exactly like this;
    a runner that burned cells before dying always touches it."""
    ck = sh.get("checkpoint")
    if not isinstance(ck, str):
        return False
    path = ck.split(" (")[0].strip()
    if not path:
        return False
    anchor = os.path.dirname(POOL)
    if path.startswith("results/") or path.startswith("results\\"):
        fp = os.path.join(anchor, path[len("results/"):])
    else:
        fp = os.path.join(ROOT, path)
    if not os.path.exists(fp):
        return True
    try:
        mtime = datetime.fromtimestamp(os.path.getmtime(fp))
        launched = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
    except Exception:
        return False
    return mtime < launched


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
        if _runner_alive(ent.get("runner", "")):
            continue
        # r177bm-c fast-confirm: runner dead + checkpoint face untouched
        # since spawn + age >= FAST_CONFIRM_MIN -> instant deterministic
        # exit; count the crash NOW instead of feeding a claim+launch+
        # commit churn loop for the rest of the FUSE_CONFIRM_MIN window.
        fast = (age >= FAST_CONFIRM_MIN
                and _ckpt_no_progress_since(shard, rec.get("ts")))
        if age < FUSE_CONFIRM_MIN and not fast:
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


def _claim_shard(sh, myid, entry_id):
    """r199 launch-claim law (r202 live case: 20:30:01 tick fired SHARD-4
    with no pool owner-write -> structural unclaimed window every cycle).

    The LAUNCHER claims the shard before firing: fresh-read pool, rival
    fresh claim -> lost (False); write owner+owner_since, atomic save,
    git add+commit+push. Push lost after commit -> keep local commit
    (session S0 rebase reconciles), return False (yield this cycle, next
    tick re-claims own fresh claim and retries push). Pre-commit fault ->
    restore pre-claim bytes, return False. True = claimed, caller fires.

    r282 fill-starvation law: a push rejected because origin moved
    (multi-machine round traffic) gets ONE pull --rebase + push-retry
    before yielding (S7 discipline ported to the tick). Live case:
    00:30/00:40/00:50 revosc claims all lost to push-reject while py sat
    at 0-4% -- fill latency 29.1min vs O-2100 10min target; at 00:30 the
    tree was clean and the recovery rebase would have landed the claim
    20min earlier. Fail-safe (r344 abort-ownership): a rebase OUR pull
    started and conflicted -> abort ours + yield; a FOREIGN rebase
    already in flight, a pull refused with "already a rebase", or a
    clean dirty-tree refusal -> NO abort (live-fire 21:48:48: the
    blind abort killed the session fold's in-flight rebase), session
    S0 reconciles (r268 stash law: no stash games from the tick).
    r290 self-commit:
    the tick's OWN dirt (autofill_state/crash_fuse) rides in the claim
    commit itself -- an inter-round tree dirtied only by the tick keeps
    the recovery rebase reachable (r288 live: keepalive push lost to a
    tick-dirtied tree -> claim stranded -> takeover gate reopened ->
    double burn)."""
    prev = None
    prev_lane = None
    committed = False
    try:
        with open(POOL, encoding="utf-8") as fh:
            prev = fh.read()
        prev_lane = _read_pool_lane_bytes()
        pool = json.loads(prev)
        hit = None
        for e in pool.get("entries", []):
            # r141 double-key law: shard keys are unique only WITHIN
            # an entry -- the fresh-read re-find is anchored by the
            # picker's entry id. Key-only match hit the W1 same-key
            # done shard first in pool order and the claim wrote the
            # WRONG entry, leaving the true W2 shard unclaimed. A None
            # anchor matches nothing (fail-closed miss, no write).
            if e.get("id") != entry_id:
                continue
            for s in e.get("shards", []):
                if s.get("key") == sh.get("key"):
                    hit = s
                    break
            if hit is not None:
                break
        if hit is None:
            _log(f"claim miss: {entry_id}/{sh.get('key')} not in pool")
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
        if _POOL_LANE_PRIMARY:
            # D-03 pool shared-write retirement: the lane is the
            # claim's AUTHORITY record (native-strict, r381 state law).
            _write_lane_file_strict(POOL, pool)
        else:
            tmp = POOL + ".tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(pool, fh, ensure_ascii=False, indent=1)
            os.replace(tmp, POOL)
        # D-20260928-02(1) pre-add mid-op guard (r331 live-fire): the
        # r201 entry guard closes only the tick-START face; a session
        # rebase/merge can start inside the sampling+scan window. The
        # git write right belongs to the loop session -> defer (restore
        # pre-claim bytes, next tick re-claims).
        mid = _mid_op()
        if mid is not None:
            _pool_rollback(prev, prev_lane)
            _log(f"claim deferred: git mid-operation ({mid}) appeared "
                 f"mid-tick -> yield git write to session, next tick "
                 f"re-claims (D-20260928-02)")
            return False
        if _pool_origin_stale():
            _pool_rollback(prev, prev_lane)
            _log("claim deferred: origin moved the pool past HEAD "
                 "(r351) -> yield to session pull, next tick re-claims")
            return False
        if _POOL_LANE_PRIMARY:
            # D-03 pool retirement: shared face = union writeback -- a
            # settle re-reads every source FRESH (mid-window session
            # defers survive, r378 catch-4 law) and a union cannot
            # lose a source row (r348/r120 + r375 vectors). Degraded
            # (corrupt source mid push-storm / merge fault) -> the
            # pre-retirement direct write keeps the claim fleet-visible
            # (r384 fuse-gate fallback family: a lane-only island
            # claim invites a rival STALE takeover).
            if not _pool_settle():
                tmp = POOL + ".tmp"
                with open(tmp, "w", encoding="utf-8") as fh:
                    json.dump(pool, fh, ensure_ascii=False, indent=1)
                os.replace(tmp, POOL)
        else:
            # D-20260928-03(1) batch-1: mirror the pool lane from the
            # exact bytes about to be committed -- the lane records
            # this machine's last committed write (anti-swallow
            # record).
            _write_lane_file(POOL, pool)
        for args in (("add", POOL, *_tick_owned_dirt()),
                     ("commit", "-m",
                      f"autofill tick claim {sh.get('key')} owner={myid} "
                      f"(r199 launch-claim + r290 self-commit) "
                      f"[via {myid}]"),
                     ("push",)):
            rc, err = _git(args)
            if rc == 0:
                continue
            if args[0] != "push":
                raise RuntimeError(err)
            # r282: push rejected -> one rebase-retry before yielding.
            committed = True     # commit landed, push lost so far
            # r344 abort-ownership: never abort a rebase we did not
            # start. A foreign rebase in flight (session fold) -> skip
            # the pull entirely; git would refuse it anyway and the
            # old blind abort below killed the session's rebase
            # (21:48:48 live-fire).
            foreign = _mid_op()
            if foreign is not None:
                _log(f"claim rebase-retry skipped: foreign rebase in "
                     f"flight ({foreign}) -> yield keeps claim commit")
                raise RuntimeError(err)
            rc2, err2 = _git(("pull", "--rebase"))
            if rc2 == 0:
                rc3, err3 = _git(("push",))
                if rc3 == 0:
                    _log(f"claim OK: {sh.get('key')} owner={myid} "
                         f"pushed (rebase-retry r282)")
                    return True
                err = err3
            else:
                refused_foreign = "already a rebase" in (err2 or "")
                if _mid_op() is not None and not refused_foreign:
                    # OUR pull started this rebase and it conflicted --
                    # ours to abort; claim commit kept for session S0
                    _git(("rebase", "--abort"))
                    _log(f"claim rebase-retry conflicted (ours) -> "
                         f"aborted, yield keeps claim commit")
                else:
                    # refused without starting one (dirty tree) or a
                    # session rebase appeared mid-window ("already a
                    # rebase") -> nothing of ours to abort
                    _log(f"claim rebase-retry refused "
                         f"({(err2 or '').strip()[-100:]}) -> yield "
                         f"keeps claim commit")
            raise RuntimeError(err)
        _log(f"claim OK: {sh.get('key')} owner={myid} pushed")
        return True
    except Exception as ex:
        if not committed and prev is not None:
            _pool_rollback(prev, prev_lane)
        _log(f"claim fault ({ex}) -> yield (committed={committed})")
        return False


def _keepalive_claims(pool, myid):
    """r288 claim-keepalive law: a locally-alive runner burning past
    KEEPALIVE_MIN on a self-owned shard refreshes owner_since so remote
    takeover gates (min(heartbeat, claim-stamp) freshness vs STALE_MIN)
    never see a live owner as stale. Live-fire: CN-TREND 30min burn +
    session push-fallback stranded the fresh heartbeat on the machine
    branch -> bm-a tick read a stale heartbeat face, takeover gate
    opened at STALE_MIN, duplicate launch = double burn. Rival-owned
    shards are never touched (a completed takeover stays lost -- do not
    fight it). Returns refreshed shard keys."""
    prev = None
    prev_lane = None
    committed = False
    keys = []
    try:
        with open(POOL, encoding="utf-8") as fh:
            prev = fh.read()
        prev_lane = _read_pool_lane_bytes()
        for e in pool.get("entries", []):
            if not _runner_alive(e.get("runner", "")):
                continue
            for sh in e.get("shards", []):
                if sh.get("status") == "done" or sh.get("owner") != myid:
                    continue
                age = _since_age_min(sh)
                if age is not None and age < KEEPALIVE_MIN:
                    continue
                sh["owner_since"] = _now()
                keys.append(sh.get("key"))
        if not keys:
            return []
        if _POOL_LANE_PRIMARY:
            # D-03 pool shared-write retirement (keepalive leg): lane
            # = authority record, shared = union writeback (same law
            # as the claim leg).
            _write_lane_file_strict(POOL, pool)
        else:
            tmp = POOL + ".tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(pool, fh, ensure_ascii=False, indent=1)
            os.replace(tmp, POOL)
        # D-20260928-02(1) pre-add mid-op guard (r331): keepalive git
        # write yields to a session rebase/merge that appeared mid-tick;
        # pre-refresh bytes restored, next tick re-refreshes (refresh
        # is idempotent under the age gate).
        mid = _mid_op()
        if mid is not None:
            _pool_rollback(prev, prev_lane)
            _log(f"keepalive deferred: git mid-operation ({mid}) "
                 f"appeared mid-tick -> yield git write to session "
                 f"(D-20260928-02)")
            return []
        if _pool_origin_stale():
            _pool_rollback(prev, prev_lane)
            _log("keepalive deferred: origin moved the pool past HEAD "
                 "(r351) -> yield to session pull, next tick "
                 "re-refreshes (idempotent under the age gate)")
            return []
        if _POOL_LANE_PRIMARY:
            if not _pool_settle():
                tmp = POOL + ".tmp"
                with open(tmp, "w", encoding="utf-8") as fh:
                    json.dump(pool, fh, ensure_ascii=False, indent=1)
                os.replace(tmp, POOL)
        else:
            # D-20260928-03(1) batch-1: pool lane mirrors the committed
            # bytes (same law as the claim leg).
            _write_lane_file(POOL, pool)
        for args in (("add", POOL, *_tick_owned_dirt()),
                     ("commit", "-m",
                      f"autofill tick keepalive "
                      f"{' '.join(str(k) for k in keys)} owner={myid} "
                      f"(r288 claim-refresh + r290 self-commit) "
                      f"[via {myid}]"),
                     ("push",)):
            rc, err = _git(args)
            if rc == 0:
                continue
            if args[0] != "push":
                raise RuntimeError(err)
            committed = True     # refreshed face landed locally already
            # r344 abort-ownership (keepalive leg): mirror the claim
            # leg -- never abort a rebase the tick did not start.
            foreign = _mid_op()
            if foreign is not None:
                _log(f"keepalive rebase-retry skipped: foreign rebase "
                     f"in flight ({foreign}) -> local commit kept for "
                     f"session S0 reconciliation")
                raise RuntimeError(err)
            rc2, err2 = _git(("pull", "--rebase"))
            if rc2 == 0:
                rc3, err3 = _git(("push",))
                if rc3 == 0:
                    _log(f"keepalive OK: {keys} owner={myid} "
                         f"pushed (rebase-retry r282)")
                    return keys
                err = err3
            else:
                refused_foreign = "already a rebase" in (err2 or "")
                if _mid_op() is not None and not refused_foreign:
                    _git(("rebase", "--abort"))
                    _log(f"keepalive rebase-retry conflicted (ours) -> "
                         f"aborted, local commit kept for session S0")
                else:
                    _log(f"keepalive rebase-retry refused "
                         f"({(err2 or '').strip()[-100:]}) -> local "
                         f"commit kept for session S0 reconciliation")
            raise RuntimeError(err)
        _log(f"keepalive OK: {keys} owner={myid} pushed")
        return keys
    except Exception as ex:
        if not committed and prev is not None:
            _pool_rollback(prev, prev_lane)
        _log(f"keepalive fault ({ex}) -> refreshed={bool(committed)} "
             f"keys={keys}")
        return keys if committed else []


def tick(dry=False):
    probe = _mid_op()
    if probe is not None:
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
        fuse = _load_fuse_gate()
    except _CorruptFuse as ex:
        _log(f"tick ABORT corrupt crash_fuse (refuse wipe, r201 law): {ex}")
        print(f"ABORT corrupt crash_fuse.json: {ex}")
        return 2
    if _confirm_crashes(state, pool, rec["machine"], fuse):
        _save_fuse(fuse)
    if not dry:
        # r288 claim-keepalive: refresh owner_since on self-owned shards
        # whose runner burns locally (proof-of-life vs remote STALE_MIN
        # takeover; live-fire: CN-TREND double-burn this round).
        ka = _keepalive_claims(pool, rec["machine"])
        if ka:
            rec["keepalive"] = ka
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
        # D-03(2) cleared-tombstone: record the clear so the lane-union
        # cannot resurrect this sig from another machine's stale lane
        # (r389 drift family).  A newer crash on the NEW code carries a
        # fresh last_crash_ts and beats the tombstone at the merge.
        fuse.setdefault("cleared", {})[sig] = {
            "cleared_ts": _now(), "cleared_by": rec["machine"],
            "reason": "code_changed", "crashes": int(reg.get("count", 0)),
            "old_code_sha256": reg.get("code_sha256")}
        del fuse["sigs"][sig]
        _save_fuse(fuse)
        _log(f"crash-fuse CLEARED {sig}: code changed since crash "
             f"(fix detected) -> launch allowed (tombstone recorded)")
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
    if not _claim_shard(sh, rec["machine"], e.get("id")):
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


def submit(a):
    """Contract-gated pool entry append (r301+r305 law: hand-submitted
    field omissions -- missing shards, missing workers_plan, null runner
    -- are silently dropped by _pick and starve the pool; assert the trio
    at the entry point instead of post-hoc tick forensics)."""
    bad = []
    a_id = (a.id or "").strip()
    if not a_id:
        bad.append("id empty")
    try:
        with open(POOL, encoding="utf-8") as fh:
            pool = json.load(fh)
    except FileNotFoundError:
        pool = {"entries": []}
    except Exception as ex:
        print(f"ABORT pool unreadable: {ex}")
        return 2
    if any(e.get("id") == a_id for e in pool.get("entries", [])):
        bad.append(f"duplicate id {a_id} (edit the existing entry instead)")
    runner = (a.runner or "").strip().replace("\\", "/")
    if not runner:
        bad.append("runner empty (r301 family: null runner killed the "
                   "keepalive scan for 27 ticks)")
    elif not os.path.isfile(os.path.join(ROOT, runner)):
        bad.append(f"runner not on disk: {runner}")
    keys = [k.strip() for k in (a.shards or "").split(",") if k.strip()]
    if not keys:
        bad.append("shards empty (r301 law: a ready entry without shards "
                   "starves the picker)")
    if not a.workers or a.workers <= 0:
        bad.append("workers_plan missing: pass --workers N explicitly "
                   "(O-2130 multi-core law, r305 law)")
    if bad:
        for b in bad:
            print(f"REFUSED: {b}")
        _log(f"submit REFUSED {a_id or '<empty>'}: " + "; ".join(bad))
        return 2
    wp = {"workers": a.workers, "priority": a.wp_priority or "BelowNormal"}
    if a.wp_note:
        wp["note"] = a.wp_note
    entry = {
        "id": a_id,
        "ticket_ref": a.ticket_ref or "",
        "prereg_ref": a.prereg_ref or "",
        "runner": runner,
        "runner_args": (a.runner_args or "run").split(),
        "lane_owner": a.lane_owner or None,
        "priority": a.priority,
        "status": "ready",
        "entered_at": _now(),
        "data_gates": a.data_gates or "",
        "shards": [{"key": k, "status": "ready",
                    "checkpoint": a.shard_checkpoint or "",
                    "note": a.shard_note or "", "owner": None}
                   for k in keys],
        "workers_plan": wp,
    }
    pool.setdefault("entries", []).append(entry)
    pool["updated_at"] = _now()
    tmp = POOL + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(pool, fh, indent=1)
    os.replace(tmp, POOL)
    # D-20260928-03(1) batch-1: submit also lands in this machine's pool
    # lane (session commit carries both files at round close).
    _write_lane_file(POOL, pool)
    _log(f"submit OK {a_id} runner={runner} shards={len(keys)} "
         f"workers={a.workers} (contract trio asserted, r301+r305)")
    print(json.dumps({"submitted": a_id, "shards": keys,
                      "workers_plan": wp}, ensure_ascii=False))
    return 0


def selftest():
    import tempfile
    global POOL, STATE, FUSE, MACHINES, LOG, _GIT_DIR, _py_cpu_pct, \
        _runner_alive, _fuse_gate_view, _pool_settle
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
        # r381 lane-primary: the state's LIVE surface is the lane file
        # (hermetic under the tmp redirect, r117 law) -- S14/S18 legs
        # target it; the shared path only exists as a transition-fallback
        # fixture when a leg plants one.
        _lane_st = _lane_path_for(STATE)
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
        before = open(_lane_st, "rb").read()
        rc = tick(dry=True)
        after = open(_lane_st, "rb").read()
        logtail = open(LOG, encoding="ascii", errors="replace").read()
        ok("S14 mid-rebase guard no-op + zero state write "
           "(r381 lane-primary surface)",
           rc == 0 and before == after and "mid-operation" in logtail)
        os.rmdir(os.path.join(_GIT_DIR, "rebase-merge"))
        _GIT_DIR = _git_orig
        # S14b corrupt-state refusal (r201): marker-poisoned EXISTING
        # state surface -> tick exit 2 + byte-identical (anti-wipe).
        # r381: the AUTHORITATIVE surface is the lane -- a corrupt lane
        # must refuse even with a readable legacy base (never a silent
        # fallback past the live surface).
        with open(_lane_st, "w", encoding="utf-8") as fh:
            fh.write('{"launches": [{"x": 1}]\n<<<<<<< ours\n}')
        before = open(_lane_st, "rb").read()
        rc = tick(dry=True)
        after = open(_lane_st, "rb").read()
        ok("S14b corrupt state lane -> exit 2 + no wipe (no fallback)",
           rc == 2 and before == after)
        # S14c absent lane + absent base -> fresh start (first-run compat)
        os.remove(_lane_st)
        rc = tick(dry=True)
        ok("S14c absent lane/base -> fresh start (compat)",
           rc == 0 and _load_state()["last_tick"]["verdict"] == "dry_launch")
        # S14d r381 transition fallback: lane absent + frozen legacy
        # base present -> tick boots from the base, and the save
        # PERSISTS to the lane (bootstrap); the base itself is never
        # rewritten.  Fixture removed afterwards so the existence-filter
        # tuple legs below stay honest.
        os.remove(_lane_st)
        with open(STATE, "w", encoding="utf-8") as fh:
            json.dump({"last_tick": {"ts": "2026-09-27 00:00:01",
                                     "machine": "legacy"},
                       "launches": [{"ts": "2026-09-27 00:00:01",
                                     "machine": "bm-z"}]}, fh)
        rc = tick(dry=True)
        lane14d = json.load(open(_lane_st, encoding="utf-8"))
        ok("S14d lane absent -> boot from frozen base, persist to lane",
           rc == 0 and lane14d.get("lane_machine") == _machine_id()
           and lane14d.get("last_tick", {}).get("verdict") == "dry_launch"
           and {"ts": "2026-09-27 00:00:01",
                "machine": "bm-z"} in lane14d.get("launches", []))
        os.remove(STATE)
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
        add_args_all = []          # r290: full argv of every git add
        fail_at = {"stage": None}
        fail_next = {"q": []}     # r282: ordered one-shot stage faults
        pull_sim = {"mode": None}  # r344: "ours_conflict"|"foreign_refusal"
        push_sim = {"mid_appears": False}  # D-20260928-02: session rebase
        #                                       appears AT push stage (the
        #                                       r344 live-fire ordering:
        #                                       marker absent at add)
        behind_sim = {"on": False}   # r351: origin moved the pool past
        #                                  HEAD (probe returns "stale")

        def _fake_git(args):
            if args[0] in ("add", "commit", "push", "pull", "rebase"):
                git_seq.append(args[0])   # write stages only -- r351
                #                            fetch/diff probes stay off
                #                            the sequence assertions
            if args[0] == "diff" and behind_sim["on"]:
                return 1, ""               # r351 pool-behind-origin face
            if args[0] == "add":
                add_args_all.append(args[1:])
            if args[0] == "push" and push_sim["mid_appears"]:
                mid = os.path.join(_GIT_DIR, "rebase-merge")
                os.makedirs(mid, exist_ok=True)
            if args[0] == "pull" and pull_sim["mode"]:
                mid = os.path.join(_GIT_DIR, "rebase-merge")
                os.makedirs(mid, exist_ok=True)
                if pull_sim["mode"] == "ours_conflict":
                    return 1, "fake pull: CONFLICT (content): ours"
                return 1, ("It seems that there is already a "
                           "rebase-merge directory, and I wonder if "
                           "you are in the middle of another rebase")
            if args[0] == "rebase":
                mid = os.path.join(_GIT_DIR, "rebase-merge")
                if os.path.isdir(mid):
                    os.rmdir(mid)
                return 0, ""
            if fail_next["q"] and fail_next["q"][0] == args[0]:
                fail_next["q"].pop(0)
                return 1, "fake git fault (queued)"
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
        r15 = _claim_shard({"key": "s0"}, "bm-b", "E1")
        p15 = json.load(open(POOL, encoding="utf-8"))["entries"][0]["shards"][0]
        ok("S15a unclaimed -> claimed (owner+since written, git 3-step)",
           r15 is True and p15.get("owner") == "bm-b"
           and bool(p15.get("owner_since"))
           and git_seq == ["add", "commit", "push"])
        # S15b rival FRESH claim -> lost, pool untouched
        _pool_with({"key": "s0", "status": "ready", "owner": "bm-z",
                    "owner_since": _now()})
        r15b = _claim_shard({"key": "s0"}, "bm-b", "E1")
        p15b = json.load(open(POOL, encoding="utf-8"))["entries"][0]["shards"][0]
        ok("S15b rival fresh claim -> yield, no overwrite",
           r15b is False and p15b.get("owner") == "bm-z")
        # S15c rival STALE claim -> takeover, owner rewritten
        _pool_with({"key": "s0", "status": "ready", "owner": "bm-z",
                    "owner_since": "2026-09-24 18:00:00"})
        r15c = _claim_shard({"key": "s0"}, "bm-b", "E1")
        p15c = json.load(open(POOL, encoding="utf-8"))["entries"][0]["shards"][0]
        ok("S15c rival stale claim -> takeover rewrites owner",
           r15c is True and p15c.get("owner") == "bm-b")
        # S15d pre-commit git fault -> False + pre-claim bytes restored
        _pool_with({"key": "s0", "status": "ready", "owner": None})
        fail_at["stage"] = "add"
        r15d = _claim_shard({"key": "s0"}, "bm-b", "E1")
        p15d = json.load(open(POOL, encoding="utf-8"))["entries"][0]["shards"][0]
        fail_at["stage"] = None
        ok("S15d git add fault -> yield + pool restored (owner None)",
           r15d is False and p15d.get("owner") is None)
        # S15e push lost AFTER commit (recovery exhausted) -> yield but
        # claim bytes kept (local commit reconciled by session S0 rebase)
        _pool_with({"key": "s0", "status": "ready", "owner": None})
        fail_at["stage"] = "push"
        r15e = _claim_shard({"key": "s0"}, "bm-b", "E1")
        p15e = json.load(open(POOL, encoding="utf-8"))["entries"][0]["shards"][0]
        fail_at["stage"] = None
        ok("S15e push lost post-commit -> yield, claim kept on disk",
           r15e is False and p15e.get("owner") == "bm-b")
        # S15f r282 rebase-retry recovery: push rejected once (origin
        # moved), pull --rebase clean-tree ok, push retry ok -> claim
        # True (live case: 00:30 revosc claim lost to a clean-tree push
        # reject, 20min of avoidable fill starvation).
        _pool_with({"key": "s0", "status": "ready", "owner": None})
        fail_next["q"] = ["push"]
        git_seq.clear()
        r15f = _claim_shard({"key": "s0"}, "bm-b", "E1")
        fail_next["q"] = []
        ok("S15f push reject -> rebase-retry -> claimed",
           r15f is True and git_seq == ["add", "commit", "push",
                                         "pull", "push"])
        # S15g r282 fail-safe (r344 semantics): rebase refused WITHOUT
        # starting one (dirty tree; no marker before or after) -> NO
        # abort (nothing of ours to abort), yield, claim bytes kept
        _pool_with({"key": "s0", "status": "ready", "owner": None})
        fail_next["q"] = ["push", "pull"]
        git_seq.clear()
        r15g = _claim_shard({"key": "s0"}, "bm-b", "E1")
        p15g = json.load(open(POOL, encoding="utf-8"))["entries"][0]["shards"][0]
        fail_next["q"] = []
        ok("S15g clean refusal (dirty tree) -> no abort + yield, claim "
           "kept",
           r15g is False and p15g.get("owner") == "bm-b"
           and git_seq[-1] == "pull" and "rebase" not in git_seq)
        # r344 abort-ownership legs: swap _GIT_DIR to the hermetic
        # fake_git dir (S14 precedent) so marker probes never touch
        # the real .git
        _gd_orig = _GIT_DIR
        _GIT_DIR = os.path.join(tmp, "fake_git")
        os.makedirs(_GIT_DIR, exist_ok=True)
        _mid = os.path.join(_GIT_DIR, "rebase-merge")
        # S15g2 foreign rebase in flight (the 21:48:48 live-fire shape:
        # session fold mid-rebase when the tick claim push rejects) ->
        # NO pull, NO abort, marker SURVIVES, claim kept. The rebase
        # starts AT push stage (push_sim), not pre-add -- the pre-add
        # guard (S15j) owns the earlier window now.
        _pool_with({"key": "s0", "status": "ready", "owner": None})
        fail_next["q"] = ["push"]
        push_sim["mid_appears"] = True
        git_seq.clear()
        r15g2 = _claim_shard({"key": "s0"}, "bm-b", "E1")
        marker_g2 = os.path.isdir(_mid)
        os.rmdir(_mid)
        push_sim["mid_appears"] = False
        p15g2 = json.load(open(POOL, encoding="utf-8"))["entries"][0]["shards"][0]
        fail_next["q"] = []
        ok("S15g2 foreign rebase in flight -> no pull/abort, marker "
           "survives, claim kept",
           r15g2 is False and marker_g2
           and git_seq == ["add", "commit", "push"]
           and p15g2.get("owner") == "bm-b")
        # S15k r351 pool-behind-origin defer (b5be80cd live-fire): the
        # tree forked before origin's pool entries landed -> claim YIELDS
        # without any git write (no doomed-to-rebase commit, no blind
        # local pool face); bytes restored, next post-pull tick re-claims.
        _pool_with({"key": "s0", "status": "ready", "owner": None})
        behind_sim["on"] = True
        git_seq.clear()
        r15k = _claim_shard({"key": "s0"}, "bm-b", "E1")
        p15k = json.load(open(POOL, encoding="utf-8"))["entries"][0]["shards"][0]
        behind_sim["on"] = False
        logtail = open(LOG, encoding="ascii", errors="replace").read()
        ok("S15k pool behind origin -> defer, zero git write, bytes kept",
           r15k is False and p15k.get("owner") is None
           and git_seq == [] and "r351" in logtail)
        # S15k2 probe fault fail-open: fetch unavailable -> None ->
        # legacy claim flow unchanged (push-rejection path still owns
        # the moved-origin case).
        _pool_with({"key": "s0", "status": "ready", "owner": None})
        fail_at["stage"] = "fetch"
        git_seq.clear()
        r15k2 = _claim_shard({"key": "s0"}, "bm-b", "E1")
        p15k2 = json.load(open(POOL, encoding="utf-8"))["entries"][0]["shards"][0]
        fail_at["stage"] = None
        ok("S15k2 probe fault -> fail-open, legacy claim proceeds",
           r15k2 is True and p15k2.get("owner") == "bm-b"
           and git_seq == ["add", "commit", "push"])
        # S15g3 OUR pull started a rebase and it conflicted -> abort
        # OURS (marker cleared), yield keeps claim
        _pool_with({"key": "s0", "status": "ready", "owner": None})
        fail_next["q"] = ["push"]
        pull_sim["mode"] = "ours_conflict"
        git_seq.clear()
        r15g3 = _claim_shard({"key": "s0"}, "bm-b", "E1")
        marker_g3 = not os.path.exists(_mid)
        pull_sim["mode"] = None
        fail_next["q"] = []
        ok("S15g3 our pull conflicted -> abort ours (marker cleared), "
           "claim kept",
           r15g3 is False and marker_g3
           and git_seq[-2:] == ["pull", "rebase"])
        # S15g4 residual race: session rebase started INSIDE the claim
        # window (marker absent at the pre-pull check) -> git refuses
        # with "already a rebase" -> NO abort despite marker present
        # (ownership via refusal signature), marker survives
        _pool_with({"key": "s0", "status": "ready", "owner": None})
        fail_next["q"] = ["push"]
        pull_sim["mode"] = "foreign_refusal"
        git_seq.clear()
        r15g4 = _claim_shard({"key": "s0"}, "bm-b", "E1")
        marker_g4 = os.path.isdir(_mid)
        os.rmdir(_mid)
        pull_sim["mode"] = None
        fail_next["q"] = []
        ok("S15g4 mid-window foreign rebase (already-a-rebase refusal) "
           "-> no abort, marker survives, claim kept",
           r15g4 is False and marker_g4
           and git_seq == ["add", "commit", "push", "pull"]
           and "rebase" not in git_seq)
        _GIT_DIR = _gd_orig
        # S15h r282 recovery exhausted: rebase ok but push retry still
        # rejected -> yield, claim bytes kept
        _pool_with({"key": "s0", "status": "ready", "owner": None})
        fail_next["q"] = ["push", "push"]
        r15h = _claim_shard({"key": "s0"}, "bm-b", "E1")
        p15h = json.load(open(POOL, encoding="utf-8"))["entries"][0]["shards"][0]
        fail_next["q"] = []
        ok("S15h push retry lost -> yield, claim kept",
           r15h is False and p15h.get("owner") == "bm-b")
        # S15i r290 self-commit: the claim commit carries the tick's OWN
        # dirt (autofill_state + crash_fuse) so the r282 recovery rebase
        # stays reachable in inter-round tick-dirtied windows (r288
        # live: keepalive push lost to tick dirt -> claim stranded ->
        # takeover gate reopened -> double burn). Absent files are
        # never git-added (existence filter).
        with open(FUSE, "w", encoding="utf-8") as fh:
            json.dump({"sigs": {}}, fh)
        _pool_with({"key": "s0", "status": "ready", "owner": None})
        add_args_all.clear()
        r15i = _claim_shard({"key": "s0"}, "bm-b", "E1")
        _lane_pl = _lane_path_for(POOL)
        ok("S15i claim add carries pool+fuse+lanes "
           "(r290 self-commit; state dirt = its lane, r381)",
           r15i is True and add_args_all
           and add_args_all[-1] == (POOL, FUSE, _lane_st,
                                    _lane_pl))
        os.remove(FUSE)
        _pool_with({"key": "s0", "status": "ready", "owner": None})
        add_args_all.clear()
        r15i2 = _claim_shard({"key": "s0"}, "bm-b", "E1")
        ok("S15i absent fuse -> existence-filtered add (pool+lanes)",
           r15i2 is True and add_args_all
           and add_args_all[-1] == (POOL, _lane_st, _lane_pl))
        # S15l D-20260928-03(1) batch-1: a successful claim also writes
        # this machine's pool lane -- payload parity + lane_machine
        # signature (anti-swallow record of the committed bytes).
        _pool_with({"key": "s0", "status": "ready", "owner": None})
        r15l = _claim_shard({"key": "s0"}, "bm-b", "E1")
        lane15l = json.load(open(_lane_pl, encoding="utf-8"))
        p15l = json.load(open(POOL, encoding="utf-8"))
        ok("S15l claim writes own pool lane (signed, owner carried)",
           r15l is True and lane15l.get("lane_machine") == _machine_id()
           and lane15l["entries"][0]["shards"][0]["owner"] == "bm-b"
           and p15l["entries"][0]["shards"][0]["owner"] == "bm-b")
        # S15m D-03(1) pool retirement: deferred claim -> TWO-SIDED
        # rollback -- shared AND lane restored to pre-op bytes (a
        # lane-only surviving claim would resurrect a phantom owner at
        # the next union settle, r288 family). r117 self-control: the
        # leg seeds its own lane state, zero residue dependence.
        _gd_orig = _GIT_DIR
        _GIT_DIR = os.path.join(tmp, "fake_git")
        os.makedirs(_GIT_DIR, exist_ok=True)
        os.makedirs(os.path.join(_GIT_DIR, "rebase-merge"), exist_ok=True)
        _pool_with({"key": "s0", "status": "ready", "owner": None})
        _write_lane_file(POOL, {"entries": [dict(
            entry, shards=[{"key": "s0", "status": "done",
                            "owner": "bm-z"}])]})
        lane15m_prev = open(_lane_pl, "rb").read()
        r15m = _claim_shard({"key": "s0"}, "bm-b", "E1")
        lane15m = open(_lane_pl, "rb").read()
        os.rmdir(os.path.join(_GIT_DIR, "rebase-merge"))
        _GIT_DIR = _gd_orig
        ok("S15m claim defer -> two-sided rollback (lane byte-exact, "
           "no phantom owner)",
           r15m is False and lane15m == lane15m_prev
           and json.load(open(POOL, encoding="utf-8"))
           ["entries"][0]["shards"][0].get("owner") is None)
        # S18d D-03(1) r381 retirement: _save_state writes ONLY the state
        # lane (lane-primary); the shared face must stay untouched
        # (frozen legacy base law).
        _save_state({"last_tick": {"ts": "2026-09-28 02:00:01",
                                    "machine": "bm-a"}, "launches": []})
        lane18 = json.load(open(_lane_st, encoding="utf-8"))
        ok("S18d state lane written (signed); shared face untouched",
           lane18.get("lane_machine") == _machine_id()
           and lane18["last_tick"]["ts"] == "2026-09-28 02:00:01"
           and not os.path.exists(STATE))
        # S18e D-03(1) batch-2 closeout: _save_fuse writes the fuse lane
        # too (8/8 B-faces wired; same dual-track law as state/pool).
        _save_fuse({"sigs": {"scripts/x.py|run": {"count": 1}}})
        _lane_fu = _lane_path_for(FUSE)
        lane18e = json.load(open(_lane_fu, encoding="utf-8"))
        fuse18e = json.load(open(FUSE, encoding="utf-8"))
        ok("S18e fuse lane written (signed, sigs byte-parity)",
           lane18e.get("lane_machine") == _machine_id()
           and lane18e["sigs"] == fuse18e["sigs"]
           and lane18e["sigs"]["scripts/x.py|run"]["count"] == 1)
        # S15j D-20260928-02(1) pre-add mid-op guard (r331 race): a
        # session rebase/merge starting INSIDE the sampling+scan window
        # (after the r201 entry guard, before add) -> claim git write
        # DEFERRED: zero git ops, pre-claim pool bytes restored, marker
        # survives (git write right belongs to the loop session).
        _gd_orig = _GIT_DIR
        _GIT_DIR = os.path.join(tmp, "fake_git")
        os.makedirs(_GIT_DIR, exist_ok=True)
        _mid = os.path.join(_GIT_DIR, "rebase-merge")
        os.makedirs(_mid, exist_ok=True)
        _pool_with({"key": "s0", "status": "ready", "owner": None})
        git_seq.clear()
        r15j = _claim_shard({"key": "s0"}, "bm-b", "E1")
        p15j = json.load(open(POOL, encoding="utf-8"))["entries"][0]["shards"][0]
        marker_j = os.path.isdir(_mid)
        os.rmdir(_mid)
        _GIT_DIR = _gd_orig
        ok("S15j mid-op mid-tick -> claim deferred, zero git ops, "
           "pool restored, marker survives",
           r15j is False and p15j.get("owner") is None
           and git_seq == [] and marker_j)
        # S15n r141 cross-entry key-collision law: shard keys are
        # unique only WITHIN an entry. Live case (W2-SCREEN first
        # burn, MSG-20260928-0655): key-only fresh-read re-find hit
        # the W1 same-key DONE shard first in pool order -> claim
        # wrote owner onto the wrong entry, true W2 shard stayed
        # unclaimed. Double key (entry.id, shard.key) claims the
        # true shard, done sibling untouched.
        w1 = dict(entry, id="E1",
                  shards=[{"key": "s0", "status": "done",
                           "owner": None, "owner_since": None}])
        w2 = dict(entry, id="E2",
                  shards=[{"key": "s0", "status": "ready",
                           "owner": None, "owner_since": None}])
        with open(POOL, "w", encoding="utf-8") as fh:
            json.dump({"entries": [w1, w2]}, fh)
        git_seq.clear()
        r15n = _claim_shard({"key": "s0"}, "bm-b", "E2")
        p15n = json.load(open(POOL, encoding="utf-8"))
        ok("S15n cross-entry same-key -> double-key claims true "
           "shard (done sibling untouched)",
           r15n is True
           and p15n["entries"][0]["shards"][0].get("owner") is None
           and p15n["entries"][1]["shards"][0].get("owner") == "bm-b"
           and git_seq == ["add", "commit", "push"])
        # S15o fail-closed anchor: no entry matches the anchor id
        # (or the caller passed None) -> claim miss, zero writes.
        _pool_with({"key": "s0", "status": "ready", "owner": None})
        before_o = open(POOL, "rb").read()
        r15o = _claim_shard({"key": "s0"}, "bm-b", "E9")
        r15o2 = _claim_shard({"key": "s0"}, "bm-b", None)
        ok("S15o anchor miss / None anchor -> fail-closed claim "
           "miss, pool byte-identical",
           r15o is False and r15o2 is False
           and open(POOL, "rb").read() == before_o)
        # S15p D-03 pool retirement anti-swallow: a session defer
        # landing on the shared face INSIDE the claim window (between
        # the fresh read and the settle) SURVIVES -- the union settle
        # re-reads every source fresh, so the pre-retirement blind
        # write of a stale in-memory copy (r378 catch-4 live shape:
        # session defer swallowed by the tick rewrite) can no longer
        # lose it, and the claim still lands (marker law).
        _pool_with({"key": "s0", "status": "ready", "owner": None})
        _settle_real = _pool_settle

        def _settle_with_mid_session_write():
            cur = json.load(open(POOL, encoding="utf-8"))
            cur["entries"][0]["status"] = "waiting"
            cur["entries"][0]["defer_note"] = "deliberate hold"
            with open(POOL, "w", encoding="utf-8") as fh:
                json.dump(cur, fh)
            return _settle_real()

        _pool_settle = _settle_with_mid_session_write
        r15p = _claim_shard({"key": "s0"}, "bm-b", "E1")
        p15p = json.load(open(POOL, encoding="utf-8"))["entries"][0]
        _pool_settle = _settle_real
        ok("S15p mid-window session defer survives the union settle "
           "(r378 marker law) + claim lands",
           r15p is True
           and p15p.get("status") == "waiting"
           and p15p.get("defer_note") == "deliberate hold"
           and p15p["shards"][0].get("owner") == "bm-b")
        # S15q settle degraded (corrupt rival source mid push-storm /
        # merge fault) -> pre-retirement direct shared write keeps the
        # claim fleet-visible (r384 fuse-gate fallback family: a
        # lane-only island claim invites a rival STALE takeover).
        _pool_with({"key": "s0", "status": "ready", "owner": None})
        _pool_settle_bad = _pool_settle
        _pool_settle = lambda: False
        git_seq.clear()
        r15q = _claim_shard({"key": "s0"}, "bm-b", "E1")
        p15q = json.load(open(POOL, encoding="utf-8"))["entries"][0]["shards"][0]
        _pool_settle = _pool_settle_bad
        ok("S15q settle degraded -> direct shared write fallback "
           "(claim fleet-visible, git 3-step)",
           r15q is True and p15q.get("owner") == "bm-b"
           and git_seq == ["add", "commit", "push"])
        # S17 r288 claim-keepalive: a locally-alive runner on a
        # self-owned shard with an aging claim-stamp refreshes
        # owner_since (commit+push) so remote takeover gates never see
        # a live owner as stale (live-fire: CN-TREND 30min burn +
        # fallback-stranded heartbeat -> bm-a takeover + double launch).
        _ka_runner = _runner_alive
        _runner_alive = lambda r: True
        # S17a alive runner + stale own claim -> refreshed, git 3-step
        _pool_with({"key": "s0", "status": "ready", "owner": "bm-b",
                    "owner_since": "2026-09-24 18:00:00"})
        git_seq.clear()
        ka = _keepalive_claims(json.load(open(POOL, encoding="utf-8")),
                               "bm-b")
        p17 = json.load(open(POOL, encoding="utf-8"))["entries"][0]["shards"][0]
        ok("S17a alive runner + stale own claim -> keepalive refresh",
           ka == ["s0"]
           and p17.get("owner_since") != "2026-09-24 18:00:00"
           and git_seq == ["add", "commit", "push"])
        # S17b fresh stamp -> no refresh, no git (cadence guard)
        _pool_with({"key": "s0", "status": "ready", "owner": "bm-b",
                    "owner_since": _now()})
        git_seq.clear()
        ka = _keepalive_claims(json.load(open(POOL, encoding="utf-8")),
                               "bm-b")
        ok("S17b fresh stamp -> no-op (cadence guard)",
           ka == [] and git_seq == [])
        # S17c rival-owned shard OR dead runner -> never touched
        # (a completed takeover stays lost -- do not fight it)
        _pool_with({"key": "s0", "status": "ready", "owner": "bm-z",
                    "owner_since": "2026-09-24 18:00:00"})
        ka = _keepalive_claims(json.load(open(POOL, encoding="utf-8")),
                               "bm-b")
        _runner_alive = lambda r: False
        _pool_with({"key": "s0", "status": "ready", "owner": "bm-b",
                    "owner_since": "2026-09-24 18:00:00"})
        ka2 = _keepalive_claims(json.load(open(POOL, encoding="utf-8")),
                                "bm-b")
        p17c = json.load(open(POOL, encoding="utf-8"))["entries"][0]["shards"][0]
        ok("S17c rival-owned / dead runner -> no touch (no fight)",
           ka == [] and ka2 == []
           and p17c.get("owner_since") == "2026-09-24 18:00:00")
        # S17d push fault post-commit -> refreshed bytes kept on disk
        _runner_alive = lambda r: True
        _pool_with({"key": "s0", "status": "ready", "owner": "bm-b",
                    "owner_since": "2026-09-24 18:00:00"})
        fail_at["stage"] = "push"
        ka = _keepalive_claims(json.load(open(POOL, encoding="utf-8")),
                               "bm-b")
        p17d = json.load(open(POOL, encoding="utf-8"))["entries"][0]["shards"][0]
        fail_at["stage"] = None
        ok("S17d push lost post-commit -> refresh kept, keys reported",
           ka == ["s0"]
           and p17d.get("owner_since") != "2026-09-24 18:00:00")
        # S17e r290: keepalive commit also self-commits tick-owned dirt
        # -- the refresh push must survive inter-round tick dirt so the
        # takeover gate keeps seeing a live owner (r288 root cause:
        # refresh push unreachable while the tree was tick-dirtied).
        with open(FUSE, "w", encoding="utf-8") as fh:
            json.dump({"sigs": {}}, fh)
        _pool_with({"key": "s0", "status": "ready", "owner": "bm-b",
                    "owner_since": "2026-09-24 18:00:00"})
        add_args_all.clear()
        ka = _keepalive_claims(json.load(open(POOL, encoding="utf-8")),
                               "bm-b")
        ok("S17e keepalive add carries pool+fuse+lanes "
           "(r290; state dirt = its lane, r381)",
           ka == ["s0"] and add_args_all
           and add_args_all[-1] == (POOL, FUSE, _lane_st,
                                    _lane_pl, _lane_fu))
        # S17f/g r344 abort-ownership (keepalive leg): mirror of the
        # claim-leg ownership law -- foreign rebase survives, ours gets
        # aborted
        _gd_orig = _GIT_DIR
        _GIT_DIR = os.path.join(tmp, "fake_git")
        os.makedirs(_GIT_DIR, exist_ok=True)
        _mid = os.path.join(_GIT_DIR, "rebase-merge")
        _pool_with({"key": "s0", "status": "ready", "owner": "bm-b",
                    "owner_since": "2026-09-24 18:00:00"})
        fail_next["q"] = ["push"]
        push_sim["mid_appears"] = True   # session rebase starts AT push
        git_seq.clear()
        ka_f = _keepalive_claims(json.load(open(POOL, encoding="utf-8")),
                                 "bm-b")
        marker_kf = os.path.isdir(_mid)
        os.rmdir(_mid)
        push_sim["mid_appears"] = False
        fail_next["q"] = []
        ok("S17f foreign rebase -> keepalive no pull/abort, marker "
           "survives, refresh kept",
           ka_f == ["s0"] and marker_kf
           and git_seq == ["add", "commit", "push"])
        _pool_with({"key": "s0", "status": "ready", "owner": "bm-b",
                    "owner_since": "2026-09-24 18:00:00"})
        fail_next["q"] = ["push"]
        pull_sim["mode"] = "ours_conflict"
        git_seq.clear()
        ka_g = _keepalive_claims(json.load(open(POOL, encoding="utf-8")),
                                 "bm-b")
        marker_kg = not os.path.exists(_mid)
        pull_sim["mode"] = None
        fail_next["q"] = []
        ok("S17g our pull conflicted -> keepalive aborts ours, refresh "
           "kept",
           ka_g == ["s0"] and marker_kg
           and git_seq[-2:] == ["pull", "rebase"])
        # S17h D-20260928-02(1) pre-add mid-op guard (keepalive leg):
        # session rebase/merge appearing mid-tick -> refresh git write
        # DEFERRED (zero git ops, pre-refresh bytes restored, marker
        # survives); next tick re-refreshes under the age gate.
        os.makedirs(_mid, exist_ok=True)
        _pool_with({"key": "s0", "status": "ready", "owner": "bm-b",
                    "owner_since": "2026-09-24 18:00:00"})
        git_seq.clear()
        ka_h = _keepalive_claims(json.load(open(POOL, encoding="utf-8")),
                                 "bm-b")
        p17h = json.load(open(POOL, encoding="utf-8"))["entries"][0]["shards"][0]
        marker_kh = os.path.isdir(_mid)
        os.rmdir(_mid)
        ok("S17h mid-op mid-tick -> keepalive deferred, zero git ops, "
           "bytes restored, marker survives",
           ka_h == [] and git_seq == []
           and p17h.get("owner_since") == "2026-09-24 18:00:00"
           and marker_kh)
        # S17i r351 pool-behind-origin defer (keepalive leg): the
        # b5be80cd live-fire face -- origin moved the pool past HEAD ->
        # refresh YIELDS with zero git ops and pre-refresh bytes
        # restored; next post-pull tick re-refreshes (idempotent).
        _pool_with({"key": "s0", "status": "ready", "owner": "bm-b",
                    "owner_since": "2026-09-24 18:00:00"})
        behind_sim["on"] = True
        git_seq.clear()
        ka_i = _keepalive_claims(json.load(open(POOL, encoding="utf-8")),
                                 "bm-b")
        p17i = json.load(open(POOL, encoding="utf-8"))["entries"][0]["shards"][0]
        behind_sim["on"] = False
        ok("S17i pool behind origin -> keepalive deferred, zero git "
           "ops, bytes restored",
           ka_i == [] and git_seq == []
           and p17i.get("owner_since") == "2026-09-24 18:00:00")
        # S17j D-03 pool retirement (keepalive leg): mid-op defer ->
        # TWO-SIDED rollback; the refresh never touches shared (guards
        # run before the settle), the lane rolls back byte-exact to
        # the pre-op snapshot (r117: the leg seeds its own lane).
        os.makedirs(_mid, exist_ok=True)
        _pool_with({"key": "s0", "status": "ready", "owner": "bm-b",
                    "owner_since": "2026-09-24 18:00:00"})
        _write_lane_file(POOL, json.load(open(POOL, encoding="utf-8")))
        lane17j_prev = open(_lane_pl, "rb").read()
        git_seq.clear()
        ka_j = _keepalive_claims(json.load(open(POOL, encoding="utf-8")),
                                 "bm-b")
        lane17j = open(_lane_pl, "rb").read()
        os.rmdir(_mid)
        ok("S17j keepalive defer -> two-sided rollback (lane "
           "byte-exact, shared untouched)",
           ka_j == [] and git_seq == []
           and lane17j == lane17j_prev
           and json.load(open(POOL, encoding="utf-8"))
           ["entries"][0]["shards"][0]["owner_since"]
           == "2026-09-24 18:00:00")
        _GIT_DIR = _gd_orig
        _runner_alive = _ka_runner
        # S18 null-runner entries (live 2026-09-27 02:40-07:10: keepalive
        # scan AttributeError'd on an explicit runner=null pool entry --
        # null guard + regression legs; S18c replays the exact live shape
        # and asserts zero fault-log delta + zero refresh + file intact).
        ok("S18a _runner_alive(None) -> False (null guard, no psutil)",
           _runner_alive(None) is False)
        ok("S18b _runner_alive('') -> False", _runner_alive("") is False)
        with open(POOL, "w", encoding="utf-8") as fh:
            json.dump({"entries": [dict(
                entry, runner=None,
                shards=[dict(entry["shards"][0], owner="bm-b",
                             owner_since="2026-09-24 18:00:00")])]}, fh)
        log18 = (open(LOG, encoding="utf-8", errors="replace").read()
                 if os.path.exists(LOG) else "")
        ka = _keepalive_claims(
            json.load(open(POOL, encoding="utf-8")), "bm-b")
        ok("S18c null-runner entry -> keepalive scan no fault, no refresh",
           ka == []
           and "keepalive fault" not in
           open(LOG, encoding="utf-8", errors="replace").read()[len(log18):]
           and json.load(open(POOL, encoding="utf-8"))
           ["entries"][0]["shards"][0]["owner_since"]
           == "2026-09-24 18:00:00")
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
        # S16i r177bm-c fast-confirm: an instant-exit launch (runner
        # dead, checkpoint face untouched since spawn, age past
        # FAST_CONFIRM_MIN but well under FUSE_CONFIRM_MIN) counts NOW
        # -- the 25-min window must not feed a claim+launch+commit
        # churn loop on host-ineligible gates (live-fire 18:22-18:31
        # W4-JUDGE P5C deep-panel absence on non-data hosts).
        st16i = {"launches": [
            {"ts": (datetime.now() - timedelta(minutes=6)).strftime(
                "%Y-%m-%d %H:%M:%S"), "machine": "bm-b",
             "verdict": "launched", "entry": "E1", "shard": "s0",
             "runner_sha256": "abc123"}]}
        pool16i = {"entries": [dict(entry, shards=[
            {"key": "s0", "status": "ready", "owner": None,
             "checkpoint": "results/fake_ns_ckpt/judge.jsonl (row "
                          "resume)"}])]}
        fu16i = {"sigs": {}}
        d16i = _confirm_crashes(st16i, pool16i, "bm-b", fu16i)
        ok("S16i fast-confirm: dead+zero-progress+age>FAST counts now",
           d16i and fu16i["sigs"].get("scripts/fake_runner.py|run",
                                      {}).get("count") == 1
           and st16i["launches"][0]["crash_counted"])
        # S16i2 negative: checkpoint touched after spawn -> real burn
        # died mid-flight; the slow flip-lag window still governs (a
        # successful-but-unflipped run must never fast-count).
        os.makedirs(os.path.join(os.path.dirname(POOL), "fake_ns_ckpt"),
                    exist_ok=True)
        _f16i = os.path.join(os.path.dirname(POOL), "fake_ns_ckpt",
                             "judge.jsonl")
        with open(_f16i, "w", encoding="utf-8") as fh:
            fh.write("{}")
        st16i2 = {"launches": [
            {"ts": (datetime.now() - timedelta(minutes=6)).strftime(
                "%Y-%m-%d %H:%M:%S"), "machine": "bm-b",
             "verdict": "launched", "entry": "E1", "shard": "s0",
             "runner_sha256": "abc123"}]}
        fu16i2 = {"sigs": {}}
        _confirm_crashes(st16i2, pool16i, "bm-b", fu16i2)
        ok("S16i2 fast-confirm negative: post-spawn checkpoint touch "
           "-> slow window holds (not counted)",
           not fu16i2["sigs"]
           and not st16i2["launches"][0].get("crash_counted"))
        os.remove(_f16i)
        os.rmdir(os.path.join(os.path.dirname(POOL), "fake_ns_ckpt"))
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
        # leg isolation (r117 hermetic law + r142 bm-c machine law):
        # _save_fuse dual-tracks the OWN lane -- on the authoring
        # machine lane_a == own lane so clearing bm-a sufficed, but on
        # any other machine the own lane (bm-c here) carried prior-leg
        # rows into the merged gate (S16c/e/f FAIL face) -> clear ALL
        # fuse lanes at every shared-fixture replant.
        def _clear_fuse_lanes():
            import glob as _g
            for _lf in _g.glob(os.path.join(
                    os.path.dirname(FUSE), "crash_fuse.*.json")):
                os.remove(_lf)
        _clear_fuse_lanes()
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
        _clear_fuse_lanes()
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
        _clear_fuse_lanes()
        # S16f D-03(1) debt-table (1) merged-read gate: a crash confirmed
        # on ANOTHER machine that lives only in its lane file (shared row
        # lost to a push-storm resolve, r376 family) must refuse relaunch
        # here too -- the registry is cross-machine; and the union write
        # absorbs the lane-only row into the shared file (protects
        # machines that have not pulled this batch yet).
        with open(FUSE, "w", encoding="utf-8") as fh:
            json.dump({"sigs": {}}, fh)
        lane_b = os.path.join(os.path.dirname(FUSE), "crash_fuse.bm-b.json")
        with open(lane_b, "w", encoding="utf-8") as fh:
            json.dump({"sigs": {"scripts/fake_runner.py|run": {
                "code_sha256": None, "count": 1, "refusals": 0}},
                "lane_machine": "bm-b"}, fh)
        with open(POOL, "w", encoding="utf-8") as fh:
            json.dump(pool16, fh)
        rc = tick(dry=True)
        st16f = _load_state()["last_tick"]
        fu16f = json.load(open(FUSE, encoding="utf-8"))
        ok("S16f lane-only sig (bm-b lane) refuses relaunch via merged "
           "gate; union write absorbs it into shared",
           rc == 0 and st16f["verdict"] == "fuse_refused_crash_loop"
           and st16f.get("fuse_refusals") == 1
           and fu16f["sigs"]["scripts/fake_runner.py|run"]["refusals"] == 1)
        os.remove(lane_b)
        # S16g merge-path fault -> bare shared gate (degraded pre-slice
        # semantics, honest log): the refusal registry still enforced.
        with open(FUSE, "w", encoding="utf-8") as fh:
            json.dump({"sigs": {"scripts/fake_runner.py|run": {
                "code_sha256": None, "count": 1, "refusals": 0}}}, fh)
        _gate_orig = _fuse_gate_view
        _fuse_gate_view = lambda: (_ for _ in ()).throw(
            RuntimeError("simulated merge-path fault"))
        rc = tick(dry=True)
        _fuse_gate_view = _gate_orig
        st16g = _load_state()["last_tick"]
        ok("S16g merge-path fault -> bare shared gate still refuses",
           rc == 0 and st16g["verdict"] == "fuse_refused_crash_loop"
           and st16g.get("fuse_refusals") == 1)
        # S16h D-03(2) cleared-tombstone: r389 drift shape live replay --
        # own code-change clear records a tombstone (shared + own lane);
        # a FOREIGN lane still carrying the stale sig cannot resurrect
        # it through the merged gate (suppressed -> launch proceeds) and
        # reconcile converges (merged == shared, permanent zero-drift).
        _clear_fuse_lanes()
        mid16h = _machine_id()
        sig16h = "scripts/fake_runner.py|run"
        with open(FUSE, "w", encoding="utf-8") as fh:
            json.dump({"sigs": {sig16h: {
                "code_sha256": "deadbeef0000", "count": 1,
                "refusals": 0,
                "last_crash_ts": "2026-09-28 06:20:04"}}}, fh)
        lane_c = os.path.join(os.path.dirname(FUSE), "crash_fuse.bm-c.json")
        with open(lane_c, "w", encoding="utf-8") as fh:
            json.dump({"sigs": {sig16h: {
                "code_sha256": "deadbeef0000", "count": 1,
                "refusals": 0,
                "last_crash_ts": "2026-09-28 06:20:04"}},
                "lane_machine": "bm-c"}, fh)
        with open(POOL, "w", encoding="utf-8") as fh:
            json.dump(pool16, fh)
        rc = tick(dry=True)          # fix detected -> clear + tombstone
        fu16h = json.load(open(FUSE, encoding="utf-8"))
        lane_own = os.path.join(os.path.dirname(FUSE),
                                f"crash_fuse.{mid16h}.json")
        lane_own_16h = json.load(open(lane_own, encoding="utf-8"))
        ok("S16h clear records tombstone on shared + own lane",
           rc == 0 and sig16h not in fu16h["sigs"]
           and fu16h["cleared"][sig16h]["reason"] == "code_changed"
           and fu16h["cleared"][sig16h]["cleared_by"] == mid16h
           and sig16h not in lane_own_16h["sigs"]
           and lane_own_16h["cleared"][sig16h]["reason"] == "code_changed")
        rc = tick(dry=True)          # foreign lane resurrect -> suppressed
        st16h = _load_state()["last_tick"]
        fu16h2 = json.load(open(FUSE, encoding="utf-8"))
        gate16h = _load_fuse_gate()
        ok("S16h foreign-lane resurrect suppressed by tombstone "
           "(gate view sig-free, launch proceeds)",
           rc == 0 and st16h["verdict"] == "dry_launch"
           and sig16h not in gate16h.get("sigs", {})
           and sig16h not in fu16h2["sigs"])
        os.remove(lane_c)
        _clear_fuse_lanes()
        # S17 submit contract gate (r301+r305 family: hand-submit field
        # omissions starve _pick silently -- assert trio at entry point).
        # fixture runner lives in the tempdir: a repo-real path would
        # make _runner_alive match THIS selftest process and wedge _pick.
        runner17 = os.path.join(tmp, "fake_runner17.py")
        with open(runner17, "w", encoding="utf-8") as fh:
            fh.write("# hermetic fixture\n")
        with open(POOL, "w", encoding="utf-8") as fh:
            json.dump({"entries": []}, fh)

        def _sa(**kw):
            d = dict(id="E17", runner=runner17, shards="s0",
                     runner_args="run", priority=1, lane_owner=None,
                     workers=4, wp_priority="BelowNormal", wp_note=None,
                     ticket_ref=None, prereg_ref=None, data_gates=None,
                     shard_checkpoint=None, shard_note=None)
            d.update(kw)
            return argparse.Namespace(**d)

        rc = submit(_sa())
        p17 = json.load(open(POOL, encoding="utf-8"))["entries"]
        ok("S17a valid submit lands with contract trio",
           rc == 0 and len(p17) == 1 and p17[0]["id"] == "E17"
           and p17[0]["runner"] == runner17.replace("\\", "/")
           and p17[0]["shards"][0]["key"] == "s0"
           and p17[0]["shards"][0]["owner"] is None
           and p17[0]["workers_plan"]["workers"] == 4)
        rc = submit(_sa(id="E17b", workers=0))
        ok("S17b no workers_plan -> refuse (r305 law)",
           rc == 2 and len(json.load(open(POOL, encoding="utf-8"))
                           ["entries"]) == 1)
        rc = submit(_sa(id="E17c", shards=" , "))
        ok("S17c no shards -> refuse (r301 law)",
           rc == 2 and len(json.load(open(POOL, encoding="utf-8"))
                           ["entries"]) == 1)
        rc = submit(_sa(id="E17d", runner="scripts/nope.py"))
        ok("S17d runner not on disk -> refuse",
           rc == 2 and len(json.load(open(POOL, encoding="utf-8"))
                           ["entries"]) == 1)
        rc = submit(_sa(id="E17"))
        ok("S17e duplicate id -> refuse",
           rc == 2 and len(json.load(open(POOL, encoding="utf-8"))
                           ["entries"]) == 1)
        _py17 = _py_cpu_pct
        _py_cpu_pct = lambda w=SAMPLE_S: 5.0
        try:
            rc = tick(dry=True)
            st17 = _load_state()["last_tick"]
            ok("S17f submitted entry takeable by tick (end-to-end)",
               rc == 0 and st17["verdict"] == "dry_launch"
               and st17.get("entry") == "E17")
            lane17 = json.load(open(_lane_pl, encoding="utf-8"))
            ok("S17g submit lands in pool lane (id union face)",
               any(e.get("id") == "E17"
                   for e in lane17.get("entries", []))
               and lane17.get("lane_machine") == _machine_id())
        finally:
            _py_cpu_pct = _py17
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
                    choices=["tick", "status", "selftest", "submit"])
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--id")
    ap.add_argument("--runner")
    ap.add_argument("--shards",
                    help="comma-separated shard keys, e.g. s0,s1")
    ap.add_argument("--runner-args", default="run")
    ap.add_argument("--priority", type=int, default=1)
    ap.add_argument("--lane-owner", dest="lane_owner")
    ap.add_argument("--workers", type=int, default=0,
                    help="O-2130 multi-core plan size (required)")
    ap.add_argument("--wp-priority", dest="wp_priority",
                    default="BelowNormal")
    ap.add_argument("--wp-note", dest="wp_note")
    ap.add_argument("--ticket-ref", dest="ticket_ref")
    ap.add_argument("--prereg-ref", dest="prereg_ref")
    ap.add_argument("--data-gates", dest="data_gates")
    ap.add_argument("--shard-checkpoint", dest="shard_checkpoint")
    ap.add_argument("--shard-note", dest="shard_note")
    a = ap.parse_args()
    if a.cmd == "tick":
        sys.exit(tick(dry=a.dry))
    if a.cmd == "status":
        status()
        sys.exit(0)
    if a.cmd == "submit":
        sys.exit(submit(a))
    sys.exit(selftest())


if __name__ == "__main__":
    main()
