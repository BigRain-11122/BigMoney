"""r494 W14-GENERATE re-park (governance): r483 canon adjudication
(RETAIL_QUANT_TRACK L11 'W14 停烧裁定') = unfreeze requires §四 gate
self-proof (trial-budget attribution + §1.2 compliance) -- r493 re-arm
9c1d97877 lacked it (read a governance park as a dead-session mechanical
park; parked_per field still carried the §1.2 ban). MSG-0540 bm-c pre-burn
inquiry honored: in-flight generate pid 54704 killed at dedup 500/10000,
w14_candidates.json absent = trial-gate consumption N=0. Re-park both
layers (r489 double-layer law). r289 format law: indent+line-ending
probe, byte-surgical write."""
import json

p = "results/runnable_pool.json"
raw = open(p, "rb").read()
crlf = raw.count(b"\r\n")
lf_only = raw.count(b"\n") - crlf
pool = json.loads(raw.decode("utf-8"))
hit = 0
for e in pool.get("entries", []):
    if e.get("id") != "TRIAL-LABOR-W14-GENERATE":
        continue
    hit += 1
    e["status"] = "waiting"
    e["park_note"] = (
        "re-parked r494 bm-b per r483 canon W14 adjudication "
        "(RETAIL_QUANT_TRACK L11: unfreeze requires this canon's sec-4 "
        "gate = trial-budget attribution + sec-1.2 compliance self-proof; "
        "r493 re-arm 9c1d97877 lacked the self-proof -- read a governance "
        "park as a dead-r472-session mechanical park, missed the "
        "parked_per sec-1.2 ban citation). MSG-20261001-0540-bmc-bmb "
        "pre-burn inquiry honored: in-flight generate pid 54704 killed "
        "at dedup 500/10000, w14_candidates.json absent = trial-gate "
        "consumption N=0 (pre-burn zero-loss window held). Unfreeze path "
        "= sec-4 self-proof OR GM dual-ruling (PERPETUAL_FACES v1.1 "
        "pending, MSG-20261001-0400); berth-holder bm-b retains the "
        "freeze-commit prereg+seeds (archive kept, canon '档存不删')")
    for s in e.get("shards", []):
        s["status"] = "waiting"
assert hit == 1, f"expected 1 W14 entry, hit {hit}"
s = json.dumps(pool, ensure_ascii=False, indent=2)
if crlf > 0 and lf_only == 0:
    s = s.replace("\n", "\r\n")
with open(p, "w", encoding="utf-8", newline="") as fh:
    fh.write(s)
chk = json.loads(open(p, encoding="utf-8").read())
for e in chk["entries"]:
    if e["id"] == "TRIAL-LABOR-W14-GENERATE":
        print("entry:", e["status"], "| shard:", [s2["status"] for s2 in e["shards"]])
        print("park_note head:", e["park_note"][:110])
print("format:", "CRLF" if crlf > 0 and lf_only == 0 else "LF", "| indent 2")
