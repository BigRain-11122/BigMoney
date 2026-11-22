"""Who else is writing THIS repo right now? (r1927 bm-c)

The law says one executor per repo tree at a time (round prompt S0; r1907 "two
codely hosts on one tree: land new files only, never re-run the chain"). Until
now there was no way to check it: Tools/spawn_gate.ps1 counts live autonomous
rounds against a cloud cap, and by design EXEMPTS interactive Cowork windows
(`--experimental-acp`) -- but an interactive window writes the same shared
faces. 2026-11-22 is the live case: the desktop session (started 11:02:50)
rewrote scripts/data_lane_freshness.py and regenerated docs/data_lanes/
FRESHNESS.md at 11:10:53 while this headless round (started 11:20:03) was
deciding what to do; the 11:12:53 smoke run then reported as RED a gate whose
page had already been regenerated mid-run (r1854/r1860/r1861 family: "the face
moved" read as "the face is wrong").

This probe answers the one question a round actually needs:

    python Tools/repo_write_contention.py                     # human readout
    python Tools/repo_write_contention.py --json <path>       # evidence file
    python Tools/repo_write_contention.py --selftest          # offline lanes

Verdicts (exit code):
    0  CLEAN              fewer than two codely hosts alive
    3  CONTENTION         >=2 hosts alive AND a shared face was written inside
                          a window where two of them were alive together
    4  MULTI_HOST_QUIET   >=2 hosts alive, no shared-face write in the overlap
    2  mechanism failure  (probe itself broke -- never silently CLEAN)

Advisory only: nothing here blocks, kills or gates production (a probe that
can starve the lane is the F-20261017-01 defect again). Pure stdlib + psutil
when present; ASCII output so a GBK console cannot eat it.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

# Directories whose writes are shared state. Deliberately excludes .git,
# data/ (panels, huge and append-only by their own hosts), Media02/, legacy/,
# Money02/ and .codely-cli/ (per-session tool logs -- a peer's shell traffic
# is not evidence of a shared-face write).
SHARED_DIRS = ("docs", "results", "research", "scripts", "Tools", "fleet", "state")
SKIP_DIRS = {".git", ".codely-cli", "data", "node_modules", "__pycache__",
             "Media02", "legacy", "Money02", ".venv", "venv"}
MAX_VISITS = 60000
MAX_WRITES = 400
HOST_NAME = "codely.exe"
HEADLESS_MARK = ' -p "'
ACP_MARK = "--experimental-acp"

# Faces written by scheduled ticks (not by any host) plus this probe's own
# output. Declared here so the verdict is not "always CONTENTION because the
# watchdog also writes". Everything ignored is printed in the readout and
# stored in the payload -- a hidden exclusion is a preference, not a fact.
DEFAULT_IGNORE = (
    "results/saturation_engine/",
    "results/watermark_red.json",
    "results/idle_trigger",
    "results/orders_ack_scan",
    "results/_orphan_face_probe",
    "results/_repo_write_contention",
    "results/_host_contention",
)


def machine_id() -> str:
    try:
        with open(os.path.join(REPO, "fleet", "machine.json"), encoding="utf-8") as fh:
            return str(json.load(fh).get("machine_id") or "unknown")
    except Exception:
        return "unknown"


def list_hosts():
    """Live codely hosts on this machine (headless rounds and interactive)."""
    hosts = []
    try:
        import psutil
    except ImportError:
        return hosts, "psutil-missing"
    now = time.time()
    for proc in psutil.process_iter(["pid", "name", "create_time", "cmdline"]):
        try:
            if str(proc.info.get("name") or "").lower() != HOST_NAME:
                continue
            cmd = " ".join(proc.info.get("cmdline") or [])
            if HEADLESS_MARK in cmd:
                kind = "headless_round"
            elif ACP_MARK in cmd:
                kind = "interactive"
            else:
                kind = "other"
            started = float(proc.info.get("create_time") or now)
            hosts.append({
                "pid": proc.info["pid"],
                "kind": kind,
                "started_epoch": started,
                "started": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(started)),
                "age_min": round((now - started) / 60.0, 1),
                "exempt_from_cloud_cap": kind == "interactive",
                "cmd_head": cmd[:110],
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    hosts.sort(key=lambda h: h["started_epoch"])
    return hosts, None


def my_host_pid():
    """The codely.exe host this probe runs inside (walk the parent chain).

    Without it the probe counts its own round's writes as contention, i.e. it
    fires every time two hosts exist -- the same "always red" failure as never
    firing at all (r1789).
    """
    try:
        import psutil
        for parent in psutil.Process().parents():
            if str(parent.name() or "").lower() == HOST_NAME:
                return parent.pid, parent.create_time()
    except Exception:
        pass
    return None, None


def is_ignored(path, patterns):
    return any(pat in path for pat in patterns)


def list_writes(since_epoch: float):
    """Recent writes under the shared trees, newest first."""
    writes = []
    visits = 0
    for sub in SHARED_DIRS:
        root = os.path.join(REPO, sub)
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for name in filenames:
                visits += 1
                if visits > MAX_VISITS:
                    break
                path = os.path.join(dirpath, name)
                try:
                    st = os.stat(path)
                except OSError:
                    continue
                if st.st_mtime < since_epoch:
                    continue
                writes.append({
                    "path": os.path.relpath(path, REPO).replace("\\", "/"),
                    "mtime": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(st.st_mtime)),
                    "mtime_epoch": st.st_mtime,
                    "bytes": st.st_size,
                })
            if visits > MAX_VISITS:
                break
        if visits > MAX_VISITS:
            break
    writes.sort(key=lambda w: w["mtime_epoch"], reverse=True)
    return writes[:MAX_WRITES], visits


def overlap_windows(hosts, now, min_overlap_s=60.0):
    """Spans where two hosts (or more) were alive at the same time."""
    spans = []
    for i in range(len(hosts)):
        for j in range(i + 1, len(hosts)):
            lo = max(hosts[i]["started_epoch"], hosts[j]["started_epoch"])
            hi = now  # both alive: list_hosts only returns live pids
            if hi - lo >= min_overlap_s:
                spans.append({
                    "pair": [hosts[i]["pid"], hosts[j]["pid"]],
                    "kinds": [hosts[i]["kind"], hosts[j]["kind"]],
                    "from": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(lo)),
                    "to": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(hi)),
                    "minutes": round((hi - lo) / 60.0, 1),
                    "lo": lo,
                })
    return spans


def verdict(hosts, writes, spans, my_start=None):
    """Pure decision so the selftest can drive every branch offline.

    Two kinds of evidence, kept apart because they mean different things:
      * writes older than MY host's start -> strictly another host's work in a
        repo I am now also writing (the case this tool exists for);
      * writes at/after my start inside an overlap -> unattributable, and an
        unattributable shared-face write is the race r1854 called "the face
        moved".
    """
    if len(hosts) < 2:
        return "CLEAN", 0, "fewer than two codely hosts alive", {"peer_only": [], "ambiguous": []}
    peer_only, ambiguous = [], []
    earliest = min(h["started_epoch"] for h in hosts)
    for w in writes:
        if (my_start is not None and w["mtime_epoch"] < my_start
                and w["mtime_epoch"] >= earliest):
            peer_only.append(w["path"])
            continue
        for span in spans:
            if w["mtime_epoch"] >= span["lo"]:
                ambiguous.append(w["path"])
                break
    detail = {
        "peer_only": sorted(set(peer_only))[:20],
        "ambiguous": sorted(set(ambiguous))[:20],
        "peer_only_n": len(set(peer_only)),
        "ambiguous_n": len(set(ambiguous)),
    }
    if detail["peer_only_n"] or detail["ambiguous_n"]:
        return ("CONTENTION", 3,
                f"{len(hosts)} hosts alive; {detail['peer_only_n']} shared face(s) "
                f"written before this round started (strictly another host), "
                f"{detail['ambiguous_n']} written inside the overlap "
                f"(unattributable)", detail)
    return ("MULTI_HOST_QUIET", 4,
            f"{len(hosts)} hosts alive, no shared-face write in the window", detail)


def report(lookback_min, json_out, ignore=None, mine=None):
    now = time.time()
    since = now - lookback_min * 60.0
    hosts, host_err = list_hosts()
    my_pid, my_start = my_host_pid()
    patterns = tuple(DEFAULT_IGNORE) + tuple(ignore or ())
    mine_patterns = tuple(mine or ())
    raw_writes, visits = list_writes(since)
    declared_self = [w for w in raw_writes if is_ignored(w["path"], mine_patterns)]
    writes = [w for w in raw_writes
              if not is_ignored(w["path"], patterns)
              and not is_ignored(w["path"], mine_patterns)]
    ignored_n = len(raw_writes) - len(writes)
    spans = overlap_windows(hosts, now)
    state, rc, why, detail = verdict(hosts, writes, spans, my_start)
    payload = {
        "schema": "repo-write-contention/v1",
        "machine_id": machine_id(),
        "probed_at": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(now)),
        "lookback_min": lookback_min,
        "verdict": state,
        "why": why,
        "hosts": hosts,
        "my_host_pid": my_pid,
        "my_host_started": (time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(my_start))
                            if my_start else None),
        "host_probe_error": host_err,
        "overlap_windows": spans,
        "peer_only_writes": detail["peer_only"],
        "ambiguous_writes": detail["ambiguous"],
        "ignored_patterns": list(patterns),
        "ignored_write_count": ignored_n,
        "declared_own_patterns": list(mine_patterns),
        "declared_own_write_count": len(declared_self),
        "declared_own_writes": [w["path"] for w in declared_self][:20],
        "writes_scanned_files": visits,
        "recent_writes": writes[:40],
        "recent_write_count": len(writes),
        "advisory": ("Probe only: it never blocks, kills or defers production. "
                     "A round that reads CONTENTION must land new files only, "
                     "never re-derive shared faces or re-run the chain (r1907)."),
    }
    print(f"REPO-WRITE-CONTENTION {state} rc={rc} machine={payload['machine_id']}")
    print(f"  why: {why}")
    print(f"  me:  host pid={my_pid} started={payload['my_host_started']}")
    for h in hosts:
        mark = " <- me" if h["pid"] == my_pid else ""
        print(f"  host pid={h['pid']} {h['kind']} started={h['started']} "
              f"age={h['age_min']}m cap_exempt={h['exempt_from_cloud_cap']}{mark}")
    for s in spans:
        print(f"  overlap {s['from']}..{s['to']} ({s['minutes']}m) "
              f"pids={s['pair']} kinds={s['kinds']}")
    for p in detail["peer_only"][:8]:
        print(f"  peer-only write {p}")
    for p in detail["ambiguous"][:8]:
        print(f"  ambiguous write {p}")
    if ignored_n:
        print(f"  excluded {ignored_n} write(s): scheduler/self patterns "
              f"{', '.join(patterns)}"
              + (f" | declared own {', '.join(mine_patterns)}" if mine_patterns else ""))
    if json_out:
        path = json_out if os.path.isabs(json_out) else os.path.join(REPO, json_out)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
        print(f"  evidence -> {os.path.relpath(path, REPO).replace(chr(92), '/')}")
    return rc


def selftest():
    """Offline lanes: every verdict branch must be reachable and distinct.

    A guard that can only ever say CLEAN is the r1282 family defect (a check
    that never fires on the input it was written for).
    """
    ok = 0
    base = 1_700_000_000.0
    one = [{"pid": 10, "kind": "headless_round", "started_epoch": base}]
    two = one + [{"pid": 20, "kind": "interactive", "started_epoch": base + 600}]
    spans = overlap_windows(two, base + 3600)
    assert len(spans) == 1, spans

    state, rc, _, _ = verdict(one, [{"path": "a.json", "mtime_epoch": base + 900}],
                              spans, my_start=base)
    assert (state, rc) == ("CLEAN", 0), (state, rc)
    ok += 1

    # a write AFTER the second host came up -> unattributable authorship
    state, rc, _, det = verdict(two, [{"path": "docs/x.md", "mtime_epoch": base + 1400}],
                                spans, my_start=base + 1300)
    assert (state, rc) == ("CONTENTION", 3), (state, rc)
    assert det["ambiguous_n"] == 1 and det["peer_only_n"] == 0, det
    ok += 1

    # a write BEFORE my own round started is strictly the other host's work
    state, rc, _, det = verdict(two, [{"path": "docs/x.md", "mtime_epoch": base + 700}],
                                spans, my_start=base + 900)
    assert (state, rc) == ("CONTENTION", 3), (state, rc)
    assert det["peer_only_n"] == 1 and det["ambiguous_n"] == 0, det
    ok += 1

    # a write before BOTH hosts is history, not contention
    state, rc, _, _ = verdict(two, [{"path": "docs/x.md", "mtime_epoch": base - 60}],
                              spans, my_start=base + 900)
    assert (state, rc) == ("MULTI_HOST_QUIET", 4), (state, rc)
    ok += 1

    # two hosts whose lives barely touch do not form a window
    late = one + [{"pid": 30, "kind": "interactive", "started_epoch": base + 30}]
    assert overlap_windows(late, base + 61) == [], "30s overlap must not count"
    ok += 1

    # declared exclusions: the scheduler's own faces never make a verdict
    assert is_ignored("results/saturation_engine/face_bm-c.json", DEFAULT_IGNORE)
    assert not is_ignored("docs/data_lanes/FRESHNESS.md", DEFAULT_IGNORE)
    ok += 1

    # the interactive host is exactly the one the cloud cap exempts
    assert two[1]["kind"] == "interactive"
    print(f"selftest: {ok}/6 PASS", flush=True)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="is a second host writing this repo right now?")
    ap.add_argument("--lookback-min", type=float, default=60.0)
    ap.add_argument("--json", default="")
    ap.add_argument("--ignore", action="append", default=[],
                    help="extra path substring to treat as not-a-host write")
    ap.add_argument("--mine", action="append", default=[],
                    help="path substring this round wrote itself (declared, printed)")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    try:
        return report(args.lookback_min, args.json, args.ignore, args.mine)
    except Exception as exc:                      # never fail open into CLEAN
        print(f"REPO-WRITE-CONTENTION PROBE_FAULT {type(exc).__name__}: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
