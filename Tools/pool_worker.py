#!/usr/bin/env python
"""BigMoney pool worker -- T-113 s2, CEO order O-20260928-2210 compute sharing.

Standalone cross-company worker client. ZERO loop dependency: any
adequate machine (fleet machine OR an onboarded external worker such as
BG-B/BG-C) can run this; it only needs a git clone of this repo and a
python with the repo's runtime requirements installed.

Cycle (single pass; the schtask "Bigmoney-PoolWorker" fires this every
N minutes -- silent VBS launcher, BelowNormal priority, single instance
via PID lock):

  1. fetch origin; read the freshest runnable_pool.json
  2. scan READY entries -> claimable shards:
       - entry.status == "ready" (waiting batches wait for THEIR deps,
         workers never touch waiting)
       - worker_class eligibility (O-2210 data-locality honesty):
         self-contained -> any machine; bm-hosted -> only the lane host
       - shard not done
       - no fresh external claim file (claim-by-file first-writer-wins,
         results/pool_claims/<entry>/<shard>.<machine>.json)
       - no fresh pool-side owner (fleet autofill claim -- the pool's
         owner field is transient but a FRESH one is respected)
  3. claim-by-file: write OUR claim file + git push it. Workers NEVER
     write runnable_pool.json (pool single-writer law untouched).
  4. run entry.runner as a subprocess at BelowNormal priority, with a
     background heartbeat thread refreshing the claim file every 5 min
     (stale > 20 min = another machine may lawfully take over, fleet law).
  5. on finish: claim state=closed (outcome ok|fail) + result_ref,
     append a capacity-ledger row to results/pool_worker_ledger.jsonl
     ({machine_id, entry, shard, started, duration_sec, cores,
     core_hours} = BigCompute monthly shared-compute KPI face),
     git push everything (claim + ledger + runner result artifacts).
  6. the POOL-SIDE harvest flip (shard done) is consumed by the fleet
     (autofill/round harvest reads closed claims as owner truth) --
     workers stay zero-write on the pool.

Exit codes: 0 = normal (ran or nothing claimable), 2 = mechanism fault
(report as-is, never mask). selftest subcommand = offline hermetic
check (zero network, zero git).
"""
import ctypes
import json
import os
import subprocess
import sys
import threading
import time
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POOL = os.path.join(ROOT, "results", "runnable_pool.json")
CLAIMS = os.path.join(ROOT, "results", "pool_claims")
LEDGER = os.path.join(ROOT, "results", "pool_worker_ledger.jsonl")
MACHINES_DIR = os.path.join(ROOT, "fleet", "machines")
STALE_MIN = 20.0          # fleet law: claim stale > 20 min = takeable
HEARTBEAT_SEC = 300.0     # claim heartbeat cadence (well under STALE_MIN)
BELOW_NORMAL = 0x00004000  # win32 BELOW_NORMAL_PRIORITY_CLASS


def _now_iso():
    # Company heartbeat convention (T-04 F5): ISO 8601 with UTC offset.
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _age_min(ts):
    """Age in minutes of an ISO-or-legacy ts; None if unparseable."""
    if not ts:
        return None
    try:
        s = str(ts)
        if "T" in s:
            dt = datetime.fromisoformat(s)
            now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
        else:
            dt = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
            now = datetime.now()
        return (now - dt).total_seconds() / 60.0
    except Exception:
        return None


def _machine_id():
    try:
        with open(os.path.join(ROOT, "fleet", "machine.json"),
                  encoding="utf-8") as fh:
            return str(json.load(fh).get("machine_id") or os.environ.get(
                "COMPUTERNAME", "unknown"))
    except Exception:
        return os.environ.get("COMPUTERNAME", "unknown")


def _git(args):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True)
    return r.returncode, (r.stderr or b"").decode(errors="replace")[:200]


def _log(msg):
    print(f"[pool_worker {datetime.now().strftime('%H:%M:%S')}] {msg}",
          flush=True)


def _pid_lock(myid):
    """Single-instance guard: one pool_worker per machine."""
    lockf = os.path.join(ROOT, "results", f"pool_worker_lock.{myid}.json")
    if os.path.exists(lockf):
        try:
            with open(lockf, encoding="utf-8") as fh:
                pid = int(json.load(fh).get("pid", 0))
            if os.name == "nt":
                k32 = ctypes.windll.kernel32
                h = k32.OpenProcess(0x1000, 0, pid)  # PROCESS_QUERY_LIMITED
                if h:
                    k32.CloseHandle(h)
                    return False, lockf  # alive holder -> single instance
            elif pid != os.getpid():
                return False, lockf
        except Exception:
            pass  # corrupt lock -> overwrite (fail-open, stale lock is a wedge)
    with open(lockf, "w", encoding="utf-8") as fh:
        json.dump({"pid": os.getpid(), "ts": _now_iso()}, fh)
    return True, lockf


