"""SATURATION_ENGINE -- resident saturation executor, bm-b instance.

T-2026-10-01-141 slices s1 (engine core) + s3 (CEO face / round-zero
wiring). Law: firm/SATURATION_ENGINE_LAW.md v1.0 (CEO direct order
O-20261001-1410 -- "saturation is a RESIDENT EXECUTOR, not a between-
rounds metric").

sec.1  Local perpetual queue: deterministic generators (frozen preregs +
       band ledger); core-idle -> ignite within seconds -- no round
       latency, ZERO claim round-trips in the hot path (engine burns
       never touch runnable_pool.json). Band-partitioned shard space:
       the queue only ever holds waves whose WAVE_CONFIGS row carries
       engine_owner == this machine (frozen by a round action with the
       band-gate + banned_direction_gate receipts); pool-era waves are
       invisible here, and cmd_supply refuses engine waves -- the two
       halves of the zero-cross-machine-duplication contract.
sec.2  Pool = ledger, not gate: engine burns are exempt from pre-claim
       authorization; ledger appends are ASYNC BATCHED (15-min or
       3-shard windows) into results/saturation_engine/ledger_<id>.jsonl.
sec.3  PreIgnitionChecks mandatory (r316 law hardened): local data
       prerequisites verified BEFORE ignite; missing = skip + report;
       zombie ignition forbidden.
sec.4  Watchdog / self-restart: burn death is re-ignited by the next
       tick with a crash backoff (>=3 crashes on one shard = quarantine,
       honest report); state is SELF-DERIVED from artifacts every tick
       (checkpoint presence = done, r488 semantics) -- never from belief.
sec.5  CEO face: per-machine py% standing row engine-written live into
       results/saturation_engine/face_<id>.json (per-machine lane file,
       git-synced by round commits -> build_status engine section ->
       dashboard). bm-b runs the full-core profile (O-20261001-1410 s1),
       burns at BELOW_NORMAL priority so pool/judged faces keep the CPU.

Residency model (honest design note): the engine is a scheduled-task
tick daemon (Bigmoney-SatEngine-bm-b, 60s cadence, S4U headless --
autofill C8 lineage), not an in-process infinite loop. Every tick is a
fresh self-derived cycle (crash-proof residency); idle-to-ignite
latency is bounded by the tick cadence (<=60s, two orders below the
10-min round latency this law kills). "Engine dead > 1 round = red" is
caught by the loop round-zero check (`saturation_engine.py status`,
wired into Tools/iteration_prompt.txt) -- status exit 1 = P0 same-round
repair.

Generators: N1 waves are frozen per-wave (law sec.4 band ledger +
per-wave prereg). The engine NEVER creates waves -- it materializes
unburned shards of already-frozen engine-owned waves (first engine wave
= W10, engine_owner=bm-b, prereg research/PERPETUAL_N1_W10_PREREG.md).
N2/N3/N4 generator hooks land with their faces (FACES registry order).

Products land in the exact layout the finalize face consumes
(results/p2cal_ext/n1_w<wave>/shard-<i>-of-12.json via the verbatim
runner scripts/perpetual_faces_n1.py -- zero runner rewrite).

Usage: tick | status | selftest
"""

import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import PATHS                      # noqa: E402
import perpetual_faces_n1 as n1              # noqa: E402

LAW_REF = ("firm/SATURATION_ENGINE_LAW.md v1.0 (T-2026-10-01-141 s1+s3, "
           "O-20261001-1410 CEO direct order)")
VERSION = "0.1"
ENGINE_DIR = os.path.join(PATHS.results_dir, "saturation_engine")
LOG_DIR = os.path.join(PATHS.root, "logs", "saturation_engine")
MACHINE_ID = json.load(open(os.path.join(
    PATHS.root, "fleet", "machine.json"), encoding="utf-8")).get("machine_id", "unknown")
STATE_PATH = os.path.join(ENGINE_DIR, f"state_{MACHINE_ID}.json")
FACE_PATH = os.path.join(ENGINE_DIR, f"face_{MACHINE_ID}.json")
HISTORY_PATH = os.path.join(ENGINE_DIR, f"history_{MACHINE_ID}.jsonl")
LEDGER_PATH = os.path.join(ENGINE_DIR, f"ledger_{MACHINE_ID}.jsonl")
LOG_PATH = os.path.join(PATHS.root, "logs", "saturation_engine.log")

