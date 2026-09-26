# r290 bm-b S0 stash-pop conflict resolver (skill: bigmoney-conflict-resolve)
# Form: runnable_pool.json = shared pool ledger (entries union semantics)
# Diagnosis: whole-file UU zone from `git stash pop` after fast-forward pull.
#   upstream (HEAD face, incl. bm-a r287 CENSUS-FUS-S2-W1 submission): 54 entries, updated_at 2026-09-27 02:38:46
#   stashed  (local runtime tick, CRLF producer):                       53 entries, updated_at 2026-09-27 01:50:09
#   Entry-level compare: 53/53 common entries BYTE-IDENTICAL; stashed has ZERO unique content.
# Recipe: take-upstream (superset + newer updated_at) = zero-loss (|A u B| == 54 == upstream count).
# Law: r188/R208 union zero-loss (here union reduces to upstream superset), r185 parse-before-write.
import json
import sys

SRC = r"C:\Users\Administrator\Desktop\Bigmoney\results\runnable_pool.json"
raw = open(SRC, "rb").read().decode("utf-8")
lines = raw.split("\n")
iu = next(i for i, l in enumerate(lines) if l.startswith("<<<<<<<"))
im = next(i for i, l in enumerate(lines) if l.startswith("======="))
ie = next(i for i, l in enumerate(lines) if l.startswith(">>>>>>>"))
upstream_text = "\n".join(lines[iu + 1 : im]) + "\n}"   # trailing '}' is common context after conflict zone
stashed_text = "\n".join(lines[im + 1 : ie]) + "\n}"

u = json.loads(upstream_text)
s = json.loads(stashed_text)
ue = {e["id"]: e for e in u["entries"]}
se = {e["id"]: e for e in s["entries"]}
assert set(se) <= set(ue), "stashed must be subset of upstream for take-upstream"
for k, v in se.items():
    assert ue[k] == v, f"common entry diverged: {k}"
assert u["updated_at"] >= s["updated_at"], "upstream must be newer"
assert len(u["entries"]) == len(ue) == 54, "expected 54 union entries"

# write back byte-exact upstream blob (LF, 1-space indent producer format of pool submit face)
with open(SRC, "wb") as f:
    f.write(upstream_text.encode("utf-8"))
# verify round-trip
check = json.loads(open(SRC, "rb").read().decode("utf-8"))
assert len(check["entries"]) == 54
assert "CENSUS-FUS-S2-W1" in {e["id"] for e in check["entries"]}
print("RESOLVED: take-upstream, 54 entries, zero-loss verified, CENSUS-FUS-S2-W1 preserved")