def _fleet_hb_age_min(machine_id):
    """Age of a fleet machine's heartbeat last_seen (fleet/machines/
    <id>.json, mirrored via git); None if absent/unparseable. Mirrors
    autofill._hb_age_min law: r178/r163 -- a machine mid-long-round
    only heartbeats at round end, so heartbeat alone misreads a live
    owner; callers combine with the claim-stamp (min of both)."""
    path = os.path.join(MACHINES_DIR, str(machine_id) + ".json")
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            ls = str(json.load(fh).get("last_seen"))
        return _age_min(ls)
    except Exception:
        return None


def _owner_age_min(owner, shard):
    """Effective owner freshness = freshest of heartbeat / claim-stamp
    (autofill _owner_age_min parity -- same-machine takeover law)."""
    ages = [a for a in (_fleet_hb_age_min(owner),
                        _age_min(shard.get("owner_since")))
            if a is not None]
    return min(ages) if ages else None


def _claim_path(entry_id, shard_key, machine):
    return os.path.join(CLAIMS, str(entry_id).replace("/", "_"),
                        f"{str(shard_key).replace('/', '_')}.{machine}.json")


def _claim_dir(entry_id):
    return os.path.join(CLAIMS, str(entry_id).replace("/", "_"))


def _shard_claim_age_min(entry_id, shard_key):
    """Freshest heartbeat age among OTHER machines' claim files for this
    shard (None = no external claim). closed-ok claims count as occupied
    (awaiting pool harvest flip); failed claims do not (let fleet take)."""
    d = _claim_dir(entry_id)
    if not os.path.isdir(d):
        return None
    pref = str(shard_key).replace("/", "_") + "."
    best = None
    for fn in os.listdir(d):
        if not (fn.startswith(pref) and fn.endswith(".json")):
            continue
        try:
            with open(os.path.join(d, fn), encoding="utf-8") as fh:
                c = json.load(fh)
            st = c.get("state")
            if st == "closed" and c.get("outcome") == "ok":
                hb = c.get("closed_at") or c.get("heartbeat")
            elif st == "failed":
                continue  # honest fail frees the shard for takeover
            else:
                hb = c.get("heartbeat")
            age = _age_min(hb)
            if age is None:
                continue
            if best is None or age < best:
                best = age
        except Exception:
            continue
    return best


def _claim_age_min_local(entry_id, shard_key, machine):
    """Age of OUR OWN claim file heartbeat; None if absent/closed."""
    p = _claim_path(entry_id, shard_key, machine)
    if not os.path.exists(p):
        return None
    try:
        with open(p, encoding="utf-8") as fh:
            c = json.load(fh)
        if c.get("state") in ("closed", "failed"):
            return None
        return _age_min(c.get("heartbeat"))
    except Exception:
        return None


def _write_claim(entry_id, shard_key, machine, state, extra=None):
    p = _claim_path(entry_id, shard_key, machine)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    c = {"machine_id": machine, "state": state,
         "pid": os.getpid(), "heartbeat": _now_iso()}
    if extra:
        c.update(extra)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(c, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, p)
    return p


def _eligible(entry, myid):
    """O-2210 worker_class data-locality eligibility."""
    wc = entry.get("worker_class", "self-contained")
    if wc == "self-contained":
        return True
    if wc == "bm-hosted":
        return entry.get("lane_owner") == myid
    _log(f"entry {entry['id']}: unknown worker_class {wc!r} -> skip")
    return False


def _scan(pool, myid):
    """Best ready, worker_class-eligible, claim-free, owner-free shard."""
    entries = [e for e in pool.get("entries", [])
               if e.get("status") == "ready" and e.get("runner")]
    entries.sort(key=lambda e: e.get("priority", 99))
    for e in entries:
        if not _eligible(e, myid):
            continue
        for sh in e.get("shards", []):
            if sh.get("status") == "done":
                continue
            ow = sh.get("owner")
            if ow:
                # fresh pool owner = occupied, INCLUDING our own machine:
                # the host's autofill tick may have claimed it -- same
                # machine must not double-burn (yield to any fresh owner).
                # Heartbeat + claim-stamp dual face (autofill parity).
                age = _owner_age_min(ow, sh)
                if age is not None and age < STALE_MIN:
                    continue
            if _shard_claim_age_min(e["id"], sh["key"]) is not None:
                continue  # fresh external claim-by-file -> yield
            return e, sh
    return None, None


class _Heartbeat(threading.Thread):
    """Refresh our claim file heartbeat while the runner burns."""
    def __init__(self, entry_id, shard_key, machine):
        super().__init__(daemon=True)
        self.entry_id, self.shard_key, self.machine = entry_id, shard_key, machine
        self.stop_flag = threading.Event()

    def run(self):
        while not self.stop_flag.wait(HEARTBEAT_SEC):
            try:
                _write_claim(self.entry_id, self.shard_key, self.machine,
                             "running")
            except Exception:
                pass  # heartbeat fail-soft: worst case = stale takeover


