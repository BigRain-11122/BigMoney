# -*- coding: utf-8 -*-
"""r554 bm-c merge resolver + close-finish: resolve the 17-UU same-day S6
double-write race (vs bm-b r734 wave) per canon:
- ts-newer-wins with format-normalized DIRECTED keys (r709/r711) on json
  faces; tie -> ours (merge-mode stage mapping :2:=ours)
- twins same-side (r708): REPORT md / LIVE md x2 / dashboard js follow
  their json decision
- CODELY.md append-only block-union (r706 zero-loss, entry-anchor dedupe)
- compute_audit rolling union base=ours (r729 law) history dedupe-union
- token_usage per-key max-union (r715/r522)
Stage-sourced python bytes (r515/r706-A); take-side faces written as EXACT
stage bytes (zero re-serialization drift); readback reparse + key
assertions (r704); zero residual conflict markers line-anchored (r505-3);
zero-UU verified pre-commit (r713); push treadmill; tail-defer close_facts
(r532/r533: measured values only, written only after 0/0 delivery)."""
import datetime
import glob
import json
import os
import re
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CNO = 0x08000000
CREATE = CNO


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
    assert rc == 0 and len(b) > 100, "stage read fail %s %s rc=%d %s" % (
        side, path, rc, (e or b"")[:120].decode("utf-8", "replace"))
    return b


def parse_ts(s):
    return datetime.datetime.fromisoformat(str(s).strip())


def jload(b):
    return json.loads(b.decode("utf-8-sig"))


def jdetect(b):
    txt = b.decode("utf-8", "replace")
    eol = "\r\n" if "\r\n" in txt else "\n"
    m = re.search(r"\n( +)\"", txt)
    indent = len(m.group(1)) if m else 1
    return eol, indent, txt.endswith("\n") or txt.endswith("\r\n")


def jdump(obj, ref_b):
    eol, indent, trail = jdetect(ref_b)
    s = json.dumps(obj, ensure_ascii=False, indent=indent)
    if trail:
        s += eol
    if eol == "\r\n":
        s = s.replace("\n", "\r\n")
    return s.encode("utf-8")


TS_FACES = [
    ("results/regime_state.json", ["updated"]),
    ("docs/daily_report/REPORT-2026-10-05.json", ["generated_at"]),
    ("docs/live_usage/LIVE-2026-10-05.json", ["generated"]),
    ("docs/live_usage/LIVE-latest.json", ["generated"]),
    ("results/_attrition_guard_scan.json", ["ts", "updated", "generated_at", "updated_at", "asof"]),
    ("results/fundamental_b_layer_filter.json", ["updated"]),
    ("results/futures_update_status.json", ["last_attempt", "ts"]),
    ("results/lhb_update_status.json", ["updated", "last_attempt"]),
    ("results/update_status.json", ["updated"]),
]
TWINS = [
    ("docs/daily_report/REPORT-2026-10-05.md", "docs/daily_report/REPORT-2026-10-05.json"),
    ("docs/live_usage/LIVE-2026-10-05.md", "docs/live_usage/LIVE-2026-10-05.json"),
    ("docs/live_usage/LIVE-latest.md", "docs/live_usage/LIVE-latest.json"),
    ("results/dashboard_status.js", "results/dashboard_status.json"),
]
DASHJSON = "results/dashboard_status.json"

decisions = {}
written = {}


def write_file(path, data):
    fp = os.path.join(ROOT, path.replace("/", os.sep))
    with open(fp, "wb") as f:
        f.write(data)
    written[path] = len(data)


def resolve_ts_face(path, keys, nested=None):
    ob, tb = stage(2, path), stage(3, path)
    oj, tj = jload(ob), jload(tb)
    val_o = val_t = None
    used = None
    if nested:
        try:
            val_o = oj[nested[0]][nested[1]]
            val_t = tj[nested[0]][nested[1]]
            used = "%s.%s" % nested
        except (KeyError, TypeError):
            val_o = val_t = None
    if used is None:
        for k in keys:
            if isinstance(oj.get(k), (str, int)) and isinstance(tj.get(k), (str, int)):
                val_o, val_t, used = oj[k], tj[k], k
                break
    assert val_o is not None and val_t is not None, \
        "no directed ts key on both sides for %s (tops o=%s t=%s)" % (
            path, list(oj)[:10], list(tj)[:10])
    to, tt = parse_ts(val_o), parse_ts(val_t)
    side = "ours" if to >= tt else "theirs"
    data = ob if side == "ours" else tb
    write_file(path, data)
    decisions[path] = {"policy": "ts-newer-wins", "key": used, "ours_ts": str(val_o),
                      "theirs_ts": str(val_t), "side": side, "bytes": len(data)}
    return side


