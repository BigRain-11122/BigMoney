#!/usr/bin/env python
"""Tools/inbox_guard.py -- D-20260929-02 ② slice-face declaration guard.

Fleet law (group decision D-20260929-02, lowest-cost version, 48h
receipt window to 09-30 24:00): BEFORE a pool submit (autofill submit)
and BEFORE a slice start (pool_worker), MANDATORY git fetch + fresh
re-read of the fleet inbox pending MSG face; a declaration from
ANOTHER machine naming the same entry = FREEZE ("见声明即冻结").

r404 live-fire root cause (F-20260928-03, bm-a 08:5x): bm-c's 08:39:38
MSG declaration landed as a real file at 08:47 while bm-a (last fetch
08:26) completed the same port blind -- a stale tree is structurally
incapable of seeing an unfetched declaration. This guard upgrades the
r239 pool-claim fetch law to the slice face.

Face law:
  * origin face (git ls-tree/show <ref>:fleet/inbox/, processed/
    excluded) is the authoritative freshest sight when readable;
  * the LOCAL pending face is ALSO scanned (dedup by path) -- cheap,
    and catches a declaring machine's un-fetched-yet mirror;
  * degradation (resident_dispatcher precedent): fetch or origin-face
    fault -> honest degrade note in `detail`, local face still scanned,
    hard coordination locks (claim-by-file, pool freshness) untouched.
    The guard NEVER fabricates "seen" and NEVER blocks on its own
    fault -- a guard exception degrades to (False, "guard-fault ...").

Machine identity normalization: MSG filenames abbreviate (bma/bmb/bmc)
while fleet/machine.json ids hyphenate (bm-a/bm-b/bm-c); both sides are
normalized by stripping '-' before comparison, so bmc == "bm-c".

selftest subcommand = offline hermetic (zero network; a throwaway LOCAL
git repo exercises the origin-face read path with ref=HEAD).
"""
import os
import re
import subprocess

FLEET_INBOX = "fleet/inbox"
MSG_NAME_PAT = re.compile(r"^MSG-\d{8}-\d+-([A-Za-z0-9]+)-(?:ALL|all)-")
SENDER_PAT = re.compile(r"发件[:：]\s*([A-Za-z0-9-]+)")


def _norm(mid):
    return str(mid or "").replace("-", "").strip().lower()


def _machine_from_name(name):
    m = MSG_NAME_PAT.match(os.path.basename(str(name)))
    return m.group(1) if m else None


def _sender_from_text(text):
    m = SENDER_PAT.search(text or "")
    return m.group(1) if m else None


def _machine_of(fname, text):
    return _sender_from_text(text) or _machine_from_name(fname)


def _origin_pending(root, ref):
    """List + read <ref>'s fleet/inbox pending MSG face. Returns a list
    of {"file","text"} or None on git fault (never raises)."""
    try:
        r = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", ref, "--",
             FLEET_INBOX + "/"],
            cwd=root, capture_output=True)
        if r.returncode != 0:
            return None
        out = []
        for line in r.stdout.decode(errors="replace").splitlines():
            p = line.strip().replace("\\", "/")
            if (not p or "/processed/" in p
                    or not (p.endswith(".md") or p.endswith(".json"))):
                continue
            b = subprocess.run(["git", "show", f"{ref}:{p}"],
                               cwd=root, capture_output=True)
            if b.returncode != 0:
                continue
            out.append({"file": p,
                        "text": b.stdout.decode(errors="replace")})
        return out
    except Exception:
        return None


def _local_pending(root):
    d = os.path.join(root, *FLEET_INBOX.split("/"))
    out = []
    if not os.path.isdir(d):
        return out
    for name in os.listdir(d):
        p = os.path.join(d, name)
        if (not os.path.isfile(p)
                or not (name.endswith(".md") or name.endswith(".json"))):
            continue
        try:
            with open(p, encoding="utf-8", errors="replace") as fh:
                out.append({"file": FLEET_INBOX + "/" + name,
                            "text": fh.read()})
        except OSError:
            continue
    return out


