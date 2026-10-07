"""r702 bm-c S0 continuation: churn absorb + pull --rebase + push.

Prior script (_r702bmc_s0i_rebuild.py) completed quit-escape + rehome +
dropped-pick restore + rebuild absorb (HEAD a52ac03c3 on main), then died
on a tuple-unpack bug at the pull --rebase stage (rebase never started:
daemon live-write faces dirtied the tree between add -A and pull).
This continuation: absorb -> pull --rebase (probe conflicts canon-resolved:
2189a866d stop --ours=origin canon / rebuild stop --theirs=fresh local scan,
r701 precedent) -> push -> O-1108 verify. Facts appended to
results/_r702bmc_s0i_facts.json (key s0j)."""
import json
import os
import subprocess

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
RB = os.path.join(REPO, ".git", "rebase-merge")
MSGFILE = os.path.join(REPO, "_r702bmc_s0j_commitmsg.txt")
FACTSPATH = os.path.join(REPO, "results", "_r702bmc_s0i_facts.json")
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


def unmerged_files():
    p, u = git(["ls-files", "-u"], check=False)
    return sorted(set(l.split("\t")[-1] for l in u.splitlines() if "\t" in l))


def absorb(label):
    git(["add", "-A"])
    p, out = git(["status", "--porcelain"], check=False)
    p, o = git(["commit", "--amend", "--no-edit"], check=False)
    step("absorb_" + label, rc=p.returncode,
         head=(git(["log", "--oneline", "-1"])[1].strip()))


def unmerged_files2():
    return unmerged_files()


# -- 1) absorb current churn into the unpushed rebuild absorb commit --
absorb("pre_rebase")

# -- 2) pull --rebase loop --
e42_escaped = False
for attempt in range(10):
    p, out = git(["pull", "--rebase", "origin", "main"], check=False)
    step("pull_rebase", attempt=attempt, rc=p.returncode, out=out.strip()[-260:])
    if p.returncode == 0:
        break
    conf = unmerged_files2()
    in_rebase = os.path.isdir(RB)
    if not conf and not in_rebase:
        # rebase refused to start: fresh daemon churn -> absorb + retry
        absorb("start_refused_%d" % attempt)
        continue
    if not conf and in_rebase:
        # E42 third state (r835) -> escape
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
        msg = ""
        if os.path.exists(msgpath):
            msg = open(msgpath, "r", encoding="utf-8", errors="replace").read()
        side = "--theirs" if "quit-escape + dropped-pick rebuild" in msg else "--ours"
        git(["checkout", side, "--", "results/_orphan_face_probe.json"])
        git(["add", "--", "results/_orphan_face_probe.json"])
        step("probe_conflict_resolve", side=side, stopped_msg=msg.strip()[:80])
        p6, o6 = git(["rebase", "--continue"], check=False,
                     env=dict(os.environ, GIT_EDITOR="true"))
        step("rebase_continue", rc=p6.returncode, out=o6.strip()[-200:])
        continue
    step("unexpected_conflict", files=conf)
    break

# -- 3) push + verify (O-1108) --
push_rc = None
p, out = git(["push"], check=False)
push_rc = p.returncode
step("push1", rc=push_rc, out=out.strip()[-300:])
if push_rc != 0:
    p, out = git(["pull", "--rebase", "origin", "main"], check=False)
    step("push_rejected_rebase", rc=p.returncode, out=out.strip()[-200:])
    if p.returncode != 0:
        step("push_rebase_stuck", unmerged=unmerged_files2())
    p, out = git(["push"], check=False)
    push_rc = p.returncode
    step("push2", rc=push_rc, out=out.strip()[-200:])
    if push_rc != 0:
        p, out = git(["push", "origin", "main:refs/heads/machine/bm-c-r702"],
                     check=False)
        step("push_fallback_branch", rc=p.returncode, out=out.strip()[-200:])

git(["fetch", "origin"])
p, out = git(["rev-list", "--count", "HEAD..origin/main"], check=False)
behind = int(out.strip() or 0)
p, out = git(["rev-list", "--count", "origin/main..HEAD"], check=False)
ahead = int(out.strip() or 0)
p, out = git(["status", "--porcelain"], check=False)
step("verify", behind=behind, ahead=ahead, dirty=out.strip()[:200])
p, out = git(["log", "--oneline", "-4"])
step("final_log", log=out.strip())

FACTS["ok"] = (behind == 0 and push_rc == 0)
old = {}
if os.path.exists(FACTSPATH):
    try:
        old = json.load(open(FACTSPATH, "r", encoding="utf-8"))
    except Exception:
        old = {}
old["s0j"] = FACTS
with open(FACTSPATH, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(old, fh, ensure_ascii=False, indent=1)
print("OK=%s behind=%d ahead=%d e42_escaped=%s push_rc=%s"
      % (FACTS["ok"], behind, ahead, e42_escaped, push_rc))
