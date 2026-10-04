# -*- coding: utf-8 -*-
# r674 bm-b post-resolve verification: marker content-check (r644, git grep simple form),
# UU full sweep (r657-1), auto-merged append-only/lane faces zero-loss (r453/r661),
# state/heartbeat/trio/eta/eligibility post-merge state.
import io, json, os, re, subprocess, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
CREATE = 0x08000000

def git(*a):
    p = subprocess.run(["git"] + list(a), capture_output=True, creationflags=CREATE)
    return p.returncode, p.stdout, p.stderr

fails = []

# 1) UU full sweep
rc, out, _ = git("status", "--porcelain=v1")
uu = [l for l in out.decode("utf-8", "replace").splitlines() if l.startswith("UU")]
print("UU remaining:", len(uu), uu[:5])
if uu:
    fails.append("UU-not-empty")

# 2) marker content check on staged (simple literal forms, r644 content law)
for pat in ("<<<<<<<", ">>>>>>>"):
    rc, out, _ = git("grep", "-l", pat, "--cached")
    hits = out.decode("utf-8", "replace").strip().splitlines() if rc == 0 else []
    print("marker %r in staged: %s" % (pat, hits if hits else "NONE"))
    if hits:
        fails.append("marker:" + pat)

# 3) nulls trio row counts (append-only superset must survive auto-merge)
for fam, p in (("VALUE", r"results\fund_value_p1\nulls.jsonl"),
               ("QUALITY", r"results\fund_quality_p1\nulls.jsonl"),
               ("DIVLOWVOL", r"results\fund_divlowvol_p1\nulls.jsonl")):
    n = sum(1 for ln in io.open(p, "rb") if ln.strip())
    print("trio %s rows=%d" % (fam, n))
    if fam == "VALUE" and n < 789:
        fails.append("VALUE-rows-lost")
    if fam == "QUALITY" and n < 612:
        fails.append("QUALITY-rows-lost")
    if fam == "DIVLOWVOL" and n < 459:
        fails.append("DIVLOWVOL-rows-lost")

# 4) round_reports.md: my entry exactly once + theirs present + no dup (r453)
data = io.open(r"logs\iteration-loop\round_reports.md", "rb").read().decode("utf-8", "replace")
mine = data.count("r674 (bm-b) PRODUCT")
theirs = data.count("r477 bm-c") + data.count("r476 bm-c") + data.count("r475 bm-c")
print("round_reports: r674-entry=%d (want 1), bm-c r475-477 mentions=%d" % (mine, theirs))
if mine != 1:
    fails.append("r674-entry-count")

# 5) state.json + heartbeat + eta + eligibility
st = json.load(io.open("state.json", encoding="utf-8"))
print("state round_no:", st.get("round_no"))
if st.get("round_no") != 674:
    fails.append("state-round")
hb = json.load(io.open(r"fleet\machines\bm-b.json", encoding="utf-8"))
print("hb last_seen:", hb.get("last_seen"), "epoch-int:", isinstance(hb.get("heartbeat_epoch_utc"), int), "acks:", len(hb.get("orders_ack", [])))
if hb.get("last_seen") != "2026-10-04T14:06:15+08:00" or len(hb.get("orders_ack", [])) != 153:
    fails.append("hb-face")
eta = json.load(io.open(r"results\trio_burn_eta.json", encoding="utf-8"))
print("eta generated:", eta.get("generated"), "value k:", eta.get("trio", {}).get("fund_value_p1", {}).get("k"))
if eta.get("trio", {}).get("fund_value_p1", {}).get("k", 0) < 785:
    fails.append("eta-face")
elig_age_h = (os.stat(r"data\fundamental\eligibility.csv").st_mtime) and round((__import__("time").time() - os.stat(r"data\fundamental\eligibility.csv").st_mtime) / 3600, 2)
print("eligibility.csv age_h:", elig_age_h)
if elig_age_h > 1.0:
    fails.append("eligibility-stale")  # bm-c fetch landed ~14:0x; must be fresh (<1h)

print("VERIFY:", "PASS" if not fails else "FAIL " + str(fails))
sys.exit(1 if fails else 0)
