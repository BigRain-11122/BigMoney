"""r266 (bm-a, live instance) splice: T-83 ticket byte-face repair (adopt dead-round r266 row).

Dead round r266 whole-file re-serialized the ticket (ensure_ascii=False face)
which flipped HEAD's escaped yield_note `\\u00a74` to raw, dropped the stray
trailing CR line and rearranged all 18 lines (R255 whole-file pseudo-diff
signal). R254/R255 mirror law: line-splice the one new row into HEAD bytes,
keep every other byte identical (incl. mixed escaped/raw faces + stray `\\r`
tail). Output diff vs HEAD must be exactly: r268 trailing comma + 1 new row.
"""
import difflib
import json
import subprocess

P = "fleet/tasks/T-2026-09-26-83-P1.json"
hb = subprocess.run(["git", "show", "HEAD:" + P], capture_output=True).stdout
wt = open(P, "rb").read()

rowline = [l for l in wt.split(b"\r\n") if l.startswith(b' "progress_r266"')]
assert len(rowline) == 1, "r266 row not found in WT"
rowline = rowline[0]
hl = hb.split(b"\r\n")
ks = [k for k, l in enumerate(hl) if l.startswith(b' "progress_r268"')]
assert len(ks) == 1
k = ks[0]
assert hl[k].endswith(b'"'), hl[k][-20:]
out = hl[:k] + [hl[k] + b","] + [rowline] + hl[k + 1:]
res = b"\r\n".join(out)

json.loads(res.decode("utf-8"))  # parse gate before write (r185)
open(P, "wb").write(res)

d = [x for x in difflib.unified_diff(
    hb.decode("utf-8").splitlines(), res.decode("utf-8").splitlines(), lineterm="", n=0)]
changed = [x for x in d if x[:1] in "+-" and not x.startswith(("---", "+++"))]
print("real changed lines vs HEAD:", len(changed))
for x in changed:
    print(x[:150])
esc = b"\\u00a74" in res
print("yield_note escaped face preserved:", esc)
print("stray CR tail preserved:", res.endswith(b"}\r\r\n"))
assert esc and res.endswith(b"}\r\r\n") and len(changed) == 3
print("SPLICE OK")
