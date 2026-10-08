# -*- coding: utf-8 -*-
"""r746 bm-c seed: byte-exact lineage build of _r746bmc_s0.py (bare 745->746)
and _r746bmc_clone.py (clone-of-clone two-number shift: 745->746 first, then
744->745 for the source-round refs) from r745 originals. Stale-token asserts
guard both shifts (r736 clone law chain). Transient seed; absorbed by the S0
commit like every round's first-build drivers (r745 s0/clone precedent)."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def shift(src_name, dst_name, reps, stale):
    src = os.path.join(ROOT, "Tools", src_name)
    dst = os.path.join(ROOT, "Tools", dst_name)
    txt = open(src, encoding="utf-8").read()
    for old, new in reps:
        txt = txt.replace(old, new)
    for needle in stale:
        assert needle not in txt, "stale token %r in %s" % (needle, dst_name)
    with open(dst, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(txt)
    return {"src": src_name, "dst": dst_name, "bytes_out": len(txt.encode("utf-8"))}


receipt = {
    "round": 746,
    "s0": shift("_r745bmc_s0.py", "_r746bmc_s0.py", [("745", "746")], ["745"]),
    "clone": shift("_r745bmc_clone.py", "_r746bmc_clone.py",
                   [("745", "746"), ("744", "745")], ["744"]),
}
print(json.dumps(receipt))
