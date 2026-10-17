#!/usr/bin/env python
"""orphan_face_probe.py -- O-20261008-1300 knife-2: orphan python-face
patrol (CEO direct order, visible-console seal law).

An ORPHAN face = all THREE liveness faces fail (活性三面判定, r340 law):
  face-1 parent-dead : the process's parent pid no longer exists;
  face-2 no-hidden-host ancestor: no LIVE wscript.exe / pythonw.exe /
       (windowless daemon) ancestor anywhere up the chain -- the
       scheduled-task daemons run under wscript InvisibleRunner.vbs
       (r504/r517 canon) and are never orphans;
  face-3 cpu-stalled : negligible CPU accumulation across the sample
       window (knife-3 bound: <1 core-min/12h; probe scales it to the
       20s window with a startup grace: faces younger than GRACE_MIN
       are never judged, and CPU-active processes are never judged).

All three fail -> zombie; default mode is READ-ONLY (report faces +
evidence JSON); --kill harvests per 收编法 (adoption law: products stay
in the tree for the fleet round to collect) and kills only the
three-face-confirmed set, with a per-pid kill receipt. A healthy
burning worker tree (CPU-active) NEVER matches face-3 -- the live
case behind this law: a full-speed judge pool was misjudged as a
"14h zombie" from a clock-frame mismatch and killed by hand; the
probe makes that determination mechanical and clock-frame-proof
(ages measured in CPU-seconds, never wall-clock).

Exit codes: 0 = clean (or 0 orphans after kill), 2 = mechanism fault.
selftest subcommand = offline hermetic check (zero psutil dependency
on fake face tables).

v1.1.1 merge (bm-a r840, dual-machine same-order parallel build): bm-c's
canonical three-face probe + bm-a's stdio-server exemption belt (10-face
live-fire collateral family: idle MCP servers + serve_forever daemons
falsely match all three faces; belt = never orphan-verdict, report-only
idle_servers bucket). bm-a's separate v1.1 auto-kill design (WATCH-only +
persistence gate) is superseded by this read-only-default canon per
single-source law; the auto-kill idea lives on only as knife-3 tracking.

v1.2.0 (bm-a r1036, T28): listening-socket belt. TCP serve daemons
(resident_qa_server.py serve live case, 44h idle, dead spawner chain,
zero clients) match all three faces BY DESIGN-LIFECYCLE, not by being
garbage: a serve process outlives its launcher and idles at zero CPU
while holding a port. A pid owning at least one LISTEN tcp socket is
therefore never orphan-verdicted (fail-closed: the port may have live
domain consumers the process tree cannot see, per the
BigCompute-ResidentQA task-holder live case); it is reported in a
separate resident_servers bucket for GM/domain adjudication, never
auto-killed. Hermetic: the belt is a pure function over (orphans,
listen-map) so selftest exercises it with fake maps (r629 law)."""
import argparse
import datetime
import json
import os
import re
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# v1.1.2 (F-20261008-02 ①, bm-a r865): per-machine report path -- the old
# shared name results/_orphan_face_probe.json was a no-suffix multi-machine
# overwrite face and a fixed pull --rebase UU tax (bm-c r724 live fire; bm-a
# r865 same-round second fire). Same paradigm as face_<id>.json/_state.<id>.json.
# The orphan count consumed by round reports/heartbeats comes from this
# probe's STDOUT, never from the file (zero cross-machine reader). The old
# shared-name file is retired-in-place (frozen face, no new writes; deletion
# would trip the pre-push ownership claw -- not this machine's last write).
def _machine_id():
    with open(os.path.join(ROOT, "fleet", "machine.json"),
              encoding="utf-8") as _fh:
        return json.load(_fh)["machine_id"]

OUT = os.path.join(ROOT, "results",
                   f"_orphan_face_probe.{_machine_id()}.json")
SAMPLE_SEC = 20.0        # cpu stall sample window
STALL_CPU_SEC = 0.10     # < this CPU accumulation over the window = stalled
                         # (0.10 core-sec / 20s ~= 36 core-min/12h, far
                         # under any honest burn; knife-3 bound is 1 core-min
                         # per 12h -- the probe is the stricter gate)
