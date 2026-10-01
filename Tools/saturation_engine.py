"""Tools/saturation_engine.py -- T-141 s1 resident saturation engine (O-20261001-1410).

LAW: firm/SATURATION_ENGINE_LAW.md v1.0 (frozen spec, CEO direct order
"从底层梳理为什么这样？然后彻底解决"). 满载从「轮间指标」升格为「常驻执行体」.

Architecture (law sec.1-sec.5, per-machine instance; this file = bm-c's):
  * RESIDENT supervisor loop, 15s cadence, hosted by schtasks 1-min
    repetition + IgnoreNew via the InvisibleRunner.vbs pattern (task
    instance = wscript waits on python -> engine death = next 1-min
    trigger restarts it; inner watchdog thread force-exits on stall).
  * LOCAL PERPETUAL QUEUE (law sec.1): work items derive LOCALLY from
    frozen authorizations -- per-wave prereg file + law band ledger row
    (scripts/perpetual_faces.py N1_BANDS single source, R250). Hot path
    has ZERO git round-trips; the only git is the 20-min SYNC WINDOW
    (fetch + ls-tree origin product truth, r488/r500 two-layer truth).
    Face scope v0.1 = N1 (nulls deepening) whose runner+prereg chain is
    fully landed (W2..W8 burned, W9 authorized by frozen prereg + ADMIT
    receipt); N2/N3 queue faces and the not-yet-landed N4 are later
    expansions (fake-supply ban: never queue a face without its runner).
  * BAND PARTITION (law sec.1): deterministic machine slots over the
    sorted fleet [bm-a,bm-b,bm-c] -> primary shards s%3==slot; secondary
    (takeover) only after primaries are exhausted. Product presence is
    the done-truth (W9 prereg: checkpoint=分片件本体 presence=done), so
    cross-machine races can only ever re-burn byte-identical shards
    (determinism law, W2..W8 proven) -- union-safe, honest in state.
  * CORE CAP (law sec.5 + CEO foreground-reserve law): bm-c burns at
    most 26/32 cores -> max concurrent shards = 26//8 = 3 (workers=8
    per shard = W9 prereg frozen workers_plan, O-2355). Ignition also
    holds above the 70% py fill line (O-1614): the engine adds work only
    when the machine is NOT already saturated (pool-lane burns included).
  * PRE-IGNITION CHECKS (law sec.3, r316): runner file + prereg file +
    law band row + core48 in-repo data + product-absent + crash fuse
    (3 strikes -> shard quarantined, honest). Missing = skip + report,
    zombie ignition forbidden.
  * DETACHED BURNS (r317 law): Popen close_fds=True with std explicitly
    redirected to log files, CREATE_NO_WINDOW (zero desktop flash,
    U060), BelowNormal priority (CEO 前台余量律). Burns survive engine
    death; restart re-derives state and ADOPTS in-flight n1 runner
    processes regardless of lane (psutil cmdline scan, engine's own pid
    excluded -- no self-match, r318 pit family).
  * STATE SELF-DERIVED (law sec.1, r488 family): done-truth re-derived
    from product presence every cycle; state file
    results/saturation_engine_state.<mid>.json is an event-written lane
    face (D-03 naming) + <=60s heartbeat for the round-zero liveness
    check (T-141 s3 wiring).
  * LEDGER (law sec.2, s2 conversion v0.2): products land in the tracked
    conventional results/p2cal_ext tree and are delivered to git by the
    engine's OWN async batched appender -- targeted pathspec commit of
    NEW product files only (never add -A, r109 law), best-effort push,
    NO engine-side rebase ever (a rejected push = local commit rides the
    next round session's rebase; byte-identical twins already on origin
    drop as empty picks, proven 10-01 CAS precedent). Batching window =
    15min oldest-pending or >=4 shards (law 10-20min / N-shard band).
    Guards before commit: rebase/merge surgery markers + index.lock
    (r312/r314 family) -- any hit = honest defer to the next window.
    Pre-claim exemption: engine-lane burns pass --lane engine to the
    runner (no pool-claim handshake files -- engine waves have no pool
    entry to flip; claim files would be orphan git traffic). Grammar
    (seed-band) consumption is logged per wave in the state face with
    the fetch-synced dedup counts (生成窗 fetch 对账, 防重烧).
    finalize() stays a wave-owner action (prereg sec.4) -- the engine
    only surfaces wave-complete flags.
  * OLD-LANE CO-EXISTENCE: perpetual_faces supply() materializer trigger
    requires py<70; while the engine burns, py>=70 keeps the materialize
    leg off (natural mutual exclusion). The adoption scan makes any
    pool-lane n1 burn visible as in-flight. T-141 note supersedes the
    materializer for perpetual faces once engines are fleet-wide.

Exit codes (house contract): 0 = normal (incl. honest idle no-op),
2 = mechanism fault -- report honestly, never mask.
Subcommands: run (default) | status (read-only face) | selftest (r117
hermetic: no network, no real burns, no real git ops).
"""
import argparse
import json
import os
import re
import subprocess
import sys
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)                      # config / science_gates
sys.path.insert(0, os.path.join(ROOT, "scripts"))  # perpetual_faces, compute_audit

try:
    import psutil
except ImportError:                            # pragma: no cover
    psutil = None