# ---- 1. ts-newer-wins faces ----
for path, keys in TS_FACES:
    resolve_ts_face(path, keys)
# dashboard json: nested meta.generated_at / meta.generated with generic fallback
ob, tb = stage(2, DASHJSON), stage(3, DASHJSON)
oj, tj = jload(ob), jload(tb)
try:
    vo, vt = oj["meta"]["generated_at"], tj["meta"]["generated_at"]
    used = "meta.generated_at"
except (KeyError, TypeError):
    try:
        vo, vt = oj["meta"]["generated"], tj["meta"]["generated"]
        used = "meta.generated"
    except (KeyError, TypeError):
        vo = vt = None
        for k in ("generated", "generated_at", "updated", "ts"):
            if isinstance(oj.get(k), (str, int)) and isinstance(tj.get(k), (str, int)):
                vo, vt, used = oj[k], tj[k], k
                break
assert vo is not None, "dashboard no ts key (meta=%s)" % list(oj.get("meta", {}))
to, tt = parse_ts(vo), parse_ts(vt)
dash_side = "ours" if to >= tt else "theirs"
write_file(DASHJSON, ob if dash_side == "ours" else tb)
decisions[DASHJSON] = {"policy": "ts-newer-wins", "key": used, "ours_ts": str(vo),
                       "theirs_ts": str(vt), "side": dash_side,
                       "bytes": len(ob if dash_side == "ours" else tb)}

# ---- 2. twins follow json same-side (r708) ----
for md, js in TWINS:
    side = decisions[js]["side"]
    data = stage(2, md) if side == "ours" else stage(3, md)
    write_file(md, data)
    decisions[md] = {"policy": "twin-same-side(r708)", "follows": js, "side": side,
                     "bytes": len(data)}

# ---- 3. CODELY.md append-only block-union (r706) ----
CP = "CODELY.md"
ob, tb = stage(2, CP), stage(3, CP)
eol_b = b"\r\n" if b"\r\n" in ob else b"\n"
olines = ob.decode("utf-8").splitlines()
tlines = tb.decode("utf-8").splitlines()


def split_entries(lines):
    ents, cur = [], None
    for l in lines:
        if l.lstrip().startswith("- ["):
            if cur:
                ents.append(cur)
            cur = [l]
        elif cur is not None:
            cur.append(l)
    if cur:
        ents.append(cur)
    return ents


o_ents = split_entries(olines)
t_ents = split_entries(tlines)
o_anchors = set(e[0] for e in o_ents)
new_ents = [e for e in t_ents if e[0] not in o_anchors]
out = list(olines)
for e in new_ents:
    while out and out[-1] == "":
        out.pop()
    out.append("")
    out.extend(x for x in e if x != "")
r_anchors = set(a for a in (e[0] for e in o_ents) if a) | set(e[0] for e in new_ents)
all_anchors = o_anchors | set(e[0] for e in t_ents)
assert r_anchors == all_anchors, "CODELY union anchor loss"
txt = ("\n".join(out) + "\n")
if eol_b == b"\r\n":
    txt = txt.replace("\n", "\r\n")
write_file(CP, txt.encode("utf-8"))
decisions[CP] = {"policy": "block-union(r706)", "ours_entries": len(o_ents),
                 "theirs_entries": len(t_ents), "new_appended": len(new_ents),
                 "bytes": len(txt.encode("utf-8"))}

# ---- 4. compute_audit rolling union base=ours (r729) ----
AP = "results/compute_audit.json"
ob, tb = stage(2, AP), stage(3, AP)
oj, tj = jload(ob), jload(tb)
seen = set()
uh = []
for e in oj.get("history", []) + tj.get("history", []):
    k = json.dumps(e, sort_keys=True, ensure_ascii=False)
    if k not in seen:
        seen.add(k)
        uh.append(e)
lo, lt = oj.get("latest", {}), tj.get("latest", {})
lvo = lvt = None
for k in ("ts", "updated", "generated_at", "time", "at"):
    if isinstance(lo.get(k), str) and isinstance(lt.get(k), str):
        lvo, lvt = lo[k], lt[k]
        break
if lvo is None:
    merged = dict(oj)
    latest_side = "ours-no-ts"
else:
    latest_side = "ours" if parse_ts(lvo) >= parse_ts(lvt) else "theirs"
    merged = dict(oj if latest_side == "ours" else tj)
merged["history"] = uh
data = jdump(merged, ob)
write_file(AP, data)
decisions[AP] = {"policy": "rolling-union(r729)", "ours_hist": len(oj.get("history", [])),
                 "theirs_hist": len(tj.get("history", [])), "union_hist": len(uh),
                 "latest_side": latest_side, "latest_ts": str(lvo), "theirs_latest_ts": str(lvt),
                 "bytes": len(data)}

