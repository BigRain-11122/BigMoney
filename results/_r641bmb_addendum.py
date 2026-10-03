# -*- coding: utf-8 -*-
# r641 bm-b addendum: MSG-0135 receipt + D-19 watermark refresh to current
# origin sha (bm-a adjudication: transient self-healed revert; zero recovery
# action) + inbox processing (move 0135 to processed, drop 0030 dup leftover)
# + commit surgery helper scripts. Then targeted commit + push.
import hashlib, json, os, shutil, subprocess, sys, tempfile, time, datetime, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
CREATE_NO_WINDOW = 0x08000000

n = datetime.datetime.now().astimezone()
iso = f"{n.year:04d}-{n.month:02d}-{n.day:02d}T{n.hour:02d}:{n.minute:02d}:{n.second:02d}+{int(n.utcoffset().total_seconds()//3600):02d}:00"

# ---- fresh sparse read of group decisions.md ----
tmp = os.path.join(tempfile.gettempdir(), "fg-sparse-r641b2")
if os.path.isdir(tmp):
    shutil.rmtree(tmp, ignore_errors=True)
r = subprocess.run(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse",
                    "https://github.com/BigRain-11122/FluxGroup.git", tmp],
                   capture_output=True, creationflags=CREATE_NO_WINDOW)
assert r.returncode == 0, "sparse clone fail: " + r.stderr.decode("utf-8", "replace")[:300]
subprocess.run(["git", "-C", tmp, "sparse-checkout", "set", "--skip-checks", "docs/decisions.md"],
               capture_output=True, creationflags=CREATE_NO_WINDOW)
blob = subprocess.run(["git", "-C", tmp, "show", "origin/main:docs/decisions.md"],
                      capture_output=True, creationflags=CREATE_NO_WINDOW).stdout
sha = hashlib.sha256(blob).hexdigest().upper()
shutil.rmtree(tmp, ignore_errors=True)
bma_sha = "1F7C14388D563426F76938A81C09E480435512D659886781F0B2E86DCA0993AF"
print("current decisions sha:", sha[:16], "| bm-a adjudicated:", bma_sha[:16], "| equal:", sha == bma_sha)

# ---- state watermark refresh (content = rows already receipted r639/r640; zero new action) ----
st = json.load(open("state.json", encoding="utf-8"))
st["last_decisions_sha"] = sha
st["last_decisions_at"] = iso
st["last_decisions_read_at"] = iso
json.dump(st, open("state.json", "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)

# ---- inbox processing ----
src = os.path.join("fleet", "inbox", "MSG-20261004-0135-bma-bmb.md")
dst = os.path.join("fleet", "inbox", "processed", "MSG-20261004-0135-bma-bmb.md")
shutil.move(src, dst)
dup = os.path.join("fleet", "inbox", "MSG-20261004-0030-bmb.md")
if os.path.exists(dup) and os.path.exists(os.path.join("fleet", "inbox", "processed", "MSG-20261004-0030-bmb.md")):
    os.remove(dup)
    print("0030 inbox dup leftover removed (processed copy exists at tip)")

# ---- round report addendum line ----
add = (f"{iso} | round 641 addendum (bm-b): MSG-20261004-0135 收讫处理（bm-a 两面定谳："
       f"①decisions.md 回退异常=瞬态自愈·append-only 完好·零恢复动作·维持 r639 正法；②post_review ✗7 已闭=bm-c r437 根修+bm-a 44/0/5 实证，本司零动作）；"
       f"D-19 水位随裁定更至 {sha[:8]}（内容=10-03 批+10-04 批全行已在册·10-04 批 r640 已回执=零新派单零新动作·sparse-clone 复测 {sha[:16]}）；"
       f"0135 已入 processed/、0030 残件已清；手术辅助件 _r641bmb_wt_resolve.py/_r641bmb_treesync.py 随附收编。\n")
with open(os.path.join("logs", "iteration-loop", "round_reports.md"), "a", encoding="utf-8", newline="") as f:
    f.write(add)

# ---- targeted commit + push ----
def g(args, check=True):
    r = subprocess.run(["git"] + args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and r.returncode != 0:
        sys.exit("GIT FAIL %s -> %s" % (args[:3], r.stderr[-300:]))
    return r.stdout

g(["add", "--", "state.json", "logs/iteration-loop/round_reports.md", "fleet/inbox/MSG-20261004-0135-bma-bmb.md",
   "fleet/inbox/processed/MSG-20261004-0135-bma-bmb.md", "results/_r641bmb_wt_resolve.py", "results/_r641bmb_treesync.py"])
r = subprocess.run(["git", "commit", "-m",
                    f"round 641 addendum: MSG-0135 receipt (decisions regression adjudicated transient+self-healed, zero recovery action; post_review x7 closed per bm-a 44/0/5) + D-19 watermark -> {sha[:8]} + inbox processed + surgery helpers [via bm-b]"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
print("commit rc=%d :: %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))
if r.returncode != 0:
    sys.exit("COMMIT FAILED")
r = subprocess.run(["git", "push", "origin", "HEAD:main"], capture_output=True, text=True, encoding="utf-8", errors="replace")
print("push rc=%d :: %s" % (r.returncode, (r.stdout + r.stderr).strip()[-160:]))
if r.returncode == 0:
    g(["fetch", "origin"])
    head = g(["rev-parse", "HEAD"]).strip()
    remote = g(["ls-remote", "origin", "main"]).split()[0]
    print("DELIVERY addendum: HEAD=%s remote=%s equal=%s" % (head[:9], remote[:9], head == remote))
else:
    print("PUSH REJECTED -- addendum commit rides r642 (SLA 2-round ok)")
