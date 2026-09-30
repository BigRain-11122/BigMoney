# r490 bm-b resolver: LOWAMP-P1-NULLS pool conflict (rebase replay of 533a5b2 onto origin)
# Recipe r312 pool-entry-done-union: done ABSORBS -> take origin(done) side wholesale;
# bm-b's transient relay-claim fields (owner=bm-c etc.) are non-authoritative claims, dropped.
# Byte-surgery on UTF-8 text, parse-verify + done-absorb assertion + CRLF audit before write.
import json

P = "results/runnable_pool.json"
b = open(P, "rb").read().decode("utf-8")
assert b.count("<<<<<<< HEAD") == 1, "expected exactly one conflict block"
i = b.find("<<<<<<< HEAD")
k1 = b.find("\n", i)          # end of <<< marker line
m = b.find("=======", k1)     # conflict separator line start
j = b.find(">>>>>>> ", m)     # >>> marker line start
k = b.find("\n", j)           # end of >>> marker line
assert 0 < i < k1 < m < j < k
head_sec = b[k1 + 1:m]        # HEAD-side content lines (incl. their trailing CRLF)
assert '"owner": "bm-b"' in head_sec and '"harvested_by": "bm-a"' in head_sec
assert '"owner": "bm-c"' not in head_sec
resolved = b[:i] + head_sec + b[k + 1:]
p = json.loads(resolved)
s = [x for e in p["entries"] if e["id"] == "LOWAMP-P1-NULLS"
     for x in e["shards"]][0]
assert s["status"] == "done"
assert s["harvested_by"] == "bm-a"
assert s["harvest_claim"].endswith("bm-a.json")
assert s["owner"] == "bm-b"  # done side kept pool owner face as-is
assert "<<<<<<<" not in resolved and ">>>>>>>" not in resolved
crlf = resolved.count("\r\n")
lf_only = resolved.count("\n") - crlf
assert lf_only == 0, (crlf, lf_only)
open(P, "wb").write(resolved.encode("utf-8"))
print("RESOLVED done-absorb OK: nulls shard done@bm-a, CRLF=%d, LF-only=%d" % (crlf, lf_only))
