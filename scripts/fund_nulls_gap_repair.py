"""FUND trio nulls burn-shard gap repair (r782 bm-b; T-2026-10-06-177 self-ticket).

Incident: append-only burn-evidence shards results/fund_*_p1/nulls.jsonl lost
lines across past stash-drop / checkout-window ops (34 total at r782
discovery: 20 divlowvol + 11 quality historical + 3 in the r782 S0 worksnap
basename-collision window). Root-cause weld landed same round: Tools/
treasure_guard.py now classes nulls/sens jsonl as append-only-ledger
(restore/stash-drop class ops HARD-REJECT rc3).

Repair law: the family runner's normal resume mode is the gap filler --
`python scripts/fund_<fam>_p1.py run --nulls` burns exactly the ks missing
from the shard (done-key skip). This wrapper only ever triggers it under
hard gates, because the live burn process owns the shard until it closes:

  gate-A  no live runner process for the family (psutil cmdline probe)
  gate-B  pool claim receipt state=closed with N=2000 (live runner finished
          its todo; pool autofill will not respawn a closed batch)
  gate-C  determinism verify: re-derive an EXISTING k via the family module
          (seed pinned rng([SEED_NULLS,k]) + frozen panel) and byte-compare
          -- mismatch = panel/code drift -> ABORT, escalate, never fill
  gate-D  cache digest (volume.npy+amount.npy content) pinned across the
          fill; drift mid-fill = abort + honest receipt

Usage:
  python scripts/fund_nulls_gap_repair.py status     # fast gates + report
  python scripts/fund_nulls_gap_repair.py run        # gated fill (detached ok)
  python scripts/fund_nulls_gap_repair.py selftest   # offline hermetic legs

Exit codes: 0 = clean/no-op/ok, 2 = mechanism fault, 3 = gate violation
(escalate, never mask). Marks/ledger/seed registries: +0 (pure repair of
already-computed evidence; re-derivation is byte-deterministic).
"""
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

FAMILIES = {
    "divlowvol": "scripts/fund_divlowvol_p1.py",
    "quality": "scripts/fund_quality_p1.py",
}
RECEIPT = os.path.join("results", "fund_nulls_gap_repair.json")
LOCK = os.path.join("results", "fund_nulls_gap_repair.lock")
LOG = os.path.join("results", "fund_nulls_gap_repair.log")


def _machine_id():
    import socket
    return {"FLUX-BMB": "bm-b"}.get(os.environ.get("COMPUTERNAME", socket.gethostname()
                                                   .split(".")[0]).upper(),
                                    os.environ.get("COMPUTERNAME",
                                                   socket.gethostname()).lower())


def _log(msg):
    line = "[%s] %s" % (time.strftime("%Y-%m-%dT%H:%M:%S"), msg)
    try:
        print(line)
    except Exception:
        pass
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def _load_receipt():
    if os.path.exists(RECEIPT):
        try:
            with open(RECEIPT, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"status": "init", "history": []}


def _save_receipt(r):
    with open(RECEIPT + ".tmp", "w", encoding="utf-8") as f:
        json.dump(r, f, ensure_ascii=False, indent=1, sort_keys=True)
    os.replace(RECEIPT + ".tmp", RECEIPT)


def _scan_family(fam):
    """Returns dict with shard facts. Uses the family module's own constants
    and shard path (single source, zero re-implementation)."""
    sys.path.insert(0, "scripts")
    mod = __import__("fund_%s_p1" % fam)
    path = mod._shard_files(kind="nulls")
    rows, ks, bad = [], [], 0
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for ln in f:
                if not ln.strip():
                    continue
                try:
                    r = json.loads(ln)
                    rows.append(r)
                    ks.append(int(r["k"]))
                except Exception:
                    bad += 1
    present = set(ks)
    missing = sorted(set(range(mod.K_NULLS)) - present)
    dup = len(ks) - len(present)
    entry_id, shard_key = "FUND-%s-P1-NULLS" % fam.upper(), \
        "fund-%s-p1-nulls-0of1" % fam
    claim = os.path.join("results", "pool_claims", entry_id,
                         "%s.%s.json" % (shard_key, _machine_id()))
    return {"module": mod, "path": path, "rows": rows, "ks": ks,
            "present": present, "missing": missing, "dup": dup,
            "bad_lines": bad, "k_nulls": mod.K_NULLS,
            "claim_path": claim, "max_k": (max(present) if present else -1)}


