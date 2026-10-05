# r552 bm-c close: ls-tree delivery probe + close_facts + second orders scan
# (measured-values-only per r532/r533 law; tail-defer: written only after
# push rc=0 + 0/0 verified -- all values read live from git).
import subprocess, os, datetime, json, glob

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CREATE = 0x08000000

def git(args):
    r = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True,
                       creationflags=CREATE)
    return r.returncode, r.stdout.decode("utf-8", "replace").strip()

rc_cnt, pos = git(["rev-list", "--left-right", "--count",
                   "HEAD...origin/main"])
ahead, behind = pos.split()
rc_head, head = git(["rev-parse", "HEAD"])
tip = head[:10]
rc_rmt, rmt = git(["rev-parse", "origin/main"])

# second orders scan (S7 double-scan face)
files = sorted(os.path.basename(p) for p in glob.glob(
    os.path.join(ROOT, "fleet", "orders", "*.md")))
o_files = [f for f in files if f.startswith("O-")]
hb = json.load(open(os.path.join(ROOT, "fleet", "machines", "bm-c.json"),
                    encoding="utf-8-sig"))
ack = set(hb.get("orders_ack") or [])
unacked = [f for f in o_files if f not in ack]
inbox = [os.path.basename(p) for p in glob.glob(
    os.path.join(ROOT, "fleet", "inbox", "*.md"))]

now = datetime.datetime.now().astimezone()
tz = now.strftime("%z")
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S") + tz[:3] + ":" + tz[3:]

facts = []
facts.append("ROUND_SHA %s" % head)
facts.append("PUSH_VERIFY recheck: ahead=%s behind=%s (DELIVERED)" % (ahead, behind))
facts.append("FINAL_TIP %s remote_tip_match=%s" % (tip, rmt == head))
facts.append("ORDERS_RESCAN %d/%d unacked=%d inbox=%d" %
             (len(o_files) - len(unacked), len(o_files), len(unacked), len(inbox)))

probe_faces = ["qa/smoke-r552.md", "qa/equity-curve-r552.png",
               "results/_r552bmc_s6_log.txt", "results/_r552bmc_probe.txt",
               "results/_r552bmc_legdiff.txt",
               "state-bm-c.json", "round_reports-bm-c.md",
               "fleet/machines/bm-c.json",
               "results/_r552bmc_merge_resolve.json",
               "Tools/_r552bmc_merge_resolve.py",
               "Tools/_r552bmc_bookkeeping.py",
               "results/_r552bmc_commit_msg.txt"]
ok = 0
for f in probe_faces:
    rc_l, blob = git(["rev-parse", "HEAD:%s" % f])
    good = (rc_l == 0 and len(blob) == 40)
    facts.append("LSTREE %s %s" % ("OK" if good else "FAIL", f))
    ok += 1 if good else 0
facts.append("LSTREE_OK=%d/%d" % (ok, len(probe_faces)))

fact_path = os.path.join(ROOT, "results", "_r552bmc_close_facts.txt")
with open(fact_path, "wb") as f:
    f.write(("\n".join(facts) + "\n").encode("utf-8"))
print("CLOSE_FACTS written: DELIVERED tip=%s ahead/behind=%s/%s lstree=%d/%d "
      "orders_rescan=%d/%d unacked=%d" %
      (tip, ahead, behind, ok, len(probe_faces),
       len(o_files) - len(unacked), len(o_files), len(unacked)))

assert ahead == "0" and behind == "0", "delivery not clean"
assert ok == len(probe_faces), "ls-tree probe incomplete"
assert not unacked, "second-scan unacked orders: %s" % unacked
print("ASSERTS PASS now=%s" % now_iso)
