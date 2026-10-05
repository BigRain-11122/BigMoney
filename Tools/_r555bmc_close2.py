# -*- coding: utf-8 -*-
# r555 bm-c close2: churn-absorb-2 post-commit dirty faces (r620 law)
# + fetch + merge origin/main single-stop + UU canonical list (r713 law).
# Zero-UU -> push + delivery verify + close_facts (tail-defer r532/r533).
# UU non-empty -> print list, exit 2 (resolver follows).
import datetime
import glob
import json
import os
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CREATE = 0x08000000


def git(args):
    r = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True,
                       creationflags=CREATE)
    return r.returncode, r.stdout.decode("utf-8", "replace").strip(), \
        r.stderr.decode("utf-8", "replace").strip()


def raw_status():
    # r548/r555 law: porcelain MUST be consumed from RAW stdout -- the
    # inherited git() helper strips the whole stream and eats the FIRST
    # line's leading status space (' M path' -> 'M path' -> ln[3:] eats the
    # path's first char). Dedicated no-strip subprocess here.
    r = subprocess.run(["git", "status", "--porcelain", "--no-renames"],
                       cwd=ROOT, capture_output=True, creationflags=CREATE)
    out = (r.stdout or b"").decode("utf-8", "replace")
    listing = []
    for ln in out.splitlines():
        if not ln.strip():
            continue
        listing.append((ln[:2], ln[3:]))
    return listing


now = datetime.datetime.now().astimezone()
tz = now.strftime("%z")
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S") + tz[:3] + ":" + tz[3:]

lock = os.path.join(ROOT, ".git", "index.lock")
if os.path.exists(lock):
    print("INDEX-LOCK PRESENT -- abort (r523 law)")
    raise SystemExit(3)

# ---- 1. churn-absorb-2: post-commit dirty faces (all own lane/regen) ----
# r555 discovery: three S6 regen faces missing from close#1 REGEN list
# (daily_scorecard leg-34 + build_status leg-37 twins) -- deterministic
# pre-add first (close v2 law), then union absorb of the rest.
PRE_ADD = [
    "results/daily_scorecard.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
]
pre_added = []
for face in PRE_ADD:
    p = os.path.join(ROOT, face.replace("/", os.sep))
    if os.path.exists(p):
        rc, _, err = git(["add", "--", face])
        if rc != 0:
            print("PRE-ADD FAIL %s rc=%d %s" % (face, rc, err[:120]))
            raise SystemExit(1)
        pre_added.append(face)
listing = raw_status()
# union count = pre-added + remaining dirty (porcelain still lists them
# until staged; count via staged diff --no-renames instead, r549-ii)
print("DIRTY-COUNT %d (pre-add %d)" % (len(listing), len(pre_added)))
added = []
for st, p in listing:
    if p in pre_added:
        continue
    rc, _, err = git(["add", "--", p])
    if rc != 0:
        print("ADD FAIL %s rc=%d %s" % (p, rc, err[:120]))
        if rc == 128:
            print("rc128 daemon race (r523): abort for retry")
            raise SystemExit(3)
        raise SystemExit(1)
    added.append(p)
    print("  + %s" % p)
rc, out, _ = git(["diff", "--cached", "--name-only", "--no-renames"])
staged_all = [l for l in out.splitlines() if l.strip()]
print("STAGED-TOTAL %d" % len(staged_all))
if not staged_all:
    print("NOTHING-TO-ABSORB (clean tree)")
else:
    msg = ("churn-absorb-2 r555 bm-c: post-commit daemon lane + S6 regen "
           "faces (round commit 217b0127a tail, r620 law pre-merge absorb) "
           "[via bm-c]")
    msgf = os.path.join(ROOT, "results", "_r555bmc_absorb2_msg.txt")
    with open(msgf, "wb") as f:
        f.write((msg + "\n").encode("utf-8"))
    rc, out, err = git(["commit", "-F", msgf])
    print("ABSORB2 COMMIT rc=%d %s" % (rc, (out or err).splitlines()[0][:130] if (out or err) else ""))
    if rc != 0:
        print((err or out)[:400])
        raise SystemExit(1)

# ---- 2. fetch + merge single-stop ----
rc, _, _ = git(["fetch", "origin"])
rc, out, _ = git(["rev-list", "--left-right", "--count", "HEAD...origin/main"])
print("PRE-MERGE ahead/behind: %s" % out.replace("\t", "/"))
rc, out, err = git(["merge", "origin/main", "-m",
                    "merge origin/main round-555 close hop-2 (absorb2 pre-merge, "
                    "r620 law; zero-UU expected else resolver) [via bm-c]"])
print("MERGE rc=%d %s" % (rc, (out or err)[:300]))
rc, uu, _ = git(["diff", "--name-only", "--diff-filter=U"])
uuf = [l for l in uu.splitlines() if l.strip()]
print("UU-COUNT %d" % len(uuf))
for l in uuf:
    print("  UU %s" % l)