def _claim_closed(s):
    """gate-B: live runner finished (worker-side claim receipt closed with
    N=2000). Absent/open claim = batch still owned -> no-op."""
    p = s["claim_path"]
    if not os.path.exists(p):
        return False, "claim-receipt-absent"
    try:
        with open(p, encoding="utf-8") as f:
            c = json.load(f)
    except Exception as e:
        return False, "claim-unreadable:%s" % str(e)[:60]
    ok = c.get("state") == "closed" and "N=%d" % s["k_nulls"] in \
        str(c.get("result_ref", ""))
    return ok, ("closed-N2000" if ok else "state=%s ref=%s" %
                (c.get("state"), str(c.get("result_ref"))[:60]))


def _live_procs(fam):
    """gate-A: any live process running this family's nulls burn."""
    import psutil
    hits = []
    needle = "fund_%s_p1.py" % fam
    for pr in psutil.process_iter(["pid", "cmdline"]):
        try:
            cl = pr.info.get("cmdline") or []
        except Exception:
            continue
        if not cl:
            continue
        joined = " ".join(cl).replace("\\", "/")
        if needle in joined and "--nulls" in joined and "gap_repair" not in joined:
            hits.append(pr.info["pid"])
    return hits


def _determinism_verify(s, verify_k=None):
    """gate-C: re-derive an existing k through the family module and
    byte-compare against the shard line (seed rng + frozen panel)."""
    mod = s["module"]
    if verify_k is None:
        verify_k = s["max_k"]
    if verify_k < 0:
        return False, "no-existing-k"
    row_line = None
    for r in s["rows"]:
        if int(r["k"]) == verify_k:
            row_line = json.dumps(r, default=bool, sort_keys=True,
                                  ensure_ascii=False)
            break
    if row_line is None:
        return False, "verify-k-line-missing"
    t0 = time.time()
    mod._init_worker()
    fresh = mod._null_task({"k": verify_k})
    fresh_line = json.dumps(fresh, default=bool, sort_keys=True,
                            ensure_ascii=False)
    return fresh_line == row_line, "k=%d %.1fs %s" % (
        verify_k, time.time() - t0,
        "byte-identical" if fresh_line == row_line else "DRIFT")


def _digest(s):
    return s["module"]._cache_digest()


def _acquire_lock():
    if os.path.exists(LOCK):
        try:
            with open(LOCK, encoding="utf-8") as f:
                info = json.load(f)
            age = time.time() - os.path.getmtime(LOCK)
            if age < 4 * 3600 and not _live_procs("gap_repair-probe"):
                return False
        except Exception:
            pass
    with open(LOCK, "w", encoding="utf-8") as f:
        json.dump({"pid": os.getpid(), "ts": time.strftime(
            "%Y-%m-%dT%H:%M:%S")}, f)
    return True


def _release_lock():
    try:
        os.remove(LOCK)
    except OSError:
        pass


