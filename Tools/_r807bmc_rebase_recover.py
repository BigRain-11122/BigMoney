# -*- coding: utf-8 -*-
"""r807(2nd) bm-c half-open rebase recovery driver v2 (r808 three-step law).

v1 lesson: this rebase carries the `interactive` flag -> continue's
commit_staged_changes opens an EDITOR for the stopped pick's message ->
headless TERM=dumb refuses ('Terminal is dumb, but EDITOR unset'). Cure =
r808 three-step: read .git/rebase-merge/author-script (dash-name!),
export GIT_AUTHOR_* env, git commit -F .git/rebase-merge/message, then
continue advances (picks 4-6 apply internally, no editor needed).

Loop law map (pit-git-resolver-rebase.md):
- stop with UU -> r805 resolver machinery (imported) -> write+add -> the
  stopped pick still needs its commit -> three-step -> continue.
- Terminal-dumb refuse at a stop -> three-step (once per stopped-sha) ->
  continue.
- churn refuse ('must edit all merge conflicts') AFTER the stopped pick was
  already three-step committed -> r685: NO stage-then-continue (duplicate
  carrier); instead churn goes into its OWN absorb commit (-F temp msg),
  then continue advances.
Exit: 0 rebase completed | 2 mechanism failure. All steps in ONE process
(back-to-back subprocess windows <1s; r516-2 treadmill defense)."""
import importlib.util
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE = 0x08000000
RM = os.path.join(ROOT, ".git", "rebase-merge")
RECEIPT = os.path.join(ROOT, "results", "_r807bmc_rebase_recover.json")
CHURN_MSG = os.path.join(ROOT, "_r807bmc_churnmsg.txt")
EXPECT_HEAD = "638d6325f0db492a0a5ae57604c8758ddfcbbb0b"


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


def rd(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def author_env():
    env = {}
    for line in rd(os.path.join(RM, "author-script")).splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            k = k.strip()
            if k in ("GIT_AUTHOR_NAME", "GIT_AUTHOR_EMAIL", "GIT_AUTHOR_DATE"):
                env[k] = v.strip().strip("'")
    return env


def threestep(tag):
    env = author_env()
    rc, out, err = git(["commit", "-F", os.path.join(RM, "message")], env=env)
    return rc, (err or out).strip()[:200], env


def main():
    r = {"round": "r807-recover-v2", "steps": [], "notes": []}
    assert os.path.isdir(RM), "rebase-merge missing (already done?)"
    rc, out, _ = git(["rev-parse", "HEAD"])
    assert out.strip() == EXPECT_HEAD, "unexpected HEAD %s" % out.strip()
    committed = set()   # stopped-shas already three-step committed
    rc_c, out_c, err_c = None, "", ""
    guard = 0
    while os.path.isdir(RM) and guard < 14:
        guard += 1
        stopped = rd(os.path.join(RM, "stopped-sha")).strip() \
            if os.path.exists(os.path.join(RM, "stopped-sha")) else ""
        faces = uu_faces()
        if faces:
            mod = load_resolver()
            receipt = {"round": "r807-recover", "decisions": {}, "staged": [],
                       "gates": {}}
            resolved = {}
            for path in sorted(faces):
                s = faces[path]
                b2 = mod.git(["cat-file", "-p", s[2]])
                b3 = mod.git(["cat-file", "-p", s[3]])
                resolved[path] = mod.resolve_face(path, b2, b3, receipt)
            bad = []
            for path, blob in resolved.items():
                if mod.has_markers(blob):
                    bad.append("markers:%s" % path)
                elif path.endswith(".json"):
                    try:
                        json.loads(blob.decode("utf-8", "replace"))
                    except ValueError as ex:
                        bad.append("json:%s" % path)
            if bad:
                r["gates_fail"] = bad
                with open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
                    json.dump(r, fh, ensure_ascii=False, indent=1)
                print("RESOLVE_VERIFY_FAIL %s" % bad)
                return 2
            for path, blob in resolved.items():
                with open(os.path.join(ROOT, *path.split("/")), "wb") as fh:
                    fh.write(blob)
            git(["add", "-A"])   # resolved + churn (r685 tolerable fold)
            r["steps"].append("g%d stop@%s: resolved %d faces (r805 machinery)"
                              % (guard, stopped[:9], len(resolved)))
        if stopped and stopped not in committed:
            rc_c, msg_c, env_c = threestep(guard)
            r["steps"].append("g%d three-step commit @%s rc=%d %s"
                              % (guard, stopped[:9], rc_c, msg_c))
            if rc_c != 0:
                r["fatal"] = "three-step commit refused"
                break
            committed.add(stopped)
            rc_c, out_c, err_c = git(["rebase", "--continue"])
            r["steps"].append("g%d continue rc=%d %r"
                              % (guard, rc_c, (err_c or out_c)[:180]))
            continue
        # stopped-sha already committed (or no stopped-sha): classify refuse
        if rc_c == 0 and not os.path.isdir(RM):
            break
        blob = (err_c or out_c or "")
        if "Terminal is dumb" in blob or "could not commit staged" in blob:
            if stopped and stopped not in committed:
                continue   # handled next iteration by three-step branch
            r["fatal"] = "terminal-dumb after committed pick: %r" % blob[:200]
            break
        if "must edit all merge conflicts" in blob or "unstaged" in blob.lower():
            # churn refuse, pick already committed -> own absorb commit (r685)
            git(["add", "-A"])
            with open(CHURN_MSG, "w", encoding="utf-8", newline="\n") as fh:
                fh.write("round 807 recover: mid-rebase churn absorb "
                         "(daemon live faces, r685 own-carrier law)\n")
            rcx, outx, errx = git(["commit", "-F", CHURN_MSG])
            r["steps"].append("g%d churn-absorb commit rc=%d %s"
                              % (guard, rcx, (errx or outx).strip()[:150]))
            rc_c, out_c, err_c = git(["rebase", "--continue"])
            r["steps"].append("g%d continue rc=%d %r"
                              % (guard, rc_c, (err_c or out_c)[:180]))
            continue
        if "no changes added" in blob or "nothing to commit" in blob:
            rc_c, out_c, err_c = git(["rebase", "--continue"])
            r["steps"].append("g%d empty-commit retry continue rc=%d %r"
                              % (guard, rc_c, (err_c or out_c)[:180]))
            continue
        r["fatal"] = "unclassified refuse: %r" % blob[:250]
        break

    r["completed"] = not os.path.isdir(RM)
    rc, out, _ = git(["rev-parse", "HEAD"])
    r["final_head"] = out.strip()
    rc, out, _ = git(["log", "--oneline", "-10"])
    r["final_log"] = out.strip()
    rc, out, _ = git(["status", "--porcelain"])
    r["final_dirty_n"] = len([l for l in out.splitlines() if l.strip()])
    rc, out, _ = git(["rev-list", "--left-right", "--count",
                      "HEAD...origin/main"])
    r["ahead_behind"] = out.strip()
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(r, fh, ensure_ascii=False, indent=1)
    print("completed=%s head=%s ahead_behind=%s fatal=%s"
          % (r["completed"], r["final_head"][:9], r["ahead_behind"],
             r.get("fatal", "-")))
    for s in r["steps"]:
        print("  " + s)
    print("FINAL-LOG:\n" + r["final_log"])
    return 0 if r["completed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
