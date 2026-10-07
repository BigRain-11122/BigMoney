"""Per-machine lane-file io (D-20260928-03(1) writer dual-track).

Group decision D-20260928-03 lane migration: each machine additionally
writes its OWN lane file ``results/<face>.<machine>.json`` -- same
payload as the shared face plus a top-level ``lane_machine``
self-signature.  Shared files keep being written unchanged during the
compat dual-track window; the deterministic reader
(``scripts/merge_lane_views.py``) unions lane files with the legacy
blob using the conflict-resolver laws, so a swallowed shared write is
always recoverable from the owning machine's lane.

Batch-1 (A-family rolling ledgers) + batch-2 (B-family gate/meter
status snapshots; host-guarded writers for machine-local-derived faces
-- heat_update_status writes its lane on the R31 host only).

Laws carried:
  * r98 identity: machine id comes from ``fleet/machine.json`` ONLY --
    never guessed from file names or content.
  * fail-loud without breaking the writer's exit contract: a lane
    fault prints to stderr and returns False; the shared write already
    happened and stays authoritative during the window.
  * atomic os.replace; dict payloads only (fail-closed otherwise --
    all six A-faces are objects).
"""
import json
import os
import sys
import time
import datetime as _dt

from .settings import PATHS

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_KNOWN_FACES = ("compute_audit", "regime_state", "autofill_state",
                "runnable_pool", "gate_attrition", "post_review_criteria",
                # batch-2 B-family (D-20260928-03(1), LANE_MIGRATION_S1
                # census): per-machine gate/meter status snapshots.
                "update_status", "heat_update_status",
                "lhb_update_status", "futures_update_status",
                "fundamental_status", "token_usage", "crash_fuse",
                "market_clock/call_latest",
                # O-20261001-2103 R2 data face (bm-a lane, S5-01 GO)
                "zt_pool_update_status")
_MID_CACHE = {"v": None}


def machine_id():
    """This machine's fleet id (r98: fleet/machine.json is the only
    source of identity; unreadable -> empty string, never a guess)."""
    if _MID_CACHE["v"] is None:
        try:
            path = os.path.join(os.path.dirname(os.path.dirname(
                os.path.abspath(__file__))), "fleet", "machine.json")
            with open(path, encoding="utf-8") as fh:
                _MID_CACHE["v"] = str(json.load(fh).get("machine_id", ""))
        except Exception:
            _MID_CACHE["v"] = ""
    return _MID_CACHE["v"]


def lane_path(face, machine=None):
    """results/<face>.<machine>.json (D-03(1) structural end-state)."""
    mid = machine if machine is not None else machine_id()
    return os.path.join(PATHS.results_dir, f"{face}.{mid}.json")


def write_lane(face, data, indent=1, machine=None):
    """Write this machine's lane file for ``face`` (atomic, superset of
    the shared payload + lane_machine).  Returns True on success; on
    fault prints to stderr and returns False -- never raises into the
    calling S6/tick writer (exit contracts are frozen)."""
    if face not in _KNOWN_FACES:
        print(f"lane_io: unknown face {face!r} -- refuse (fail-closed)",
              file=sys.stderr)
        return False
    if not isinstance(data, dict):
        print(f"lane_io: face {face!r} payload is "
              f"{type(data).__name__}, dict required -- refuse",
              file=sys.stderr)
        return False
    mid = machine if machine is not None else machine_id()
    if not mid:
        print("lane_io: machine_id unreadable (fleet/machine.json) -- "
              "refuse write (r98 identity law)", file=sys.stderr)
        return False
    payload = dict(data)
    payload["lane_machine"] = mid
    path = lane_path(face, mid)
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            # default=str mirrors the regime face writer convention
            # (pandas/numpy scalars in probe payloads).
            json.dump(payload, fh, ensure_ascii=False, indent=indent,
                      default=str)
        os.replace(tmp, path)
        return True
    except Exception as ex:
        print(f"lane_io: lane write fault {path!r}: {ex} "
              f"(shared face stays authoritative)", file=sys.stderr)
        try:
            os.remove(tmp)
        except OSError:
            pass
        return False


