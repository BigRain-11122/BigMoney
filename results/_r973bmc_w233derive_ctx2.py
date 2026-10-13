# -*- coding: utf-8 -*-
import io, re
t = io.open(r"results\_w232bmc_freeze_edits.py", encoding="utf-8", newline="").read()

def dump(pat, before=20, after=700, n=1):
    print("=" * 20, pat)
    for i, m in enumerate(re.finditer(re.escape(pat), t)):
        if i >= n: break
        print(repr(t[max(0, m.start()-before):m.start()+after]))

dump("# STRUCTURAL CHOICE (vs the W230 editor)", after=760)
dump('"prereg_bundle"', after=520)
dump("MSG-20261013-1345-bmc.md", after=60, n=3)
dump('f"W231 ledger head', before=120, after=120)
dump('"seat": seat_found', after=80)
dump('W229/W228/W227/W226', before=200, after=120)
dump("r967 window", before=200, after=160, n=3)
dump("a15 = ", before=60, after=200)
dump('"w225_transitive"', after=200)
dump("assert block.count(\"if w < 231\")", before=120, after=300)
print("=" * 20, "band-fact assert region")
i = t.index("WAVE_CONFIGS[232]")
print(repr(t[i-200:i+300]))
