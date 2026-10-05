# -*- coding: utf-8 -*-
"""r555 bm-c merge resolver: 1-UU same-day S6 double-write face
(results/_attrition_guard_scan.json) per canon ts-newer-wins with
format-normalized directed keys (r709/r711); tie -> ours (merge-mode
:2:=ours). Stage-sourced python bytes (r515/r706-A); write EXACT stage
bytes; readback reparse (r704); zero residual markers line-anchored
(r505-3); zero-UU verified pre-commit (r713); merge commit -F (r524);
push treadmill; tail-defer close_facts (r532/r533)."""
import datetime
import glob
import json
import os
import re
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CREATE = 0x08000000

UU_FACES = ["results/_attrition_guard_scan.json"]
TS_KEYS = ["ts", "updated", "generated_at", "updated_at", "asof", "generated"]


def git(*args):
    r = subprocess.run(["git", "-C", ROOT] + list(args), capture_output=True,
                       creationflags=CREATE)
    return r.returncode, r.stdout, r.stderr


def git_t(*args):
    r = subprocess.run(["git", "-C", ROOT] + list(args), capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       creationflags=CREATE)
    return r.returncode, (r.stdout or "").strip(), (r.stderr or "").strip()


def stage(side, path):
    rc, b, e = git("show", ":%d:%s" % (side, path))
    assert rc == 0 and len(b) > 100, "stage read fail %s %s rc=%d" % (
        side, path, rc)
    return b


def parse_ts(s):
    return datetime.datetime.fromisoformat(str(s).strip())


def jload(b):
    return json.loads(b.decode("utf-8-sig"))


decisions = {}

for path in UU_FACES:
    ob, tb = stage(2, path), stage(3, path)
    oj, tj = jload(ob), jload(tb)
    val_o = val_t = used = None
    for k in TS_KEYS:
        if isinstance(oj.get(k), (str, int)) and isinstance(tj.get(k), (str, int)):
            val_o, val_t, used = oj[k], tj[k], k
            break
    assert val_o is not None, "no directed ts key on both sides for %s (tops o=%s t=%s)" % (
        path, list(oj)[:10], list(tj)[:10])
    to, tt = parse_ts(val_o), parse_ts(val_t)
    side = "ours" if to >= tt else "theirs"
    data = ob if side == "ours" else tb
    fp = os.path.join(ROOT, path.replace("/", os.sep))
    with open(fp, "wb") as f:
        f.write(data)
    # readback assertions (r704)
    got = open(fp, "rb").read()
    assert got == data, "take-side byte drift %s" % path
    jload(got)
    txt = got.decode("utf-8", "replace")
    assert not re.search(r"^(<{7} |>{7} )", txt, re.M) and not re.search(r"^={7}$", txt, re.M), \
        "residual conflict marker in %s" % path
    decisions[path] = {"policy": "ts-newer-wins", "key": used, "ours_ts": str(val_o),
                       "theirs_ts": str(val_t), "side": side, "bytes": len(data)}
    print("RESOLVED %s side=%s key=%s ours=%s theirs=%s" % (path, side, used, val_o, val_t))