DETACHED = (0x00000008 | 0x00000200)   # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP

NSHARDS = 12                 # law sec.4 wave face: 12 shards per N1 wave
WORKERS = 8                  # O-20260930-2355 multicore law per shard
SAMPLE_S = 2.0               # instantaneous py-CPU sample window (autofill face)
MAX_ACTIVE_BURNS = 1         # v0.1: one shard burn at a time; the pool
                             # daemon stays the multi-launch saturator for
                             # pool faces -- the engine is the never-dry floor
PY_IGNITE_CEIL = 75.0        # ignite only with headroom (pool/judged first)
RAM_FLOOR_GB = 4.0           # bm-b shared-machine discipline (heartbeat law)
LEDGER_FLUSH_MIN = 15.0      # sec.2 async batch window (10-20min band)
LEDGER_FLUSH_N = 3           # sec.2 N-shard batch trigger
CRASH_QUARANTINE = 3         # sec.4 crash backoff ceiling per shard
HEARTBEAT_STALE_S = 300      # status: alive if a tick landed < 5 min ago
HISTORY_TAIL = 120             # face-history derive lane (1-min rows,
                              # ~2h trend window; keeps git churn bounded)


def _now_iso():
    return time.strftime("%Y-%m-%dT%H:%M:%S") + time.strftime("%z")[:3] \
        + ":" + time.strftime("%z")[3:]


def _log(msg):
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"{_now_iso()} [{MACHINE_ID}] {msg}\n")
    except Exception:
        pass


def _py_cpu_pct(window=SAMPLE_S):
    """Instantaneous python-process CPU load as % of machine capacity
    (autofill _py_cpu_pct face verbatim)."""
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


def _ram_free_gb():
    try:
        import psutil
        return psutil.virtual_memory().available / (1 << 30)
    except Exception:
        return None


def _shard_path(cfg, shard, nshards=NSHARDS):
    return os.path.join(PATHS.results_dir, "p2cal_ext", cfg["shard_subdir"],
                        f"shard-{shard}-of-{nshards}.json")


def _shard_done(wave, cfg, shard, nshards=NSHARDS):
    """Checkpoint presence=done (r488 semantics) via the runner's single-
    source validator (_shard_valid), wave pinned (BATCH face)."""
    path = _shard_path(cfg, shard, nshards)
    if not os.path.exists(path):
        return False
    n1._set_wave(wave)
    try:
        return n1._shard_valid(path, shard, nshards)
    finally:
        n1._set_wave(2)


# --- sec.1 queue generator (pure; hermetic-testable) ------------------------

def _queue_items(wave_configs, done_probe, active_keys, machine_id,
                 nshards=NSHARDS):
    """Local perpetual queue: every unburned shard of every engine-owned
    wave, lowest wave first, lowest shard first. Pure function -- the
    tick wires real configs/probes; the selftest wires fixtures."""
    items = []
    for wave in sorted(wave_configs):
        cfg = wave_configs[wave]
        if cfg.get("engine_owner") != machine_id:
            continue                      # pool-era / other-machine waves: invisible
        for shard in range(nshards):
            key = f"n1w{wave}-{shard}of{nshards}"
            if key in active_keys:
                continue
            if done_probe(wave, cfg, shard, nshards):
                continue
            items.append({"face": "N1", "wave": wave, "shard": shard,
                         "nshards": nshards, "key": key,
                         "batch": cfg["batch"],
                         "runner": "scripts/perpetual_faces_n1.py",
                         "runner_args": ["run", "--shard", str(shard),
                                         "--of", str(nshards),
                                         "--wave", str(wave),
                                         "--workers", str(WORKERS)]})
    return items


# --- sec.3 PreIgnitionChecks (r316 hardened; pure) --------------------------

def _pre_ignition_checks(item, cfg, prereg_path, daily_dir, done_probe,
                          crash_counts):
    """Fail-closed local prerequisite verification BEFORE ignite (r316
    law: missing = skip + report, zombie ignition forbidden). Returns
    (ok, reasons)."""
    reasons = []
    if not os.path.exists(prereg_path):
        reasons.append(f"prereg missing: {prereg_path}")
    if cfg.get("engine_owner") != MACHINE_ID:
        reasons.append("wave not engine-owned by this machine")
    try:
        csvs = [f for f in os.listdir(daily_dir)
                if f.endswith(".csv") and f[:-4].isdigit()]
    except Exception:
        csvs = []
    if len(csvs) < 48:
        reasons.append(f"core48 panel face short: {len(csvs)} csv files")
    if done_probe(item["wave"], cfg, item["shard"], item["nshards"]):
        reasons.append("checkpoint already valid (presence=done)")
    if crash_counts.get(item["key"], 0) >= CRASH_QUARANTINE:
        reasons.append(f"crash quarantine (>={CRASH_QUARANTINE} crashes)")
    return (not reasons), reasons