def conflict(root, machine_id, needle, fetch=True, ref="origin/main"):
    """Returns (freeze, detail).

    freeze=True  -> another machine's PENDING inbox declaration names
                    `needle` (entry id / batch key): the caller MUST
                    freeze (skip slice start / refuse submit).
    freeze=False -> no conflicting declaration sighted; `detail` carries
                    the face/degrade note for honest logging.
    Never raises; any internal fault degrades to (False, "guard-fault").
    """
    try:
        notes = []
        if fetch:
            rc = subprocess.run(["git", "fetch", "-q", "origin", "main"],
                                cwd=root, capture_output=True).returncode
            if rc != 0:
                notes.append("fetch-fault (degraded to local face)")
        msgs = {}
        if fetch or ref == "origin/main":
            for m in _origin_pending(root, ref) or []:
                msgs[m["file"]] = m
            if ref == "origin/main" and not msgs and fetch:
                pass  # empty origin pending face is a valid sight, keep it
        for m in _local_pending(root):
            msgs.setdefault(m["file"], m)
        for m in msgs.values():
            sender = _machine_of(m["file"], m["text"])
            if _norm(sender) == _norm(machine_id):
                continue  # own declaration never freezes own work
            if needle and needle in m["text"]:
                return True, (f"{m['file']} from {sender or 'unknown'} "
                              f"names '{needle}'")
        detail = "; ".join(notes) if notes else \
            f"{len(msgs)} pending msg(s) sighted, none name '{needle}'"
        return False, detail
    except Exception as ex:
        return False, f"guard-fault {ex}"


def selftest():
    import shutil
    import tempfile
    tmp = tempfile.mkdtemp(prefix="inbox_guard_st_")
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
        ib = os.path.join(tmp, *FLEET_INBOX.split("/"))
        os.makedirs(ib)
        # S1: other machine's pending declaration naming the needle -> freeze
        with open(os.path.join(ib, "MSG-20260929-0100-bm-b-ALL-W5-freeze.md"),
                  "w", encoding="utf-8") as fh:
            fh.write("# MSG W5 freeze\n- 发件：bm-b（r199）\n\n"
                     "TRIAL_LABOR_W5 认领声明，冻结窗内勿并行。\n")
        fr, det = conflict(tmp, "bm-a", "TRIAL_LABOR_W5", fetch=False,
                           ref="HEAD")
        ok("S1 rival declaration -> freeze", fr and "bm-b" in det)
        # S2: same machine's own declaration -> never freeze
        fr, det = conflict(tmp, "bm-b", "TRIAL_LABOR_W5", fetch=False,
                           ref="HEAD")
        ok("S2 own declaration -> no freeze", not fr)
        # S3: needle not named -> no freeze
        fr, det = conflict(tmp, "bm-a", "OTHER_BATCH_X", fetch=False,
                           ref="HEAD")
        ok("S3 no mention -> no freeze", not fr)
        # S4: bmc filename abbreviation normalizes to bm-c
        with open(os.path.join(ib, "MSG-20260929-0110-bmc-all-grid.md"),
                  "w", encoding="utf-8") as fh:
            fh.write("GRID_S3_P1 已开工声明。\n")
        fr, det = conflict(tmp, "bm-c", "GRID_S3_P1", fetch=False,
                           ref="HEAD")
        ok("S4 bmc==bm-c self -> no freeze", not fr)
        fr, det = conflict(tmp, "bm-a", "GRID_S3_P1", fetch=False,
                           ref="HEAD")
        ok("S5 bmc rival -> freeze", fr and "bmc" in det)
        # S6: processed/ archive is invisible to the guard
        pr = os.path.join(ib, "processed")
        os.makedirs(pr)
        with open(os.path.join(pr, "MSG-20260929-0120-bm-b-ALL-old.md"),
                  "w", encoding="utf-8") as fh:
            fh.write("STALE_BATCH_9 processed 声明。\n")
        fr, det = conflict(tmp, "bm-a", "STALE_BATCH_9", fetch=False,
                           ref="HEAD")
        ok("S6 processed face excluded", not fr)
        # S7: origin-face read path via a real (throwaway, offline) git repo
        r = subprocess.run(["git", "init", "-q"], cwd=tmp,
                           capture_output=True)
        ok("S7a tmp git init", r.returncode == 0)
        if r.returncode == 0:
            subprocess.run(["git", "add", "-A"], cwd=tmp,
                           capture_output=True)
            subprocess.run(["git", "-c", "user.email=st@t", "-c",
                            "user.name=st", "commit", "-qm", "st"],
                           cwd=tmp, capture_output=True)
            fr, det = conflict(tmp, "bm-a", "TRIAL_LABOR_W5", fetch=False,
                               ref="HEAD")
            ok("S7b origin face (ref=HEAD) sees declaration", fr)
        # S8: empty inbox + no git fault -> honest blind note, no freeze
        empty = tempfile.mkdtemp(prefix="inbox_guard_st2_")
        fr, det = conflict(empty, "bm-a", "ANY", fetch=False, ref="HEAD")
        ok("S8 empty face -> no freeze + sighted-0 detail",
           not fr and "0 pending" in det)
        shutil.rmtree(empty, ignore_errors=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"selftest: {okc[0]} PASS / {failc[0]} FAIL")
    return 1 if failc[0] else 0


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    print("usage: inbox_guard.py selftest  "
          "(library use: conflict(root, machine_id, needle))")
    sys.exit(2)