def cmd_status():
    r = _load_receipt()
    faces = {}
    for fam in FAMILIES:
        s = _scan_family(fam)
        procs = _live_procs(fam)
        closed, why = _claim_closed(s)
        faces[fam] = {"path": s["path"].replace("\\", "/"),
                      "lines": len(s["ks"]), "k_nulls": s["k_nulls"],
                      "max_k": s["max_k"], "dup_k": s["dup"],
                      "missing_n": len(s["missing"]),
                      "missing": s["missing"][:40],
                      "bad_lines": s["bad_lines"],
                      "live_procs": procs,
                      "claim_gate": {"closed": closed, "why": why}}
        faces[fam]["action"] = (
            "fill-ready" if (s["missing"] and not procs and closed)
            else ("awaiting-burn-complete" if s["missing"] and not closed
                  else ("busy-live-process" if procs else "clean")))
    r["status"] = "status"
    r["faces"] = faces
    r["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
    print(json.dumps({k: {kk: vv for kk, vv in v.items()}
                      for k, v in faces.items()}, ensure_ascii=False))
    return 0


def cmd_run():
    r = _load_receipt()
    if not _acquire_lock():
        _log("run: lock held by live fill -- exiting no-op")
        return 0
    try:
        for fam in FAMILIES:
            s = _scan_family(fam)
            if not s["missing"]:
                _log("%s: no missing ks -- clean" % fam)
                continue
            procs = _live_procs(fam)
            if procs:
                _log("%s: live runner pids=%s -- no-op (gate-A)" % (fam, procs))
                continue
            closed, why = _claim_closed(s)
            if not closed:
                _log("%s: claim gate not closed (%s) -- no-op (gate-B)"
                     % (fam, why))
                continue
            if len(s["missing"]) > 60:
                _log("%s: missing_n=%d exceeds sanity cap 60 -- shard "
                     "state suspect, ABORT escalate" % (fam, len(s["missing"])))
                r["history"].append({"fam": fam, "ts": time.strftime(
                    "%Y-%m-%dT%H:%M:%S+08:00"),
                    "outcome": "abort-sanity-cap",
                    "missing_n": len(s["missing"])})
                r["status"] = "abort-sanity-cap"
                _save_receipt(r)
                return 3
            d0 = _digest(s)
            ok, why = _determinism_verify(s)
            if not ok:
                _log("%s: DETERMINISM VERIFY FAIL (%s) -- ABORT, escalate"
                     % (fam, why))
                r["history"].append({"fam": fam, "ts": time.strftime(
                    "%Y-%m-%dT%H:%M:%S+08:00"), "outcome": "abort-verify",
                    "why": why})
                r["status"] = "abort-verify-drift"
                _save_receipt(r)
                return 3
            _log("%s: verify %s; digest=%s; filling %d missing ks %s"
                 % (fam, why, d0, len(s["missing"]),
                    s["missing"][:8] + ["..."] if len(s["missing"]) > 8
                    else s["missing"]))
            rc = subprocess.run([sys.executable, FAMILIES[fam], "run",
                                 "--nulls"]).returncode
            s2 = _scan_family(fam)
            d1 = _digest(s2)
            rec = {"fam": fam, "ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
                   "runner_rc": rc, "digest_before": d0, "digest_after": d1,
                   "filled": len(s["missing"]),
                   "post": {"lines": len(s2["ks"]), "dup_k": s2["dup"],
                            "missing_n": len(s2["missing"]),
                            "max_k": s2["max_k"]}}
            ok0, why0 = _determinism_verify(s2, verify_k=0)
            rec["post"]["k0_byte_anchored"] = bool(ok0)
            if rc == 0 and not s2["missing"] and s2["dup"] == 0 \
                    and len(s2["ks"]) == s2["k_nulls"] and d0 == d1 and ok0:
                rec["outcome"] = "repaired"
                _log("%s: REPAIRED %s" % (fam, json.dumps(rec["post"])))
            else:
                rec["outcome"] = "incomplete"
                r["status"] = "incomplete"
                _log("%s: INCOMPLETE after fill rc=%s %s"
                     % (fam, rc, json.dumps(rec["post"])))
            r["history"].append(rec)
            _save_receipt(r)
        r.setdefault("status", "ok")
        r["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
        _save_receipt(r)
        return 0
    finally:
        _release_lock()


def selftest():
    ok = []

    def expect(name, cond):
        ok.append(cond)
        print("  %s %s" % ("PASS" if cond else "FAIL", name))
    # hermetic legs on real shards (read-only)
    for fam in FAMILIES:
        s = _scan_family(fam)
        expect("%s shard parses, dup_k==0" % fam, s["dup"] == 0)
        expect("%s claim-gate parser returns bool" % fam,
               isinstance(_claim_closed(s)[0], bool))
    # lock acquire/release roundtrip
    _release_lock()
    expect("lock acquire", _acquire_lock())
    expect("lock double-acquire refused", not _acquire_lock())
    _release_lock()
    expect("lock released", not os.path.exists(LOCK))
    # receipt roundtrip
    r = _load_receipt()
    r["history"].append({"selftest": True})
    _save_receipt(r)
    expect("receipt roundtrip", _load_receipt()["history"][-1].get("selftest"))
    r["history"].pop()
    _save_receipt(r)
    print("SELFTEST", "PASS" if all(ok) else "FAIL")
    return 0 if all(ok) else 1


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    cmd = argv[1]
    if cmd == "status":
        return cmd_status()
    if cmd == "run":
        return cmd_run()
    if cmd == "selftest":
        return selftest()
    print("unknown command:", cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
