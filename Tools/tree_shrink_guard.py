"""Tree-shrink tripwire: a commit must not silently lose most of the repo.

Why this exists (r1133 bm-a, live-fire P0): the group repo's tip ceebc703 was
built from a partial index, so its tree carried only the two receipt files it
meant to add and dropped the other 3,494 files -- docs/decisions.md,
docs/orders.md, all of cph4/. Nothing in the repo noticed; the damage was found
by a consumer that tried to read decisions.md and got "exists on disk, but not
in origin/main". A commit-tree built from an empty or partial index is invisible
to hooks (it bypasses pre-commit entirely) and produces a perfectly valid,
successfully pushed commit whose only symptom is a smaller tree.

The check is deliberately dumb and cheap: count files in a commit's tree and in
its first parent's tree. A drop larger than the allowed budget is a red flag,
because normal work never deletes thousands of files at once.

Usage
  python Tools/tree_shrink_guard.py check --repo <path> [--commits N]
                                          [--max-drop N] [--json]
  python Tools/tree_shrink_guard.py selftest

Exit codes: 0 clean, 1 shrink detected, 2 mechanism failure (git unreadable).
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

DEFAULT_COMMITS = 20
DEFAULT_MAX_DROP = 0
# Deliberate deletions are legal, but they have to be declared by name. A
# declaration that does not match the commit's actual deletion set byte for
# byte is NOT an excuse -- it stays red, so "declare everything" cannot be used
# to silence the tripwire (r1165: r1164 dropped three scratch files and the guard
# would have stayed red for twenty commits, inviting someone to just raise
# --max-drop, which is the one fix that destroys the mechanism).
DECLARATIONS_PATH = os.path.join("fleet", "tree_shrink_declarations.json")


def _git(repo: str, *args: str) -> str:
    p = subprocess.run(["git", "-C", repo] + list(args), capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} rc={p.returncode}: {p.stderr.strip()}")
    return p.stdout


def file_count(repo: str, rev: str) -> int:
    """Number of blobs (not subtrees) in <rev>'s tree."""
    try:
        out = _git(repo, "ls-tree", "-r", "--name-only", rev)
    except RuntimeError as e:
        # A root commit has no parent to compare against; anything else is real.
        raise
    return len([ln for ln in out.splitlines() if ln.strip()])


def dropped_paths(repo: str, sha: str, parent: str) -> list[str]:
    """Paths a commit deleted relative to <parent> (D entries only, sorted)."""
    out = _git(repo, "diff-tree", "-r", "--no-commit-id", "--name-status", parent, sha)
    paths = []
    for ln in out.splitlines():
        parts = ln.split("\t")
        if len(parts) >= 2 and parts[0].strip().startswith("D"):
            paths.append(parts[1].strip().replace("\\", "/"))
    return sorted(paths)


def load_declarations(repo: str) -> dict:
    """{sha_prefix_lower: {"paths": [...], "by": ..., "reason": ...}}.

    A missing file is the normal state. A malformed file returns {} plus an
    error string: the caller reports it, and nothing gets cleared by accident.
    """
    path = os.path.join(repo, DECLARATIONS_PATH)
    if not os.path.isfile(path):
        return {"declarations": {}, "error": None}
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except (OSError, ValueError) as e:
        return {"declarations": {}, "error": f"unreadable declaration file: {e}"}
    out = {}
    for d in raw.get("declarations") or []:
        sha = str(d.get("commit", "")).strip().lower()
        if not sha:
            continue
        out[sha] = {
            "paths": sorted(str(p).replace("\\", "/") for p in (d.get("paths") or [])),
            "by": d.get("by"),
            "reason": d.get("reason"),
        }
    return {"declarations": out, "error": None}


def match_declaration(decl: dict, sha: str, actual: list[str]) -> tuple[bool, str]:
    """Exact-set match: the declared paths must BE the deleted paths."""
    hit = decl.get(sha.lower()) or decl.get(sha.lower()[:12])
    if not hit:
        return False, "undeclared"
    if hit["paths"] == [p.replace("\\", "/") for p in actual]:
        return True, "declared"
    return False, (f"declaration mismatch: declared {len(hit['paths'])} "
                   f"path(s), commit deleted {len(actual)}")


def parents(repo: str, rev: str) -> list[str]:
    out = _git(repo, "rev-list", "--parents", "-n", "1", rev).strip().split()
    return out[1:]


