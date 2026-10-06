# -*- coding: utf-8 -*-
import io
pfsrc = io.open('scripts/perpetual_faces.py', encoding='utf-8', newline='').read()
n1src = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8', newline='').read()
checks = [
    ("pf: new face", "bm-b r779 read-only-observer processed, a2d002357" in pfsrc),
    ("pf: old face gone", "bm-a r784 finalize window" not in pfsrc),
    ("pf: old deferred gone", "move deferred to the W161 finalize window" not in pfsrc),
    ("n1: new face frag1", "self-ack inbox->processed move landed (bm-b" in n1src),
    ("n1: new face frag2", "r779 read-only-observer processed, a2d002357)." in n1src),
    ("n1: old face gone", "bm-a r784 finalize window" not in n1src),
]
ok = True
for name, val in checks:
    print(("PASS" if val else "FAIL"), name)
    ok = ok and val
print("ALL PASS" if ok else "SOME FAILED")
