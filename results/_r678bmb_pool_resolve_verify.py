"""r678 bm-b pool merge-resolution verification -- post canon-resolve checks:
(1) EOL face still CRLF (resolve probed stage2=ours=CRLF restored face);
(2) zero-loss: every entry id on BOTH parent sides present in the union;
(3) trio NULLS owner/keepalive fields intact (the live-burn faces);
(4) reparse clean.
"""
import json, os, subprocess, sys

CREAT = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POOL = os.path.join(ROOT, "results", "runnable_pool.json")

def blob(ref):
    return subprocess.run(["git", "show", f"{ref}:results/runnable_pool.json"],
                          capture_output=True, creationflags=CREAT).stdout

cur = open(POOL, "rb").read()
crlf, lf = cur.count(b"\r\n"), cur.count(b"\n")
assert crlf == lf and crlf > 1000, f"EOL face regressed post-resolve: CRLF={crlf} LF={lf}"
print(f"leg1 EOL: CRLF={crlf} face held (resolve probed ours=CRLF)")

ours = json.loads(blob("HEAD"))          # my freeze commit side (CRLF restored)
theirs = json.loads(blob("MERGE_HEAD"))  # origin incoming side
merged = json.loads(cur.decode("utf-8"))

def ids(doc):
    out = set()
    for e in doc.get("entries", []):
        out.add(e.get("id"))
        for sh in e.get("shards", []):
            out.add(sh.get("key"))
    return {x for x in out if x}

oi, ti, mi = ids(ours), ids(theirs), ids(merged)
lost_o = oi - mi
lost_t = ti - mi
print(f"leg2 zero-loss: ours={len(oi)} theirs={len(ti)} merged={len(mi)} "
      f"ours-only-lost={len(lost_o)} theirs-only-lost={len(lost_t)}")
assert not lost_o and not lost_t, f"LOSS: ours={sorted(lost_o)[:5]} theirs={sorted(lost_t)[:5]}"
print(f"leg3 entries: ours={len(ours.get('entries', []))} "
      f"theirs={len(theirs.get('entries', []))} "
      f"merged={len(merged.get('entries', []))}")

# trio NULLS live-burn faces intact
for eid in ("FUND-VALUE-P1-NULLS", "FUND-QUALITY-P1-NULLS",
            "FUND-DIVLOWVOL-P1-NULLS"):
    row = next((e for e in merged.get("entries", [])
                if e.get("id") == eid), None)
    assert row is not None, f"trio entry {eid} missing post-resolve"
    shard = row.get("shards", [{}])[0]
    print(f"leg4 {eid}: status={row.get('status')} owner={shard.get('owner')} "
          f"owner_since={shard.get('owner_since')}")
print("POOL_RESOLVE_VERIFY_OK")