with open(os.path.join(ROOT, "results", "_r555bmc_merge_resolve.json"), "wb") as f:
    f.write((json.dumps({"round": 555, "machine": "bm-c",
                         "generated": datetime.datetime.now().astimezone().isoformat(),
                         "faces": decisions}, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))

# ---- add + zero-UU verify + merge commit ----
for path in list(decisions.keys()) + ["results/_r555bmc_merge_resolve.json"]:
    rc, _, err = git_t("add", "--", path)
    if rc != 0 and "index.lock" in (err or ""):
        import time
        time.sleep(5)
        rc, _, err = git_t("add", "--", path)
    if rc != 0:
        print("ADD FAIL %s rc=%d %s" % (path, rc, (err or "")[:160]))
        raise SystemExit(1)
rc, uu, _ = git_t("diff", "--name-only", "--diff-filter=U")
uuf = [l for l in uu.splitlines() if l.strip()]
assert not uuf, "UU not empty pre-commit (r713): %s" % uuf

msg = ("merge origin/main round-555 close hop-2 (1 UU same-day S6 race: attrition scan)\n\n"
       "Resolved per canon: ts-newer-wins format-normalized directed keys (r709/r711); "
       "stage-sourced python bytes (r515/r706-A); readback reparse+byte asserts (r704); "
       "zero residual markers (r505-3); zero-UU verified pre-commit (r713). "
       "Receipt results/_r555bmc_merge_resolve.json [via bm-c]")
msgf = os.path.join(ROOT, ".codely-cli", "scratch", "_r555bmc_msg_merge.txt")
with open(msgf, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(msg + "\n")
rc, out, err = git_t("commit", "-F", msgf)
print("MERGE_COMMIT rc=%d %s" % (rc, (out or err).splitlines()[0][:150] if (out or err) else ""))
if rc != 0:
    print((err or out)[:400])
    raise SystemExit(1)

# ---- push treadmill ----
hops = 2  # close.py PUSH#1..#3 + close2 merge consumed
delivered = False
while hops < 6:
    rc, out, err = git_t("push")
    hops += 1
    print("PUSH#%d rc=%d %s" % (hops, rc, (err or out)[:240]))
    if rc == 0:
        delivered = True
        break
    rc, _, _ = git_t("fetch", "origin")
    rc, out, _ = git_t("rev-list", "--left-right", "--count", "HEAD...origin/main")
    print("  behind check: %s" % out.replace("\t", "/"))
    rc, out, err = git_t("merge", "origin/main", "-m",
                         "merge origin/main round-555 close hop-%d (push treadmill) [via bm-c]" % hops)
    print("  MERGE rc=%d %s" % (rc, (err or out)[:200]))
    rc, uu, _ = git_t("diff", "--name-only", "--diff-filter=U")
    uuf = [l for l in uu.splitlines() if l.strip()]
    if uuf:
        print("UU_REQUIRES_RESOLVER round-2 faces=%s" % uuf)
        raise SystemExit(2)

rc, out, _ = git_t("rev-list", "--left-right", "--count", "HEAD...origin/main")
ahead, behind = out.split()
rc, head, _ = git_t("rev-parse", "HEAD")
rc, rmt, _ = git_t("rev-parse", "origin/main")
assert delivered and ahead == "0" and behind == "0", "delivery not clean"
print("DELIVERED tip=%s ahead/behind=%s/%s remote_match=%s" % (head[:10], ahead, behind, rmt == head))

# ---- ls-tree delivery probe (13 faces) ----
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
    rc_l, blob, _ = git_t("rev-parse", "HEAD:%s" % f)
    good = (rc_l == 0 and len(blob) == 40)
    if not good:
        print("LSTREE FAIL %s" % f)
    ok += 1 if good else 0
print("LSTREE_OK=%d/%d" % (ok, len(probe_faces)))
assert ok == len(probe_faces), "ls-tree probe incomplete"

# ---- second orders scan (S7 double-scan) ----
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

# ---- close_facts (tail-defer, measured values only) ----
now = datetime.datetime.now().astimezone()
tz = now.strftime("%z")
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S") + tz[:3] + ":" + tz[3:]
facts = ["ROUND_SHA 217b0127a",
         "ABSORB2_SHA 007de9953",
         "ABSORB2_COUNT 22",
         "MERGE_RESOLVE faces=%d receipt=results/_r555bmc_merge_resolve.json" % len(decisions),
         "PUSH_VERIFY recheck: ahead=%s behind=%s (DELIVERED, hops=%d)" % (ahead, behind, hops),
         "FINAL_TIP %s remote_tip_match=%s" % (head[:10], rmt == head),
         "ORDERS_RESCAN %d/%d unacked=%d inbox=%d" %
         (len(o_files) - len(unacked), len(o_files), len(unacked), len(inbox)),
         "LSTREE_OK=%d/%d" % (ok, len(probe_faces))]
for f in probe_faces:
    rc_l, blob, _ = git_t("rev-parse", "HEAD:%s" % f)
    facts.append("LSTREE %s %s" % ("OK" if (rc_l == 0 and len(blob) == 40) else "FAIL", f))
with open(os.path.join(ROOT, "results", "_r555bmc_close_facts.txt"), "wb") as f:
    f.write(("\n".join(facts) + "\n").encode("utf-8"))
print("CLOSE_FACTS written: DELIVERED tip=%s hops=%d now=%s" % (head[:10], hops, now_iso))
print("ASSERTS PASS")