# --- sec.2 ledger batching (pure gate) --------------------------------------

def _flush_due(n_buffer, minutes_since_flush):
    if n_buffer <= 0:
        return False
    return n_buffer >= LEDGER_FLUSH_N or minutes_since_flush >= LEDGER_FLUSH_MIN


def _ignite_ok(py_pct, active_n, ram_free, max_active=MAX_ACTIVE_BURNS,
               py_ceil=PY_IGNITE_CEIL, ram_floor=RAM_FLOOR_GB):
    if active_n >= max_active:
        return False, "active burn cap"
    if py_pct is not None and py_pct >= py_ceil:
        return False, f"py {py_pct}% >= {py_ceil}% (headroom gate)"
    if ram_free is not None and ram_free < ram_floor:
        return False, f"free RAM {ram_free:.1f}GB < {ram_floor}GB floor"
    return True, ""


# --- state (self-derived every tick) ----------------------------------------

def _load_state():
    if os.path.exists(STATE_PATH):
        try:
            with open(STATE_PATH, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"version": VERSION, "machine_id": MACHINE_ID, "law_ref": LAW_REF,
            "active": [], "ledger_buffer": [], "last_flush_at": None,
            "crashes": {}, "shards_done_total": 0,
            "last_shard_done_at": None, "last_tick": None, "skips": []}


def _save_state(st):
    os.makedirs(ENGINE_DIR, exist_ok=True)
    tmp = STATE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
    os.replace(tmp, STATE_PATH)


def _reap_active(st, pid_alive, done_probe, now_epoch):
    """sec.4 self-derivation: classify each active burn from ARTIFACTS --
    valid checkpoint = completed (ledger row buffered, async per sec.2);
    dead pid + no valid checkpoint = crash (backoff counter, re-ignited
    by a later tick); live pid + no checkpoint = still burning."""
    completed, crashed, still = [], [], []
    for b in st.get("active", []):
        alive = pid_alive(b.get("pid"))
        if done_probe(b["wave"], b["cfg"], b["shard"], b["nshards"]):
            row = {"machine_id": MACHINE_ID, "face": "N1",
                   "wave": b["wave"], "batch": b["batch"], "shard": b["shard"],
                   "nshards": b["nshards"], "key": b["key"],
                   "pid": b.get("pid"), "started_at": b.get("started_at"),
                   "done_at": _now_iso(), "done_epoch": int(now_epoch),
                   "elapsed_sec": round(
                       now_epoch - (b.get("started_epoch") or now_epoch), 1)}
            completed.append(row)
        elif not alive:
            crashed.append(b)
        else:
            still.append(b)
    return completed, crashed, still


