"""r279 bm-b: T-88 ticket yield resolution -- upstream(bm-a) claim fields kept whole,
bm-b adds honest yield trace field only (r278 T-86 yield precedent)."""
import json, subprocess

PATH = "fleet/tasks/T-2026-09-26-88-P1.json"
ours = subprocess.run(["git", "show", ":2:" + PATH], capture_output=True, check=True).stdout   # upstream (bm-a claim)
do = json.loads(ours.decode("utf-8-sig"))
assert do["status"] == "claimed" and do["claimed_by"] == "bm-a", f"unexpected upstream state {do.get('claimed_by')}"

d = dict(do)  # whole upstream face = canonical (yield)
d["progress_r279_bmb"] = (
    "bm-b r279 yield: my claim commit 7313592d 23:24:37 lost to bm-a 0cd23254 23:18:36 per fleet/README s4 "
    "commit-time ordering (S0 fetch window did not carry bm-a's claim -- honest race, r278 T-86 precedent; "
    "bm-a owns science face). bm-b duplicate first-cut DOMAIN_AUDIT.md DISCARDED from my commit (bm-a 12-domain "
    "first-cut canonical); my r279 measured findings preserved as donation addendum "
    "research/DOMAIN_AUDIT-r279bmb-measured-notes.md (owner-consumable, non-authoritative): MM-ETF 511880/511990/511660 "
    "absent from data/daily 1724 face (s3 cash-leg leg must add to collection universe), ext_slots dzjy/gdhs/margin "
    "unregistered supply faces, futures_daily=10 mains measured (TS incl), fundamental eligibility=11,626 rows, "
    "data/ah_panel empty on bm-b (lane-guard honest no-op). bm-b participation faces unchanged: s3 cash-leg "
    "collector (repo GC001/R-001 + MM-ETF) = shard/supply candidate when owner opens it."
)

raw = ours
bom = raw.startswith(b"\xef\xbb\xbf"); crlf = b"\r\n" in raw; tail_nl = raw.endswith(b"\n")
lines = raw.decode("utf-8-sig").splitlines()
indent = len(lines[1]) - len(lines[1].lstrip(" ")) if len(lines) > 1 else 1
out = json.dumps(d, ensure_ascii=False, indent=indent)
if tail_nl: out += "\n"
if crlf: out = out.replace("\n", "\r\n")
b = ("\xef\xbb\xbf" + out.encode("utf-8")) if bom else out.encode("utf-8")
open(PATH, "wb").write(b)
back = json.loads(open(PATH, "rb").read().decode("utf-8-sig"))
assert back["claimed_by"] == "bm-a" and "progress_r279_bmb" in back
print("T-88 resolved: claimed_by=bm-a + yield trace; faces bom/crlf/tail/indent =", bom, crlf, tail_nl, indent)
