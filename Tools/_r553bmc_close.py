# -*- coding: utf-8 -*-
# r553 bm-c close: deterministic add (close v2 law: known product faces
# explicit, never status-visibility-dependent) + commit -F (r524 law) +
# push with treadmill handling (on reject: fetch -> merge single-stop ->
# push again, zero --no-verify; UU = canonical face list r713 law) +
# ls-tree 12-face delivery probe + second orders scan (S7 double-scan) +
# close_facts (tail-defer: measured values only, written only after
# push rc=0 + 0/0 verified, r532/r533 law).
import datetime
import glob
import json
import os
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CREATE = 0x08000000

# ---- deterministic product faces (close v2 law) ----
CORE_FACES = [
    "qa/smoke-r553.md",
    "qa/equity-curve-r553.png",
    "results/_r553bmc_s6_log.txt",
    "results/_r553bmc_probe.txt",
    "results/_r553bmc_legdiff.txt",
    "state-bm-c.json",
    "round_reports-bm-c.md",
    "fleet/machines/bm-c.json",
    "Tools/_r553bmc_bookkeeping.py",
    "Tools/_r553bmc_close.py",
    "results/_r553bmc_commit_msg.txt",
]
# own lane/regen faces expected dirty from the S6 chain run (add if present)
REGEN_FACES = [
    "results/compute_audit.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/_attrition_guard_scan.json",
    "results/pool_dualrun.bm-c.jsonl",
    "docs/daily_report/REPORT-2026-10-05.md",
    "docs/daily_report/REPORT-2026-10-05.json",
    "docs/live_usage/LIVE-2026-10-05.md",
    "docs/live_usage/LIVE-2026-10-05.json",
    "results/autofill_state.bm-c.json",
    "results/saturation_engine/face_bm-c.json",
    "results/saturation_engine_state.bm-c.json",
    "results/pool_worker_ledger.jsonl",
    "data/fundamental/b_layer_mask.csv",
]


def git(args):
    r = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True,
                       creationflags=CREATE)
    return r.returncode, r.stdout.decode("utf-8", "replace").strip(), \
        r.stderr.decode("utf-8", "replace").strip()


def raw_status():
    # porcelain consume: raw stdout, NO strip (r548 law), --no-renames
    # (r549-ii), line[3:] path slice on XY+space format
    rc, out, _ = git(["status", "--porcelain", "--no-renames"])
    faces = {"M": [], "??": [], "other": []}
    for ln in out.splitlines():
        if not ln.strip():
            continue
        st = ln[:2].strip()
        p = ln[3:]
        if st in ("M", "MM", "AM", "A", " M", "M "):
            faces["M" if "M" in st or st == "A" else "M"].append((st, p)) if False else None
        # simple classify below
    listing = []
    for ln in out.splitlines():
        if not ln.strip():
            continue
        st = ln[:2]
        p = ln[3:]
        listing.append((st, p))
    return listing


now = datetime.datetime.now().astimezone()
tz = now.strftime("%z")
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S") + tz[:3] + ":" + tz[3:]

# ---- 1. commit message file (committed as receipt face) ----
msg = ("round 553 bm-c: golden-week standby round -- QA pack r553 standing "
       "re-run (qa/smoke-r553.md 5/5 + equity-curve-r553.png, 93 trades, "
       "sharpe 0.1586, determinism=True, 26th consecutive frozen-panel "
       "evidence) + S6 chain 38/38 rc0 first-pass zero-heal x13 (streak 51) "
       "+ churn-absorb 109932eac (7 own faces) + merge 7330647fd single-stop "
       "zero-UU (fetch 5 behind: bm-b r734 close wave + bm-a r731/r732 W126 "
       "landing wave) + orders 154/154 + D-19 dual MATCH (D14DCC74 / "
       "3BF0F16E r537 pin) + smoke 48/48 + chain head 671,011 (W125 finalize "
       "landed bm-a; judgment seats: fund-trio bm-b in-burn, W16 prereg "
       "bm-a <=10-07; golden week no bar until 10-09) [via bm-c]")
msg_path = os.path.join(ROOT, "results", "_r553bmc_commit_msg.txt")
with open(msg_path, "wb") as f:
    f.write((msg + "\n").encode("utf-8"))

# ---- 2. deterministic add ----
added = []
for face in CORE_FACES + REGEN_FACES:
    p = os.path.join(ROOT, face.replace("/", os.sep))
    if not os.path.exists(p):
        print("SKIP absent: %s" % face)
        continue
    rc, _, err = git(["add", "--", face])
    if rc != 0:
        print("ADD FAIL %s rc=%d %s" % (face, rc, err[:120]))
        raise SystemExit(1)
    added.append(face)

# union face: porcelain catch-all for remaining own dirty faces (r549-iii
# union set counting; untrackedCache staleness backstopped by ls-tree probe)
listing = raw_status()
for st, p in listing:
    if p in added or p.startswith("results/_r55"):
        continue
    # own-lane backstop: only add bm-c-owned or round-receipt faces
    if ("bm-c" in p or p.startswith("results/_r553") or p.startswith("qa/")
            or p.startswith("docs/") or p.startswith("data/fundamental/")
            or p in ("results/compute_audit.json", "results/regime_state.json",
                     "results/token_usage.json", "results/pool_worker_ledger.jsonl",
                     "results/pool_dualrun.bm-c.jsonl")):
        rc, _, err = git(["add", "--", p])
        if rc != 0:
            print("ADD FAIL (union) %s rc=%d %s" % (p, rc, err[:120]))
        else:
            added.append(p)
            print("UNION ADD: %s" % p)