MACHINE_FILE = os.path.join(ROOT, "fleet", "machine.json")
FLEET_ORDER = ["bm-a", "bm-b", "bm-c"]   # sorted fleet = partition slots (law sec.1)
N1_SHARDS = 12                           # frozen per-wave shard count (law sec.4 W2..W9)
WORKERS_PER_SHARD = 8                    # W9 prereg frozen workers_plan (O-2355)
CORE_CAP = {"bm-c": 26}                  # CEO foreground-reserve law; others = full cores
PY_FILL_LINE = 70.0                      # O-1614 fill line: above = machine saturated
MACHINE_IGNITE_HOLD = 88.0               # CEO 10%-reserve law: no new burn above this
CYCLE_S = 15                             # supervision cadence (秒级起烧, law sec.1)
HEARTBEAT_S = 60                         # state-face heartbeat bound
SYNC_EVERY_S = 20 * 60                    # sync window cadence (law sec.1/sec.2)
SYNC_TIMEOUT_S = 90
APPEND_EVERY_S = 15 * 60                  # law sec.2 batch window (10-20min band)
APPEND_MIN_SHARDS = 4                     # N-shard batch trigger (law sec.2)
APPEND_TIMEOUT_S = 120
GIT_BUSY_MARKERS = ("rebase-merge", "rebase-apply", "MERGE_HEAD",
                    "CHERRY_PICK_HEAD", "REVERT_HEAD", "index.lock")
FUSE_MAX = 3                             # crash fuse per (face, wave, shard)
STALL_EXIT_S = 300                       # inner watchdog: stall -> hard exit, task restarts
LOG_DIR = os.path.join(ROOT, "logs", "saturation_engine")
TASK_NAME = "Bigmoney-SaturationEngine"

STATE_VERSION = "v0.3-s3a"
LAW_REF = ("firm/SATURATION_ENGINE_LAW.md v1.0 (T-2026-10-01-141 s1+s3, "
           "O-20261001-1410 CEO direct order)")
FACE_DIR = os.path.join(ROOT, "results", "saturation_engine")


# ----------------------------------------------------------------- helpers
def read_machine_id():
    try:
        with open(MACHINE_FILE, encoding="utf-8") as fh:
            return json.load(fh)["machine_id"]
    except Exception:
        return "unknown"


def core_cap(mid):
    return CORE_CAP.get(mid) or (psutil.cpu_count() if psutil else os.cpu_count())


def max_concurrent(mid):
    return max(1, core_cap(mid) // WORKERS_PER_SHARD)   # bm-c: 26//8 = 3


def state_path(mid):
    return os.path.join(ROOT, "results", "saturation_engine_state.%s.json" % mid)


def face_path(mid):
    """Law sec.5 CEO-face lane file (s3; reader: build_status
    _engine_face_state aggregates every face_*.json present)."""
    return os.path.join(FACE_DIR, "face_%s.json" % mid)


def product_path(wave, shard, nshards=N1_SHARDS):
    return os.path.join(ROOT, "results", "p2cal_ext", "n1_w%d" % wave,
                        "shard-%d-of-%d.json" % (shard, nshards))


def prereg_path(wave):
    return os.path.join(ROOT, "research", "PERPETUAL_N1_W%d_PREREG.md" % wave)


RUNNER = os.path.join(ROOT, "scripts", "perpetual_faces_n1.py")
DAILY_DIR = os.path.join(ROOT, "data", "daily")
CORE48_MIN_FILES = 48                        # in-repo core48 gate (W9 prereg 宿主门)


def n1_bands():
    """Law sec.4 band ledger single source (import, never re-implement)."""
    import perpetual_faces as pf
    return dict(pf.N1_BANDS)


def partition_slot(mid):
    return FLEET_ORDER.index(mid) if mid in FLEET_ORDER else 0


def _py_cpu_pct():
    """python-family CPU as % of machine capacity (psutil; audit parity face)."""
    if not psutil:
        return None
    cores = psutil.cpu_count() or 1
    total = 0.0
    for p in psutil.process_iter(["name", "cpu_percent"]):
        try:
            info = p.info
            if (info.get("name") or "").lower().startswith(("python", "pythonw")):
                total += info.get("cpu_percent") or 0.0
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return round(total / cores, 2)


def _machine_cpu_pct():
    if not psutil:
        return None
    return psutil.cpu_percent(interval=0.4)


# ------------------------------------------------------------ queue derive
def derive_n1_queue(bands, preregs, done, quarantined, slot,
                    nshards=N1_SHARDS, max_items=64, owner_mid=None):
    """Ordered eligible work items, primary partition first (law sec.1).

    Pure function (selftest-legible): bands = {wave: row}, preregs = {wave:
    path-or-None}, done/quarantined = sets of (wave, shard). Waves ascend
    (complete earlier waves first); within a wave primary slots first, then
    secondary takeover order. Authorization = band row + prereg presence.
    engine_owner gate (r508 convention parity, sec.1 zero-cross-machine-
    duplication): a band row carrying engine_owner != owner_mid is a
    FOREIGN engine wave -- invisible here; rows without the field are
    pool-era legacy waves and stay eligible as before.
    """
    items = []
    for wave in sorted(bands):
        if not preregs.get(wave):
            continue                             # never fake-supply (law sec.1)
        row = bands[wave]
        if owner_mid is not None:
            owner = row.get("engine_owner") if isinstance(row, dict) else None
            if owner and owner != owner_mid:
                continue
        primary = [s for s in range(nshards) if s % len(FLEET_ORDER) == slot]
        secondary = [s for s in range(nshards) if s % len(FLEET_ORDER) != slot]
        for shard in primary + secondary:
            key = (wave, shard)
            if key in done or key in quarantined:
                continue
            items.append({"face": "N1", "wave": wave, "shard": shard,
                          "nshards": nshards, "primary": shard in primary,
                          "authorization": "pre-claim-exempt (law sec.2)"})
            if len(items) >= max_items:
                return items
    return items


def pre_ignition_checks(item, runner=RUNNER, daily_dir=DAILY_DIR,
                         min_daily_files=CORE48_MIN_FILES):
    """Law sec.3 (r316): local re-verification BEFORE ignition. [] = pass."""
    fails = []
    wave = item["wave"]
    if not (os.path.isfile(runner) and os.access(runner, os.X_OK | os.R_OK)):
        fails.append("runner missing: %s" % runner)
    if not os.path.isfile(prereg_path(wave)):
        fails.append("prereg missing: %s" % prereg_path(wave))
    try:
        if wave not in n1_bands():
            fails.append("law band row missing for wave %d" % wave)
    except Exception as exc:                     # import face = mechanism fault
        fails.append("band ledger unreadable: %r" % (exc,))
    try:
        n_daily = len([f for f in os.listdir(daily_dir) if f.endswith(".csv")])
    except OSError:
        n_daily = 0
    if n_daily < min_daily_files:
        fails.append("core48 data gate: %d csv < %d in %s"
                     % (n_daily, min_daily_files, daily_dir))
    if os.path.exists(product_path(wave, item["shard"], item["nshards"])):
        fails.append("product already present (done-truth)")
    return fails


def build_burn_cmd(item, workers=WORKERS_PER_SHARD):
    return [sys.executable, RUNNER, "run",
            "--shard", str(item["shard"]), "--of", str(item["nshards"]),
            "--wave", str(item["wave"]), "--workers", str(workers),
            "--lane", "engine"]          # law sec.2: pre-claim-exempt lane


def ignite(item, log_dir=LOG_DIR):
    """Detached burn (r317: close_fds=True + explicit std redirection)."""
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "n1_w%d_shard%d.log"
                            % (item["wave"], item["shard"]))
    cmd = build_burn_cmd(item)
    with open(log_file, "ab") as lh:
        proc = subprocess.Popen(
            cmd, cwd=ROOT, stdout=lh, stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL, close_fds=True,
            creationflags=subprocess.CREATE_NO_WINDOW
            | subprocess.BELOW_NORMAL_PRIORITY_CLASS)
    return proc.pid, log_file


