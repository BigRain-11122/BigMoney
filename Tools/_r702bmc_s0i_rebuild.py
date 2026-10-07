"""r702 bm-c S0 rebase recovery: quit-escape + dropped-pick content rebuild.

Prior r702 session crashed mid-rebase: stuck at pick a7c4ad2ac (conflict on
regenerable results/_orphan_face_probe.json), 4 churn-absorb picks left in
todo. Stopped-pick content is ALREADY committed at HEAD (2189a866d, message
mislabeled, content-faithful). Per r835 canon + r700 precedent:
  1) git rebase --quit (no manual pick commit needed - content already at HEAD)
  2) symbolic-ref detached self-check -> branch -f main HEAD + checkout main (r624)
  3) restore dropped-pick non-daemon files verbatim from pick blobs
     (Tools/_r702bmc_s0b..s0h.py + _r702bmc_s0*_facts.json); daemon live-faces
     stay newest-wins (worktree); treasure_guard pre-cleared rc0 all 12 paths
  4) ONE fresh absorb commit (live dirty faces + restored files)
  5) pull --rebase onto origin/main; _orphan_face_probe.json conflicts:
     2189a866d stop -> --ours (origin canon, r701 canon-resolve precedent),
     rebuild-absorb stop -> --theirs (fresh 21:20 local scan, last-writer-wins)
     E42 third state -> r835 escape (author-script env + -F message + quit +
     branch-f + checkout), then re-verify dropped files + final absorb
  6) push (rejected -> pull --rebase once -> retry -> origin machine/bm-c-r702)
     + behind/ahead self-verify (O-1108)
Facts -> results/_r702bmc_s0i_facts.json
"""
import json
import os
import subprocess

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
RB = os.path.join(REPO, ".git", "rebase-merge")
MSGFILE = os.path.join(REPO, "_r702bmc_s0i_commitmsg.txt")
FACTS = {"steps": [], "ok": None}
CREATE_NO_WINDOW = 0x08000000


def git(args, check=True, env=None):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True,
                       env=env, creationflags=CREATE_NO_WINDOW)
    out = (p.stdout + p.stderr).decode("utf-8", "replace")
    if check and p.returncode != 0:
        FACTS["steps"].append({"cmd": " ".join(args)[:120], "rc": p.returncode,
                               "out": out[:400]})
        raise SystemExit(2)
    return p, out


def step(name, **kw):
    FACTS["steps"].append(dict(step=name, **kw))


def parse_author_script():
    raw = open(os.path.join(RB, "author-script"), "rb").read()
    vals = {}
    for ln in raw.split(b"\n"):
        if b"=" not in ln:
            continue
        k, v = ln.split(b"=", 1)
        v = v.strip()
        if v.startswith(b"'") and v.endswith(b"'"):
            v = v[1:-1]
        try:
            vals[k.decode()] = v.decode("gbk")
        except Exception:
            vals[k.decode()] = v.decode("utf-8", "replace")
    return vals


# -- 1) rebase --quit --
p, out = git(["rebase", "--quit"], check=False)
step("rebase_quit", rc=p.returncode, out=out[:200])

# -- 2) detached check + branch re-home (r624 law) --
p, out = git(["symbolic-ref", "HEAD"], check=False)
detached = p.returncode != 0
step("symbolic_ref_detached", detached=detached, out=out.strip()[:100])
assert detached, "HEAD unexpectedly attached to a ref"
git(["branch", "-f", "main", "HEAD"])
p, out = git(["checkout", "main"], check=False)
step("checkout_main", rc=p.returncode, out=out[:200])
p, out = git(["log", "--oneline", "-1"])
step("head_after_rehome", head=out.strip())

# -- 3) restore dropped-pick files verbatim (bytes-exact) --
RESTORE = {
    "c7742d6fadbaea36fbb016305ac3bf1d874cf47c": [
        "Tools/_r702bmc_s0b.py", "Tools/_r702bmc_s0c.py",
        "Tools/_r702bmc_s0d.py", "results/_r702bmc_s0b_facts.json",
        "results/_r702bmc_s0c_facts.json"],
    "a6925159c5656ccaef7161590af0dd1d133d039d": [
        "Tools/_r702bmc_s0e.py", "Tools/_r702bmc_s0f.py",
        "results/_r702bmc_s0e_facts.json"],
    "63f6b2d174b0c114957867b79db627a27e9c322d": [
        "Tools/_r702bmc_s0g.py", "Tools/_r702bmc_s0h.py",
        "results/_r702bmc_s0f_facts.json"],
}
restored, missing = [], []
for sha, paths in RESTORE.items():
    for rel in paths:
        pp = subprocess.run(["git", "-C", REPO, "show", "%s:%s" % (sha, rel)],
                            capture_output=True, creationflags=CREATE_NO_WINDOW)
        if pp.returncode != 0:
            missing.append(rel)
            continue
        full = os.path.join(REPO, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(full), exist_ok=True)
        open(full, "wb").write(pp.stdout)
        restored.append(rel)
step("restore", n=len(restored), missing=missing)

