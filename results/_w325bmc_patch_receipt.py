# -*- coding: utf-8 -*-
import io, json

p = "scripts/perpetual_faces.py"
t = io.open(p, encoding="utf-8", newline="").read()
old = "    # (freeze n/a) + W324 finalize product landed (ledger head"
new = "    # (freeze 9d495afdcd) + W324 finalize product landed (ledger head"
assert t.count(old) == 1, t.count(old)
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new))

rp = "results/_w325bmc_freeze_receipt.json"
r = json.load(open(rp, encoding="utf-8"))
r["upstream_w324"]["freeze_sha"] = "9d495afdcdce0fb3f23fbc539ad0fd6be8b89f45"
r["upstream_w324"]["freeze_sha_note"] = (
    "the lineage template greps 'W{prev} five-face freeze splice'; the actual r1229 "
    "commit subject is 'W324 PREREG FROZEN + five-face freeze splice', so the first "
    "run recorded n/a -- corrected here by machine-read short sha from git log "
    "(disclosed, not smoothed)")
open(rp, "w", encoding="utf-8").write(json.dumps(r, indent=1, ensure_ascii=False))
print("patched")