def _write_face(st, py_pct, ram_free, verdict):
    row = {"machine_id": MACHINE_ID, "engine": "saturation-engine",
           "version": VERSION, "law_ref": LAW_REF,
           "ts": _now_iso(), "epoch": int(time.time()),
           "py_cpu_pct": py_pct, "engine_alive": True,
           "ram_free_gb": round(ram_free, 1) if ram_free is not None else None,
           "active_burns": [{"batch": b["batch"], "shard": b["shard"],
                             "pid": b.get("pid"),
                             "started_at": b.get("started_at")}
                            for b in st.get("active", [])],
           "queue_depth": len(st.get("queue", [])),
           "shards_done_total": st.get("shards_done_total", 0),
           "last_shard_done_at": st.get("last_shard_done_at"),
           "last_flush_at": st.get("last_flush_at"),
           "verdict": verdict}
    os.makedirs(ENGINE_DIR, exist_ok=True)
    tmp = FACE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(row, f, ensure_ascii=False, indent=1)
    os.replace(tmp, FACE_PATH)
    try:
        with open(HISTORY_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        with open(HISTORY_PATH, encoding="utf-8") as f:
            lines = f.readlines()
        if len(lines) > HISTORY_TAIL:
            with open(HISTORY_PATH, "w", encoding="utf-8") as f:
                f.writelines(lines[-HISTORY_TAIL:])
    except Exception:
        pass
    return row


def _flush_ledger(st, now_epoch):
    """sec.2 async batched ledger append (10-20min or N-shard windows)."""
    if not st.get("ledger_buffer"):
        return 0
    os.makedirs(ENGINE_DIR, exist_ok=True)
    n = 0
    with open(LEDGER_PATH, "a", encoding="utf-8") as f:
        for row in st["ledger_buffer"]:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            n += 1
    st["ledger_buffer"] = []
    st["last_flush_at"] = _now_iso()
    return n


# --- tick -------------------------------------------------------------------

def tick(dry=False):
    t0 = time.time()
    now_epoch = time.time()
    py = _py_cpu_pct()
    ram = _ram_free_gb()
    st = _load_state()

    def done_probe(wave, cfg, shard, nshards):
        return _shard_done(wave, cfg, shard, nshards)

    def pid_alive(pid):
        if not pid:
            return False
        try:
            import psutil
            p = psutil.Process(int(pid))
            return p.is_running() and p.status() != psutil.STATUS_ZOMBIE
        except Exception:
            return False

    # sec.4 self-derivation from artifacts
    completed, crashed, still = _reap_active(st, pid_alive, done_probe, now_epoch)
    for row in completed:
        st["ledger_buffer"].append(row)
        st["shards_done_total"] = st.get("shards_done_total", 0) + 1
        st["last_shard_done_at"] = row["done_at"]
        _log(f"shard DONE {row['batch']}/{row['key']} "
             f"elapsed={row['elapsed_sec']}s -> ledger buffer "
             f"(n={len(st['ledger_buffer'])})")
    for b in crashed:
        st["crashes"][b["key"]] = st["crashes"].get(b["key"], 0) + 1
        _log(f"burn CRASHED {b['batch']}/{b['key']} pid={b.get('pid')} "
             f"(crashes={st['crashes'][b['key']]}, self-restart next tick)")
    st["active"] = still

    # sec.1 local queue materialization (frozen engine-owned waves only)
    active_keys = {b["key"] for b in st["active"]}
    st["queue"] = _queue_items(n1.WAVE_CONFIGS, done_probe, active_keys,
                               MACHINE_ID)

    # sec.3 + ignite (idle->ignite, zero claim round-trips)
    verdict = "idle"
    skips = []
    while st["queue"] and len(st["active"]) < MAX_ACTIVE_BURNS:
        item = st["queue"][0]
        ok, reasons = _pre_ignition_checks(
            item, n1.WAVE_CONFIGS[item["wave"]],
            os.path.join(PATHS.root, "research",
                         f"PERPETUAL_N1_W{item['wave']}_PREREG.md"),
            PATHS.daily_dir, done_probe, st.get("crashes", {}))
        if not ok:
            st["queue"].pop(0)
            skips.append({"key": item["key"], "reasons": reasons})
            _log(f"PreIgnitionChecks SKIP {item['key']}: {'; '.join(reasons)}")
            continue
        gate_ok, gate_reason = _ignite_ok(py, len(st["active"]), ram)
        if not gate_ok:
            verdict = f"gate:{gate_reason}"
            break
        if dry:
            verdict = f"dry_launch:{item['key']}"
            break
        os.makedirs(LOG_DIR, exist_ok=True)
        logf = os.path.join(LOG_DIR, f"{item['batch']}-{item['shard']}.log")
        cmd = [sys.executable,
               os.path.join(PATHS.root, item["runner"])] + item["runner_args"]
        with open(logf, "a", encoding="utf-8") as lf:
            p = subprocess.Popen(cmd, cwd=PATHS.root, stdout=lf,
                                 stderr=subprocess.STDOUT,
                                 creationflags=DETACHED, close_fds=True)
        try:
            import psutil
            psutil.Process(p.pid).nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        except Exception:
            pass
        try:                                  # core-spread sampler rides
            subprocess.Popen(                  # every launch (O-2355 law-2)
                [sys.executable, os.path.join(PATHS.root, "Tools",
                                              "core_sampler.py"),
                 str(p.pid), item["batch"], item["key"]],
                cwd=PATHS.root, creationflags=DETACHED, close_fds=True)
        except Exception as ex:
            _log(f"core-sampler spawn fault (non-fatal): {ex}")
        st["active"].append({"face": "N1", "wave": item["wave"],
                             "shard": item["shard"], "nshards": item["nshards"],
                             "key": item["key"], "batch": item["batch"],
                             "pid": p.pid, "started_at": _now_iso(),
                             "started_epoch": int(time.time()),
                             "log": logf,
                             "cfg": n1.WAVE_CONFIGS[item["wave"]]})
        st["queue"].pop(0)
        verdict = f"ignited:{item['key']} pid={p.pid}"
        _log(f"IGNITE {item['batch']}/{item['key']} pid={p.pid} "
             f"workers={WORKERS} py={py}% ram={ram and round(ram, 1)}GB "
             f"queue_left={len(st['queue'])}")
        break                                  # v0.1: one burn per tick cycle

    # sec.2 batched ledger flush (window opens when the first row buffers)
    if st.get("ledger_buffer") and st.get("last_flush_at") is None:
        st["last_flush_at"] = _now_iso()
    if st.get("last_flush_at"):
        try:
            mins = (now_epoch - time.mktime(time.strptime(
                st["last_flush_at"][:19], "%Y-%m-%dT%H:%M:%S"))) / 60.0
        except Exception:
            mins = LEDGER_FLUSH_MIN + 1
    else:
        mins = 0.0
    if _flush_due(len(st.get("ledger_buffer", [])), mins):
        n = _flush_ledger(st, now_epoch)
        _log(f"ledger FLUSH {n} rows (batched, sec.2)")
        verdict += f" ledger_flush={n}"

    st["skips"] = skips
    st["last_tick"] = {"ts": _now_iso(), "epoch": int(now_epoch),
                       "py_cpu_pct": py, "ram_free_gb": ram,
                       "verdict": verdict,
                       "active_n": len(st["active"]),
                       "queue_depth": len(st.get("queue", [])),
                       "elapsed_sec": round(time.time() - t0, 1)}
    _save_state(st)
    face = _write_face(st, py, ram, verdict)
    print(json.dumps({"tick": st["last_tick"],
                      "face_epoch": face["epoch"],
                      "shards_done_total": st["shards_done_total"],
                      "ledger_buffer_n": len(st["ledger_buffer"])},
                     ensure_ascii=False))
    return 0


def status():
    """Round-zero engine-alive check (law sec.4 / T-141 s3): exit 0 =
    alive (heartbeat fresh), exit 1 = DEAD -> same-round P0 repair."""
    if not os.path.exists(STATE_PATH):
        print(json.dumps({"engine_alive": False, "machine_id": MACHINE_ID,
                          "reason": "no state file (engine never ticked)"},
                         ensure_ascii=False))
        return 1
    try:
        with open(STATE_PATH, encoding="utf-8") as f:
            st = json.load(f)
    except Exception as ex:
        print(json.dumps({"engine_alive": False, "machine_id": MACHINE_ID,
                          "reason": f"state unreadable: {ex}"},
                         ensure_ascii=False))
        return 1
    lt = st.get("last_tick") or {}
    age = None
    if lt.get("epoch"):
        age = round(time.time() - int(lt["epoch"]), 0)
    alive = age is not None and age <= HEARTBEAT_STALE_S
    out = {"engine_alive": bool(alive), "machine_id": MACHINE_ID,
           "heartbeat_age_sec": age, "py_cpu_pct": lt.get("py_cpu_pct"),
           "active_burns": [f"{b['batch']}/{b['key']} pid={b.get('pid')}"
                            for b in st.get("active", [])],
           "queue_depth": len(st.get("queue", [])),
           "shards_done_total": st.get("shards_done_total", 0),
           "last_verdict": lt.get("verdict"),
           "law_ref": LAW_REF}
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0 if alive else 1


def selftest():
    import tempfile
    tmp = tempfile.mkdtemp(prefix="_satengine_st_")

    # 1. sec.1 queue generator: owner filter + done/active exclusions
    fake_cfgs = {2: {"batch": "POOL-ERA", "prereg": "x",
                     "a_seed_base": 1, "b_exit_seed_base": 1,
                     "shard_subdir": "n1_poolera", "out_name": "x.json"},
                 10: {"batch": "PERPETUAL-N1-W10", "prereg": "x",
                      "a_seed_base": 34_100, "b_exit_seed_base": 28_700,
                      "shard_subdir": "n1_w10", "out_name": "x.json",
                      "engine_owner": "bm-b"},
                 11: {"batch": "OTHER-MACHINE", "prereg": "x",
                      "a_seed_base": 1, "b_exit_seed_base": 1,
                      "shard_subdir": "n1_w11", "out_name": "x.json",
                      "engine_owner": "bm-a"}}
    done = set()
    probe = lambda w, c, s, n: (w, s) in done
    q = _queue_items(fake_cfgs, probe, set(), "bm-b", nshards=12)
    assert len(q) == 12, "queue must hold the 12 shards of the owned wave"
    assert all(i["wave"] == 10 for i in q), "pool-era/other-owner waves invisible"
    assert q[0]["runner_args"] == ["run", "--shard", "0", "--of", "12",
                                   "--wave", "10", "--workers", "8"], \
        "runner args face drift"
    done.add((10, 0)); done.add((10, 5))
    q = _queue_items(fake_cfgs, probe, {"n1w10-3of12"}, "bm-b", nshards=12)
    assert len(q) == 9, "done + active shards must be excluded (12-2-1)"
    assert "n1w10-0of12" not in [i["key"] for i in q] \
        and "n1w10-3of12" not in [i["key"] for i in q], "exclusion drift"
    done.update((10, s) for s in range(12))
    q = _queue_items(fake_cfgs, probe, set(), "bm-b", nshards=12)
    assert q == [], "fully burned wave = honest empty queue"

    # 2. sec.3 PreIgnitionChecks fail-closed (r316)
    daily = os.path.join(tmp, "daily")
    os.makedirs(daily, exist_ok=True)
    prereg = os.path.join(tmp, "PERPETUAL_N1_W10_PREREG.md")
    item = {"wave": 10, "shard": 0, "nshards": 12, "key": "n1w10-0of12",
            "batch": "PERPETUAL-N1-W10"}
    ok, reasons = _pre_ignition_checks(
        item, fake_cfgs[10], prereg, daily, lambda *a: False, {})
    assert not ok and any("prereg missing" in r for r in reasons), \
        "missing prereg must fail-closed"
    open(prereg, "w", encoding="utf-8").write("prereg")
    ok, reasons = _pre_ignition_checks(
        item, fake_cfgs[10], prereg, daily, lambda *a: False, {})
    assert not ok and any("panel face short" in r for r in reasons), \
        "short panel must fail-closed"
    for i in range(48):
        open(os.path.join(daily, f"{600_000 + i}.csv"), "w").write("date,close")
    ok, reasons = _pre_ignition_checks(
        item, fake_cfgs[10], prereg, daily, lambda *a: False, {})
    assert ok and not reasons, "all-present case must admit"
    ok, reasons = _pre_ignition_checks(
        item, fake_cfgs[10], prereg, daily, lambda *a: True, {})
    assert not ok and any("presence=done" in r for r in reasons), \
        "valid checkpoint must refuse re-ignite (r488)"
    ok, reasons = _pre_ignition_checks(
        item, fake_cfgs[11], prereg, daily, lambda *a: False, {})
    assert not ok and any("engine-owned" in r for r in reasons), \
        "non-owned wave must fail-closed"
    ok, reasons = _pre_ignition_checks(
        item, fake_cfgs[10], prereg, daily, lambda *a: False,
        {"n1w10-0of12": CRASH_QUARANTINE})
    assert not ok and any("quarantine" in r for r in reasons), \
        "crash-quarantined shard must fail-closed (sec.4 backoff)"

    # 3. real validator face: crafted W10 checkpoint vs n1._shard_valid
    ck = os.path.join(tmp, "shard-0-of-12.json")
    a_lo, a_hi = 0, 2000 // 12
    b_lo, b_hi = 0, 200 // 12
    json.dump({"batch": "PERPETUAL-N1-W10", "shard": 0, "nshards": 12,
               "a_range": [a_lo, a_hi], "b_range": [b_lo, b_hi],
               "families": {"A_random_engine_exit": {"n": a_hi - a_lo,
                                                     "runs": [{}] * (a_hi - a_lo)},
                            "B_random_entry_random_exit": {
                                "n": b_hi - b_lo,
                                "runs": [{}] * (b_hi - b_lo)}}},
              open(ck, "w", encoding="utf-8"))
    n1._set_wave(10)
    try:
        assert n1._shard_valid(ck, 0, 12), "crafted valid W10 ckpt must pass"
    finally:
        n1._set_wave(2)
    bad = os.path.join(tmp, "shard-1-of-12.json")
    json.dump({"batch": "PERPETUAL-N1-W10", "shard": 1, "nshards": 12,
               "a_range": [a_hi, 2 * a_hi], "b_range": [b_hi, 2 * b_hi],
               "families": {"A_random_engine_exit": {"n": 1, "runs": [{}]},
                            "B_random_entry_random_exit": {"n": 1,
                                                           "runs": [{}]}}},
              open(bad, "w", encoding="utf-8"))
    n1._set_wave(10)
    try:
        assert not n1._shard_valid(bad, 1, 12), \
            "short-count ckpt must fail (presence=done is earned)"
    finally:
        n1._set_wave(2)

    # 4. sec.2 batched flush gate boundaries
    assert not _flush_due(0, 999), "empty buffer never flushes"
    assert not _flush_due(1, 5), "1 row at 5min must batch (not yet due)"
    assert _flush_due(1, 20), "1 row at 20min must flush (window band)"
    assert _flush_due(3, 0), "3 rows flush immediately (N-shard trigger)"
    assert _flush_due(2, 15), "2 rows at 15min flush (window midpoint)"

    # 5. ignite gate boundaries (headroom + RAM floor)
    assert _ignite_ok(10.0, 0, 8.0)[0], "idle machine must ignite"
    assert not _ignite_ok(80.0, 0, 8.0)[0], "py above ceiling must hold"
    assert not _ignite_ok(10.0, 1, 8.0)[0], "active cap must hold"
    assert not _ignite_ok(10.0, 0, 2.0)[0], "RAM floor must hold"
    assert _ignite_ok(None, 0, None)[0], "unknown probes = honest ignite"

    # 6. sec.4 self-derivation: artifacts decide, never belief
    st = {"active": [{"face": "N1", "wave": 10, "shard": 0, "nshards": 12,
                      "key": "n1w10-0of12", "batch": "PERPETUAL-N1-W10",
                      "pid": 999999, "started_at": "x",
                      "started_epoch": 100, "cfg": n1.WAVE_CONFIGS[10]},
                     {"face": "N1", "wave": 10, "shard": 1, "nshards": 12,
                      "key": "n1w10-1of12", "batch": "PERPETUAL-N1-W10",
                      "pid": 999998, "started_at": "x",
                      "started_epoch": 100, "cfg": n1.WAVE_CONFIGS[10]}],
          "crashes": {}}
    done2 = {"n1w10-0of12"}
    probe2 = lambda w, c, s, n: f"n1w{w}-{s}of{n}" in done2
    completed, crashed, still = _reap_active(
        st, lambda pid: False, probe2, 200)
    assert len(completed) == 1 and completed[0]["key"] == "n1w10-0of12", \
        "valid ckpt (dead pid) = completed from artifact"
    assert len(crashed) == 1 and crashed[0]["key"] == "n1w10-1of12", \
        "dead pid + no ckpt = crash (self-restart next tick)"
    assert still == [], "no live pids in fixture"
    assert completed[0]["elapsed_sec"] == 100.0, "elapsed derive"

    # 7. real W10 face: wave row present + prereg on tree
    cfg = n1.WAVE_CONFIGS[10]
    assert cfg.get("engine_owner") == "bm-b", "W10 engine_owner drift"
    assert os.path.exists(os.path.join(
        PATHS.root, "research", "PERPETUAL_N1_W10_PREREG.md")), \
        "W10 prereg missing (engine queue would be a lie)"
    assert os.path.exists(os.path.join(PATHS.root, "firm",
                                       "SATURATION_ENGINE_LAW.md")), \
        "law file missing"
    print("selftest: PASS (7 legs: queue generator owner/done/active "
          "exclusions + PreIgnitionChecks fail-closed [prereg/panel/"
          "presence/quarantine/owner] + real W10 ckpt validator face + "
          "sec.2 batched flush gate + ignite headroom/RAM gates + sec.4 "
          "artifact self-derivation [completed/crash] + law/prereg "
          "presence)")
    return 0


def main():
    argv = sys.argv[1:]
    if "selftest" in argv:
        return selftest()
    if "status" in argv:
        return status()
    if "tick" in argv or not argv:
        return tick(dry="--dry" in argv)
    print(__doc__)
    print("usage: tick [--dry] | status | selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main())