def scan(repo: str, commits: int = DEFAULT_COMMITS,
         max_drop: int = DEFAULT_MAX_DROP, rev: str = "HEAD") -> dict:
    rows = []
    out = _git(repo, "rev-list", f"-n{commits}", rev).split()
    for sha in out:
        par = parents(repo, sha)
        if not par:
            rows.append({"commit": sha[:12], "files": file_count(repo, sha),
                         "parent": None, "drop": 0, "root": True,
                         "subject": _git(repo, "log", "-1", "--format=%s", sha).strip()[:120]})
            continue
        n_cur = file_count(repo, sha)
        n_par = file_count(repo, par[0])
        rows.append({"commit": sha[:12], "files": n_cur, "parent": par[0][:12],
                     "parent_files": n_par, "drop": n_par - n_cur,
                     "subject": _git(repo, "log", "-1", "--format=%s", sha).strip()[:120]})
    # A shrink that was later repaired is history, not a live defect: the tip
    # already carries the files again. Only an UNREPAIRED shrink is a failure,
    # otherwise the guard would stay red until the bad commit scrolled out of
    # the window and nobody would read it any more.
    tip_files = file_count(repo, rev)
    decl = load_declarations(repo)
    hits = []
    for r in rows:
        if r["drop"] <= max_drop:
            continue
        r = dict(r)
        r["repaired"] = tip_files >= r["parent_files"]
        hits.append(r)
    live, declared = [], []
    for r in hits:
        if r["repaired"]:
            continue
        full = _git(repo, "rev-parse", r["commit"]).strip()
        par = parents(repo, full)
        actual = dropped_paths(repo, full, par[0]) if par else []
        ok, why = match_declaration(decl["declarations"], full, actual)
        r["declaration"] = why
        r["dropped_paths"] = actual
        if ok:
            declared.append(r)
        else:
            live.append(r)
    return {"repo": os.path.abspath(repo), "scanned": len(rows), "rev": rev,
            "tip_files": tip_files, "max_drop_allowed": max_drop,
            "shrinks": hits, "declared": declared, "unrepaired": live,
            "declaration_error": decl["error"], "rows": rows,
            "clean": not live}