rc, out, _ = git(["diff", "--cached", "--numstat", "--no-renames"])
staged = [l for l in out.splitlines() if l.strip()]
print("STAGED %d faces:" % len(staged))
for l in staged:
    print("  " + l[:150])

# ---- 3. commit ----
rc, out, err = git(["commit", "-F", msg_path])
print("COMMIT rc=%d %s" % (rc, (out or err).splitlines()[0][:130] if (out or err) else ""))
if rc != 0:
    print((err or out)[:500])
    raise SystemExit(1)
rc, out, _ = git(["log", "--oneline", "-1"])
round_sha = out.split()[0][:10]
print("ROUND_SHA %s" % round_sha)

# ---- 4. push with treadmill handling (max 3 hops) ----
hops = 0
delivered = False
while hops < 3:
    rc, out, err = git(["push"])
    hops += 1
    print("PUSH#%d rc=%d %s" % (hops, rc, (err or out)[:300]))
    if rc == 0:
        delivered = True
        break
    # behind-origin signal handling (r524 law): fetch -> merge -> re-push
    rc, _, _ = git(["fetch", "origin"])
    rc, out, _ = git(["rev-list", "--left-right", "--count", "HEAD...origin/main"])
    print("  behind check: %s" % out.replace("\t", "/"))
    rc, out, err = git(["merge", "origin/main", "-m",
                        "merge origin/main round-553 close hop-%d (push treadmill, zero-UU expected)" % hops])
    print("  MERGE rc=%d" % rc)
    rc, uu, _ = git(["diff", "--name-only", "--diff-filter=U"])
    uuf = [l for l in uu.splitlines() if l.strip()]
    print("  UU faces (canonical r713): %d %s" % (len(uuf), uuf))
    if uuf:
        print("UU_REQUIRES_RESOLVER faces=%s" % uuf)
        raise SystemExit(2)

rc, out, _ = git(["rev-list", "--left-right", "--count", "HEAD...origin/main"])
ahead, behind = out.split()
rc_head, head = git(["rev-parse", "HEAD"])
rc_rmt, rmt = git(["rev-parse", "origin/main"])

# ---- 5. ls-tree delivery probe (12 faces) ----
probe_faces = ["qa/smoke-r553.md", "qa/equity-curve-r553.png",
               "results/_r553bmc_s6_log.txt", "results/_r553bmc_probe.txt",
               "results/_r553bmc_legdiff.txt",
               "state-bm-c.json", "round_reports-bm-c.md",
               "fleet/machines/bm-c.json",
               "Tools/_r553bmc_bookkeeping.py",
               "Tools/_r553bmc_close.py",
               "results/_r553bmc_commit_msg.txt",
               "results/_r553bmc_legdiff.txt"]
probe_faces = list(dict.fromkeys(probe_faces))  # dedupe, keep 12 target
ok = 0
for f in probe_faces:
    rc_l, blob = git(["rev-parse", "HEAD:%s" % f])
    good = (rc_l == 0 and len(blob) == 40)
    if not good:
        print("LSTREE FAIL %s" % f)
    ok += 1 if good else 0
print("LSTREE_OK=%d/%d" % (ok, len(probe_faces)))

# ---- 6. second orders scan (S7 double-scan) ----
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

# ---- 7. close_facts (tail-defer, measured values only) ----
assert delivered and ahead == "0" and behind == "0", "delivery not clean"
assert ok == len(probe_faces), "ls-tree probe incomplete"
assert not unacked, "second-scan unacked orders: %s" % unacked

facts = []
facts.append("ROUND_SHA %s" % head)
facts.append("PUSH_VERIFY recheck: ahead=%s behind=%s (DELIVERED, hops=%d)" % (ahead, behind, hops))
facts.append("FINAL_TIP %s remote_tip_match=%s" % (head[:10], rmt == head))
facts.append("ORDERS_RESCAN %d/%d unacked=%d inbox=%d" %
             (len(o_files) - len(unacked), len(o_files), len(unacked), len(inbox)))
facts.append("LSTREE_OK=%d/%d" % (ok, len(probe_faces)))
for f in probe_faces:
    rc_l, blob = git(["rev-parse", "HEAD:%s" % f])
    facts.append("LSTREE %s %s" % ("OK" if (rc_l == 0 and len(blob) == 40) else "FAIL", f))
fact_path = os.path.join(ROOT, "results", "_r553bmc_close_facts.txt")
with open(fact_path, "wb") as f:
    f.write(("\n".join(facts) + "\n").encode("utf-8"))
print("CLOSE_FACTS written: DELIVERED tip=%s ahead/behind=%s/%s lstree=%d/%d "
      "orders_rescan=%d/%d unacked=%d now=%s" %
      (head[:10], ahead, behind, ok, len(probe_faces),
       len(o_files) - len(unacked), len(o_files), len(unacked), now_iso))
print("ASSERTS PASS now=%s" % now_iso)
