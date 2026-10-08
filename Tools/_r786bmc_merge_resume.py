"""r786 bm-c S0 merge-resume resolver (r785 dead-session mid-merge #1:
MERGE_HEAD e7a7218fd since 00:30:02, single UU results/_attrition_guard_scan.json;
r785 session died after commit 6796c38a3 00:30:00 + pull-merge start 00:30:02).
Laws applied: r611(3)/r637 continuation (MERGE_HEAD in place -> resume actual
remaining UU set, no rollback, no full rebuild); r515 complete-side source =
index stage blobs :2:/:3: (never worktree reconstruction, zealous common-tail
blind spot); r710-A blob extraction = python subprocess bytes, never PS
redirection (UTF-16 poison); r710-B len>100+reparse gate before any write;
r773/r756 ts compare = normalized parse, never mixed-format string compare;
full-blob side take (not line surgery); r704 write-back re-read assertion;
r637 marker scan scoped to resolved faces only (historical conflict-evidence
receipts in results/ are permanent false-red mines).
Per-face policy: S6-output / probe-output regen faces -> ts-newer-wins, tie or
unparseable -> ours (S6 chain this round regenerates them anyway); this round's
known face _attrition_guard_scan.json = r773 precedent exactly (ours r785
00:21:47 vs theirs 00:09:52 -> ours wins on data).
Re-runnable for merge#2 (origin tip 9e5097507, 8 more commits behind after
merge#1 completes): same policy table, probe-act-assert loop."""
import datetime
import json
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECEIPT = os.path.join(ROOT, "results", "_r786bmc_merge_resume.json")
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
TS_KEYS = ("ts", "updated", "updated_at", "generated", "generated_at",
           "scanned_at", "last_scan", "asof")


def git(args):
    return subprocess.run(["git"] + args, cwd=ROOT, capture_output=True,
                          creationflags=CNW)


def uu_faces():
    r = git(["ls-files", "-u"])
    if r.returncode != 0:
        raise SystemExit("ls-files -u rc=%d: %s" % (r.returncode,
                                                    r.stderr.decode("utf-8", "replace")))
    paths = []
    for line in r.stdout.decode("utf-8", "replace").splitlines():
        parts = line.split("\t")
        if len(parts) == 2 and parts[1] not in paths:
            paths.append(parts[1])
    return paths


def stage_blob(stage, path):
    r = git(["show", ":%d:%s" % (stage, path)])
    if r.returncode != 0 or not r.stdout:
        raise SystemExit("stage :%d:%s unreadable rc=%d (stage collapsed?)"
                         % (stage, path, r.returncode))
    return r.stdout


def norm_ts(s):
    if not isinstance(s, str):
        return None
    t = s.strip().replace(" ", "T", 1) if " " in s and "T" not in s[:12] else s
    try:
        return datetime.datetime.fromisoformat(t)
    except ValueError:
        return None


def face_ts(obj):
    for k in TS_KEYS:
        v = norm_ts(obj.get(k)) if isinstance(obj, dict) else None
        if v is not None:
            return k, v
    return None, None


MARKER = re.compile(rb"^(<<<<<<< |>>>>>>> |======= ?$)", re.M)

# r522/r773 union faces: rolling-history JSON -> history rows = serialization-key
# union zero-loss (rows are OBJECTS not strings -- r522 dict-key-inversion law),
# latest/base face = explicit-key ts-newer-wins (r711-3 explicit anchor), union
# history re-sorted chronologically (normalized parse, never string compare).
UNION_FACES = {"results/compute_audit.json"}
HIST_KEYS = ("ts", "generated", "generated_at", "updated", "updated_at",
             "asof")


def hist_row_ts(row):
    if not isinstance(row, dict):
        return None
    for k in HIST_KEYS:
        v = norm_ts(row.get(k))
        if v is not None:
            return v
    return None