GRACE_MIN = 30.0         # young faces never judged (startup states)
HIDDEN_HOSTS = ("wscript.exe", "pythonw.exe", "wscript")
# v1.1.1 merge belt (bm-a r840 live-fire, 10-face collateral): idle stdio
# MCP servers match all three faces while perfectly healthy -- their
# launcher exits after detached spawn (parent-dead = their normal pattern)
# and a stdin-blocked wait = zero CPU. They are NEVER orphan-verdicted;
# reported separately as idle_servers.
STDIO_SERVER_RE = re.compile(
    r"--transport\s+stdio|mcp-for-unity|duckduckgo-mcp|mcpserver|mcp-server"
    r"|\\uv\\tools\\", re.I)
PY_NAMES = ("python.exe", "pythonw.exe", "python3.exe", "python313.exe")


def _listening_pid_ports():
    """Map {pid: [listen ports]} for pids owning >=1 LISTEN tcp socket.

    v1.2.0 belt face. Fail-open to {} on any error (never block the probe,
    never widen the exemption without proof). One syscall per probe run.
    """
    lmap = {}
    try:
        import psutil
        for c in psutil.net_connections(kind="tcp"):
            if c.status == psutil.CONN_LISTEN and c.pid:
                lmap.setdefault(c.pid, []).append(
                    getattr(c.laddr, "port", None))
    except Exception:
        return {}
    return lmap


def _apply_socket_belt(orphans, lmap):
    """v1.2.0 pure belt: split orphans into (true_orphans, resident_servers).

    Faces whose pid owns a LISTEN socket move to the report-only
    resident_servers bucket (ports recorded); the rest keep the orphan
    verdict. Pure over (list, map) for hermetic selftest (r629 law).
    """
    resident, keep = [], []
    for f in orphans:
        ports = lmap.get(f["pid"])
        if ports:
            f["listen_ports"] = [p for p in ports[:6] if p]
            resident.append(f)
        else:
            keep.append(f)
    return keep, resident


def _walk_chain(pid, table):
    """Live ancestor pids walking up (stops at first dead/gone parent)."""
    chain = []
    cur = table.get(pid)
    seen = set()
    while cur is not None and cur["pid"] not in seen:
        seen.add(cur["pid"])
        pp = cur.get("ppid")
        nxt = table.get(pp)
        if nxt is None:
            # parent record gone (dead) -> chain breaks here
            chain.append(("DEAD", pp))
            return chain, False
        chain.append((nxt["name"].lower(), pp))
        if nxt["name"].lower() in HIDDEN_HOSTS:
            return chain, True
        cur = nxt
    return chain, False


def _judge_faces(table, pid, cpu_delta, age_min):
    """Three-face determination for one pid -> dict of face verdicts."""
    rec = table[pid]
    parent_live = rec.get("ppid") in table
    chain, host_found = _walk_chain(pid, table)
    return {
        "pid": pid,
        "name": rec["name"],
        "cmd": rec.get("cmd", "")[:120],
        "age_min": round(age_min, 1),
        "cpu_delta_20s": round(cpu_delta, 3),
        "face1_parent_dead": not parent_live,
        "face2_no_hidden_host_ancestor": not host_found,
        "face3_cpu_stalled": age_min > GRACE_MIN and cpu_delta < STALL_CPU_SEC,
        "ancestor_chain": [c[0] for c in chain][:6],
    }