def mirror_shared(face, indent=1, machine=None):
    """Seed/refresh a lane file from the current shared face (read ->
    write_lane).  Used to bootstrap faces whose writers are scattered
    one-off scripts; union semantics make the superset snapshot
    lossless for the reader."""
    shared = os.path.join(PATHS.results_dir, f"{face}.json")
    try:
        with open(shared, encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        print(f"lane_io: shared face {face!r} absent -- nothing to "
              "mirror", file=sys.stderr)
        return False
    except Exception as ex:
        print(f"lane_io: shared face {face!r} unreadable: {ex} "
              f"(never mirror from a corrupt source)", file=sys.stderr)
        return False
    return write_lane(face, data, indent=indent, machine=machine)


def _row_identity(r):
    """Stable per-row identity for keyed-array union: append-only
    ledger rows key on (batch, ts) (gate_attrition family); anything
    else unions by full JSON value."""
    if isinstance(r, dict) and ("batch" in r or "ts" in r):
        return ("k", r.get("batch"), r.get("ts"))
    return ("v", json.dumps(r, sort_keys=True, ensure_ascii=False))


def _union_face_payload(prev, data):
    """Lossless shared->lane union (r452 clobber #4 root fix):
    the mirror must never drop rows that exist ONLY in the lane file
    (T-101 line batches write the lane face only -- r240 lane-primary
    law).  Base = the lane's own append-only ordering; rows whose key
    also exists on the shared side take the shared (authoritative)
    content in place; shared rows the lane lacks append at the tail;
    scalar fields refresh from shared while lane-only fields survive.
    This honors the function's documented 'union semantics' contract
    that the former replace-with-shared implementation violated."""
    merged = dict(prev)
    for k, v in data.items():
        if isinstance(v, list):
            base = prev.get(k)
            if not isinstance(base, list):
                merged[k] = list(v)
                continue
            by_key = {_row_identity(r): r for r in v}
            out = []
            for r in base:
                ik = _row_identity(r)
                # same-key rows take the shared (authoritative) content
                out.append(by_key.pop(ik) if ik in by_key else r)
            out.extend(by_key.values())
            merged[k] = out
        else:
            merged[k] = v
    return merged


def mirror_shared_if_changed(face, machine=None):
    """Every-round maintenance mirror for scattered-writer faces
    (gate_attrition / post_review_criteria): refresh the own-machine
    lane from the shared face ONLY when the semantic payload actually
    changed -- parsed-payload compare is formatting-agnostic, so the
    mixed indent conventions across the many one-off runner writers
    never cause phantom churn.  The merge is a LOSSLESS union: rows
    that exist only in the lane (lane-primary writers, r240 law) are
    preserved in place, shared-known rows refresh to the shared
    content, and shared rows missing from the lane append at the tail
    -- a replace-with-shared rewrite is the r452 clobber #4 shape and
    must never happen.  Returns True when the lane is up-to-date after
    the call (an unchanged skip counts as up-to-date).  Fail-soft to
    stderr, never raises into the calling S6 leg; a missing shared
    face is a quiet no-op, not a fault."""
    if face not in _KNOWN_FACES:
        print(f"lane_io: unknown face {face!r} -- refuse (fail-closed)",
              file=sys.stderr)
        return False
    shared = os.path.join(PATHS.results_dir, f"{face}.json")
    try:
        with open(shared, encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        return False
    except Exception as ex:
        print(f"lane_io: shared face {face!r} unreadable: {ex} "
              "(mirror skipped, shared stays authoritative)",
              file=sys.stderr)
        return False
    if not isinstance(data, dict):
        print(f"lane_io: shared face {face!r} is "
              f"{type(data).__name__}, dict required -- skip",
              file=sys.stderr)
        return False
    mid = machine if machine is not None else machine_id()
    lane = lane_path(face, mid) if mid else None
    if lane and os.path.exists(lane):
        try:
            with open(lane, encoding="utf-8") as fh:
                prev = json.load(fh)
            if isinstance(prev, dict):
                prev.pop("lane_machine", None)
                if prev == data:
                    return True  # unchanged -- churn-free skip
                merged = _union_face_payload(prev, data)
                if merged == prev:
                    return True  # union result identical -- churn-free skip
                return write_lane(face, merged, machine=machine)
        except Exception:
            pass  # corrupt lane -> rewrite from shared below
    return write_lane(face, data, machine=machine)


# --- D-20260928-03(1) batch-3 C-family: single-writer host guard -----
#
# Census (r370, results/_r370bma_lane_census.py): C-family faces are
# deterministic idempotent re-derives -- byte-identical across machines
# modulo wall-clock envelope fields (generated_at/age_min), so per-
# machine lane files for them are pure churn and the census-sanctioned
# C treatment is 单机执笔 single-writer ("消费面合并读 or 单机执笔",
# LANE_MIGRATION_S1 §二).  Static-HTML consumers (dashboard_status.js
# <- bigmoney/dashboard/town.html file:// loads) cannot merge-read,
# which rules the lane pattern out for the top-treadmill faces anyway.
# Non-host machines skip the shared derive entirely (honest stdout
# no-op, R31 lane-guard precedent); a health-machine stale-takeover
# keeps the CEO face fresh when the host is down (O-2100 s2.4
# STALE_MIN law -- the derive is idempotent, so a rare takeover race
# is a trivial near-identical add/add, never a swallow risk).

C_SINGLE_WRITER_HOSTS = {
    "results/dashboard_status.json": "bm-a",
    "results/dashboard_status.js": "bm-a",
    "results/daily_scorecard.json": "bm-a",
    "results/daily_scorecard.html": "bm-a",
    "results/strategy_scorecard.json": "bm-a",
    "results/scorecard_v1.json": "bm-a",
    # --- D-20260928-03(1) batch-3 slice-2: paper family (LANE_MIGRATION_S1
    # sec.7 census C-family -- deterministic idempotent re-derives, byte-
    # identical add/add, bar-gated low-frequency writers). Family tokens
    # (trailing /*) gate the whole writer run (multi-file faces: PROS-*,
    # export-<D>.json, marks jsonl); exact paths gate single files. Host
    # =bm-a: IntradayMarks schtask armed on bm-a (T-91 s3), t35_paper_export
    # R94 bm-a wiring, slice-1 precedent. t24_prospect_paper cells jsonl
    # (results/t24_prospect_paper_cells.jsonl) rides the same writer-run
    # gate. market_clock_call l3_activation_table only -- call_latest/
    # CALL-*.md stay B-family per-machine lanes (r375 batch-2).
    "results/paper/*": "bm-a",
    "results/prospect_paper/*": "bm-a",
    "results/prospect_promotion/*": "bm-a",
    "results/paper_export/*": "bm-a",
    "results/t35_open_fill_verify.json": "bm-a",
    "results/market_clock/l3_activation_table.json": "bm-a",
}
C_HOST_STALE_MIN = 20.0   # O-2100 s2.4 / autofill STALE_MIN precedent


def _hb_age_min(hb):
    """Heartbeat age in minutes from a parsed heartbeat dict
    (heartbeat_epoch_utc int preferred per smoke-F7, else last_seen
    ISO). None when no parseable signal (dead-host face)."""
    epoch = hb.get("heartbeat_epoch_utc")
    if isinstance(epoch, int) and not isinstance(epoch, bool):
        return max(0.0, (time.time() - epoch) / 60.0)
    last_seen = hb.get("last_seen")
    if isinstance(last_seen, str):
        try:
            ts = _dt.datetime.fromisoformat(last_seen)
            # naive timestamps read as local (fleet clocks share +08:00);
            # .timestamp() handles both naive-local and aware forms
            return max(0.0, (time.time() - ts.timestamp()) / 60.0)
        except ValueError:
            return None
    return None


def _host_heartbeat_age_min(host):
    """Age in minutes of the host's latest heartbeat signal as read from
    the LOCAL work tree.  Returns None when the heartbeat file is
    missing/unreadable or carries no parseable signal -- callers treat
    None as dead-host (takeover face)."""
    path = os.path.join(_REPO_ROOT, "fleet", "machines", f"{host}.json")
    try:
        with open(path, encoding="utf-8") as fh:
            hb = json.load(fh)
    except Exception:
        return None
    return _hb_age_min(hb)


def _host_heartbeat_age_min_origin(host):
    """Origin-ref heartbeat age (r366 fix candidate, landed r371): the
    non-host machine's WORK-TREE copy of the host's heartbeat is only as
    fresh as its last pull/rebase -- a behind-origin tree or a surgical
    reset window can present a stale heartbeat while the host is actively
    pushing (live-fire 2026-10-02 12:5x: local read 34min-stale vs origin
    fresh -> guard released a stale-takeover derive over a live host).
    Reads the host heartbeat straight from the origin/main raw blob;
    any failure (no git, detached, timeout, bad json) -> None and callers
    fall back to local-tree judgment."""
    import subprocess
    try:
        r = subprocess.run(
            ["git", "show", f"origin/main:fleet/machines/{host}.json"],
            capture_output=True, cwd=_REPO_ROOT, timeout=10,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if r.returncode != 0:
            return None
        return _hb_age_min(json.loads(r.stdout.decode("utf-8", "replace")))
    except Exception:
        return None


def _origin_commit_age_min(host, ref="origin/main", scan=40):
    """r701 third liveness signal (r700 pool_worker law face extended to
    the lane_io guard): a host mid-long-round heartbeats only at round
    end while its session/daemon keeps committing and pushing -- a recent
    origin commit naming the host = the host is alive even with BOTH the
    local and origin heartbeats stale (r700 live-fire: four C-faces
    stale-takeover-derived on a live-but-heartbeat-stale bm-a).  Returns
    the freshest such commit age in minutes, or None (no sighting / git
    fault).  Attribution needle = machine-id substring in the subject
    (fleet convention tags: 'via bm-a', 'lane: bm-c', 'bm-a r834 ...').
    Conservative-by-design: a false 'alive' merely defers takeover a few
    minutes; the double-write hazard only runs in the false-'dead'
    direction.  Note the r371 caveat applies verbatim: the local
    origin/main ref is only as fresh as the last fetch, so a stale fetch
    reads the host older than it is = takeover proceeds = pre-r701
    behavior at worst."""
    import subprocess
    if not host:
        return None
    try:
        r = subprocess.run(
            ["git", "log", ref, f"-{scan}", "--format=%ct%x00%s"],
            capture_output=True, cwd=_REPO_ROOT, timeout=10,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if r.returncode != 0:
            return None
        now = time.time()
        best = None
        needle = str(host).lower()
        for line in r.stdout.decode(errors="replace").splitlines():
            if "\x00" not in line:
                continue
            ts_s, subj = line.split("\x00", 1)
            try:
                age = (now - int(ts_s)) / 60.0
            except ValueError:
                continue
            if age < 0:
                age = 0.0
            if needle in subj.lower() and (best is None or age < best):
                best = age
        return best
    except Exception:
        return None


def shared_derive_write_allowed(face_rel, verbose=True):
    """Single-writer admission for a deterministic idempotent re-derive
    shared face (D-03(1) batch-3 C-family).  True = this machine should
    derive+write this cycle: the designated host always; a non-host
    only as stale-takeover (host heartbeat older than C_HOST_STALE_MIN,
    or host heartbeat unreadable = dead-host).  Fail-open legs: a face
    absent from the map keeps legacy write behavior (explicit opt-in
    per face), and an unreadable machine id cannot prove non-host so
    it writes as before (r98: never guess identity)."""
    host = C_SINGLE_WRITER_HOSTS.get(face_rel)
    if host is None:
        return True
    mid = machine_id()
    if not mid or mid == host:
        return True
    age = _host_heartbeat_age_min(host)
    if age is not None and age < C_HOST_STALE_MIN:
        if verbose:
            print(f"lane_io single-writer guard: {face_rel} host={host} "
                  f"heartbeat fresh ({age:.0f}min) -> skip derive this "
                  f"cycle (D-20260928-03 batch-3 C-family)")
        return False
    # local view says stale/unreadable -> cross-check origin before any
    # takeover (r366/r371): a behind-origin or reset-window local tree can
    # present a stale host heartbeat while the host is actively pushing.
    age_o = _host_heartbeat_age_min_origin(host)
    if age_o is not None and age_o < C_HOST_STALE_MIN:
        if verbose:
            local_face = f"{age:.0f}min stale view" if age is not None \
                else "unreadable view"
            print(f"lane_io single-writer guard: {face_rel} host={host} "
                  f"origin heartbeat fresh ({age_o:.0f}min, local "
                  f"{local_face}) -> skip derive this cycle "
                  f"(r366 stale-view veto)")
        return False
    # origin heartbeat also stale/unreadable -> third liveness signal
    # (r701, r700 pool_worker law): a host mid-long-round pushes
    # products/ledger commits between heartbeat writes -- a fresh origin
    # commit naming the host = alive, veto the takeover (conservative
    # direction only; commit unreadable -> takeover stands as before).
    age_c = _origin_commit_age_min(host)
    if age_c is not None and age_c < C_HOST_STALE_MIN:
        if verbose:
            print(f"lane_io single-writer guard: {face_rel} host={host} "
                  f"origin commit fresh ({age_c:.0f}min, heartbeats "
                  f"stale) -> skip derive this cycle "
                  f"(r701 third-signal veto)")
        return False
    if verbose:
        basis = (f"heartbeat stale {age:.0f}min" if age is not None
                 else "heartbeat unreadable")
        print(f"lane_io single-writer guard: {face_rel} host={host} "
              f"{basis} -> stale-takeover derive by {mid} "
              f"(O-2100 s2.4 STALE_MIN law)")
    return True


def _selftest():
    """Offline hermetic legs for the batch-3 single-writer guard
    (zero fleet reads via monkeypatch, zero disk writes)."""
    import config.lane_io as li
    saved_mid = li.machine_id
    saved_age = li._host_heartbeat_age_min
    saved_age_o = li._host_heartbeat_age_min_origin
    saved_age_c = li._origin_commit_age_min
    faces = dict(li.C_SINGLE_WRITER_HOSTS)
    face = "results/__selftest_face.json"
    try:
        li.C_SINGLE_WRITER_HOSTS = {face: "bm-z"}
        state = {"age": None}
        state_o = {"age": None, "calls": 0}
        state_c = {"age": None, "calls": 0}

        def age(host):
            return state["age"]

        def age_o(host):
            state_o["calls"] += 1
            return state_o["age"]

        def age_c(host, ref="origin/main", scan=40):
            state_c["calls"] += 1
            return state_c["age"]

        li._host_heartbeat_age_min = age
        li._host_heartbeat_age_min_origin = age_o
        li._origin_commit_age_min = age_c
        legs = []

        # L1 host machine -> always allowed (even with stale heartbeat)
        li.machine_id = lambda: "bm-z"
        state["age"] = 99.0
        legs.append(("host-always", li.shared_derive_write_allowed(face)
                     is True and li.shared_derive_write_allowed(face,
                                                                verbose=False)
                     is True))
        # L2 non-host + host fresh -> skip
        li.machine_id = lambda: "bm-x"
        state["age"] = 3.0
        legs.append(("nonhost-fresh-skip",
                     li.shared_derive_write_allowed(face) is False))
        # L3 non-host + host stale -> takeover
        state["age"] = 25.0
        legs.append(("nonhost-stale-takeover",
                     li.shared_derive_write_allowed(face) is True))
        # L4 non-host + heartbeat unreadable -> takeover
        state["age"] = None
        legs.append(("nonhost-deadhost-takeover",
                     li.shared_derive_write_allowed(face) is True))
        # L5 face absent from map -> legacy write (fail-open)
        legs.append(("unknown-face-fail-open",
                     li.shared_derive_write_allowed(
                         "results/__unmapped.json") is True))
        # L6 machine id unreadable -> legacy write (r98 no-guess)
        li.machine_id = lambda: ""
        state["age"] = 3.0
        legs.append(("unknown-mid-fail-open",
                     li.shared_derive_write_allowed(face) is True))
        # L7 boundary: age == C_HOST_STALE_MIN is NOT < STALE_MIN -> takeover
        li.machine_id = lambda: "bm-x"
        state["age"] = li.C_HOST_STALE_MIN
        legs.append(("boundary-equal-takeover",
                     li.shared_derive_write_allowed(face,
                                                    verbose=False) is True))
        # L8 slice-2 structure: paper-family faces registered host=bm-a
        # (family tokens + exact paths; guards against accidental map
        # regression -- D-20260928-03(1) batch-3 slice-2)
        slice2 = ("results/paper/*", "results/prospect_paper/*",
                  "results/prospect_promotion/*", "results/paper_export/*",
                  "results/t35_open_fill_verify.json",
                  "results/market_clock/l3_activation_table.json")
        legs.append(("slice2-map-registered",
                     all(faces.get(f) == "bm-a" for f in slice2)))
        # L9 family token behavior: trailing-/* key gates identically
        li.C_SINGLE_WRITER_HOSTS = {"results/__fam/*": "bm-z"}
        state["age"] = 3.0
        legs.append(("family-token-nonhost-skip",
                     li.shared_derive_write_allowed(
                         "results/__fam/*", verbose=False) is False))
        li.C_SINGLE_WRITER_HOSTS = {face: "bm-z"}

        # --- r366/r371 origin-ref veto legs (stale-view false-takeover)
        li.machine_id = lambda: "bm-x"
        # L10 local stale + origin fresh -> veto (host alive per origin)
        state["age"] = 25.0
        state_o["age"] = 3.0
        legs.append(("origin-fresh-veto",
                     li.shared_derive_write_allowed(face,
                                                    verbose=False) is False))
        # L11 local stale + origin also stale -> takeover stands
        state_o["age"] = 30.0
        legs.append(("origin-also-stale-takeover",
                     li.shared_derive_write_allowed(face,
                                                    verbose=False) is True))
        # L12 local unreadable + origin fresh -> veto (dead local view)
        state["age"] = None
        state_o["age"] = 3.0
        legs.append(("origin-fresh-veto-dead-local",
                     li.shared_derive_write_allowed(face,
                                                    verbose=False) is False))
        # L13 local fresh -> skip WITHOUT consulting origin (fast path)
        state["age"] = 3.0
        calls0 = state_o["calls"]
        legs.append(("local-fresh-fastpath-no-origin-read",
                     li.shared_derive_write_allowed(face,
                                                    verbose=False) is False
                     and state_o["calls"] == calls0))
        # L14 origin unreadable -> fall back to local judgment (takeover)
        state["age"] = 25.0
        state_o["age"] = None
        legs.append(("origin-unreadable-fallback-takeover",
                     li.shared_derive_write_allowed(face,
                                                    verbose=False) is True))
        state_o["age"] = None

        # --- r701 third-signal legs (origin-commit liveness veto;
        # r700 pool_worker S23 law face, hermetic via monkeypatch)
        # reset: local stale + origin-hb stale for every leg below
        state["age"] = 25.0
        state_o["age"] = 25.0
        # L15 the r700 live-fire shape: both heartbeats stale but the
        # host keeps committing -> veto (live-but-heartbeat-stale host)
        state_c["age"] = 3.0
        legs.append(("origin-commit-fresh-veto",
                     li.shared_derive_write_allowed(face,
                                                    verbose=False) is False))
        # L16 all three signals stale -> takeover stands
        state_c["age"] = 25.0
        legs.append(("all-signals-stale-takeover",
                     li.shared_derive_write_allowed(face,
                                                    verbose=False) is True))
        # L17 commit signal unreadable -> takeover stands (pre-r701
        # behavior preserved, conservative fallback)
        state_c["age"] = None
        legs.append(("commit-unreadable-takeover",
                     li.shared_derive_write_allowed(face,
                                                    verbose=False) is True))
        # L18 boundary: commit age == C_HOST_STALE_MIN is NOT < -> takeover
        state_c["age"] = li.C_HOST_STALE_MIN
        legs.append(("commit-boundary-equal-takeover",
                     li.shared_derive_write_allowed(face,
                                                    verbose=False) is True))
        # L19 host machine -> always allowed WITHOUT consulting the
        # commit signal (host fast path mirrors L1)
        li.machine_id = lambda: "bm-z"
        c_calls0 = state_c["calls"]
        legs.append(("host-always-no-commit-read",
                     li.shared_derive_write_allowed(face,
                                                    verbose=False) is True
                     and state_c["calls"] == c_calls0))
        li.machine_id = lambda: "bm-x"
        # L20 local-fresh fast path never consults the commit signal
        state["age"] = 3.0
        c_calls0 = state_c["calls"]
        legs.append(("local-fresh-fastpath-no-commit-read",
                     li.shared_derive_write_allowed(face,
                                                    verbose=False) is False
                     and state_c["calls"] == c_calls0))
        # L21 origin-hb fresh veto path consults neither the commit
        # signal (short-circuit order: hb before commit)
        state["age"] = 25.0
        state_o["age"] = 3.0
        c_calls0 = state_c["calls"]
        legs.append(("origin-hb-veto-no-commit-read",
                     li.shared_derive_write_allowed(face,
                                                    verbose=False) is False
                     and state_c["calls"] == c_calls0))
        state_o["age"] = None
        state_c["age"] = None

        # --- r452 union-mirror legs (clobber #4 root fix, hermetic tmp disk)
        import shutil
        import tempfile
        import types
        li.machine_id = lambda: "bm-z"
        saved_paths, saved_lane = li.PATHS, li.lane_path
        tmpd = tempfile.mkdtemp(prefix="laneio_r452_")
        li.PATHS = types.SimpleNamespace(results_dir=tmpd)
        li.lane_path = (lambda f, machine=None:
                        os.path.join(tmpd, f"{f}.lane-{machine or 'bm-z'}.json"))
        uface = "gate_attrition"  # known-face gate must pass
        r1 = {"batch": "B1", "ts": "t1", "v": 1}
        r2 = {"batch": "B2", "ts": "t2", "v": 2}
        r3u = {"batch": "T-101-V4-A14-UNION", "ts": "t3u", "v": 3}
        r4 = {"batch": "B4", "ts": "t4", "v": 4}
        shared = {"schema": "s", "entries": [r1, r2], "history": [r1]}
        lane0 = {"schema": "s", "entries": [r1, r2, r3u],
                 "history": [r1], "lane_machine": "bm-z"}
        with open(os.path.join(tmpd, uface + ".json"), "w",
                  encoding="utf-8") as fh:
            json.dump(shared, fh)
        with open(li.lane_path(uface), "w", encoding="utf-8") as fh:
            json.dump(lane0, fh)
        writes = {"n": 0}
        _real_write = li.write_lane

        def _count_write(f, data, indent=1, machine=None):
            writes["n"] += 1
            return _real_write(f, data, indent=indent, machine=machine)

        li.write_lane = _count_write
        # LU1 lane-unique row survives the mirror (old code clobbered to 2)
        ok1 = li.mirror_shared_if_changed(uface)
        lu1 = json.load(open(li.lane_path(uface), encoding="utf-8"))
        legs.append(("union-lane-unique-preserved",
                     ok1 is True and len(lu1["entries"]) == 3
                     and any(r["batch"] == "T-101-V4-A14-UNION"
                             for r in lu1["entries"])))
        # LU2 churn-free: converged union == lane -> no write
        n0 = writes["n"]
        legs.append(("union-churn-free-skip",
                     li.mirror_shared_if_changed(uface) is True
                     and writes["n"] == n0))
        # LU3 shared-new row appends at the tail
        shared["entries"] = [r1, r2, r4]
        with open(os.path.join(tmpd, uface + ".json"), "w",
                  encoding="utf-8") as fh:
            json.dump(shared, fh)
        li.mirror_shared_if_changed(uface)
        lu3 = json.load(open(li.lane_path(uface), encoding="utf-8"))
        legs.append(("union-shared-new-appended",
                     len(lu3["entries"]) == 4
                     and lu3["entries"][-1]["batch"] == "B4"))
        # LU4 same-key row refreshes to the shared (authoritative) content
        shared["entries"] = [{"batch": "B1", "ts": "t1", "v": 99}, r2, r4]
        with open(os.path.join(tmpd, uface + ".json"), "w",
                  encoding="utf-8") as fh:
            json.dump(shared, fh)
        li.mirror_shared_if_changed(uface)
        lu4 = json.load(open(li.lane_path(uface), encoding="utf-8"))
        legs.append(("union-same-key-shared-authoritative",
                     next(r for r in lu4["entries"]
                          if r["batch"] == "B1")["v"] == 99
                     and len(lu4["entries"]) == 4))
        li.write_lane = _real_write
        shutil.rmtree(tmpd, ignore_errors=True)
        li.PATHS, li.lane_path = saved_paths, saved_lane

        ok = sum(1 for _, r in legs if r)
        for name, r in legs:
            print(f"  [{'PASS' if r else 'FAIL'}] {name}")
        print(f"lane_io batch-3 guard selftest: {ok}/{len(legs)} PASS")
        return 0 if ok == len(legs) else 1
    finally:
        li.machine_id = saved_mid
        li._host_heartbeat_age_min = saved_age
        li._host_heartbeat_age_min_origin = saved_age_o
        li._origin_commit_age_min = saved_age_c
        li.C_SINGLE_WRITER_HOSTS = faces


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(_selftest())
    print("usage: python -m config.lane_io selftest")
    sys.exit(0)