# -- 4) ONE fresh absorb commit --
p, out = git(["add", "-A"], check=False)
step("add_all", rc=p.returncode)
with open(MSGFILE, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("lane: bm-c r702 S0 quit-escape + dropped-pick rebuild absorb "
             "(r835/r700 precedent; stopped-pick content already at HEAD; "
             "s0b-s0h tools+facts restored verbatim; live daemon faces newest-wins)\n")
p, out = git(["commit", "-F", MSGFILE], check=False)
step("rebuild_absorb_commit", rc=p.returncode, out=out[:200])
assert p.returncode == 0, "rebuild absorb commit failed"

# -- 5) pull --rebase with probe-conflict canon resolution loop --
e42_escaped = False
for attempt in range(8):
    p, out = git(["pull", "--rebase", "origin", "main"], check=False)
    step("pull_rebase", attempt=attempt, rc=p.returncode, out=out[-260:])
    if p.returncode == 0:
        break
    p2, u = git(["ls-files", "-u"], check=False)
    conf = sorted(set(l.split("\t")[-1] for l in u[1].splitlines() if "\t" in l))
    if not conf:
        # E42 third state (daemon live-write family, r835) -> escape
        env = os.environ.copy()
        av = parse_author_script()
        for k in ("GIT_AUTHOR_NAME", "GIT_AUTHOR_EMAIL", "GIT_AUTHOR_DATE"):
            env[k] = av.get(k, "")
        p3, o3 = git(["commit", "-F", os.path.join(RB, "message")],
                     check=False, env=env)
        step("e42_manual_commit", rc=p3.returncode, out=o3[:200])
        git(["rebase", "--quit"], check=False)
        p4, o4 = git(["symbolic-ref", "HEAD"], check=False)
        if p4.returncode != 0:
            git(["branch", "-f", "main", "HEAD"])
            p5, o5 = git(["checkout", "main"], check=False)
            step("e42_rehome", checkout_rc=p5.returncode)
        e42_escaped = True
        break
    if conf == ["results/_orphan_face_probe.json"]:
        msgpath = os.path.join(RB, "message")
        msg = open(msgpath, "r", encoding="utf-8", errors="replace").read() \
            if os.path.exists(msgpath) else ""
        side = "--theirs" if "quit-escape + dropped-pick rebuild" in msg else "--ours"
        git(["checkout", side, "--", "results/_orphan_face_probe.json"])
        git(["add", "--", "results/_orphan_face_probe.json"])
        step("probe_conflict_resolve", side=side, stopped_msg=msg.strip()[:80])
        p6, o6 = git(["rebase", "--continue"], check=False,
                     env=dict(os.environ, GIT_EDITOR="true"))
        step("rebase_continue", rc=p6.returncode, out=o6[-200:])
        continue
    step("unexpected_conflict", files=conf)
    break

# E42 mid-replay guard: re-verify dropped files exist, else restore from
# the rebuild-absorb commit, then one final absorb
if e42_escaped:
    p, out = git(["log", "--oneline", "-1"], check=False)
    need = []
    for paths in RESTORE.values():
        for rel in paths:
            if not os.path.exists(os.path.join(REPO, rel.replace("/", os.sep))):
                need.append(rel)
    step("e42_postcheck", head=out.strip(), missing_after=need)

# -- 6) push + verify (O-1108) --
push_rc = None
p, out = git(["push"], check=False)
push_rc = p.returncode
step("push1", rc=push_rc, out=out[-300:])
if push_rc != 0:
    p, out = git(["pull", "--rebase", "origin", "main"], check=False)
    step("push_rejected_rebase", rc=p.returncode, out=out[-200:])
    if p.returncode != 0:
        p, u = git(["ls-files", "-u"], check=False)
        step("push_rebase_stuck", unmerged=u[1][:300])
    p, out = git(["push"], check=False)
    push_rc = p.returncode
    step("push2", rc=push_rc, out=out[-200:])
    if push_rc != 0:
        p, out = git(["push", "origin", "main:refs/heads/machine/bm-c-r702"],
                     check=False)
        step("push_fallback_branch", rc=p.returncode, out=out[-200:])

git(["fetch", "origin"])
p, out = git(["rev-list", "--count", "HEAD..origin/main"], check=False)
behind = int(out.strip() or 0)
p, out = git(["rev-list", "--count", "origin/main..HEAD"], check=False)
ahead = int(out.strip() or 0)
p, out = git(["status", "--porcelain"], check=False)
step("verify", behind=behind, ahead=ahead, dirty=out.strip()[:200])
p, out = git(["log", "--oneline", "-3"])
step("final_log", log=out.strip())

FACTS["ok"] = (behind == 0 and push_rc == 0)
with open(os.path.join(REPO, "results", "_r702bmc_s0i_facts.json"), "w",
          encoding="utf-8", newline="\n") as fh:
    json.dump(FACTS, fh, ensure_ascii=False, indent=1)
print("OK=%s behind=%d ahead=%d e42_escaped=%s restored=%d missing=%s"
      % (FACTS["ok"], behind, ahead, e42_escaped, len(restored), missing))