def resolve_union(path, log):
    ours = stage_blob(2, path)
    theirs = stage_blob(3, path)
    jo, jt = json.loads(ours.decode("utf-8")), json.loads(theirs.decode("utf-8"))
    lo, lt = jo.get("latest", {}), jt.get("latest", {})
    ko, to = face_ts(lo)
    kt, tt = face_ts(lt)
    if to and tt and to >= tt or (to and not tt):
        base_obj, base_side = jo, "ours"
        why_l = "latest %s %s >= theirs" % (ko, to.isoformat() if to else "?")
    else:
        base_obj, base_side = jt, "theirs"
        why_l = "latest %s %s > ours" % (kt, tt.isoformat() if tt else "?")
    ho, ht = jo.get("history") or [], jt.get("history") or []
    assert all(isinstance(r, dict) for r in ho + ht), "non-dict history row"
    oid = {}
    for r in ho + ht:
        oid.setdefault(json.dumps(r, ensure_ascii=False, sort_keys=True), r)
    union = list(oid.values())
    n_ours = len(ho)
    n_theirs = len(ht)
    union.sort(key=lambda r: (hist_row_ts(r) is None,
                               hist_row_ts(r) or datetime.datetime.min,
                               json.dumps(r, ensure_ascii=False, sort_keys=True)))
    merged = dict(base_obj)
    merged["history"] = union
    blob = json.dumps(merged, ensure_ascii=False, indent=1).encode("utf-8") + b"\n"
    if MARKER.search(blob):
        raise SystemExit("%s union blob contains conflict markers" % path)
    with open(os.path.join(ROOT, path), "wb") as f:
        f.write(blob)
    with open(os.path.join(ROOT, path), "rb") as f:
        back = f.read()
    if back != blob:
        raise SystemExit("%s union write-back mismatch" % path)
    json.loads(back.decode("utf-8"))
    r = git(["add", "--", path])
    if r.returncode != 0:
        raise SystemExit("git add %s rc=%d" % (path, r.returncode))
    log.append({"path": path, "side": "union:%s-latest" % base_side,
                "why": "%s; history union rows ours=%d theirs=%d -> %d "
                       "(serialization-key dedupe, zero-loss, chronological)"
                       % (why_l, n_ours, n_theirs, len(union)),
                "ours_ts": str(to), "theirs_ts": str(tt)})


def resolve(path, log):
    if path in UNION_FACES:
        return resolve_union(path, log)
    ours = stage_blob(2, path)
    theirs = stage_blob(3, path)
    jo, jt = json.loads(ours.decode("utf-8")), json.loads(theirs.decode("utf-8"))
    ko, to = face_ts(jo)
    kt, tt = face_ts(jt)
    if to and tt:
        side, why = ("ours", "ts-newer-wins %s %s >= theirs %s %s"
                     % (ko, to.isoformat(), kt, tt.isoformat())) if to >= tt \
            else ("theirs", "ts-newer-wins %s %s > ours %s %s"
                  % (kt, tt.isoformat(), ko, to.isoformat()))
    elif to:
        side, why = "ours", "theirs ts unparseable"
    elif tt:
        side, why = "theirs", "ours ts unparseable"
    else:
        side, why = "ours", "no-parseable-ts tie -> ours (regen face)"
    blob = ours if side == "ours" else theirs
    if MARKER.search(blob):
        raise SystemExit("%s winner blob contains conflict markers" % path)
    with open(os.path.join(ROOT, path), "wb") as f:
        f.write(blob)
    with open(os.path.join(ROOT, path), "rb") as f:
        back = f.read()
    if back != blob:
        raise SystemExit("%s write-back mismatch" % path)
    json.loads(back.decode("utf-8"))
    r = git(["add", "--", path])
    if r.returncode != 0:
        raise SystemExit("git add %s rc=%d" % (path, r.returncode))
    log.append({"path": path, "side": side, "why": why,
                "ours_ts": str(to), "theirs_ts": str(tt)})


def main():
    mh = git(["rev-parse", "-q", "--verify", "MERGE_HEAD"])
    if mh.returncode != 0:
        print("NO-MERGE-IN-PROGRESS (nothing to resume)")
        return 0
    merge_head = mh.stdout.decode().strip()
    log = []
    faces = uu_faces()
    for p in faces:
        resolve(p, log)
    left = uu_faces()
    receipt = {"round": "r786", "machine": "bm-c", "merge_head": merge_head,
               "uu_before": faces, "resolved": log, "uu_after": left,
               "law_refs": ["r611(3)/r637 resume", "r515 stage-source",
                            "r710 bytes+gate", "r773 ts-newer-wins",
                            "r704 write-back", "r637 scoped marker scan"]}
    with open(RECEIPT, "w", encoding="utf-8") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=1)
    print("MERGE-RESUME merge_head=%s uu=%d resolved=%d remaining=%d receipt=%s"
          % (merge_head[:9], len(faces), len(log), len(left),
             os.path.basename(RECEIPT)))
    for row in log:
        print("  %s -> %s (%s)" % (row["path"], row["side"], row["why"]))
    return 1 if left else 0


if __name__ == "__main__":
    raise SystemExit(main())
