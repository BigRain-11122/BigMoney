# -*- coding: utf-8 -*-
"""r1055 probe-3: for each P5e CHUNK face, compare transform(actual) vs the
current derived-editor dst. Equal = my transform is consistent with the
clone's already-correct dsts (zero-risk swap of src only)."""
import io, re

ED = r"results\_w254bmc_derive_editor.py"
SRC = r"results\_w253bmc_freeze_edits.py"
act = io.open(SRC, encoding="utf-8").read()

def seg(start, end):
    i0 = act.find(start)
    i1 = act.find(end, i0)
    assert i0 >= 0 and i1 > i0, "anchor fail: %r" % start[:50]
    return act[i0:i1 + len(end)]

def bshift_u(m):
    v = int(m.group(0).replace("_", "")) + 2200
    return "%d_%03d" % (v // 1000, v % 1000)

def bshift_c(m):
    return str(int(m.group(0)) + 2200)

def transform(s):
    s = s.replace("W254", "W255")
    s = s.replace("253", "254")
    s = s.replace("252", "253")
    s = re.sub(r"\b5(?:6[7-9]|7[0-8])_[0-9]{3}\b", bshift_u, s)
    s = re.sub(r"(?<![0-9])5(?:6[7-9]|7[0-8])[0-9]{3}\.\.5(?:6[7-9]|7[0-8])[0-9]{3}(?![0-9])",
               lambda m: "%d..%d" % (int(m.group(0)[:6]) + 2200, int(m.group(0)[8:]) + 2200), s)
    s = re.sub(r"(?<![\d.])5(?:6[7-9]|7[0-8])[0-9]{3}(?![\d.])", bshift_c, s)
    s = s.replace("FOURTH consecutive", "FIFTH consecutive")
    s = s.replace("fourth consecutive", "fifth consecutive")
    s = s.replace("THIRD consecutive", "FOURTH consecutive")
    s = s.replace("Third consecutive", "Fourth consecutive")
    s = s.replace("third consecutive", "fourth consecutive")
    s = s.replace("SECOND consecutive", "THIRD consecutive")
    s = s.replace("Second consecutive", "Third consecutive")
    s = s.replace("second consecutive", "third consecutive")
    s = s.replace("W251_W253_bands_respected", "W252_W253_bands_respected")
    s = s.replace("seed-gap face ENDED at W253", "seed-gap face ENDED at W252")
    return s

REGIONS = {
 "P5e-hdr": seg("# NEW FACE vs the W252 editor (honest disclosure, frozen W253 prereg sec.3",
                "# B_hop_lands_inside_A=false; hops=1)."),
 "P5e-bandfacts": seg("# W253 FACE (probe receipt leg1 relation_asserts):",
                "# machine-derived from the LIVE registered row, never transcribed."),
 "P5e-pfcmt": seg('"    # band gate ADMIT results/_w253bmc_20261016_probe_receipt.json: A = 1-HOP"',
                '"    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)",'),
 "P5e-pre": seg('"wave 253: "',
                '"re-derive + live-trace re-read, no staircase-equality assumption); ADMIT receipt "'),
 "P5e-pr": seg("'          \"A=1-HOP STAIRCASE-AFFECTS-A walk (hops=1, A_hop_chain verbatim, A_clean_at_naive_start=false, \"'",
                '"THIRD consecutive above-own-A landing), chain-order splice from the "'),
 "P5e-tailcmt": seg('"        # band facts (law sec.4 W253 row): A = 1-HOP STAIRCASE-AFFECTS-A"',
                '"        # re-derive + live-trace re-read, no staircase-equality assumption);",'),
}

t = io.open(ED, encoding="utf-8").read()
for tag, actual in REGIONS.items():
    tagmark = '"%s")' % tag
    i1 = t.find(tagmark)
    i0 = t.rfind("chunk('''", 0, i1)
    region = t[i0:i1 + len(tagmark)]
    parts = region.split("'''")
    assert len(parts) == 5, "wrapper %d for %s" % (len(parts), tag)
    cur_dst = parts[3].strip()
    my_dst = transform(actual).strip()
    if cur_dst == my_dst:
        print("[MATCH] %s dst identical (%d chars)" % (tag, len(my_dst)))
    else:
        print("[DIFF ] %s cur=%d mine=%d" % (tag, len(cur_dst), len(my_dst)))
        # first divergence
        k = 0
        while k < min(len(cur_dst), len(my_dst)) and cur_dst[k] == my_dst[k]:
            k += 1
        print("   first diff @%d" % k)
        print("   cur : ...%r" % cur_dst[max(0, k-50):k+90])
        print("   mine: ...%r" % my_dst[max(0, k-50):k+90])