def cmd_check(args) -> int:
    try:
        res = scan(args.repo, args.commits, args.max_drop, args.rev)
    except RuntimeError as e:
        print(f"tree-shrink guard: mechanism failure: {e}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
    else:
        if res.get("declaration_error"):
            print(f"tree-shrink guard: {res['declaration_error']} "
                  f"(nothing else was cleared by it)")
        if res["clean"]:
            extra = (f" ({len(res['shrinks'])} repaired shrink(s) earlier in history)"
                     if res["shrinks"] else "")
            if res["declared"]:
                extra += (f"; {len(res['declared'])} declared deletion(s), "
                          f"paths match exactly")
            print(f"tree-shrink guard CLEAN: {res['scanned']} commit(s) in "
                  f"{res['repo']}, tip has {res['tip_files']} file(s), "
                  f"no unrepaired loss > {args.max_drop}{extra}")
        else:
            print(f"tree-shrink guard SHRINK: {len(res['unrepaired'])} commit(s) "
                  f"lost files and the tip has not recovered")
            for r in res["unrepaired"]:
                print(f"  {r['commit']} {r['parent_files']} -> {r['files']} "
                      f"(-{r['drop']}) {r['subject']}")
                if r.get("dropped_paths"):
                    print(f"    dropped: {', '.join(r['dropped_paths'])}")
                if r.get("declaration") and r["declaration"] != "undeclared":
                    print(f"    declaration: {r['declaration']}")
    return 0 if res["clean"] else 1


# --------------------------------------------------------------------------
# group face: the incident this guard exists for happened in the group repo, so
# the check must be able to reach it without hard-coding one machine's layout.
# --------------------------------------------------------------------------

def find_group_tree(start: str) -> str | None:
    """Walk up from <start> looking for a git repo that owns cph4/ (the group).

    Returns the repo path, or None when this machine has no group tree (bm-b and
    bm-c do not always carry one -- that is an honest no-op, not a failure).
    """
    cur = os.path.abspath(start)
    for _ in range(5):
        cur = os.path.dirname(cur)
        if not cur or cur == os.path.dirname(cur):
            break
        if os.path.isdir(os.path.join(cur, ".git")) and \
                os.path.isdir(os.path.join(cur, "cph4")):
            return cur
    return None


def cmd_check_group(args) -> int:
    repo = args.repo and os.path.abspath(args.repo) or find_group_tree(os.getcwd())
    if not repo:
        print("tree-shrink guard: no group tree on this machine -- honest no-op")
        return 0
    # prefer the fetched origin tip: the local branch may be behind the damage
    rev = "origin/main"
    try:
        _git(repo, "rev-parse", "--verify", rev)
    except RuntimeError:
        rev = "HEAD"
    try:
        res = scan(repo, args.commits, args.max_drop, rev)
    except RuntimeError as e:
        print(f"tree-shrink guard: mechanism failure on {repo}: {e}", file=sys.stderr)
        return 2
    if res["clean"]:
        tail = (f" ({len(res['shrinks'])} repaired shrink(s) in history)"
                if res["shrinks"] else "")
        print(f"tree-shrink guard CLEAN: group {rev} @ {repo}, {res['scanned']} "
              f"commit(s), tip {res['tip_files']} file(s){tail}")
    else:
        print(f"tree-shrink guard SHRINK: group {rev} @ {repo}")
        for r in res["unrepaired"]:
            print(f"  {r['commit']} {r['parent_files']} -> {r['files']} "
                  f"(-{r['drop']}) {r['subject']}")
    return 0 if res["clean"] else 1


# --------------------------------------------------------------------------
# gate wiring: a guard that is not installed is a document, not a gate. This
# checks that both repos' push gates exist, are LF, and carry the same rule --
# and that this machine's installed pre-push is the committed source (drift
# check). Behavioural proof lives in selftest L8-L12, which pushes for real.
# --------------------------------------------------------------------------

GATE_TOKENS = ("TREE-SHRINK-GATE", "MAX_DROP", "MAX_PCT", "count_files")


def _read_norm(path: str) -> str:
    with open(path, "rb") as f:
        return f.read().decode("utf-8", errors="replace").replace("\r\n", "\n")


def cmd_check_gates(args) -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    repo = os.path.dirname(here)
    problems: list[str] = []

    canon = os.path.join(here, "git-hooks", "tree-shrink-gate.sh")
    hook_src = os.path.join(here, "git-hooks", "pre-push")
    installed = os.path.join(repo, ".git", "hooks", "pre-push")
    for p in (canon, hook_src):
        if not os.path.isfile(p):
            problems.append(f"missing committed gate file: {p}")
    if os.path.isfile(canon):
        txt = _read_norm(canon)
        missing = [t for t in GATE_TOKENS if t not in txt]
        if missing:
            problems.append(f"{os.path.basename(canon)} lacks tokens {missing}")
        if "\r" in open(canon, "rb").read().decode("utf-8", "replace"):
            problems.append("gate file carries CR bytes (sh will break)")
    if os.path.isfile(hook_src) and "tree-shrink-gate.sh" not in _read_norm(hook_src):
        problems.append("bigmoney pre-push does not call the tree-shrink gate")
    wired = os.path.isfile(installed) and os.path.isfile(hook_src) and \
        _read_norm(installed) == _read_norm(hook_src)
    if not wired:
        problems.append("installed .git/hooks/pre-push differs from the committed "
                        "source (run Tools/register_prepush_claw.ps1)")

    grp = find_group_tree(os.getcwd())
    group_state = "no group tree on this machine -- honest no-op"
    if grp:
        hp = ""
        try:
            hp = _git(grp, "config", "--get", "core.hooksPath").strip()
        except RuntimeError:
            hp = ""
        ghook = os.path.join(grp, hp.replace("/", os.sep), "pre-push") if hp else ""
        if not hp:
            problems.append(f"group repo has no core.hooksPath, so a committed "
                            f"hook would be ignored: {grp}")
        elif not os.path.isfile(ghook):
            problems.append(f"group push gate missing: {ghook}")
        else:
            gtxt = _read_norm(ghook)
            missing = [t for t in GATE_TOKENS if t not in gtxt]
            if missing:
                problems.append(f"group push gate lacks tokens {missing}")
            if "\r" in open(ghook, "rb").read().decode("utf-8", "replace"):
                problems.append("group push gate carries CR bytes (sh will break)")
            group_state = f"group gate present at {ghook} (hooksPath={hp})"

    if problems:
        print("tree-shrink gates BROKEN:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"tree-shrink gates wired: bigmoney pre-push installed+matches source, "
          f"canonical gate {len(GATE_TOKENS)} tokens present | {group_state}")
    return 0


# --------------------------------------------------------------------------
# selftest: a fixture repo where the second commit is built from a partial
# index, exactly reproducing the ceebc703 failure mode.
# --------------------------------------------------------------------------

def _fixture_repo(root: str) -> None:
    env = dict(os.environ, GIT_AUTHOR_NAME="tsg", GIT_AUTHOR_EMAIL="tsg@local",
               GIT_COMMITTER_NAME="tsg", GIT_COMMITTER_EMAIL="tsg@local")


def _g(repo: str, *args: str) -> str:
    p = subprocess.run(
        ["git", "-C", repo] + list(args), capture_output=True, text=True,
        encoding="utf-8", errors="replace",
        env=dict(os.environ, GIT_AUTHOR_NAME="tsg", GIT_AUTHOR_EMAIL="tsg@local",
                 GIT_COMMITTER_NAME="tsg", GIT_COMMITTER_EMAIL="tsg@local",
                 GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull))
    if p.returncode != 0:
        raise RuntimeError(f"fixture git {' '.join(args)} rc={p.returncode}: {p.stderr}")
    return p.stdout.strip()


def cmd_selftest() -> int:
    tmp = tempfile.mkdtemp(prefix="tsg-")
    legs: list[tuple[str, bool, str]] = []

    def leg(name: str, ok: bool, detail: str = "") -> None:
        legs.append((name, ok, detail))
        print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}")

    try:
        repo = os.path.join(tmp, "repo")
        os.makedirs(repo)
        _g(repo, "init", "-q", "-b", "main")

        # L1: a normal commit does not trip the guard.
        for i in range(6):
            with open(os.path.join(repo, f"f{i}.txt"), "w", encoding="utf-8") as f:
                f.write(f"{i}\n")
        _g(repo, "add", "-A")
        _g(repo, "commit", "-qm", "six files")
        res = scan(repo, commits=1)
        leg("L1 clean history stays clean", res["clean"],
            f"files={res['rows'][0]['files']}")

        # L2: reproduce the failure -- commit-tree from a PARTIAL index.
        good = _g(repo, "rev-parse", "HEAD")
        idx = os.path.join(tmp, "partial.index")
        env = dict(os.environ, GIT_INDEX_FILE=idx,
                   GIT_AUTHOR_NAME="tsg", GIT_AUTHOR_EMAIL="tsg@local",
                   GIT_COMMITTER_NAME="tsg", GIT_COMMITTER_EMAIL="tsg@local")
        # only the new file, nothing else -> exactly the ceebc703 shape
        with open(os.path.join(repo, "only.txt"), "w", encoding="utf-8") as f:
            f.write("only\n")
        subprocess.run(["git", "-C", repo, "hash-object", "-w", "only.txt"],
                       capture_output=True, text=True, env=env)
        blob = _g(repo, "hash-object", "-w", "only.txt")
        subprocess.run(["git", "-C", repo, "read-tree", "--empty"], env=env,
                       capture_output=True, text=True)
        subprocess.run(["git", "-C", repo, "update-index", "--add", "--cacheinfo",
                        f"100644,{blob},only.txt"], env=env, capture_output=True, text=True)
        tree = _g_env(repo, env, "write-tree")
        bad = _g_env_commit(repo, env, tree, good)
        _g(repo, "reset", "-q", "--hard", bad)

        res2 = scan(repo, commits=1)
        leg("L2 partial-index commit is caught", not res2["clean"],
            f"drop={res2['rows'][0]['drop']} files={res2['rows'][0]['files']}")
        # 6 files -> 1 file, so the drop is 5: the surviving new file is not lost.
        leg("L3 the drop equals parent_files - files", res2["shrinks"][0]["drop"] == 5,
            f"drop={res2['shrinks'][0]['drop']} parent={res2['shrinks'][0]['parent_files']}")

        # L4: the budget lets an intentional bulk deletion through.
        res3 = scan(repo, commits=1, max_drop=10)
        leg("L4 an explicit budget clears smaller deletions", res3["clean"],
            f"max_drop=10 drop={res3['rows'][0]['drop']}")

        # L5: a root commit has no parent and must not be reported as a shrink.
        root = _g(repo, "rev-list", "--max-parents=0", "HEAD").split()[-1]
        res4 = scan(repo, commits=100, rev=root)
        row = [r for r in res4["rows"] if r["commit"] == root[:12]][0]
        leg("L5 root commit is not a shrink", row.get("root") is True and row["drop"] == 0,
            f"files={row['files']}")

        # L6: unreadable rev is a mechanism failure (rc2), not a fake pass.
        try:
            scan(repo, commits=1, rev="no-such-ref")
            ok = False
        except RuntimeError:
            ok = True
        leg("L6 unknown rev raises instead of passing", ok)

        # L7: a repaired shrink is recorded but is not a live failure -- the tip
        # already carries the files again, so this must not stay red forever.
        # Repair shape = the real one (r1133): a forward commit whose tree is the
        # good tree again, parented on the bad commit.
        idx2 = os.path.join(tmp, "repair.index")
        env2 = dict(env, GIT_INDEX_FILE=idx2)
        subprocess.run(["git", "-C", repo, "read-tree", good], env=env2,
                       capture_output=True, text=True)
        tree2 = _g_env(repo, env2, "write-tree")
        repair = _g_env_commit(repo, env2, tree2, bad)
        _g(repo, "reset", "-q", "--hard", repair)
        res5 = scan(repo, commits=5)
        leg("L7 repaired shrink is history, not a live defect",
            res5["clean"] and len(res5["shrinks"]) == 1
            and res5["shrinks"][0]["repaired"] is True,
            f"clean={res5['clean']} hits={len(res5['shrinks'])} tip={res5['tip_files']}")

        # L13-L17: a deliberate deletion is legal only when it is declared by
        # name, and only when the declared set IS the deleted set. Everything
        # short of an exact match must stay red, otherwise "declare it" would be
        # a cheaper way to silence the tripwire than raising --max-drop.
        drepo = os.path.join(tmp, "declrepo")
        os.makedirs(drepo)
        _g(drepo, "init", "-q", "-b", "main")
        for i in range(4):
            with open(os.path.join(drepo, f"d{i}.txt"), "w", encoding="utf-8") as f:
                f.write(f"{i}\n")
        _g(drepo, "add", "-A")
        _g(drepo, "commit", "-qm", "four files")
        os.makedirs(os.path.join(drepo, "fleet"), exist_ok=True)

        def write_decl(entries) -> None:
            with open(os.path.join(drepo, DECLARATIONS_PATH), "w", encoding="utf-8") as f:
                json.dump({"schema": 1, "declarations": entries}, f, indent=1)

        os.remove(os.path.join(drepo, "d3.txt"))
        _g(drepo, "add", "-A")
        _g(drepo, "commit", "-qm", "drop one scratch file")
        dsha = _g(drepo, "rev-parse", "HEAD")
        res6 = scan(drepo, commits=3)
        leg("L13 an undeclared deletion is still a defect",
            not res6["clean"] and res6["unrepaired"][0]["dropped_paths"] == ["d3.txt"],
            f"clean={res6['clean']} paths={res6['unrepaired'][0]['dropped_paths'] if res6['unrepaired'] else None}")

        write_decl([{"commit": dsha, "paths": ["d3.txt"], "by": "fixture",
                     "reason": "scratch"}])
        res7 = scan(drepo, commits=3)
        leg("L14 an exact declaration clears it",
            res7["clean"] and len(res7["declared"]) == 1
            and res7["unrepaired"] == [], f"clean={res7['clean']} declared={len(res7['declared'])}")

        write_decl([{"commit": dsha, "paths": ["d2.txt"], "by": "fixture",
                     "reason": "wrong path"}])
        res8 = scan(drepo, commits=3)
        leg("L15 a declaration naming a different path does not clear it",
            not res8["clean"], f"clean={res8['clean']}")

        write_decl([{"commit": dsha, "paths": ["d2.txt", "d3.txt"], "by": "fixture",
                     "reason": "superset"}])
        res9 = scan(drepo, commits=3)
        leg("L16 a declaration that also claims a surviving file does not clear it",
            not res9["clean"], f"clean={res9['clean']}")

        with open(os.path.join(drepo, DECLARATIONS_PATH), "w", encoding="utf-8") as f:
            f.write("{not json")
        res10 = scan(drepo, commits=3)
        leg("L17 a corrupt declaration file is reported and clears nothing",
            not res10["clean"] and "unreadable declaration file" in str(res10["declaration_error"]),
            f"clean={res10['clean']} err={res10['declaration_error']}")

        # L8-L11: the real gate, exercised through git's own hook machinery
        # (a check the tool can compute is not the same thing as a push that
        # gets refused -- r1294: installed is not declared).
        here = os.path.dirname(os.path.abspath(__file__))
        canon = os.path.join(here, "git-hooks", "tree-shrink-gate.sh")
        grp = find_group_tree(os.getcwd())
        group = os.path.join(grp, "Tools", "hooks", "pre-push") if grp else ""

        def push_fixture(tag: str, hook_src: str) -> tuple[str, str]:
            base = os.path.join(tmp, tag)
            origin = os.path.join(base, "origin.git")
            work = os.path.join(base, "work")
            os.makedirs(work)
            _g(base, "init", "-q", "--bare", origin)
            _g(work, "init", "-q", "-b", "main")
            _g(work, "remote", "add", "origin", origin)
            for i in range(40):
                with open(os.path.join(work, f"f{i}.txt"), "w", encoding="utf-8") as f:
                    f.write(f"{i}\n")
            _g(work, "add", "-A")
            _g(work, "commit", "-qm", "forty files")
            _g(work, "push", "-q", "origin", "main")
            hook_dir = os.path.join(work, ".git", "hooks")
            shutil.copyfile(hook_src, os.path.join(hook_dir, "pre-push"))
            os.chmod(os.path.join(hook_dir, "pre-push"), 0o755)
            return origin, work

        def partial_commit(work: str, base: str) -> str:
            good = _g(work, "rev-parse", "HEAD")
            pidx = os.path.join(base, "partial.index")
            penv = dict(os.environ, GIT_INDEX_FILE=pidx,
                        GIT_AUTHOR_NAME="tsg", GIT_AUTHOR_EMAIL="tsg@local",
                        GIT_COMMITTER_NAME="tsg", GIT_COMMITTER_EMAIL="tsg@local")
            with open(os.path.join(work, "receipt.md"), "w", encoding="utf-8") as f:
                f.write("receipt\n")
            pblob = _g(work, "hash-object", "-w", "receipt.md")
            subprocess.run(["git", "-C", work, "read-tree", "--empty"], env=penv,
                           capture_output=True, text=True)
            subprocess.run(["git", "-C", work, "update-index", "--add", "--cacheinfo",
                            f"100644,{pblob},receipt.md"], env=penv,
                           capture_output=True, text=True)
            ptree = _g_env(work, penv, "write-tree")
            bad = _g_env_commit(work, penv, ptree, good)
            _g(work, "reset", "-q", "--hard", bad)
            return bad, good

        # L8: an ordinary push passes the gate.
        origin, work = push_fixture("canon_clean", canon)
        with open(os.path.join(work, "note.txt"), "w", encoding="utf-8") as f:
            f.write("note\n")
        _g(work, "add", "-A")
        _g(work, "commit", "-qm", "add one file")
        rc = _g_rc(work, "push", "-q", "origin", "main")
        leg("L8 an ordinary push passes the gate", rc == 0, f"rc={rc}")

        # L9: the ceebc703 shape is refused by the push itself.
        before = _g(origin, "rev-parse", "main")
        bad, good = partial_commit(work, os.path.dirname(origin))
        rc, err = _g_rc_err(work, "push", "origin", "main")
        after = _g(origin, "rev-parse", "main")
        leg("L9 a partial-index push is refused",
            rc != 0 and "TREE-SHRINK-GATE" in err and before == after,
            f"rc={rc} origin_same={before == after}")

        # L10: the documented escape hatch still works.
        rc = _g_rc(work, "push", "-q", "--no-verify", "origin", "main")
        leg("L10 --no-verify still allows a deliberate bulk deletion", rc == 0,
            f"rc={rc}")

        # L11: a shrink that already sits in HISTORY and was repaired must not
        # wedge the repo -- only commits being introduced are judged. This is
        # the live group shape (ceebc703 repaired by 0aa00453).
        ridx = os.path.join(os.path.dirname(origin), "repair.index")
        renv = dict(os.environ, GIT_INDEX_FILE=ridx,
                    GIT_AUTHOR_NAME="tsg", GIT_AUTHOR_EMAIL="tsg@local",
                    GIT_COMMITTER_NAME="tsg", GIT_COMMITTER_EMAIL="tsg@local")
        subprocess.run(["git", "-C", work, "read-tree", good], env=renv,
                       capture_output=True, text=True)
        rtree = _g_env(work, renv, "write-tree")
        repair = _g_env_commit(work, renv, rtree, bad)
        _g(work, "reset", "-q", "--hard", repair)
        with open(os.path.join(work, "after.txt"), "w", encoding="utf-8") as f:
            f.write("after\n")
        _g(work, "add", "-A")
        _g(work, "commit", "-qm", "work after the repair")
        rc = _g_rc(work, "push", "-q", "origin", "main")
        rc2 = _g_rc(work, "push", "-q", "origin", "main:refs/heads/tsg-repair")
        leg("L11 repaired history does not wedge later pushes", rc == 0 and rc2 == 0,
            f"rc={rc} new_branch_rc={rc2}")

        # L12: the group-vendored copy blocks the same shape (no drift between
        # the two repos' rules).
        if os.path.isfile(group):
            origin2, work2 = push_fixture("group_clean", group)
            before2 = _g(origin2, "rev-parse", "main")
            partial_commit(work2, os.path.dirname(origin2))
            rc2, err2 = _g_rc_err(work2, "push", "origin", "main")
            leg("L12 the group-vendored hook blocks the same shape",
                rc2 != 0 and "TREE-SHRINK-GATE" in err2
                and before2 == _g(origin2, "rev-parse", "main"), f"rc={rc2}")
        else:
            leg("L12 the group-vendored hook blocks the same shape", True,
                "no group tree on this machine -- honest skip")
    except Exception as e:  # fixture failure is a real failure
        leg("fixture", False, str(e))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    n_pass = sum(1 for _, ok, _ in legs if ok)
    print(f"\nselftest: {n_pass}/{len(legs)} PASS")
    return 0 if n_pass == len(legs) else 1


