# -*- coding: utf-8 -*-
# r641 bm-b worktree conflict resolver (cherry-pick 81d1e7adc onto origin/main
# tip 4ebd41f04 = bm-a r652). Resolution laws:
#  - CODELY.md: UNION (origin bm-a lessons + my r641 line) -- append-only memory.
#  - shared rotate faces (attrition scan / lhb status): ts-newer-wins.
#  - r633bma rehearsal faces (bm-a-owned runner artifact): ts-newer-wins
#    (bm-a r652 refresh likely newer than my adopted 01:34-01:43 reruns).
# Then cherry-pick --continue + CAS push + delivery self-proof.
import json, os, re, subprocess, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WT = os.path.join(os.environ.get("TEMP", "."), "bmb-wt-r641")

def wtgit(args, check=True):
    r = subprocess.run(["git", "-C", WT] + args, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if check and r.returncode != 0:
        sys.exit("WT GIT FAIL %s -> %s" % (args[:3], r.stderr[-400:]))
    return r.stdout

def stage(n, path):
    return wtgit(["show", ":%d:%s" % (n, path)])

def ts_of(raw):
    try:
        d = json.loads(raw)
        return d.get("ts") or d.get("generated") or ""
    except Exception:
        return ""

# ---- CODELY.md union ----
p = "CODELY.md"
s2, s3 = stage(2, p), stage(3, p)
mine = [ln for ln in s3.splitlines() if "r641 bm-b" in ln and ln.startswith("- [2026-10-04")]
assert len(mine) == 1, "my CODELY line not found uniquely: %d" % len(mine)
if any("r641 bm-b" in ln for ln in s2.splitlines()):
    resolved = s2
    print("CODELY: my line already present on origin side -- pure origin")
else:
    resolved = s2.rstrip("\n") + "\n" + mine[0] + "\n"
    print("CODELY: union origin + my r641 line")
open(os.path.join(WT, p), "w", encoding="utf-8", newline="").write(resolved)

# ---- ts-newer-wins faces ----
for p in ["results/_attrition_guard_scan.json",
          "results/lhb_update_status.json",
          "results/_r633bma_finalize_rehearsal_fund_quality_p1.json",
          "results/_r633bma_finalize_rehearsal_fund_value_p1.json",
          "results/_r633bma_finalize_rehearsal_fund_divlowvol_p1.json",
          "results/_r633bma_finalize_rehearsal_summary.json"]:
    s2, s3 = stage(2, p), stage(3, p)
    t2, t3 = ts_of(s2), ts_of(s3)
    win = s3 if (t3 or "") >= (t2 or "") else s2
    src = "mine" if win is s3 else "origin"
    open(os.path.join(WT, p), "w", encoding="utf-8", newline="").write(win)
    print(f"rotate {p}: origin_ts={t2} mine_ts={t3} -> {src}")
    wtgit(["add", "--", p])
wtgit(["add", "--", "CODELY.md"])

st = wtgit(["status", "--porcelain"])
assert not any(l.startswith(("UU", "AA")) for l in st.splitlines()), st
env = dict(os.environ, GIT_EDITOR="true")
r = subprocess.run(["git", "-C", WT, "cherry-pick", "--continue"],
                    capture_output=True, text=True, encoding="utf-8",
                    errors="replace", env=env)
print("continue rc=%d :: %s" % (r.returncode, (r.stdout + r.stderr).strip()[-150:]))
if r.returncode != 0:
    sys.exit("CONTINUE FAILED")
print("PICKED:", wtgit(["log", "--oneline", "-1"]).strip())

# ---- CAS push + delivery self-proof ----
r = subprocess.run(["git", "-C", WT, "push", "origin", "HEAD:main"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
print("push rc=%d :: %s" % (r.returncode, (r.stdout + r.stderr).strip()[-200:]))
if r.returncode != 0:
    sys.exit("PUSH REJECTED -- needs CAS retry")
head = wtgit(["rev-parse", "HEAD"]).strip()
wtgit(["fetch", "origin"])
remote = wtgit(["ls-remote", "origin", "main"]).split()[0]
ahead = wtgit(["rev-list", "--count", "HEAD..origin/main"]).strip()
print("DELIVERY: HEAD=%s remote=%s equal=%s behind-after-fetch=%s" % (head[:9], remote[:9], head == remote, ahead))
assert head == remote and ahead == "0", "DELIVERY NOT VERIFIED"
print("DELIVERED-VERIFIED")