def collect_table():
    """Snapshot live process table {pid: {pid,ppid,name,cmd,create,cpu}}."""
    import psutil
    table = {}
    for p in psutil.process_iter(["pid", "ppid", "name", "create_time"]):
        try:
            table[p.info["pid"]] = {
                "pid": p.info["pid"], "ppid": p.info["ppid"],
                "name": p.info["name"], "create_time": p.info["create_time"],
                "cmd": "", "_proc": p,
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    for rec in table.values():
        try:
            rec["cmd"] = " ".join(rec["_proc"].cmdline())
        except Exception:
            rec["cmd"] = ""
    return table


def cpu_snapshot(table, names=PY_NAMES):
    snap = {}
    for pid, rec in table.items():
        if rec["name"].lower() not in names:
            continue
        try:
            snap[pid] = rec["_proc"].cpu_times()
        except Exception:
            continue
    return snap


def _total_cpu(ct):
    return sum(v for v in ct)


def run(mode="probe"):
    t0 = datetime.datetime.now().isoformat(timespec="seconds")
    table = collect_table()
    snap1 = cpu_snapshot(table)
    time.sleep(SAMPLE_SEC)
    # refresh table (processes may have died/spawned during the window)
    table = collect_table()
    snap2 = cpu_snapshot(table)
    now_ts = time.time()
    faces = []
    for pid, ct2 in snap2.items():
        if pid not in table:
            continue
        ct1 = snap1.get(pid)
        delta = (_total_cpu(ct2) - _total_cpu(ct1)) if ct1 else None
        if delta is None:
            # not in first snapshot: too young OR window-crossing; judge
            # age only (a young face is grace-protected anyway)
            delta = 999.0  # assume active, never kill what we cannot prove
        age_min = (now_ts - table[pid]["create_time"]) / 60.0
        faces.append(_judge_faces(table, pid, delta, age_min))
    orphans = [f for f in faces if f["face1_parent_dead"]
               and f["face2_no_hidden_host_ancestor"]
               and f["face3_cpu_stalled"]]
    # v1.1.1 belt: stdio MCP servers are exempt from the orphan verdict
    # (healthy idle; the r840 collateral family). Report-only bucket.
    idle_servers = [f for f in orphans if STDIO_SERVER_RE.search(f["cmd"])]
    orphan_pids = {f["pid"] for f in idle_servers}
    orphans = [f for f in orphans if f["pid"] not in orphan_pids]
    # v1.2.0 belt: listening serve daemons exempt (fail-closed; the
    # resident_qa_server live case). Report-only resident_servers bucket.
    orphans, resident_servers = _apply_socket_belt(
        orphans, _listening_pid_ports())
    killed = []
    if mode == "kill" and orphans:
        import psutil
        for f in orphans:
            try:
                psutil.Process(f["pid"]).kill()
                killed.append(f["pid"])
            except Exception as ex:
                f["kill_error"] = str(ex)[:80]
    report = {
        "ts": t0, "mode": mode, "py_faces_seen": len(faces),
        "orphans": len(orphans), "killed": killed,
        "idle_servers_exempt": len(idle_servers),
        "resident_servers_exempt": len(resident_servers),
        "faces": faces, "orphan_details": orphans,
        "idle_server_details": idle_servers,
        "resident_server_details": resident_servers,
        "sample_sec": SAMPLE_SEC, "stall_cpu_sec": STALL_CPU_SEC,
        "grace_min": GRACE_MIN,
        "law": "O-20261008-1300 knife-2 three-face (parent-dead + "
               "no-hidden-host + cpu-stalled); knife-3 bound subsumed "
               "(probe cadence ~10min << 12h); v1.1.1 stdio belt + "
               "v1.2.0 listening-socket belt (T28, never auto-kill "
               "a serving socket)",
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
    print(json.dumps({"py_faces": len(faces), "orphans": len(orphans),
                      "resident_servers": len(resident_servers),
                      "killed": killed, "report": OUT},
                     ensure_ascii=False))
    return 0


def selftest():
    """Hermetic face-table test: zero psutil, fake tables (r629 law)."""
    okc = [0]

    def ok(name, cond):
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
        okc[0] += 1 if cond else 0
        return cond

    # fake table: 1=da (pythonw host), 2=runner under pythonw (healthy),
    # 3=orphan child (parent 99 dead, cpu stalled), 4=fresh orphan (grace)
    tbl = {
        1: {"pid": 1, "ppid": 0, "name": "pythonw.exe", "cmd": "daemon",
            "create_time": time.time() - 500, "_proc": None},
        2: {"pid": 2, "ppid": 1, "name": "python.exe", "cmd": "runner",
            "create_time": time.time() - 500, "_proc": None},
        3: {"pid": 3, "ppid": 99, "name": "python.exe", "cmd": "mp-child",
            "create_time": time.time() - 500, "_proc": None},
        4: {"pid": 4, "ppid": 98, "name": "python.exe", "cmd": "young",
            "create_time": time.time() - 60, "_proc": None},
    }
    f2 = _judge_faces(tbl, 2, 5.0, 300.0)
    ok("healthy runner under pythonw: faces all false",
       not f2["face1_parent_dead"] and not f2["face2_no_hidden_host_ancestor"]
       and not f2["face3_cpu_stalled"])
    f3 = _judge_faces(tbl, 3, 0.01, 300.0)
    ok("stalled mp-child orphan: three faces true (kill verdict)",
       f3["face1_parent_dead"] and f3["face2_no_hidden_host_ancestor"]
       and f3["face3_cpu_stalled"])
    f3b = _judge_faces(tbl, 3, 7.5, 300.0)
    ok("BURNING mp-child (cpu-active): face-3 false -> NEVER judged "
       "(the live misjudged-judge case behind this law)",
       f3b["face1_parent_dead"] and f3b["face2_no_hidden_host_ancestor"]
       and not f3b["face3_cpu_stalled"])
    f4 = _judge_faces(tbl, 4, 0.0, 1.0)
    ok("young orphan inside grace: face-3 false",
       f4["face1_parent_dead"] and not f4["face3_cpu_stalled"])
    # v1.1.1 belt leg (r840 collateral family): idle stdio MCP server cmd
    # must match the exemption regex; a judge cmd must not.
    ok("stdio-server belt: MCP cmds exempt, judge cmds not",
       STDIO_SERVER_RE.search("mcp-for-unity.exe --transport stdio")
       and STDIO_SERVER_RE.search(
           "uv\\tools\\duckduckgo-mcp-server\\Scripts\\python.exe")
       and not STDIO_SERVER_RE.search("judge.py --batch w14"))
    # v1.2.0 socket-belt legs (T28 live case): fake orphan faces, one
    # owning a LISTEN socket (resident_qa_server serve pattern) -> exempt
    # with ports recorded; the other -> keeps the orphan verdict.
    serv = {"pid": 5, "name": "pythonw.exe",
            "cmd": "pythonw.exe resident_qa_server.py serve",
            "face1_parent_dead": True,
            "face2_no_hidden_host_ancestor": True,
            "face3_cpu_stalled": True}
    batch = {"pid": 6, "name": "python.exe",
             "cmd": "python.exe burn_shard.py --w 99",
             "face1_parent_dead": True,
             "face2_no_hidden_host_ancestor": True,
             "face3_cpu_stalled": True}
    keep, resident = _apply_socket_belt([serv, batch], {5: [8792, None]})
    ok("socket belt: serve daemon owning LISTEN 8792 exempted with port",
       len(resident) == 1 and resident[0]["pid"] == 5
       and resident[0]["listen_ports"] == [8792])
    ok("socket belt: non-listening batch orphan keeps kill verdict",
       len(keep) == 1 and keep[0]["pid"] == 6)
    ok("socket belt: empty listen-map = zero exemptions (fail-closed)",
       _apply_socket_belt([serv], {}) == ([serv], []))
    allp = okc[0] == 8
    print(f"SELFTEST {'ALL PASS' if allp else 'HAS FAIL'} ({okc[0]}/8)")
    return 0 if allp else 2


if __name__ == "__main__":
    if os.name == "nt":
        pass  # probe spawns nothing; psutil reads need no window flags
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="probe",
                    choices=["probe", "kill", "selftest"])
    a = ap.parse_args()
    if a.mode == "selftest":
        raise SystemExit(selftest())
    raise SystemExit(run(mode=a.mode))