def _g_rc(repo: str, *args: str) -> int:
    return _g_rc_err(repo, *args)[0]


def _g_rc_err(repo: str, *args: str) -> tuple[int, str]:
    p = subprocess.run(
        ["git", "-C", repo] + list(args), capture_output=True, text=True,
        encoding="utf-8", errors="replace",
        env=dict(os.environ, GIT_AUTHOR_NAME="tsg", GIT_AUTHOR_EMAIL="tsg@local",
                 GIT_COMMITTER_NAME="tsg", GIT_COMMITTER_EMAIL="tsg@local",
                 GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull))
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def _g_env(repo: str, env: dict, *args: str) -> str:
    p = subprocess.run(["git", "-C", repo] + list(args), capture_output=True,
                       text=True, encoding="utf-8", errors="replace", env=env)
    if p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} rc={p.returncode}: {p.stderr}")
    return p.stdout.strip()


def _g_env_commit(repo: str, env: dict, tree: str, parent: str) -> str:
    p = subprocess.run(["git", "-C", repo, "commit-tree", tree, "-p", parent, "-m",
                        "partial index commit"], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env)
    if p.returncode != 0:
        raise RuntimeError(p.stderr)
    return p.stdout.strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="scan a repo's recent commits for tree shrink")
    c.add_argument("--repo", default=".", help="repo path (default: cwd)")
    c.add_argument("--commits", type=int, default=DEFAULT_COMMITS)
    c.add_argument("--max-drop", type=int, default=DEFAULT_MAX_DROP,
                   help="files a commit may delete before it is flagged (default 0)")
    c.add_argument("--rev", default="HEAD", help="tip to walk back from (default HEAD)")
    c.add_argument("--json", action="store_true")
    c.set_defaults(func=cmd_check)
    g = sub.add_parser("check_group", help="scan the group repo's origin/main tip")
    g.add_argument("--repo", default=None, help="group repo path (default: auto-detect)")
    g.add_argument("--commits", type=int, default=8)
    g.add_argument("--max-drop", type=int, default=DEFAULT_MAX_DROP)
    g.set_defaults(func=cmd_check_group)
    s = sub.add_parser("selftest", help="offline fixture tests")
    s.set_defaults(func=lambda a: cmd_selftest())
    w = sub.add_parser("check_gates", help="verify both repos' push gates are installed")
    w.set_defaults(func=cmd_check_gates)
    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
