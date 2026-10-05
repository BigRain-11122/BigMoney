# -*- coding: utf-8 -*-
# r553 bm-c close recovery: post-push receipts completed after in-window
# close-script crash (ValueError tuple-unpack at rev-parse step -- PUSH#2
# had ALREADY delivered 0-clean; zero data harm, only receipts were
# pending). Measured values only (r532/r533 law): rev-list 0/0 recheck +
# ls-tree delivery probe + second orders scan + close_facts write. The
# unpack bug itself is fixed in Tools/_r553bmc_close.py in-place (post-push
# tail face, absorbed r554 per r714 law; fixmsg note documents it).
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
    return (r.returncode, r.stdout.decode("utf-8", "replace").strip(),
            r.stderr.decode("utf-8", "replace").strip())


now = datetime.datetime.now().astimezone()
tz = now.strftime("%z")
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S") + tz[:3] + ":" + tz[3:]

rc, out, _ = git(["rev-list", "--left-right", "--count", "HEAD...origin/main"])
ahead, behind = out.split()
rc_head, head, _ = git(["rev-parse", "HEAD"])
rc_rmt, rmt, _ = git(["rev-parse", "origin/main"])
print("POS recheck (ahead/behind) = %s/%s tip=%s remote_match=%s" %
      (ahead, behind, head[:10], rmt == head))

probe_faces = ["qa/smoke-r553.md", "qa/equity-curve-r553.png",
               "results/_r553bmc_s6_log.txt", "results/_r553bmc_probe.txt",
               "results/_r553bmc_legdiff.txt",
               "state-bm-c.json", "round_reports-bm-c.md",
               "fleet/machines/bm-c.json",
               "Tools/_r553bmc_bookkeeping.py",
               "Tools/_r553bmc_close.py",
               "results/_r553bmc_commit_msg.txt"]
ok = 0
rows = []
for f in probe_faces:
    rc_l, blob, _ = git(["rev-parse", "HEAD:%s" % f])
    good = (rc_l == 0 and len(blob) == 40)
    rows.append("LSTREE %s %s" % ("OK" if good else "FAIL", f))
    if not good:
        print("LSTREE FAIL %s" % f)
    ok += 1 if good else 0
print("LSTREE_OK=%d/%d" % (ok, len(probe_faces)))

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

assert ahead == "0" and behind == "0", "delivery not clean: %s/%s" % (ahead, behind)
assert ok == len(probe_faces), "ls-tree probe incomplete"
assert not unacked, "second-scan unacked orders: %s" % unacked

facts = []
facts.append("ROUND_SHA %s" % head)
facts.append("PUSH_VERIFY recheck: ahead=%s behind=%s (DELIVERED, 2-hop treadmill: push#1 reject behind-2 -> fetch -> merge zero-UU -> push#2 rc0)" % (ahead, behind))
facts.append("FINAL_TIP %s remote_tip_match=%s" % (head[:10], rmt == head))
facts.append("RECOVERY_NOTE close-script ValueError tuple-unpack crash AFTER push#2 delivery; receipts completed by Tools/_r553bmc_close_recovery.py measured-values-only (zero data harm); unpack bug fixed in Tools/_r553bmc_close.py in-place, fix tail absorbed r554")
facts.append("ORDERS_RESCAN %d/%d unacked=%d inbox=%d" %
             (len(o_files) - len(unacked), len(o_files), len(unacked), len(inbox)))
facts.append("LSTREE_OK=%d/%d (11-face set: zero-UU round, no merge-resolve pair)" % (ok, len(probe_faces)))
facts.extend(rows)
fact_path = os.path.join(ROOT, "results", "_r553bmc_close_facts.txt")
with open(fact_path, "wb") as f:
    f.write(("\n".join(facts) + "\n").encode("utf-8"))
print("CLOSE_FACTS written: DELIVERED tip=%s ahead/behind=%s/%s lstree=%d/%d "
      "orders_rescan=%d/%d unacked=%d now=%s" %
      (head[:10], ahead, behind, ok, len(probe_faces),
       len(o_files) - len(unacked), len(o_files), len(unacked), now_iso))
print("ASSERTS PASS now=%s" % now_iso)