if uuf:
    print("UU_REQUIRES_RESOLVER")
    raise SystemExit(2)

# ---- 3. push + delivery verify ----
hops = 1
delivered = False
while hops < 4:
    rc, out, err = git(["push"])
    hops += 1
    print("PUSH#%d rc=%d %s" % (hops, rc, (err or out)[:240]))
    if rc == 0:
        delivered = True
        break
    rc, _, _ = git(["fetch", "origin"])
    rc, out, _ = git(["rev-list", "--left-right", "--count", "HEAD...origin/main"])
    print("  behind check: %s" % out.replace("\t", "/"))
    rc, out, err = git(["merge", "origin/main", "-m",
                        "merge origin/main round-555 close hop-%d (push treadmill) [via bm-c]" % hops])
    print("  MERGE rc=%d" % rc)
    rc, uu, _ = git(["diff", "--name-only", "--diff-filter=U"])
    if [l for l in uu.splitlines() if l.strip()]:
        print("UU_REQUIRES_RESOLVER round-2")
        raise SystemExit(2)

rc, out, _ = git(["rev-list", "--left-right", "--count", "HEAD...origin/main"])
ahead, behind = out.split()
rc, head, _ = git(["rev-parse", "HEAD"])
rc, rmt, _ = git(["rev-parse", "origin/main"])
assert delivered and ahead == "0" and behind == "0", "delivery not clean"
print("DELIVERED tip=%s ahead/behind=%s/%s remote_match=%s" % (head[:10], ahead, behind, rmt == head))

# ---- 4. ls-tree delivery probe (13 faces) ----
probe_faces = ["qa/smoke-r555.md", "qa/equity-curve-r555.png",
               "results/_r555bmc_s6_log.txt",
               "results/_r555bmc_legdiff.txt", "CODELY.md",
               "research/HANDOVER.md",
               "state-bm-c.json", "round_reports-bm-c.md",
               "fleet/machines/bm-c.json",
               "Tools/_r555bmc_bookkeeping.py",
               "Tools/_r555bmc_close.py",
               "Tools/_r555bmc_legdiff.py",
               "results/_r555bmc_commit_msg.txt"]
ok = 0
for f in probe_faces:
    rc_l, blob, _ = git(["rev-parse", "HEAD:%s" % f])
    good = (rc_l == 0 and len(blob) == 40)
    if not good:
        print("LSTREE FAIL %s" % f)
    ok += 1 if good else 0
print("LSTREE_OK=%d/%d" % (ok, len(probe_faces)))
assert ok == len(probe_faces), "ls-tree probe incomplete"

# ---- 5. second orders scan (S7 double-scan) ----
files = sorted(os.path.basename(p) for p in glob.glob(
    os.path.join(ROOT, "fleet", "orders", "*.md")))
o_files = [f for f in files if f.startswith("O-")]
hb = json.load(open(os.path.join(ROOT, "fleet", "machines", "bm-c.json"),
                    encoding="utf-8-sig"))
ack_raw = hb.get("orders_ack") or []
ack = set(ack_raw) if isinstance(ack_raw, list) else set()
unacked = [f for f in o_files
           if f not in ack and os.path.splitext(f)[0] not in ack]
inbox = [os.path.basename(p) for p in glob.glob(
    os.path.join(ROOT, "fleet", "inbox", "*.md"))]
print("ORDERS_RESCAN %d/%d unacked=%d inbox=%d" %
      (len(o_files) - len(unacked), len(o_files), len(unacked), len(inbox)))
assert not unacked, "second-scan unacked orders: %s" % unacked

# ---- 6. close_facts (tail-defer, measured values only) ----
facts = []
facts.append("ROUND_SHA 217b0127a")
facts.append("ABSORB2_COUNT %d" % len(added))
facts.append("PUSH_VERIFY recheck: ahead=%s behind=%s (DELIVERED, hops=%d)" % (ahead, behind, hops))
facts.append("FINAL_TIP %s remote_tip_match=%s" % (head[:10], rmt == head))
facts.append("ORDERS_RESCAN %d/%d unacked=%d inbox=%d" %
             (len(o_files) - len(unacked), len(o_files), len(unacked), len(inbox)))
facts.append("LSTREE_OK=%d/%d" % (ok, len(probe_faces)))
for f in probe_faces:
    rc_l, blob, _ = git(["rev-parse", "HEAD:%s" % f])
    facts.append("LSTREE %s %s" % ("OK" if (rc_l == 0 and len(blob) == 40) else "FAIL", f))
fact_path = os.path.join(ROOT, "results", "_r555bmc_close_facts.txt")
with open(fact_path, "wb") as f:
    f.write(("\n".join(facts) + "\n").encode("utf-8"))
print("CLOSE_FACTS written now=%s" % now_iso)
print("ASSERTS PASS")
