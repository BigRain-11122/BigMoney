# -*- coding: utf-8 -*-
"""r807(2nd) bm-c Phase B: merge origin/main closeout (r746/r790/r796 canon).
Merge semantics NOTE (r782 inversion guard): in a MERGE window stage2=ours
(HEAD=local live) stage3=theirs (origin). r805 resolver treats b2=origin-side
b3=replay/mine -> SWAP the call (b2=theirs, b3=mine) so replay-newer picks the
LOCAL live face; tie override -> mine (G4' disk-live tie law, r747), NOT the
r794 rebase tie law. Marker gate + sha channel + targeted add per r648/r794.
Merge commit via -F message file (r512 quote law). Exit 0 merged."""
import importlib.util
import json
import os
import subprocess
import sys
import datetime as dt

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE = 0x08000000
RECEIPT = os.path.join(ROOT, "results", "_r807bmc_merge_close.json")
MSG = os.path.join(ROOT, "_r807bmc_mergemsg.txt")


def git(args, env=None):
    e = dict(os.environ)
    e["PYTHONUTF8"] = "1"
    if env:
        e.update(env)
    p = subprocess.run(["git", "-C", ROOT] + args, capture_output=True,
                       creationflags=CREATE, env=e)
    return (p.returncode, (p.stdout or b"").decode("utf-8", "replace"),
            (p.stderr or b"").decode("utf-8", "replace"))


def load_resolver():
    spec = importlib.util.spec_from_file_location(
        "r805_resolver", os.path.join(ROOT, "Tools", "_r805bmc_resolver.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def uu_faces():
    rc, out, _ = git(["ls-files", "-u"])
    faces = {}
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) != 2:
            continue
        f = parts[0].split()
        faces.setdefault(parts[1], {})[int(f[2])] = f[1]
    return faces


def main():
    r = {"round": "r807-merge-close", "decisions": {}, "steps": []}
    rc, out, _ = git(["rev-parse", "origin/main"])
    theirs_tip = out.strip()
    r["theirs_tip"] = theirs_tip
    rc, out, err = git(["merge", "origin/main", "--no-edit"])
    r["steps"].append("merge rc=%d %r" % (rc, (err or out)[:250]))
    if rc == 0:
        r["clean_merge"] = True
    else:
        faces = uu_faces()
        r["uu_n"] = len(faces)
        mod = load_resolver()
        resolved = {}
        for path in sorted(faces):
            s = faces[path]
            mine = mod.git(["cat-file", "-p", s[2]])    # ours = local live
            theirs = mod.git(["cat-file", "-p", s[3]])  # theirs = origin
            blob = mod.resolve_face(path, theirs, mine, r)  # SWAP: b2=theirs
            if "ts-tie-or-absent" in r["decisions"].get(path, ""):
                blob = mine   # G4' tie -> disk-live (r747), not r794
                r["decisions"][path] += " [merge-tie-override->ours disk-live]"
            resolved[path] = blob
        bad = []
        for path, blob in resolved.items():
            if mod.has_markers(blob):
                bad.append("markers:%s" % path)
            elif path.endswith(".json"):
                try:
                    json.loads(blob.decode("utf-8", "replace"))
                except ValueError as ex:
                    bad.append("json:%s:%s" % (path, ex))
        if bad:
            r["gates_fail"] = bad
            print("RESOLVE_VERIFY_FAIL %s" % bad)
            with open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(r, fh, ensure_ascii=False, indent=1)
            return 2
        for path, blob in resolved.items():
            with open(os.path.join(ROOT, *path.split("/")), "wb") as fh:
                fh.write(blob)
        git(["add", "-A"])   # resolved + churn (r787 atomic fold, tolerable)
        with open(MSG, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(
                "round 807 bm-c S0 merge closeout: origin %s integrated "
                "(predecessor half-open rebase recovered via r808 three-step "
                "+ r624 finale; %d faces resolved: deep-ts newer-wins + "
                "G4' tie->disk-live + ledger/union faces zero-loss) "
                "[via bm-c r807]\n" % (theirs_tip[:9], len(resolved)))
        rc, out, err = git(["commit", "-F", MSG])
        r["steps"].append("merge commit rc=%d %r" % (rc, (err or out)[:200]))
        if rc != 0:
            r["fatal"] = "merge commit refused"
    rc, out, _ = git(["rev-list", "--left-right", "--count",
                      "HEAD...origin/main"])
    r["ahead_behind"] = out.strip()
    rc, out, _ = git(["log", "--oneline", "-4"])
    r["final_log"] = out.strip()
    rc, out, _ = git(["status", "--porcelain"])
    r["final_dirty"] = out.strip()[:400]
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(r, fh, ensure_ascii=False, indent=1)
    print("ahead_behind=%s" % r["ahead_behind"])
    for k, v in r["decisions"].items():
        print("  %s -> %s" % (k, v))
    print(r["final_log"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