def adopt_inflight():
    """Re-derive in-flight n1 burns from the process table (any lane)."""
    adopted = []
    if not psutil:
        return adopted
    me = os.getpid()
    for p in psutil.process_iter(["pid", "cmdline"]):
        try:
            if p.info["pid"] == me:
                continue                          # no self-match (r318 family)
            cl = p.info.get("cmdline") or []
            joined = " ".join(cl)
            if "perpetual_faces_n1.py" not in joined or " run" not in " " + joined:
                continue
            def arg(name, default=None):
                return cl[cl.index(name) + 1] if name in cl else default
            adopted.append({
                "pid": p.info["pid"],
                "wave": int(arg("--wave", 2)),
                "shard": int(arg("--shard", -1)),
                "nshards": int(arg("--of", N1_SHARDS)),
                "adopted": True,
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, ValueError, IndexError):
            continue
    return adopted


def _git(args, cwd=None, timeout=SYNC_TIMEOUT_S):
    """Zero-window git (CREATE_NO_WINDOW, U060/r317 discipline)."""
    return subprocess.run(
        ["git", "-C", cwd or ROOT] + args, capture_output=True, text=True,
        timeout=timeout, creationflags=subprocess.CREATE_NO_WINDOW)


def parse_remote_shards(stdout_text):
    """ls-tree --name-only emits FULL paths (results/p2cal_ext/n1_w9/
    shard-0-of-12.json); collect the shard indices from the basename.
    (s2 fix: the s1 parse matched bare names only -> remote_done was
    always empty; caught live 2026-10-01 r321 against the real origin
    face -- the dedup leg is load-bearing for law sec.2 防重烧.)"""
    out = set()
    for line in stdout_text.splitlines():
        name = line.strip().split("/")[-1]
        if name.startswith("shard-") and name.endswith(".json"):
            try:
                out.add(int(name.split("-")[1]))
            except (ValueError, IndexError):
                continue
    return out


def sync_window(active_waves):
    """Law sec.1/2: the fetch/reconcile surface (never in the hot path).

    fetch origin (no tree touch, zero-window) then ls-tree the product
    dirs of active waves -> remote done-truth. Never mutates anything;
    failure degrades honestly to local-only truth.
    """
    remote_done, err = set(), None
    try:
        r = _git(["fetch", "origin"])
        if r.returncode != 0:
            err = "fetch rc=%d %s" % (r.returncode, (r.stderr or "").strip()[:160])
            return remote_done, err
        for wave in active_waves:
            r = _git(["ls-tree", "--name-only", "origin/main",
                      "results/p2cal_ext/n1_w%d/" % wave])
            if r.returncode != 0:
                err = "ls-tree w%d rc=%d" % (wave, r.returncode)
                continue
            remote_done |= {(wave, s) for s in parse_remote_shards(r.stdout)}
    except subprocess.TimeoutExpired:
        err = "sync timeout"
    except OSError as exc:
        err = "sync oserror %r" % (exc,)
    return remote_done, err


# ------------------------------------------------- law sec.2 s2 conversion
def git_busy(repo=None):
    """Concurrent-surgery markers (r312/r314 family): any rebase/merge in
    progress or a held index lock means the engine MUST NOT commit this
    cycle (defer to the next batch window)."""
    gd = os.path.join(repo or ROOT, ".git")
    return [m for m in GIT_BUSY_MARKERS if os.path.exists(os.path.join(gd, m))]


def untracked_products(repo=None, area="results/p2cal_ext"):
    """Pending-append face: burned product files not yet in local git
    (ls-files --others; ground truth self-derived from git, r488 family).
    Returns (pending_list, err); pending items carry {path, wave, shard,
    age_s} -- only the frozen product path convention is collected."""
    r = _git(["ls-files", "--others", "--exclude-standard", "--", area],
             cwd=repo or ROOT, timeout=60)
    if r.returncode != 0:
        return None, "ls-files rc=%d" % r.returncode
    now = time.time()
    pend = []
    for raw in r.stdout.splitlines():
        p = raw.strip().strip('"')
        if not p:
            continue
        m = re.match(r"(?:^|.*/)n1_w(\d+)/shard-(\d+)-of-(\d+)\.json$",
                     p.replace("\\", "/"))
        if not m:
            continue
        fp = os.path.join(repo or ROOT, p.replace("/", os.sep))
        try:
            age = now - os.path.getmtime(fp)
        except OSError:
            age = None
        pend.append({"path": p, "wave": int(m.group(1)),
                     "shard": int(m.group(2)), "age_s": age})
    return pend, None


def append_due(pending):
    """Law sec.2 batching decision (pure, selftest-legible): flush when
    >= N shards are pending OR the oldest has waited out the window
    (10-20min band -> 15min). Empty = never."""
    if not pending:
        return False
    if len(pending) >= APPEND_MIN_SHARDS:
        return True
    ages = [p["age_s"] for p in pending if p["age_s"] is not None]
    return bool(ages) and max(ages) >= APPEND_EVERY_S


def ledger_append_batch(pending, mid, repo=None, dry=False):
    """Law sec.2 face: async batched ledger append -- targeted pathspec
    commit of NEW product files only (never add -A, r109 law), then a
    best-effort push. NO engine-side rebase ever: a rejected push leaves
    the local commit for the next round session's pull --rebase to
    replay (byte-identical twins already on origin drop as empty picks,
    proven 10-01 CAS precedent). Guards: rebase/merge markers + held
    index lock (r312/r314 family) -> honest defer. Never raises."""
    repo = repo or ROOT
    rec = {"epoch": int(time.time()), "n_paths": len(pending), "mid": mid}
    try:
        marks = git_busy(repo)
        if marks:
            rec.update({"outcome": "deferred",
                        "reason": "git busy: %s" % ",".join(marks)})
            return rec
        paths = [p["path"] for p in pending]
        r = _git(["add", "--"] + paths, cwd=repo, timeout=APPEND_TIMEOUT_S)
        if r.returncode != 0:
            rec.update({"outcome": "deferred", "reason":
                        "add rc=%d %s" % (r.returncode, (r.stderr or "")[:160])})
            return rec
        # pathspec commit: takes ONLY these paths from the worktree; any
        # concurrent session's staged set stays staged untouched (r494
        # staged-index 吞件 guard by construction).
        msg = ("saturation engine ledger append (%s): %d n1 product shard(s) "
               "[law sec.2 batched]" % (mid, len(paths)))
        r = _git(["-c", "user.name=saturation-engine (%s)" % mid,
                  "-c", "user.email=engine@bigmoney.local",
                  "commit", "-m", msg, "--"] + paths,
                 cwd=repo, timeout=APPEND_TIMEOUT_S)
        if r.returncode != 0:
            rec.update({"outcome": "deferred", "reason":
                        "commit rc=%d %s" % (r.returncode, (r.stderr or "")[:200])})
            return rec
        rec["committed"] = ((r.stdout or "").strip().splitlines() or [""])[0]
        if dry:
            rec["outcome"] = "committed_dry"
            return rec
        r = _git(["push", "origin", "HEAD:refs/heads/main"],
                 cwd=repo, timeout=APPEND_TIMEOUT_S)
        rec["push_rc"] = r.returncode
        if r.returncode == 0:
            rec["outcome"] = "pushed"
        else:
            rec.update({"outcome": "push_rejected_local_kept",
                        "reason": (r.stderr or "")[:200]})
    except Exception as exc:               # honest, never crash the loop
        rec.update({"outcome": "error", "reason": repr(exc)[:200]})
    return rec


def derive_grammar_consumption(bands, preregs, done, remote_done):
    """Law sec.2 照记 face: per authorized wave, record the grammar (seed
    band) consumption plus the fetch-synced dedup counts (生成窗 fetch
    对账, 防重烧). Pure (selftest-legible)."""
    out = []
    for wave in sorted(bands):
        if not preregs.get(wave):
            continue
        row = bands[wave] or {}
        out.append({
            "face": "N1", "wave": wave,
            "a_band": list(row.get("a", ())),
            "b_exit_band": list(row.get("b_exit", ())),
            "authorization": "per-wave prereg + law sec.4 band ledger "
                             "(pre-claim exempt, sec.2)",
            "dedup": {"local_done": sum(1 for (w, _) in done if w == wave),
                      "remote_done": sum(1 for (w, _) in remote_done
                                         if w == wave)},
        })
    return out


def derive_face(mid, now, st, burns, done, py_pct, ram_free_gb, fatal=None):
    """Law sec.5 CEO-face row (T-141 s3): schema mirrors the bm-b instance
    (reader contract = monitor/build_status.py _engine_face_state --
    machine_id + int epoch drive the standing/alive row; extras advisory).
    Pure (selftest-legible)."""
    active = [{"wave": w, "shard": s, "pid": rec.get("pid")}
              for (w, s), rec in burns.items()]
    queue_depth = len(st.get("queue_next") or [])
    if fatal is not None:
        verdict = "fault"
    elif active:
        verdict = "burning"
    elif queue_depth:
        verdict = "queued"
    else:
        verdict = "idle"
    last_done = (st.get("completed") or [{}])[-1].get("ended_epoch")
    last_flush = st.get("last_append_epoch")

    def _iso(epoch):
        return time.strftime("%Y-%m-%dT%H:%M:%S+08:00",
                             time.localtime(epoch)) if epoch else None
    return {
        "machine_id": mid, "engine": "saturation-engine",
        "version": STATE_VERSION, "law_ref": LAW_REF,
        "ts": _iso(int(now)), "epoch": int(now),
        "py_cpu_pct": py_pct, "engine_alive": fatal is None,
        "ram_free_gb": ram_free_gb, "active_burns": active,
        "queue_depth": queue_depth, "shards_done_total": len(done),
        "last_shard_done_at": _iso(last_done),
        "last_flush_at": _iso(last_flush), "verdict": verdict,
    }


# ------------------------------------------------------------------- state
def load_state(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


def write_state(path, st):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(st, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    os.replace(tmp, path)


def heartbeat_due(st, now):
    last = st.get("heartbeat_epoch") or 0
    return (now - last) >= HEARTBEAT_S


# --------------------------------------------------------------------- run
def run_engine(mid, once=False):
    if psutil:
        psutil.cpu_percent(interval=None)         # prime the sampler
        _py_cpu_pct()                              # prime per-process counters
        # (first process_iter cpu_percent read is always 0.0 -- without this
        # priming the first cycle mis-reads py load as idle and over-ignites;
        # observed r319: 3 extra W9 ignitions during an S6-chain window)
    spath = state_path(mid)
    os.makedirs(LOG_DIR, exist_ok=True)
    slot, cap, maxburn = partition_slot(mid), core_cap(mid), max_concurrent(mid)
    st = load_state(spath)
    crash = dict(st.get("crash_counts") or {})
    quarantined = set(tuple(k) for k in st.get("quarantined") or [])
    st.update({"machine_id": mid, "engine": "saturation_engine",
               "version": STATE_VERSION, "law": "firm/SATURATION_ENGINE_LAW.md v1.0",
               "core_cap": cap, "workers_per_shard": WORKERS_PER_SHARD,
               "max_concurrent_burns": maxburn, "partition_slot": slot,
               "face_scope_note": "v0.1 N1-only queue (N2/N3 expansion pending "
                                  "runner CLI verify; N4 not landed -- fake-supply ban)",
               "alive": True})
    burns = {}    # (wave,shard) -> {"pid":..,"started":..,"log":..,"adopted":bool}
    for a in adopt_inflight():                    # restart adoption
        if a["shard"] >= 0:
            burns[(a["wave"], a["shard"])] = {
                "pid": a["pid"], "started": None, "log": None,
                "adopted": True}
    last_sync = 0.0
    remote_done, sync_err = set(), None
    cycle = 0

    # inner watchdog: stall -> hard exit, schtasks restarts (law sec.4)
    stall = {"t": time.time()}
    def _watchdog():
        while True:
            time.sleep(30)
            if time.time() - stall["t"] > STALL_EXIT_S:
                os._exit(3)
    threading.Thread(target=_watchdog, daemon=True).start()

    while True:
        cycle += 1
        stall["t"] = time.time()
        now = time.time()

        # 1. re-derive done-truth from product presence (r488/r500 family)
        done = set()
        try:
            bands = n1_bands()
        except Exception as exc:
            _flush(st, spath, now, burns, done, quarantined, crash,
                   remote_done, sync_err, cycle, mid, fatal="band import %r" % (exc,))
            return 2
        active_waves = sorted(bands)
        for wave in active_waves:
            for s in range(N1_SHARDS):
                if os.path.exists(product_path(wave, s)):
                    done.add((wave, s))
        done |= remote_done

        # 2. supervise burns: completion / crash bookkeeping
        for key in list(burns):
            rec = burns[key]
            wave, shard = key
            if os.path.exists(product_path(wave, shard)):
                st.setdefault("completed", []).append(
                    {"wave": wave, "shard": shard, "pid": rec["pid"],
                     "ended_epoch": int(now), "rc": None})
                st["completed"] = st["completed"][-200:]
                burns.pop(key)
                continue
            alive = False
            try:
                alive = psutil.pid_exists(rec["pid"]) if psutil else True
            except Exception:
                alive = True
            if not alive:
                burns.pop(key)
                crash["%d:%d" % (wave, shard)] = crash.get("%d:%d" % (wave, shard), 0) + 1
                if crash["%d:%d" % (wave, shard)] >= FUSE_MAX:
                    quarantined.add(key)

        # 3. sync window (20-min cadence; the reconcile surface)
        if now - last_sync >= SYNC_EVERY_S:
            remote_done, sync_err = sync_window(active_waves)
            done |= remote_done
            last_sync = now

        # 3.5 law sec.2 (s2): grammar consumption log (recorded with the
        #     fetch-synced dedup counts, 生成窗 fetch 对账) + async
        #     batched ledger append (products -> git, 15min/N-shard)
        st["grammar_consumption"] = derive_grammar_consumption(
            bands,
            {w: prereg_path(w) if os.path.isfile(prereg_path(w)) else None
             for w in active_waves},
            done, remote_done)
        pending, pend_err = untracked_products()
        st["append_pending"] = len(pending) if pending is not None else None
        st["append_err"] = pend_err
        if pending and append_due(pending):
            rec = ledger_append_batch(pending, mid)
            st.setdefault("ledger_appends", []).append(rec)
            st["ledger_appends"] = st["ledger_appends"][-40:]
            if rec.get("epoch"):
                st["last_append_epoch"] = rec["epoch"]

        # 4. ignite while: burns below cap AND machine under fill line
        py_pct, mach_pct = _py_cpu_pct(), _machine_cpu_pct()
        wave_complete = {}
        for wave in active_waves:
            wave_complete[str(wave)] = sum(1 for (w, _) in done if w == wave)
        st["wave_shards_done"] = wave_complete
        st["wave_complete_flags"] = [int(w) for w in active_waves
                                     if wave_complete[str(w)] >= N1_SHARDS]
        if (py_pct is None or py_pct < PY_FILL_LINE) and \
                (mach_pct is None or mach_pct < MACHINE_IGNITE_HOLD):
            queue = derive_n1_queue(bands,
                                    {w: prereg_path(w) if os.path.isfile(
                                        prereg_path(w)) else None
                                     for w in active_waves},
                                    done, quarantined, slot, owner_mid=mid)
            st["queue_next"] = queue[:8]
            for item in queue:
                if len(burns) >= maxburn:
                    break
                key = (item["wave"], item["shard"])
                if key in burns:
                    continue
                fails = pre_ignition_checks(item)
                if fails:
                    st.setdefault("last_ignition_refusals", []).append(
                        {"wave": item["wave"], "shard": item["shard"],
                         "fails": fails, "epoch": int(now)})
                    st["last_ignition_refusals"] = st["last_ignition_refusals"][-20:]
                    continue
                pid, log_file = ignite(item)
                burns[key] = {"pid": pid, "started": now, "log": log_file,
                              "adopted": False}
                st.setdefault("ignitions", []).append(
                    {"wave": item["wave"], "shard": item["shard"], "pid": pid,
                     "epoch": int(now), "primary": item["primary"]})
                st["ignitions"] = st["ignitions"][-200:]
        else:
            st["queue_next"] = []

        # 5. state face (event-written + bounded heartbeat)
        st["burns_active"] = [{"wave": w, "shard": s, "pid": r["pid"],
                               "adopted": r["adopted"]} for (w, s), r in burns.items()]
        st["cycle"] = cycle
        if heartbeat_due(st, now) or burns or cycle == 1:
            _flush(st, spath, now, burns, done, quarantined, crash,
                   remote_done, sync_err, cycle, mid,
                   py_pct=py_pct, mach_pct=mach_pct)
        if once:
            return 0
        time.sleep(CYCLE_S)


def _flush(st, spath, now, burns, done, quarantined, crash, remote_done,
           sync_err, cycle, mid, py_pct=None, mach_pct=None, fatal=None):
    st["heartbeat_epoch"] = int(now)
    st["last_cycle_ts"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(now))
    st["py_cpu_pct"] = py_pct
    st["machine_cpu_pct"] = mach_pct
    st["done_count"] = len(done)
    st["quarantined"] = sorted([list(k) for k in quarantined])
    st["crash_counts"] = crash
    st["sync"] = {"last_epoch": int(now), "remote_done_count": len(remote_done),
                  "err": sync_err}
    st["alive"] = fatal is None
    if fatal:
        st["fatal"] = fatal
    try:
        write_state(spath, st)
    except OSError:
        pass                                         # never crash the loop on IO
    # law sec.5 CEO face row (s3): lane file live-written with every state
    # flush (<=60s heartbeat bound); reader = build_status aggregation.
    ram_gb = None
    if psutil:
        try:
            ram_gb = round(psutil.virtual_memory().available / (1024 ** 3), 1)
        except Exception:
            ram_gb = None
    try:
        os.makedirs(FACE_DIR, exist_ok=True)
        write_state(face_path(mid), derive_face(
            mid, now, st, burns, done, py_pct, ram_gb, fatal=fatal))
    except Exception:
        pass                                         # never crash the loop on IO


# ------------------------------------------------------------------ status
def cmd_status(mid):
    st = load_state(state_path(mid))
    bands = {}
    try:
        bands = n1_bands()
    except Exception:
        pass
    done = set()
    for wave in sorted(bands):
        for s in range(N1_SHARDS):
            if os.path.exists(product_path(wave, s)):
                done.add((wave, s))
    print(json.dumps({
        "machine_id": mid, "state_present": bool(st),
        "alive_flag": st.get("alive"), "heartbeat_epoch": st.get("heartbeat_epoch"),
        "heartbeat_age_s": (time.time() - st["heartbeat_epoch"])
        if st.get("heartbeat_epoch") else None,
        "burns_active": st.get("burns_active", []),
        "queue_next": st.get("queue_next", []),
        "wave_shards_done": st.get("wave_shards_done", {}),
        "wave_complete_flags": st.get("wave_complete_flags", []),
        "disk_done_count": len(done), "quarantined": st.get("quarantined", []),
        "sync": st.get("sync"), "py_cpu_pct": st.get("py_cpu_pct"),
        "append_pending": st.get("append_pending"),
        "append_err": st.get("append_err"),
        "last_append": (st.get("ledger_appends") or [None])[-1],
        "grammar_consumption": st.get("grammar_consumption", []),
    }, ensure_ascii=False, indent=1))
    return 0


# ---------------------------------------------------------------- selftest
def selftest():
    """r117 hermetic: no network, no real burns, no real git ops."""
    fails = []
    n_legs = [0]
    def leg(name, cond):
        n_legs[0] += 1
        print("  [%s] %s" % ("PASS" if cond else "FAIL", name))
        if not cond:
            fails.append(name)

    # 1. partition math: disjoint cover of the wave by the 3 slots
    cover = [set(s for s in range(N1_SHARDS) if s % 3 == slot)
             for slot in range(3)]
    leg("partition disjoint", all(not (cover[i] & cover[j])
                                  for i in range(3) for j in range(i + 1, 3)))
    leg("partition cover", set().union(*cover) == set(range(N1_SHARDS)))

    # 2. product path convention matches runner output face
    leg("product path", product_path(9, 2).replace("\\", "/").endswith(
        "results/p2cal_ext/n1_w9/shard-2-of-12.json"))
    leg("prereg path", prereg_path(9).replace("\\", "/").endswith(
        "research/PERPETUAL_N1_W9_PREREG.md"))

    # 3. queue derivation: authorization + primary-first + done/quarantine skip
    bands = {2: "row", 3: "row"}
    preregs = {2: "yes", 3: None}                     # wave 3 unauthorized
    q = derive_n1_queue(bands, preregs, set(), set(), slot=2)
    leg("queue unauthorized wave excluded",
        all(item["wave"] != 3 for item in q))
    leg("queue primary first",
        q and all(item["primary"] for item in q[:4])
        and all(not item["primary"] for item in q[4:8]))
    leg("queue skip done", derive_n1_queue(
        bands, preregs, {(2, 2)}, set(), slot=2)
        and all((item["wave"], item["shard"]) != (2, 2)
                for item in derive_n1_queue(bands, preregs, {(2, 2)}, set(), slot=2)))
    leg("queue skip quarantined", all(
        (item["wave"], item["shard"]) != (2, 5)
        for item in derive_n1_queue(bands, preregs, set(), {(2, 5)}, slot=2)))

    # 4. pre-ignition negative faces (r316)
    fake_item = {"face": "N1", "wave": 9, "shard": 11, "nshards": 12}
    f_runner = pre_ignition_checks(fake_item, runner="/nonexistent/runner.py")
    leg("PI runner missing detected",
        any("runner missing" in x for x in f_runner))
    f_data = pre_ignition_checks(fake_item, runner=RUNNER,
                                 daily_dir="/nonexistent/daily")
    leg("PI data gate detected",
        any("core48 data gate" in x for x in f_data))

    # 5. band ledger single source (import face only; pf owns its own asserts)
    try:
        bands = n1_bands()
        leg("band ledger W9 row present", 9 in bands)
    except Exception as exc:
        leg("band ledger import", False)
        print("    (%r)" % (exc,))

    # 6. burn cmdline contract (s2: engine-lane flag, law sec.2)
    cmd = build_burn_cmd({"wave": 9, "shard": 2, "nshards": 12})
    leg("burn cmd", cmd[-11:] == ["run", "--shard", "2", "--of", "12",
                                  "--wave", "9", "--workers", "8",
                                  "--lane", "engine"])

    # 7. fuse math
    leg("fuse max constant", FUSE_MAX == 3)

    # 8. state round-trip
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "st.json")
        probe = {"machine_id": "selftest", "heartbeat_epoch": 1}
        write_state(p, probe)
        leg("state round-trip", load_state(p).get("machine_id") == "selftest")

    # 9. real-tree face: W2..W8 done-truth on disk (12 each, environment fact)
    done_w8 = sum(1 for s in range(N1_SHARDS)
                  if os.path.exists(product_path(8, s)))
    leg("env W8 shards done >=12", done_w8 >= N1_SHARDS)

    # 10. law sec.2 s2 faces: batching decision + consumption log +
    #     exemption face + busy markers + hermetic end-to-end append
    leg("append_due empty", not append_due([]))
    # s2 live bugfix face: ls-tree emits FULL paths -- the s1 bare-name
    # parse starved remote_done (dedup leg load-bearing, caught r321)
    leg("remote shard parse full-path shape",
        parse_remote_shards(
            "results/p2cal_ext/n1_w9/shard-0-of-12.json\n"
            "results/p2cal_ext/n1_w9/shard-10-of-12.json\n"
            "results/p2cal_ext/n1_w9/shard-11-of-12.json\n") == {0, 10, 11})
    leg("remote shard parse noise-safe",
        parse_remote_shards("shard-x-of-12.json\nn1_w9/other.json\n") == set())
    leg("append_due N-shard trigger",
        append_due([{"age_s": 1.0}] * APPEND_MIN_SHARDS))
    leg("append_due window trigger",
        append_due([{"age_s": APPEND_EVERY_S + 1.0}]))
    leg("append_due young single no-flush",
        not append_due([{"age_s": 30.0}]))
    cons = derive_grammar_consumption(
        {9: {"a": (26_100, 28_099), "b_exit": (28_100, 28_299)}, 10: {}},
        {9: "research/PERPETUAL_N1_W9_PREREG.md", 10: None},
        {(9, 0)}, {(9, 3)})
    leg("consumption excludes unauthorized wave",
        all(c["wave"] != 10 for c in cons))
    leg("consumption dedup counts",
        any(c["dedup"] == {"local_done": 1, "remote_done": 1} for c in cons))
    leg("queue pre-claim-exempt face",
        all(i["authorization"] == "pre-claim-exempt (law sec.2)"
            for i in derive_n1_queue({2: "row"}, {2: "p"}, set(), set(),
                                     slot=1)))
    leg("queue authorization absent for unauthorized wave",
        not derive_n1_queue({2: "row"}, {2: None}, set(), set(), slot=1))
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        fake = os.path.join(td, "fakebusy")
        os.makedirs(os.path.join(fake, ".git", "rebase-merge"))
        leg("git_busy marker detection", git_busy(fake) == ["rebase-merge"])
        # hermetic end-to-end append: temp repo + bare remote (real git
        # binary, ZERO company-repo/network surface)
        repo = os.path.join(td, "repo")
        bare = os.path.join(td, "bare.git")
        def _g(args, cwd):
            return subprocess.run(
                ["git"] + args, cwd=cwd, capture_output=True, text=True,
                timeout=60, creationflags=subprocess.CREATE_NO_WINDOW)
        ok = True
        for a, c in ((["init", "-q", "--initial-branch=main", repo], td),
                     (["init", "-q", "--bare", "--initial-branch=main", bare], td)):
            ok &= _g(a, c).returncode == 0
        open(os.path.join(repo, "base.txt"), "w").write("base\n")
        ok &= _g(["add", "base.txt"], repo).returncode == 0
        ok &= _g(["-c", "user.name=st", "-c", "user.email=st@t",
                  "commit", "-q", "-m", "base"], repo).returncode == 0
        ok &= _g(["remote", "add", "origin", bare], repo).returncode == 0
        ok &= _g(["push", "-q", "origin", "main"], repo).returncode == 0
        pdir = os.path.join(repo, "results", "p2cal_ext", "n1_w9")
        os.makedirs(pdir)
        open(os.path.join(pdir, "shard-0-of-12.json"), "w").write("{}")
        pend, perr = untracked_products(repo=repo)
        leg("hermetic pending derive",
            perr is None and bool(pend) and pend[0]["wave"] == 9
            and pend[0]["shard"] == 0
            and pend[0]["path"].endswith("n1_w9/shard-0-of-12.json"))
        rec = ledger_append_batch(pend, "selftest", repo=repo)
        ls = _g(["ls-tree", "--name-only", "origin/main",
                 "results/p2cal_ext/n1_w9/"], repo)
        leg("hermetic append committed+pushed",
            ok and rec.get("outcome") == "pushed"
            and "shard-0-of-12.json" in ls.stdout)
        # busy-guard defer face: marker present -> honest defer, no commit
        os.makedirs(os.path.join(repo, ".git", "CHERRY_PICK_HEAD"))
        open(os.path.join(pdir, "shard-1-of-12.json"), "w").write("{}")
        pend2, _ = untracked_products(repo=repo)
        rec2 = ledger_append_batch(pend2, "selftest", repo=repo)
        leg("hermetic busy defer", rec2.get("outcome") == "deferred"
            and "CHERRY_PICK_HEAD" in rec2.get("reason", ""))

    # 11. s3 CEO face (law sec.5): reader-contract keys + verdict logic
    face = derive_face("selftest", 1790000000.0, {"queue_next": []},
                       {(9, 0): {"pid": 7, "adopted": False}}, {(9, 0)},
                       12.5, 4.5)
    leg("face reader-contract keys", all(
        k in face for k in ("machine_id", "epoch", "py_cpu_pct",
                            "engine_alive", "active_burns", "queue_depth",
                            "shards_done_total", "ts")))
    leg("face epoch int", isinstance(face["epoch"], int))
    leg("face verdict burning", face["verdict"] == "burning"
        and face["shards_done_total"] == 1)
    leg("face verdict idle",
        derive_face("s", 1.0, {"queue_next": []}, {}, set(), 0.0, 1.0)
        ["verdict"] == "idle")
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "face_x.json")
        write_state(p, face)
        leg("face round-trip", load_state(p).get("machine_id") == "selftest")

    # 12. sec.1 engine_owner gate (r508 convention parity): foreign
    #     engine waves invisible, legacy field-absent rows stay eligible
    gbands = {11: {"a": (1, 2), "engine_owner": "bm-b"},
              12: {"a": (3, 4), "engine_owner": "bm-c"}}
    qg = derive_n1_queue(gbands, {11: "p", 12: "p"}, set(), set(), slot=2,
                         owner_mid="bm-c")
    leg("owner gate excludes foreign wave",
        all(i["wave"] != 11 for i in qg) and any(i["wave"] == 12 for i in qg))
    leg("owner gate legacy rows allowed",
        all(i["wave"] == 2 for i in derive_n1_queue(
            {2: {"a": (1, 2)}}, {2: "p"}, set(), set(), slot=2,
            owner_mid="bm-c")))

    total = n_legs[0]
    print("selftest: %d/%d PASS" % (total - len(fails), total)
          if not fails else "selftest: FAIL %r" % fails)
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser(description="T-141 s1 resident saturation engine")
    ap.add_argument("subcommand", nargs="?", default="run",
                    choices=["run", "status", "selftest"])
    ap.add_argument("--once", action="store_true",
                    help="single supervision cycle (diagnostics)")
    args = ap.parse_args()
    mid = read_machine_id()
    if args.subcommand == "selftest":
        return selftest()
    if args.subcommand == "status":
        return cmd_status(mid)
    return run_engine(mid, once=args.once)


if __name__ == "__main__":
    sys.exit(main())