def _ledger_row(machine, entry_id, shard_key, started, duration_sec, rc):
    row = {
        "machine_id": machine, "entry": entry_id, "shard": shard_key,
        "started": started, "duration_sec": round(duration_sec, 1),
        "cores": os.cpu_count() or 1,
        "core_hours": round((os.cpu_count() or 1) * duration_sec / 3600.0, 4),
        "exit_code": rc, "ts": _now_iso(),
    }
    with open(LEDGER, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def _push_claims_and_ledger(myid, note):
    """git add claims+ledger ONLY -> commit+push. Deliberately does NOT
    sweep other results/ dirt: runner artifacts stay in the tree for the
    POOL-SIDE harvest face (fleet round/autofill consumes the closed
    claim, then commits the artifacts with proper round bookkeeping) --
    a worker swallowing unrelated in-flight results state is the r398
    dirty-tree hazard family. Push lost to origin movement -> ONE pull
    --rebase + push retry, then leave the local commit standing (next
    pass re-pushes, r199 spirit)."""
    _git(["add", "results/pool_claims", "results/pool_worker_ledger.jsonl"])
    rc, err = _git(["commit", "-m",
                    f"pool_worker {myid}: {note} [claim-by-file O-2210]"])
    if "nothing to commit" in err:
        return True
    rc, err = _git(["push", "origin", "main"])
    if rc != 0:
        rc2, _ = _git(["pull", "--rebase"])
        if rc2 != 0:
            _git(["rebase", "--abort"])
            _log("push refused + rebase conflict -> local commit stands, "
                 "next pass retries (zero loss)")
            return False
        rc, err = _git(["push", "origin", "main"])
        if rc != 0:
            _log(f"push retry refused ({err}) -> local commit stands")
            return False
    return True


def run_pass(dry=False):
    myid = _machine_id()
    ok, lockf = _pid_lock(myid)
    if not ok:
        _log("another pool_worker instance holds the lock -> exit")
        return 0
    _git(["fetch", "origin"])
    with open(POOL, encoding="utf-8") as fh:
        pool = json.load(fh)
    e, sh = _scan(pool, myid)
    if not e:
        _log("nothing claimable (pool fresh-read)")
        _push_claims_and_ledger(myid, "pass no-op sweep")  # retry pending pushes
        return 0
    entry_id, shard_key = e["id"], sh["key"]
    if dry:
        _log(f"DRY: would claim {entry_id}/{shard_key}")
        return 0
    # claim-by-file: first-writer-wins on our own file's existence
    if _claim_age_min_local(entry_id, shard_key, myid) is not None:
        _log(f"our claim on {entry_id}/{shard_key} is fresh -> re-own")
    _write_claim(entry_id, shard_key, myid, "claimed",
                 {"started": _now_iso()})
    _push_claims_and_ledger(myid, f"claim {entry_id}/{shard_key}")
    started_ts = _now_iso()
    t0 = time.time()
    hb = _Heartbeat(entry_id, shard_key, myid)
    hb.start()
    cmd = [sys.executable, os.path.join(ROOT, e["runner"]), *e.get("runner_args", [])]
    _log(f"RUN {entry_id}/{shard_key}: {' '.join(cmd[1:])}")
    try:
        p = subprocess.Popen(cmd, cwd=ROOT)
        if os.name == "nt" and hasattr(p, "_handle"):
            try:
                ctypes.windll.kernel32.SetPriorityClass(
                    int(p._handle), BELOW_NORMAL)
            except Exception:
                pass  # priority is best-effort, never fatal
        rc = p.wait()
    finally:
        hb.stop_flag.set()
    dur = time.time() - t0
    outcome = "ok" if rc == 0 else "fail"
    _write_claim(entry_id, shard_key, myid, "closed",
                 {"outcome": outcome, "exit_code": rc,
                  "started": started_ts, "closed_at": _now_iso(),
                  "result_ref": f"runner rc={rc} (artifacts in results/)"})
    _ledger_row(myid, entry_id, shard_key, started_ts, dur, rc)
    _log(f"closed {entry_id}/{shard_key} outcome={outcome} "
         f"({dur:.0f}s) -> push")
    _push_claims_and_ledger(
        myid, f"close {entry_id}/{shard_key} outcome={outcome}")
    return 0


def selftest():
    """Offline hermetic selftest: zero network, zero git, zero pool writes."""
    import shutil, tempfile
    tmp = tempfile.mkdtemp(prefix="poolworker_st_")
    okc = [0]
    failc = [0]

    def ok(name, cond):
        if cond:
            okc[0] += 1
        else:
            failc[0] += 1
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
        return cond

    try:
        # S1 ts roundtrip + age
        ts = _now_iso()
        ok("S1 now_iso parses + age>=0", (_age_min(ts) or -1) >= 0)
        ok("S2 legacy ts parses", _age_min("2026-09-28 23:00:00") is not None)
        ok("S3 garbage ts -> None", _age_min("not-a-ts") is None)
        # S4 eligibility
        e_sc = {"id": "X1", "worker_class": "self-contained", "shards": []}
        e_bm = {"id": "X2", "worker_class": "bm-hosted",
                "lane_owner": "bm-b", "shards": []}
        ok("S4 self-contained any machine", _eligible(e_sc, "bg-b"))
        ok("S5 bm-hosted host match", _eligible(e_bm, "bm-b"))
        ok("S6 bm-hosted non-host refused", not _eligible(e_bm, "bg-b"))
        # S7 scan respects worker_class + done + fresh owner
        pool = {"entries": [
            {"id": "A", "status": "ready", "runner": "scripts/x.py",
             "priority": 1, "worker_class": "bm-hosted",
             "lane_owner": "bm-b",
             "shards": [{"key": "s0", "status": "ready", "owner": None}]},
            {"id": "B", "status": "ready", "runner": "scripts/y.py",
             "priority": 2, "worker_class": "self-contained",
             "shards": [{"key": "s1", "status": "done"},
                        {"key": "s2", "status": "ready",
                         "owner": "bm-c",
                         "owner_since": _now_iso()}]},
            {"id": "C", "status": "ready", "runner": "scripts/z.py",
             "priority": 3, "worker_class": "self-contained",
             "shards": [{"key": "s3", "status": "ready", "owner": None}]},
        ]}
        e, sh = _scan(pool, "bg-b")
        ok("S7 scan skips bm-hosted+done+fresh-owner -> lands C/s3",
           e and e["id"] == "C" and sh["key"] == "s3")
        # S8 claim-by-file first-writer-wins + failed-free + closed-ok block
        global CLAIMS
        real_claims = CLAIMS
        CLAIMS = os.path.join(tmp, "pool_claims")
        d = os.path.join(CLAIMS, "C")
        os.makedirs(d, exist_ok=True)
        rival = os.path.join(d, "s3.bg-z.json")
        with open(rival, "w", encoding="utf-8") as fh:
            json.dump({"machine_id": "bg-z", "state": "running",
                       "heartbeat": _now_iso()}, fh)
        ok("S8 fresh rival claim blocks", _shard_claim_age_min("C", "s3") is not None)
        with open(rival, "w", encoding="utf-8") as fh:
            json.dump({"machine_id": "bg-z", "state": "failed",
                       "heartbeat": _now_iso()}, fh)
        ok("S9 failed claim frees shard", _shard_claim_age_min("C", "s3") is None)
        with open(rival, "w", encoding="utf-8") as fh:
            json.dump({"machine_id": "bg-z", "state": "closed",
                       "outcome": "ok", "closed_at": _now_iso()},
                      fh)
        ok("S10 closed-ok blocks (awaiting harvest)", _shard_claim_age_min("C", "s3") is not None)
        # S11 our-claim age
        _write_claim("C", "s9", "bg-b", "running")
        ok("S11 own claim heartbeat fresh", (_claim_age_min_local("C", "s9", "bg-b") or 99) < 1)
        # S12 ledger row shape
        global LEDGER
        real_ledger = LEDGER
        LEDGER = os.path.join(tmp, "ledger.jsonl")
        row = _ledger_row("bg-b", "C", "s9", started=_now_iso(),
                          duration_sec=61.0, rc=0)
        lines = [json.loads(x) for x in open(LEDGER, encoding="utf-8")]
        ok("S12 ledger row appended with required keys",
           lines and all(k in lines[-1] for k in
                         ("machine_id", "entry", "shard", "started",
                          "duration_sec", "cores", "core_hours")))
        ok("S13 core_hours math (rounded face)",
           abs(row["core_hours"] -
               round(row["cores"] * row["duration_sec"] / 3600.0, 4)) < 1e-9)
        CLAIMS = real_claims
        LEDGER = real_ledger
        allp = failc[0] == 0
        print(f"SELFTEST {'ALL PASS' if allp else 'HAS FAIL'} "
              f"({okc[0]} pass / {failc[0]} fail)")
        return 0 if allp else 2
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    # pythonw (windowless) guard: sys.stdout is None under pythonw and a
    # bare print would crash the worker -- route to devnull instead.
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w")
        sys.stderr = open(os.devnull, "w")
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    if len(sys.argv) > 1 and sys.argv[1] == "--dry":
        sys.exit(run_pass(dry=True))
    sys.exit(run_pass())