# ---- 5. token_usage per-key max-union (r715/r522) ----
TP = "results/token_usage.json"
ob, tb = stage(2, TP), stage(3, TP)
oj, tj = jload(ob), jload(tb)
vo, vt = oj["generated"], tj["generated"]
pref = "o" if parse_ts(vo) >= parse_ts(vt) else "t"


def maxmerge(a, b, pref):
    if isinstance(a, dict) and isinstance(b, dict):
        out = {}
        for k in a.keys() | b.keys():
            if k in a and k in b:
                out[k] = maxmerge(a[k], b[k], pref)
            else:
                out[k] = a[k] if k in a else b[k]
        return out
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) \
            and not isinstance(a, bool) and not isinstance(b, bool):
        return max(a, b)
    return a if pref == "o" else b


merged = maxmerge(oj, tj, pref)
data = jdump(merged, ob)
write_file(TP, data)
decisions[TP] = {"policy": "per-key-max-union(r715/r522)", "ours_generated": str(vo),
                 "theirs_generated": str(vt), "newer_side": pref, "bytes": len(data)}

# ---- 6. readback assertions (r704) + zero residual markers (r505-3) ----
for path in list(decisions.keys()):
    fp = os.path.join(ROOT, path.replace("/", os.sep))
    raw = open(fp, "rb").read()
    assert len(raw) == written[path], "written size drift %s" % path
    txt = raw.decode("utf-8", "replace")
    assert not re.search(r"^(<{7} |>{7} )", txt, re.M) and not re.search(r"^={7}$", txt, re.M), \
        "residual conflict marker in %s" % path
    if path.endswith(".json"):
        jload(raw)  # reparse OK
# take-side byte equality
for path, d in decisions.items():
    if d["policy"] == "ts-newer-wins":
        expect = stage(2, path) if d["side"] == "ours" else stage(3, path)
        got = open(os.path.join(ROOT, path.replace("/", os.sep)), "rb").read()
        assert got == expect, "take-side byte drift %s" % path
    if d["policy"] == "twin-same-side(r708)":
        expect = stage(2, path) if d["side"] == "ours" else stage(3, path)
        got = open(os.path.join(ROOT, path.replace("/", os.sep)), "rb").read()
        assert got == expect, "twin byte drift %s" % path
# union invariants
craw = open(os.path.join(ROOT, CP), "rb").read().decode("utf-8", "replace")
centries = split_entries(craw.splitlines())
c_anchors = set(e[0] for e in centries)
assert c_anchors == all_anchors, "CODELY readback anchor loss"
aj = jload(open(os.path.join(ROOT, AP), "rb").read())
assert len(aj["history"]) == decisions[AP]["union_hist"], "audit history len drift"
tj2 = jload(open(os.path.join(ROOT, TP), "rb").read())
assert tj2["generated"] == (decisions[TP]["ours_generated"] if pref == "o" else decisions[TP]["theirs_generated"]), "token generated drift"

