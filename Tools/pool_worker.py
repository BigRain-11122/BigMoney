#!/usr/bin/env python
"""BigMoney pool worker -- T-113 s2, CEO order O-20260928-2210 compute sharing.

Standalone cross-company worker client. ZERO loop dependency: any
adequate machine (fleet machine OR an onboarded external worker such as
BG-B/BG-C) can run this; it only needs a git clone of this repo and a
python with the repo's runtime requirements installed.

Cycle (single pass; the schtask "Bigmoney-PoolWorker" fires this every
N minutes -- silent VBS launcher, BelowNormal priority, single instance
via PID lock):

  1. mid-git-op guard (D-20260928-02): another session mid-rebase/merge
     or a live index.lock -> honest defer, zero git faces touched
  2. fetch origin; read the freshest runnable_pool.json
  3. scan READY entries -> claimable shards:
       - entry.status == "ready" (waiting batches wait for THEIR deps,
         workers never touch waiting)
       - worker_class eligibility (O-2210 data-locality honesty):
         self-contained -> any machine; bm-hosted -> only the lane host
       - shard not done
       - no fresh external claim file (claim-by-file first-writer-wins,
         results/pool_claims/<entry>/<shard>.<machine>.json)
       - no fresh pool-side owner (fleet autofill claim -- the pool's
         owner field is transient but a FRESH one is respected)
  4. claim-by-file: write OUR claim file + git push it. Pre-claim, the
     ORIGIN claims face is read (T-115): a rival's fresh/closed claim on
     origin that our fetch-stale local dir missed = honest skip (r406
     grid-0of1 duplicate-burn fix). Workers NEVER
     write runnable_pool.json (pool single-writer law untouched).
  5. run entry.runner as a subprocess at BelowNormal priority, with a
     background heartbeat thread refreshing the claim file every 5 min
     (stale > 20 min = another machine may lawfully take over, fleet law).
  6. on finish: claim state=closed (outcome ok|fail) + result_ref,
     append a capacity-ledger row to results/pool_worker_ledger.jsonl
     ({machine_id, entry, shard, started, duration_sec, cores,
     core_hours} = BigCompute monthly shared-compute KPI face),
     git push everything (claim + ledger + runner result artifacts).
  7. the POOL-SIDE harvest flip (shard done) is consumed by the fleet
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


def _mid_git_op(root=None):
    """D-20260928-02 fleet law: mid-rebase/merge marker or a live git
    index.lock -> this background self-committer defers its git-write
    face (tick x round-session rebase race family, r331 bm-b evidence;
    parity with autofill r201 guard + resident_dispatcher index.lock
    leg). Structural markers only -- a stale lock is maintenance work
    for the fleet round, never bulldozed by a worker."""
    gd = os.path.join(root or ROOT, ".git")
    for marker in ("rebase-merge", "rebase-apply", "MERGE_HEAD",
                   "index.lock"):
        if os.path.exists(os.path.join(gd, marker)):
            return marker
    return None


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


def _origin_claims_verdict(entry_id, shard_key, myid, root=None,
                           ref="origin/main"):
    """T-115 (r406 grid-0of1 duplicate-burn): read the ORIGIN claims
    face for this shard BEFORE claiming. The local claims dir can be
    fetch-stale (bm-a 01:07 re-claim vs bm-c 01:02 claim+close already
    on origin); rival declarations live in git, so origin is the truth
    face. Returns (verdict, detail), verdict in:
      occupied-fresh   rival claim heartbeat < STALE_MIN -> yield
      occupied-closed  rival closed-ok -> yield (tick flips the pool)
      takeover         every rival claim stale > STALE_MIN -> allowed
      free             no rival claim sighted (absent dir is not a
                       fault); gate fault degrades to free with the
                       fault in detail (claim-by-file push still locks)
    Classification mirrors _shard_claim_age_min local law exactly
    (failed frees; closed-ok occupies; heartbeat freshness decides) --
    a semantic split between the two faces would re-create the
    duplicate-burn through the back door."""
    try:
        r = subprocess.run(
            ["git", "ls-tree", ref,
             f"results/pool_claims/{str(entry_id).replace('/', '_')}/",
             "--name-only"],
            cwd=root or ROOT, capture_output=True)
        if r.returncode != 0:
            return "free", f"ls-tree fault ({ref}) -- degraded"
        pref = str(shard_key).replace("/", "_") + "."
        rivals = []
        for line in r.stdout.decode(errors="replace").splitlines():
            base = os.path.basename(line.strip())
            if not (base.startswith(pref) and base.endswith(".json")):
                continue
            if base[len(pref):-5].strip().lower() == str(myid).lower():
                continue  # own claim file never blocks own (re-own law)
            s = subprocess.run(
                ["git", "show",
                 f"{ref}:results/pool_claims/"
                 f"{str(entry_id).replace('/', '_')}/{base}"],
                cwd=root or ROOT, capture_output=True)
            if s.returncode != 0:
                continue
            try:
                rivals.append(json.loads(s.stdout.decode(errors="replace")))
            except ValueError:
                continue
        if not rivals:
            return "free", "no rival claim files on origin face"
        for c in rivals:
            if c.get("state") == "closed" and c.get("outcome") == "ok":
                return ("occupied-closed",
                        f"rival {c.get('machine_id')} closed-ok -- "
                        f"awaiting pool harvest flip")
        live = []
        for c in rivals:
            if c.get("state") == "failed":
                continue  # honest fail frees the shard (local law parity)
            age = _age_min(c.get("heartbeat") or c.get("closed_at"))
            if age is None:
                continue
            live.append((age, str(c.get("machine_id"))))
        if not live:
            return "free", "rival files all failed/unparseable"
        age, who = min(live)
        if age < STALE_MIN:
            return ("occupied-fresh",
                    f"rival {who} claim fresh ({age:.1f}min)")
        return ("takeover",
                f"rival {who} claim stale ({age:.1f}min > "
                f"{STALE_MIN:.0f}min)")
    except Exception as ex:
        return "free", f"origin-claims gate fault {ex}"


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
    mid = _mid_git_op()
    if mid:
        _log(f"push deferred: mid-git-op ({mid}) -- local files stand, "
             "next pass re-pushes (zero loss)")
        return False
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


def _load_pool(ref="origin/main"):
    """O-2210 item-3 (r404-cont): freshest pool face = ORIGIN blob (pool
    single-writer authority), local file only as fallback. Local-file
    reads caused the r404 duplicate-burn: the worker re-burned a shard
    bm-c had already judged-done on origin because the local copy was
    push-lag stale."""
    r = subprocess.run(["git", "show", f"{ref}:results/runnable_pool.json"],
                       cwd=ROOT, capture_output=True)
    if r.returncode == 0:
        try:
            return json.loads(r.stdout.decode(errors="replace"))
        except ValueError:
            _log("origin pool blob unparseable -> local-file fallback")
    else:
        _log(f"origin pool blob unavailable (ref {ref}) -> local-file fallback")
    with open(POOL, encoding="utf-8") as fh:
        return json.load(fh)


def run_pass(dry=False):
    myid = _machine_id()
    ok, lockf = _pid_lock(myid)
    if not ok:
        _log("another pool_worker instance holds the lock -> exit")
        return 0
    mid = _mid_git_op()
    if mid:
        _log(f"mid-git-op detected ({mid}) -> honest defer, next pass "
             f"retries (D-20260928-02 law)")
        return 0
    _git(["fetch", "origin"])
    pool = _load_pool()
    e, sh = _scan(pool, myid)
    if not e:
        _log("nothing claimable (pool fresh-read)")
        _push_claims_and_ledger(myid, "pass no-op sweep")  # retry pending pushes
        return 0
    entry_id, shard_key = e["id"], sh["key"]
    # D-20260929-02 ② slice-start declaration freeze: the pass already
    # fetched origin above, so the guard reads the post-fetch origin
    # inbox face fresh (fetch=False) -- a rival machine's pending MSG
    # naming this entry = skip the pass entirely ("见声明即冻结");
    # guard fault = honest degrade, claim-by-file locks untouched.
    try:
        import inbox_guard
        freeze, gdetail = inbox_guard.conflict(ROOT, myid, entry_id,
                                               fetch=False)
    except Exception as ex:
        freeze, gdetail = False, f"guard-fault {ex}"
    if freeze:
        _log(f"declaration freeze on {entry_id}: {gdetail} -> skip pass "
             f"(D-20260929-02 ②; declaring machine lands the work)")
        return 0
    if "guard-fault" in gdetail:
        _log(f"inbox-guard degrade on {entry_id}: {gdetail}")
    # T-115: pre-claim ORIGIN claims-face read (the pass fetched origin
    # above, so this reads the post-fetch face). Fresh rival claim ->
    # skip pass; closed-ok -> skip (tick flips the pool); stale rival ->
    # honest takeover; gate fault -> degrade (claim-by-file push locks).
    cverdict, cdetail = _origin_claims_verdict(entry_id, shard_key, myid)
    if cverdict.startswith("occupied"):
        _log(f"origin claims face: {entry_id}/{shard_key} {cverdict} "
             f"({cdetail}) -> skip pass (T-115 law)")
        return 0
    if cverdict == "takeover":
        _log(f"origin claims face: {entry_id}/{shard_key} TAKEOVER "
             f"({cdetail})")
    elif "gate fault" in cdetail or "ls-tree fault" in cdetail:
        _log(f"origin-claims degrade on {entry_id}: {cdetail}")
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
        # S14/S15 origin-blob read face (O-2210 item-3, r404-cont):
        # bogus ref degrades to local-file fallback without crash;
        # real origin/main blob readable as pool face.
        pool_fb = _load_pool(ref="refs/heads/__pw_selftest_bogus__")
        ok("S14 bogus ref -> local-file fallback returns pool",
           isinstance(pool_fb, dict) and len(pool_fb.get("entries", [])) > 0)
        pool_or = _load_pool()
        ok("S15 origin-main blob readable (post-fetch face)",
           isinstance(pool_or, dict) and "entries" in pool_or)
        # S16-S19 D-20260928-02 mid-git-op guard (hermetic fake roots)
        # (renumbered from r188 S14-S17 post-union with r404-cont S14/S15)
        fake = os.path.join(tmp, "fake_repo")
        ok("S16 clean tree -> no marker", _mid_git_op(fake) is None)
        os.makedirs(os.path.join(fake, ".git", "rebase-merge"))
        ok("S17 rebase-merge marker detected",
           _mid_git_op(fake) == "rebase-merge")
        shutil.rmtree(os.path.join(fake, ".git", "rebase-merge"))
        with open(os.path.join(fake, ".git", "MERGE_HEAD"), "w") as fh:
            fh.write("x")
        ok("S18 MERGE_HEAD marker detected",
           _mid_git_op(fake) == "MERGE_HEAD")
        os.remove(os.path.join(fake, ".git", "MERGE_HEAD"))
        with open(os.path.join(fake, ".git", "index.lock"), "w") as fh:
            fh.write("x")
        ok("S19 index.lock detected (live git op -> defer)",
           _mid_git_op(fake) == "index.lock")
        # S20 T-115: pre-claim ORIGIN claims-face gate, hermetic via a
        # throwaway offline git repo read at ref=HEAD (inbox_guard S7
        # pattern): fresh-active blocks / closed-ok blocks / stale ->
        # takeover / failed -> free / own file ignored / absent dir free.
        crepo = os.path.join(tmp, "claims_repo")
        os.makedirs(os.path.join(crepo, "results", "pool_claims", "G"))
        cdir = os.path.join(crepo, "results", "pool_claims", "G")

        def _cw(fn, obj):
            with open(os.path.join(cdir, fn), "w", encoding="utf-8") as fh:
                json.dump(obj, fh)

        def _cc():
            subprocess.run(["git", "add", "-A"], cwd=crepo,
                           capture_output=True)
            subprocess.run(["git", "-c", "user.email=st@t", "-c",
                            "user.name=st", "commit", "-qm", "st"],
                           cwd=crepo, capture_output=True)

        r = subprocess.run(["git", "init", "-q"], cwd=crepo,
                           capture_output=True)
        ok("S20a tmp git init", r.returncode == 0)
        if r.returncode == 0:
            from datetime import timedelta
            _cw("grid-0of1.bm-c.json",
                {"machine_id": "bm-c", "state": "claimed",
                 "heartbeat": _now_iso()})
            _cc()
            v, det = _origin_claims_verdict("G", "grid-0of1", "bm-a",
                                            root=crepo, ref="HEAD")
            ok("S20b rival fresh claim -> occupied-fresh",
               v == "occupied-fresh")
            _cw("grid-0of1.bm-c.json",
                {"machine_id": "bm-c", "state": "closed", "outcome": "ok",
                 "closed_at": _now_iso(), "heartbeat": _now_iso()})
            _cc()
            v, det = _origin_claims_verdict("G", "grid-0of1", "bm-a",
                                            root=crepo, ref="HEAD")
            ok("S20c rival closed-ok -> occupied-closed",
               v == "occupied-closed")
            stale_ts = (datetime.now().astimezone()
                        - timedelta(minutes=25)).isoformat(timespec="seconds")
            _cw("grid-0of1.bm-c.json",
                {"machine_id": "bm-c", "state": "running",
                 "heartbeat": stale_ts})
            _cc()
            v, det = _origin_claims_verdict("G", "grid-0of1", "bm-a",
                                            root=crepo, ref="HEAD")
            ok("S20d stale rival -> takeover allowed", v == "takeover")
            _cw("grid-0of1.bm-c.json",
                {"machine_id": "bm-c", "state": "failed",
                 "heartbeat": _now_iso()})
            _cw("grid-0of1.bm-a.json",
                {"machine_id": "bm-a", "state": "running",
                 "heartbeat": _now_iso()})
            _cc()
            v, det = _origin_claims_verdict("G", "grid-0of1", "bm-a",
                                            root=crepo, ref="HEAD")
            ok("S20e failed rival + own file -> free",
               v == "free" and "failed" in det)
            v, det = _origin_claims_verdict("NOPE", "x0", "bm-a",
                                            root=crepo, ref="HEAD")
            ok("S20f absent claims dir -> free (not a fault)",
               v == "free" and "no rival" in det)
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
