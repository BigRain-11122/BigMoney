# -*- coding: utf-8 -*-
"""r835 bm-c push-race driver: absorb->fetch->rebase(auto-resolve ts-newer-wins)->push->verify loop (r824 three-step, scripted)."""
import subprocess, re, json, sys, time

def run(args):
    r = subprocess.run(args, capture_output=True)
    return r.returncode, r.stdout.decode("utf-8", "replace"), r.stderr.decode("utf-8", "replace")

def sh(side, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (side, path)], capture_output=True)
    return r.stdout.decode("utf-8", "replace")

def ts_of(text):
    m = re.search(r'"ts"\s*:\s*"([^"]+)"', text)
    if m:
        return m.group(1)
    m2 = re.search(r"ts[\"']?\s*[:=]\s*[\"']?([0-9T:\.\+\-]+)", text)
    return m2.group(1) if m2 else "?"

for attempt in range(3):
    # 1) absorb daemon churn
    run(["git", "add", "-A"])
    rc, out, err = run(["git", "commit", "-m", "r835 churn absorb: pre-push race absorb (daemon faces)"])
    committed = rc == 0
    print("absorb commit rc=%d committed=%s" % (rc, committed))
    # 2) fetch
    run(["git", "fetch", "origin"])
    rc_a = int(run(["git", "rev-list", "--count", "origin/main..HEAD"])[1].strip())
    rc_b = int(run(["git", "rev-list", "--count", "HEAD..origin/main"])[1].strip())
    print("ahead=%d behind=%d" % (rc_a, rc_b))
    if rc_b == 0:
        break
    # 3) rebase with auto-resolve loop
    p = subprocess.run(["git", "rebase", "origin/main"], capture_output=True)
    print("rebase rc=%d" % p.returncode)
    guard = 0
    while p.returncode != 0 and guard < 8:
        guard += 1
        rc3, unmerged, _ = run(["git", "diff", "--name-only", "--diff-filter=U"])
        files = [f for f in unmerged.strip().splitlines() if f]
        if not files:
            # zero-UU refusal -> unstaged churn face: absorb + manual commit (r863/r808 law)
            run(["git", "add", "-A"])
            rc4, _, _ = run(["git", "commit", "-F", ".git/rebase-merge/message"])
            if rc4 != 0:
                msg = run(["git", "log", "-1", "--pretty=%B", "REBASE_HEAD"])[1]
                if not msg.strip():
                    msg = "r835 churn absorb: rebase pick (manual fallback)"
                run(["git", "commit", "-m", msg.strip()])
            p = subprocess.run(["git", "rebase", "--continue"], capture_output=True)
            print("  zero-UU continue rc=%d" % p.returncode)
            continue
        for fp in files:
            o = sh(2, fp)
            t = sh(3, fp)
            to, tt = ts_of(o), ts_of(t)
            if tt >= to:
                pick, side = t, "MINE"
            else:
                pick, side = o, "REMOTE"
            # notes-union upgrade for task/board json when both sides grew
            if fp.endswith(".json") and '"notes"' in o and '"notes"' in t:
                try:
                    rj, mj = json.loads(o), json.loads(t)
                    rn, mn = rj.get("notes", ""), mj.get("notes", "")
                    if mn and rn and rn not in mn and mn not in rn:
                        rj["notes"] = rn + mn
                        pick = json.dumps(rj, ensure_ascii=False, indent=1)
                        side = "UNION(notes)"
                except Exception:
                    pass
            open(fp, "w", encoding="utf-8", newline="").write(pick)
            print("  resolved %s -> %s (remote=%s mine=%s)" % (fp, side, to, tt))
        run(["git", "add", "-A"])
        rc5, _, _ = run(["git", "commit", "-F", ".git/rebase-merge/message"])
        if rc5 != 0:
            msg = run(["git", "log", "-1", "--pretty=%B", "REBASE_HEAD"])[1]
            if not msg.strip():
                msg = "r835 churn absorb: rebase pick (manual fallback)"
            run(["git", "commit", "-m", msg.strip()])
        p = subprocess.run(["git", "rebase", "--continue"], capture_output=True)
        print("  continue rc=%d" % p.returncode)
    if p.returncode != 0:
        print("REBASE STUCK rc=%d -- giving up this attempt" % p.returncode)
        run(["git", "rebase", "--abort"])
        sys.exit(2)
    # 4) push
    rc6, out6, err6 = run(["git", "push", "origin", "main"])
    print("push rc=%d %s" % (rc6, (err6 or out6).strip()[-120:]))
    if rc6 == 0:
        break
    time.sleep(2)

# verify
run(["git", "fetch", "origin"])
a = run(["git", "rev-list", "--count", "origin/main..HEAD"])[1].strip()
b = run(["git", "rev-list", "--count", "HEAD..origin/main"])[1].strip()
head = run(["git", "log", "--oneline", "-1", "origin/main"])[1].strip()
print("VERIFY ahead=%s behind=%s origin/main=%s" % (a, b, head))
sys.exit(0 if (int(a) == 0 and int(b) == 0) else 1)
