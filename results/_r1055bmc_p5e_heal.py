# -*- coding: utf-8 -*-
"""r1055 heal-2: rebuild ALL SEVEN P5e chunk faces in the W254 derive editor
from ground truth -- src = verbatim region from the actual W253 freeze-edits
script (xf() blankets produce the correct needle automatically); dst = the
W254 wave-shift transform of the actual region (bands +2200 machine-verified
staircase-era law + wave labels +1 + ordinal prose +1 + disclosed rsv-key
and seed-gap historical fixes per W253-editor precedent)."""
import io, re, py_compile

ED = r"results\_w254bmc_derive_editor.py"
SRC = r"results\_w253bmc_freeze_edits.py"

act = io.open(SRC, encoding="utf-8").read()

def seg(start, end, name):
    i0 = act.find(start)
    i1 = act.find(end, i0)
    assert i0 >= 0, "start anchor not found: %s" % name
    assert i1 > i0, "end anchor not found: %s" % name
    return act[i0:i1 + len(end)]

REGIONS = {
 "P5e-hdr": seg("# NEW FACE vs the W252 editor (honest disclosure, frozen W253 prereg sec.3",
                "# B_hop_lands_inside_A=false; hops=1).", "hdr"),
 "P5e-bandfacts": seg("# W253 FACE (probe receipt leg1 relation_asserts):",
                "# machine-derived from the LIVE registered row, never transcribed.", "bandfacts"),
 "P5e-pfcmt": seg('"    # band gate ADMIT results/_w253bmc_20261016_probe_receipt.json: A = 1-HOP"',
                '"    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)",', "pfcmt"),
 "P5e-pre": seg('"wave 253: "',
                '"re-derive + live-trace re-read, no staircase-equality assumption); ADMIT receipt ",', "pre"),
 "P5e-pr": seg("'          \"A=1-HOP STAIRCASE-AFFECTS-A walk (hops=1, A_hop_chain verbatim, A_clean_at_naive_start=false, \"'",
                "\"THIRD consecutive above-own-A landing), chain-order splice from the \"", "pr"),
 "P5e-tailcmt": seg('"        # band facts (law sec.4 W253 row): A = 1-HOP STAIRCASE-AFFECTS-A"',
                '"        # re-derive + live-trace re-read, no staircase-equality assumption);",', "tailcmt"),
}

def bshift_u(m):
    v = int(m.group(0).replace("_", "")) + 2200
    return "%d_%03d" % (v // 1000, v % 1000)

def bshift_c(m):
    return str(int(m.group(0)) + 2200)

def transform(s):
    # blankets in pass order (mirrors the editor's P2/P3/P4 on script text)
    s = s.replace("W254", "W255")
    s = s.replace("253", "254")
    s = s.replace("252", "253")
    # band-space +2200 (staircase-era law, machine-verified per clone P0)
    s = re.sub(r"\b5(?:6[7-9]|7[0-8])_[0-9]{3}\b", bshift_u, s)
    s = re.sub(r"(?<![0-9])5(?:6[7-9]|7[0-8])[0-9]{3}\.\.5(?:6[7-9]|7[0-8])[0-9]{3}(?![0-9])",
               lambda m: "%d..%d" % (int(m.group(0)[:6]) + 2200, int(m.group(0)[8:]) + 2200), s)
    s = re.sub(r"(?<![\d.])5(?:6[7-9]|7[0-8])[0-9]{3}(?![\d.])", bshift_c, s)
    # ordinal prose: high-first to avoid double-shift
    s = s.replace("FOURTH consecutive", "FIFTH consecutive")
    s = s.replace("fourth consecutive", "fifth consecutive")
    s = s.replace("THIRD consecutive", "FOURTH consecutive")
    s = s.replace("Third consecutive", "Fourth consecutive")
    s = s.replace("third consecutive", "fourth consecutive")
    s = s.replace("SECOND consecutive", "THIRD consecutive")
    s = s.replace("Second consecutive", "Third consecutive")
    s = s.replace("second consecutive", "third consecutive")
    # disclosed fixes (W253-editor precedent family):
    # (a) rsv-key face: blanket produces W251_W253 hybrid; W254 probe receipt
    #     leg1 keys are W252_W253 (registered pair at W254-seat time)
    s = s.replace("W251_W253_bands_respected", "W252_W253_bands_respected")
    # (b) historical seed-gap face: ENDED at W252 is a frozen historical fact,
    #     blanket shifted it to W253 -> restore
    s = s.replace("seed-gap face ENDED at W253", "seed-gap face ENDED at W252")
    return s

t = io.open(ED, encoding="utf-8").read()
log = []
for tag, actual in REGIONS.items():
    dst = transform(actual)
    # locate the chunk call by tag
    tagmark = '"%s")' % tag
    i1 = t.find(tagmark)
    assert i1 > 0, "tag not found: %s" % tag
    i0 = t.rfind("chunk('''", 0, i1)
    assert i0 >= 0, "chunk start not found: %s" % tag
    region = t[i0:i1 + len(tagmark)]
    parts = region.split("'''")
    assert len(parts) == 5, "chunk wrapper shape %d != 5 for %s" % (len(parts), tag)
    old_src = parts[1].strip()
    assert old_src.startswith("# NEW FACE") or old_src.startswith("ra = leg") or old_src.startswith('"    #') \
        or old_src.startswith("# W25") or old_src.startswith('"wave') or old_src.startswith("' ") \
        or old_src.startswith('"        #'), "unexpected src head for %s: %r" % (tag, old_src[:50])
    parts[1] = "\n" + actual + "\n"
    parts[3] = "\n" + dst + "\n"
    t = t[:i0] + "'''".join(parts) + t[i1 + len(tagmark):]
    log.append("%s: src %d->%d, dst %d->%d" % (tag, len(old_src), len(actual), len(parts[3].strip()), len(dst)))

io.open(ED, "w", encoding="utf-8", newline="").write(t)
py_compile.compile(ED, doraise=True)
print("HEAL-2 OK")
for l in log:
    print(" ", l)
# spot checks on dst integrity
for tag, actual in REGIONS.items():
    d = transform(actual)
    assert "574_101" in d and "576_300" in d and "THIRD consecutive A-hop" in d, "dst spot-check failed: %s" % tag
    assert "W251_W253" not in d, "rsv hybrid survived: %s" % tag
print("dst spot-checks PASS (574_101/576_300/THIRD-A-hop present, no rsv hybrid)")