print("RESOLVED %d faces: %s" % (len(decisions), sorted(decisions.keys())))
with open(os.path.join(ROOT, "results", "_r554bmc_merge_resolve.json"), "wb") as f:
    f.write((json.dumps({"round": 554, "machine": "bm-c", "generated": datetime.datetime.now().isoformat(),
                         "faces": decisions}, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))

# ---- 7. add all + zero-UU verify (r713) + merge commit (retry once on index.lock, r523) ----
for path in list(decisions.keys()) + ["results/_r554bmc_merge_resolve.json"]:
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
msg = ("merge origin/main round-554 close hop-2 (17 UU same-day S6 race vs bm-b r734 wave)\n\n"
       "Resolved per canon: ts-newer-wins format-normalized directed keys (r709/r711) x10 json "
       "+ twins same-side (r708: REPORT/LIVE md x2/dashboard js follow json) + CODELY.md "
       "block-union (r706 zero-loss) + compute_audit rolling union base=ours (r729) + "
       "token_usage per-key max-union (r715/r522). Stage-sourced python bytes (r515/r706-A); "
       "readback reparse+key asserts PASS (r704); zero residual markers; zero-UU verified "
       "pre-commit (r713). Receipt results/_r554bmc_merge_resolve.json [via bm-c]")
msgf = os.path.join(ROOT, ".codely-cli", "scratch", "_r554bmc_msg_merge.txt")
with open(msgf, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(msg + "\n")
rc, out, err = git_t("commit", "-F", msgf)
print("MERGE_COMMIT rc=%d %s" % (rc, (out or err).splitlines()[0][:150] if (out or err) else ""))
if rc != 0:
    print((err or out)[:400])
    raise SystemExit(1)

# ---- 8. push treadmill (delivered hops counted from close#1) ----
hops = 1  # close.py PUSH#1 already consumed
delivered = False
while hops < 4:
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
                         "merge origin/main round-554 close hop-%d (push treadmill)" % hops)
    print("  MERGE rc=%d %s" % (rc, (err or out)[:200]))
    rc, uu, _ = git_t("diff", "--name-only", "--diff-filter=U")
    if [l for l in uu.splitlines() if l.strip()]:
        print("UU_REQUIRES_RESOLVER round-2")
        raise SystemExit(2)

rc, out, _ = git_t("rev-list", "--left-right", "--count", "HEAD...origin/main")
ahead, behind = out.split()
rc, head, _ = git_t("rev-parse", "HEAD")
rc, rmt, _ = git_t("rev-parse", "origin/main")
rc, log4, _ = git_t("log", "--oneline", "-5")
round_sha = ""
for l in log4.splitlines():
    if "round 554 bm-c: golden-week standby round" in l:
        round_sha = l.split()[0][:10]
        break
assert delivered and ahead == "0" and behind == "0" and round_sha, "delivery not clean"

# ---- 9. ls-tree delivery probe (12 faces) ----
probe_faces = ["qa/smoke-r554.md", "qa/equity-curve-r554.png",
               "results/_r554bmc_s6_log.txt", "results/_r554bmc_probe.txt",
               "results/_r554bmc_legdiff.txt", "CODELY.md",
               "state-bm-c.json", "round_reports-bm-c.md",
               "fleet/machines/bm-c.json",
               "Tools/_r554bmc_bookkeeping.py",
               "Tools/_r554bmc_close.py",
               "results/_r554bmc_commit_msg.txt"]
ok = 0
for f in probe_faces:
    rc_l, blob, _ = git_t("rev-parse", "HEAD:%s" % f)
    good = (rc_l == 0 and len(blob) == 40)
    ok += 1 if good else 0
    if not good:
        print("LSTREE FAIL %s" % f)
print("LSTREE_OK=%d/%d" % (ok, len(probe_faces)))
assert ok == len(probe_faces), "ls-tree probe incomplete"

# ---- 10. second orders scan (S7 double-scan) ----
files = sorted(os.path.basename(p) for p in glob.glob(
    os.path.join(ROOT, "fleet", "orders", "*.md")))
o_files = [f for f in files if f.startswith("O-")]
hb = json.load(open(os.path.join(ROOT, "fleet", "machines", "bm-c.json"),
                    encoding="utf-8-sig"))
ack_raw = hb.get("orders_ack") or []
ack = set(ack_raw) if isinstance(ack_raw, list) else set()
unacked = [f for f in o_files if f not in ack and os.path.splitext(f)[0] not in ack]
inbox = [os.path.basename(p) for p in glob.glob(
    os.path.join(ROOT, "fleet", "inbox", "*.md"))]
print("ORDERS_RESCAN %d/%d unacked=%d inbox=%d" %
      (len(o_files) - len(unacked), len(o_files), len(unacked), len(inbox)))
assert not unacked, "second-scan unacked orders: %s" % unacked

# ---- 11. close_facts (tail-defer, measured values only) ----
now = datetime.datetime.now().astimezone()
tz = now.strftime("%z")
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S") + tz[:3] + ":" + tz[3:]
facts = ["ROUND_SHA %s" % round_sha,
         "ABSORB2_SHA a007c3895",
         "STAGED_COUNT 40",
         "MERGE_RESOLVE faces=17 receipt=results/_r554bmc_merge_resolve.json",
         "PUSH_VERIFY recheck: ahead=%s behind=%s (DELIVERED, hops=%d)" % (ahead, behind, hops),
         "FINAL_TIP %s remote_tip_match=%s" % (head[:10], rmt == head),
         "ORDERS_RESCAN %d/%d unacked=%d inbox=%d" %
         (len(o_files) - len(unacked), len(o_files), len(unacked), len(inbox)),
         "LSTREE_OK=%d/%d" % (ok, len(probe_faces))]
for f in probe_faces:
    rc_l, blob, _ = git_t("rev-parse", "HEAD:%s" % f)
    facts.append("LSTREE %s %s" % ("OK" if (rc_l == 0 and len(blob) == 40) else "FAIL", f))
with open(os.path.join(ROOT, "results", "_r554bmc_close_facts.txt"), "wb") as f:
    f.write(("\n".join(facts) + "\n").encode("utf-8"))
print("CLOSE_FACTS written: DELIVERED tip=%s round=%s hops=%d now=%s" %
      (head[:10], round_sha, hops, now_iso))
