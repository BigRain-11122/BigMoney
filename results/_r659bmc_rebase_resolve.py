# r659 bm-c rebase resolver: single UU face results/_attrition_guard_scan.json
# Laws: r648 (ls-files -u -> cat-file -p sha direct read; marker hard gate)
#       r773 (per-face ts evidence, newer-wins), r756/r711 (ts normalize before compare)
#       r787 (add -A + rebase --continue atomic back-to-back in ONE process)
#       r808 (sequencer-stuck fallback: author-script + manual commit -F + continue)
#       r710 law A (python subprocess bytes capture + wb write, never PS redirect)
import subprocess, json, sys, os, datetime

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NO_WINDOW = 0x08000000
FACE = "results/_attrition_guard_scan.json"

def git(args, check=True):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True, creationflags=NO_WINDOW)
    if check and p.returncode != 0:
        sys.stdout.write("GIT_FAIL %s rc=%d %s\n" % (args[0], p.returncode, p.stderr.decode("utf-8", "replace")[:300]))
    return p.returncode, p.stdout, p.stderr

def read_blob(sha):
    rc, out, err = git(["cat-file", "-p", sha])
    if rc != 0 or not out:
        sys.stdout.write("BLOB_READ_FAIL sha=%s rc=%d len=%d\n" % (sha, rc, len(out)))
        sys.exit(2)
    return out

def marker_count(b):
    n = 0
    for ln in b.decode("utf-8", "replace").splitlines():
        s = ln.strip()
        if s.startswith("<<<<<<< ") or s.startswith(">>>>>>> ") or s == "=======":
            n += 1
    return n

def parse_ts(obj):
    # face-level explicit keys first (r711 law 3), then any ts-like top-level
    for k in ("ts", "generated", "generated_at", "updated", "updated_at", "scanned_at"):
        v = obj.get(k) if isinstance(obj, dict) else None
        if isinstance(v, str) and len(v) >= 10:
            return k, v
    return None, None

def norm(v):
    v = v.strip()
    try:
        return datetime.datetime.fromisoformat(v.replace(" ", "T") if " " in v[:12] and "T" not in v[:12] else v)
    except Exception:
        try:
            return datetime.datetime.fromisoformat(v)
        except Exception:
            return None

# 1) stage shas via ls-files -u (r648: only reliable channel)
rc, out, err = git(["ls-files", "-u"])
lines = [l for l in out.decode().splitlines() if l.strip()]
stages = {}
for l in lines:
    parts = l.split()
    stages[int(parts[2])] = parts[1]  # mode(0) sha(1) stage(2) TAB path(3)
sys.stdout.write("STAGES=%s\n" % sorted(stages.keys()))
if 2 not in stages or 3 not in stages:
    sys.stdout.write("NO_STAGE_PAIR — aborting, no write\n")
    sys.exit(2)

b2 = read_blob(stages[2])   # onto side (origin tip content)
b3 = read_blob(stages[3])   # replaying side (mine)
m2, m3 = marker_count(b2), marker_count(b3)
sys.stdout.write("MARKERS onto=%d mine=%d\n" % (m2, m3))
try:
    j2, j3 = json.loads(b2), json.loads(b3)
except Exception as e:
    sys.stdout.write("PARSE_FAIL %s\n" % e)
    sys.exit(2)

k2, v2 = parse_ts(j2)
k3, v3 = parse_ts(j3)
t2, t3 = norm(v2) if v2 else None, norm(v3) if v3 else None
sys.stdout.write("TS onto[%s]=%s mine[%s]=%s\n" % (k2, v2, k3, v3))

# decision: marker-contaminated side loses outright (r648); else newer-wins (r773)
if m3 > 0 and m2 == 0:
    winner, side = b2, "onto-clean"
elif m2 > 0 and m3 == 0:
    winner, side = b3, "mine-clean"
elif t3 is not None and (t2 is None or t3 >= t2):
    winner, side = b3, "mine-newer-or-equal"
elif t2 is not None:
    winner, side = b2, "onto-newer"
else:
    winner, side = b3, "no-ts-fallback-mine-with-audit"
sys.stdout.write("DECISION=%s len=%d\n" % (side, len(winner)))

# 2) byte-exact write + reparse gate (r710 law B/C)
with open(os.path.join(REPO, FACE), "wb") as f:
    f.write(winner)
with open(os.path.join(REPO, FACE), "rb") as f:
    back = f.read()
assert back == winner, "write-back mismatch"
json.loads(back)
sys.stdout.write("WRITE_OK reparse-pass markers=%d\n" % marker_count(back))

# 3) atomic tail: add -A then rebase --continue back-to-back in this process (r787)
rc, out, err = git(["add", "-A"])
sys.stdout.write("ADD rc=%d\n" % rc)
rc, out, err = git(["rebase", "--continue"])
sys.stdout.write("CONTINUE rc=%d %s\n" % (rc, (out + err).decode("utf-8", "replace")[:400]))
if rc != 0:
    # r808 fallback: manual commit with preserved author/date then continue
    amd = os.path.join(REPO, ".git", "rebase-merge")
    if os.path.isdir(amd):
        env = dict(os.environ)
        try:
            with open(os.path.join(amd, "author-script"), "r", encoding="utf-8", errors="replace") as f:
                for ln in f:
                    ln = ln.strip()
                    if "=" in ln and (ln.startswith("GIT_AUTHOR_NAME") or ln.startswith("GIT_AUTHOR_EMAIL") or ln.startswith("GIT_AUTHOR_DATE")):
                        k, _, v = ln.partition("=")
                        env[k.strip()] = v.strip().strip("'")
            rc2, out2, err2 = git(["commit", "-F", os.path.join(amd, "message")], check=False)
            sys.stdout.write("MANUAL_COMMIT rc=%d\n" % rc2)
            rc3, out3, err3 = git(["rebase", "--continue"], check=False)
            sys.stdout.write("CONTINUE2 rc=%d %s\n" % (rc3, (out3 + err3).decode("utf-8", "replace")[:300]))
        except Exception as e:
            sys.stdout.write("FALLBACK_FAIL %s\n" % e)

# 4) post-state
still = os.path.isdir(os.path.join(REPO, ".git", "rebase-merge"))
rc, out, err = git(["log", "--oneline", "-3"])
sys.stdout.write("LOG:\n%s\n" % out.decode("utf-8", "replace"))
rc, out, err = git(["rev-list", "--left-right", "--count", "origin/main...HEAD"])
sys.stdout.write("LR(origin/HEAD)=%s\n" % out.decode().strip())
rc, out, err = git(["status", "--porcelain"])
sys.stdout.write("STATUS_CLEAN=%s\n" % (len(out.decode().strip()) == 0))
sys.stdout.write("REBASE_ACTIVE=%s\n" % still)
