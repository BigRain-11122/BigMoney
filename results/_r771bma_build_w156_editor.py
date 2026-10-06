# -*- coding: utf-8 -*-
"""r771 bm-a W156 freeze-edits builder: transform the r768 W155 editor's
RUNTIME strings (not its source text -- the r769/r770 generator draft
failed on template-source escape forms) into the W156 editor script.

Cross-contamination guard: EVERY band numeral form (ranges, range()
machinery, row tuples, band tails for the +1 relations, bare band
starts) goes to a DIGIT-FREE placeholder before any other replacement
and is restored only after the bare 155->156 / 154->155 passes, so no
VM product can be re-shifted ('W155' contains '155'; '(355_804, 357_803)'
contains '355_804'; products of one VM row are never fed to a later row).
Projection wave W156 -> @PW@ -> W157 (r769 gate leg3 W157+ face);
projection numerals 357_804..359_803 / 358_004..358_203 -> 360_004..362_003 /
360_204..360_403. sec8 succession: W155 gate stays r768, W155 sec8 becomes
r769 (prereg L4/L31 authoritative face). Delivery-window: payload = W156
arc generator per the ffce2936f push evidence (direct fast-forward
behind-0, self-ack deferred to the W156 finalize window).
Output: results/_r771bma_w156_freeze_edits.py (compiled)."""
import io
import json
import py_compile

CRLF = "\r\n"
RT = json.load(io.open(r"results/_r771bma_w155_runtime_strings.json", encoding="utf-8"))
a1, r1, a2, r2, a3, r3, a4, r4 = (RT[k] for k in ("a1", "r1", "a2", "r2", "a3", "r3", "a4", "r4"))

PSTART = '        # registered row parity (r307 pinned constants, recent estate)'
PEND = '            "registered W154 row parity drift (r307; bm-a r767)"'
W155_PARITY = CRLF.join([
    '        assert pf.N1_BANDS[155] == {"a": (355_804, 357_803),',
    '                                    "b_exit": (357_804, 358_003),',
    '                                    "engine_owner": "bm-a"}, \\',
    '            "registered W155 row parity drift (r307; bm-a r768)"',
])

PH0 = [
    ("range(355_804, 357_804)", "@GA@"),
    ("range(357_804, 358_004)", "@GB@"),
    ("355_804..357_803", "@RA@"),
    ("357_804..358_003", "@RB@"),
    ("353_604..355_603", "@RC@"),
    ("355_604..355_803", "@RD@"),
    ("355_604..357_603", "@RE@"),
    ("355_804..356_003", "@RF@"),
    ("(353_604, 355_603)", "@TA@"),
    ("(355_604, 355_803)", "@TB@"),
    ("(355_804, 357_803)", "@TC@"),
    ("(357_804, 358_003)", "@TD@"),
    ("355_803", "@BA@"),
    ("357_803", "@BB@"),
    ("355_804", "@SA@"),
    ("357_804", "@SB@"),
]
PH0_BACK = {
    "@GA@": "range(358_004, 360_004)",
    "@GB@": "range(360_004, 360_204)",
    "@RA@": "358_004..360_003",
    "@RB@": "360_004..360_203",
    "@RC@": "355_804..357_803",
    "@RD@": "357_804..358_003",
    "@RE@": "357_804..359_803",
    "@RF@": "358_004..358_203",
    "@TA@": "(355_804, 357_803)",
    "@TB@": "(357_804, 358_003)",
    "@TC@": "(358_004, 360_003)",
    "@TD@": "(360_004, 360_203)",
    "@BA@": "358_003",
    "@BB@": "360_003",
    "@SA@": "358_004",
    "@SB@": "360_004",
}

VM_REST = [
    ("734,811", "737,011"),
    ("336,720", "338,920"),
    ("1fedffbe4", "ffce2936f"),
    ("3095cb47e", "dde679c63"),
    ("MSG-2026-10-06-0943", "MSG-2026-10-06-1009"),
    ("ONE HUNDRED-AND-FORTY-FIFTH", "ONE HUNDRED-AND-FORTY-SIXTH"),
    ("seventy-first", "seventy-second"),
    ("fourteenth", "fifteenth"),
    ("rows 144", "rows 145"),
    ("rows 70", "rows 71"),
    ("r768", "r769"),
    ("r767", "r768"),
    ("W155", "W156"),
    ("W154", "@PWV@"),
    ("w155", "w156"),
    ("w154", "@Pwv@"),
]
RESTORES = {
    "@PWV@": "W155", "@Pwv@": "w155",
    "@PW@": "W157", "@Pw@": "w157",
    "@PA@": "360_004..362_003", "@PB@": "360_204..360_403",
}

SEC8_CONTIG = ("r768 gate leg3 + r768 sec8 succession", "r768 gate leg3 + r769 sec8 succession")
SEC8_WRAP_OLD = "r768 gate" + CRLF + "    # leg3 + r768 sec8 succession"
SEC8_WRAP_NEW = "r768 gate" + CRLF + "    # leg3 + r769 sec8 succession"

DELIV = {
    "r1": (
        "probe receipt +" + CRLF +
        "    # W155 finalize products; deletion-set EMPTY; delivery window" + CRLF +
        "    # absorbed a behind-2 bm-c r610 guard-round peer commit via" + CRLF +
        "    # merge, zero --no-verify; same-window self-ack inbox->processed" + CRLF +
        "    # move r769;",
        "probe receipt +" + CRLF +
        "    # W156 arc generator; deletion-set EMPTY; delivery window" + CRLF +
        "    # = direct fast-forward behind-0 at fetch (r769 pre-seat" + CRLF +
        "    # push), zero merge, zero --no-verify; self-ack inbox->processed" + CRLF +
        "    # move deferred to the W156 finalize window;"),
    "r2": (
        "probe receipt + W155 finalize \"" + CRLF +
        "                                       \"products; deletion-set EMPTY; delivery window absorbed a \"" + CRLF +
        "                                       \"behind-2 bm-c r610 guard-round peer commit via merge, \"" + CRLF +
        "                                       \"zero --no-verify; pre-seat probe and freeze-window band-gate \"" + CRLF +
        "                                       \"runs derive identical, no fork face), \"",
        "probe receipt + W156 arc generator; \"" + CRLF +
        "                                       \"deletion-set EMPTY; delivery window = direct fast-forward \"" + CRLF +
        "                                       \"behind-0 at fetch (r769 pre-seat push), zero merge, zero \"" + CRLF +
        "                                       \"--no-verify; pre-seat probe and freeze-window band-gate \"" + CRLF +
        "                                       \"runs derive identical, no fork face), \""),
    "r3": (
        "probe receipt + W155 finalize" + CRLF +
        "    #     products; deletion-set EMPTY; delivery window absorbed a" + CRLF +
        "    #     behind-2 bm-c r610 guard-round peer commit via merge;" + CRLF +
        "    #     zero --no-verify; same-window self-ack inbox->processed move" + CRLF +
        "    #     r769).",
        "probe receipt + W156 arc generator;" + CRLF +
        "    #     deletion-set EMPTY; delivery window = direct fast-forward" + CRLF +
        "    #     behind-0 at fetch (r769 pre-seat push), zero merge, zero" + CRLF +
        "    #     --no-verify; self-ack inbox->processed move deferred to" + CRLF +
        "    #     the W156 finalize window)."),
}

EXPECT = {
    "a1": [('    155: {"a": (355_804, 357_803), "b_exit": (357_804, 358_003),', 1)],
    "r1": [('    156: {"a": (358_804, 360_003)', 0),
           ('    156: {"a": (358_004, 360_003), "b_exit": (360_004, 360_203),', 1),
           ('360_004..362_003 CLEAN hops=0 / B first-clean', 1),
           ('360_204..360_403', 1),
           ('registered W156 B band 360_004..360_203 will refuse the naive', 1),
           ('W157 freezer MUST re-derive on the post-W156', 1),
           ('W156 arc generator', 1),
           ('W156 finalize window', 1),
           ('MSG-2026-10-06-1009-bma-w156-seat', 1),
           ('ffce2936f', 1),
           ('r769 pre-seat', 2),
           ('r768 gate' + CRLF + '    # leg3 + r769 sec8 succession', 1)],
    "r2": [('"a_seed_base": 358_804', 0),
           ('"a_seed_base": 358_004,', 1),
           ('"b_exit_seed_base": 360_004,', 1),
           ('"shard_subdir": "n1_w156", "out_name": "n1_w156_results.json",', 1),
           ('156: {"batch": "PERPETUAL-N1-W156",', 1),
           ('W156 arc generator', 1),
           ('A = FIRST-CLEAN past the registered W155 B band', 1),
           ('B first-clean 360_204..360_403', 1),
           ('r768 gate leg3 + r769 sec8 succession', 1),
           ('W1..W155 finalize ALL LANDED', 1),
           ('net chain head 737,011', 1),
           ('K=338,920', 2),
           ('ONE HUNDRED-AND-FORTY-SIXTH', 1),
           ('rows 145', 1),
           ('dde679c63', 1)],
    "r3": [('_set_wave(156)', 1),
           ('assert WAVE_CONFIGS[156]["a_seed_base"] == 358_004 == 358_003 + 1,', 1),
           ('assert WAVE_CONFIGS[156]["b_exit_seed_base"] == 360_004 == 360_003 + 1,', 1),
           ('arith_a156 = set(range(358_004, 360_004))', 1),
           ('arith_b156 = set(range(360_004, 360_204))', 1),
           ('W156 A/B same-freeze mutual exclusion', 1),
           ('PERPETUAL-N1-W156-SHARD-0', 1),
           ('n1w156-0of12', 1),
           ('"n1_w156_results.json"), "W156 path drift"', 1),
           ('range(17, 156)', 1),
           ('range(16, 156)', 1),
           ('W2..W155 registered single state', 1),
           ('PERPETUAL_N1_W156_PREREG.md', 1),
           ('W156 arc generator', 1),
           ('r768 gate leg3 + r769 sec8 succession', 2),
           ('registered W155 row parity drift (r307; bm-a r768)', 1),
           ('staircase fifteenth', 2),
           ('seventy-second', 1),
           ('355_804', 1),
           ('357_804..358_003', 2)],   # prior-wave (W155) B band citations via @RD@
    "r4": [('"results/_r768bma_w155_band_gate.json, law sec.4 W155 row, "', 1),
           ('"+ W156 materializer face [same guard set, dep=W17..W155 "', 1),
           ('W155 bm-a r769 one-pass, K=338,920', 1),
           ('results/_r769bma_w156_band_gate.json, law sec.4 W156 row,', 1),
           ('r769 bm-a] "', 1)],
    "a3": [('    finally:', 1)],
    "a2": [('"shard_subdir": "n1_w155", "out_name": "n1_w155_results.json",', 1)],
    "a4": [('"results/_r768bma_w155_band_gate.json, law sec.4 W155 row, "', 1),
           ('"r768 bm-a] "', 1)],
}


def T(s, tag, counts):
    parity = None
    if PSTART in s:
        i0 = s.find(PSTART)
        i1 = s.find(PEND)
        assert i0 > 0 and i1 > i0, (tag, i0, i1)
        parity = s[i0:i1 + len(PEND)]
        s = s[:i0] + "@PAR@" + s[i1 + len(PEND):]
        counts[tag + ":parity"] = 1
    # projection wave + projection numerals FIRST (they contain band starts)
    s = s.replace("W156", "@PW@").replace("w156", "@Pw@")
    s = s.replace("357_804..359_803", "@PA@").replace("358_004..358_203", "@PB@")
    for old, new in PH0:
        c = s.count(old)
        if c:
            counts[f"{tag}:{old}"] = c
        s = s.replace(old, new)
    for old, new in VM_REST:
        c = s.count(old)
        if c:
            counts[f"{tag}:{old[:24]}"] = c
        s = s.replace(old, new)
    s = s.replace("155", "156").replace("154", "155")
    # restores AFTER the bare passes (double-shift guard)
    for ph, val in {**RESTORES, **PH0_BACK}.items():
        s = s.replace(ph, val)
    # sec8 succession (r768 gate kept, sec8 -> r769 per prereg L4/L31)
    counts[tag + ":sec8-contig"] = s.count(SEC8_CONTIG[0])
    s = s.replace(SEC8_CONTIG[0], SEC8_CONTIG[1])
    if tag == "r1":
        assert s.count(SEC8_WRAP_OLD) == 1, "r1 wrapped sec8 form missing"
        s = s.replace(SEC8_WRAP_OLD, SEC8_WRAP_NEW)
    elif tag == "r3":
        assert counts[tag + ":sec8-contig"] == 2, "r3 sec8 count != 2"
    elif tag == "r2":
        assert counts[tag + ":sec8-contig"] == 1, "r2 sec8 count != 1"
    # delivery-window narrative
    if tag in DELIV:
        old, new = DELIV[tag]
        assert s.count(old) == 1, f"{tag} delivery needle count={s.count(old)}"
        s = s.replace(old, new)
        counts[tag + ":delivery"] = 1
    if parity is not None:
        assert s.count("@PAR@") == 1
        s = s.replace("@PAR@", parity + CRLF + W155_PARITY)
    for ph in ("@PAR@", "@PW@", "@Pw@", "@PA@", "@PB@", "@PWV@", "@Pwv@") + tuple(PH0_BACK):
        assert ph not in s, (tag, ph)
    return s


counts = {}
new = {}
for k in ("a1", "r1", "a2", "r2", "a3", "r3", "a4", "r4"):
    new[k] = T(RT[k], k, counts)

print("=== replacement counts (nonzero) ===")
for k in sorted(counts):
    print(f"  {k}: {counts[k]}")

fails = []
print("=== structural expectations ===")
for k, checks in EXPECT.items():
    for needle, want in checks:
        got = new[k].count(needle)
        mark = "OK " if got == want else "FAIL"
        print(f"  [{mark}] {k}: {needle[:66]!r} got={got} want={want}")
        if got != want:
            fails.append(f"{k}: {needle[:70]}")

STALE = ["355_804..357_803", "355_604..357_603", "355_804..356_003",
         "353_604..355_603", "355_604..355_803", "734,811", "336,720",
         "1fedffbe4", "3095cb47e", "MSG-2026-10-06-0943", "seventy-first",
         "FOURTEENTH", "rows 144", "behind-2 bm-c r610", "same-window self-ack"]
# NOTE: '357_804..358_003' is NOT stale -- it is the prior-wave (W155) B band
# citation restored via @RD@ (r1 x1, r2 x1, r3 x2 legitimate occurrences).
for k in ("r1", "r2", "r3", "r4"):
    for stale in STALE:
        assert stale not in new[k], (k, stale)

A1_EXPECT = ('    155: {"a": (355_804, 357_803), "b_exit": (357_804, 358_003),' + CRLF +
             '         "engine_owner": "bm-a"},' + CRLF + '}')
assert new["a1"] == A1_EXPECT, "a1 anchor mismatch:\n%r" % new["a1"]
# insert-point semantics (r = anchor minus tail-marker + inserted + tail-marker)
assert new["r1"].startswith(new["a1"][:-1]) and new["r1"].endswith(CRLF + "}"), "r1/a1 prefix"
assert new["r2"].startswith(new["a2"][: -len("                       }")]) and \
    new["r2"].endswith("                       }"), "r2/a2 prefix"
assert new["r3"].startswith(new["a3"][: -len("    # --- T-141 s2 lane face")]) and \
    new["r3"].endswith("    # --- T-141 s2 lane face"), "r3/a3 prefix"
assert new["r4"].startswith(new["a4"][: -len('          "+ T-141 s2 "')]) and \
    new["r4"].endswith('          "+ T-141 s2 "'), "r4/a4 prefix"
assert not fails, f"expectation failures: {fails}"

pf_live = io.open(r"scripts/perpetual_faces.py", encoding="utf-8", newline="").read()
n1_live = io.open(r"scripts/perpetual_faces_n1.py", encoding="utf-8", newline="").read()
for needle, live, nm in ((new["a1"], pf_live, "pf:a1"), (new["a2"], n1_live, "n1:a2"),
                         (new["a3"], n1_live, "n1:a3"), (new["a4"], n1_live, "n1:a4")):
    c = live.count(needle)
    assert c == 1, f"{nm} live anchor count={c}"
print("live anchor pre-checks: pf:a1=1 n1:a2=1 n1:a3=1 n1:a4=1 OK")

# ---- emit the W156 editor --------------------------------------------------------
tpl = io.open(r"results/_r768bma_w155_freeze_edits.py", encoding="utf-8", newline="").read()
tl = tpl.splitlines(keepends=True)
i_edit_def = next(i for i, l in enumerate(tl) if l.startswith("def edit("))
i_edit1 = next(i for i, l in enumerate(tl) if l.startswith("# --- edit 1"))
edit_fn = "".join(tl[i_edit_def:i_edit1])

DOC = '''# -*- coding: utf-8 -*-
"""r771 bm-a W156 freeze edits: four insertions (pf N1_BANDS[156] row +
n1 WAVE_CONFIGS[156] + n1 W156 materializer leg + n1 PASS snippet).
EOL-adaptive (r370 law: files are CRLF-dominant -- blocks written CRLF);
needle count==1 (r745); insert-after-last-registered-row + post-anchor
content checks (r560); anchor = predecessor full lines, no whole-anchor
backfill (r580/r581); AST gate after every edit batch (r580/r581).
prereg block built by programmatic double-quote wrapping with the tail
paren KEPT on the last item (r761 Rev.B lesson + r762/r763/r764/r766/
r768 precedent).
Bloodline: r768 _r768bma_w155_freeze_edits.py machinery verbatim, W156
facts live-registry-driven (band gate _r769bma_w156_band_gate.json rc0);
pairs derived at the RUNTIME-STRING level by the r771 transform probe
(results/_r771bma_build_w156_editor.py) after the r769/r770 text-level
generator draft hit template-source escape-form mismatches (48-needle
escaping family + digit-free placeholder cross-contamination guard +
W157+ projection + delivery-window + sec8 succession fixes applied at
runtime level; prereg sec.3 seed-scale fix 355_804/357_804 -> 358_804x/
358_004+360_004 T-90 alignment pre-freeze)."""
'''

out = [DOC, "import ast\nimport io\n\n",
       'PF = r"scripts/perpetual_faces.py"\n', 'N1 = r"scripts/perpetual_faces_n1.py"\n',
       'CRLF = "\\r\\n"\n\n\n', edit_fn, "\n"]
for k in ("a1", "r1", "a2", "r2", "a3", "r3", "a4", "r4"):
    out.append(f"{k} = {new[k]!r}\n")
    if k in ("r1", "r2", "r3", "r4"):
        out.append("\n")
out.append("\n# --- apply the four edits ---------------------------------------------------------\n")
out.append("edit(PF, [(a1, r1)])\n\n")
out.append("edit(N1, [(a2, r2), (a3, r3), (a4, r4)])\n\n")
out.append('''# --- post-edit structural assertions --------------------------------------------
import sys
sys.path.insert(0, ".")
sys.path.insert(0, "scripts")
import importlib
import perpetual_faces as pf
importlib.reload(pf)
assert sorted(pf.N1_BANDS)[-1] == 156 and len(pf.N1_BANDS) == 154, \\
    "pf N1_BANDS row-count drift after W156 insert"
assert pf.N1_BANDS[156] == {"a": (358_004, 360_003),
                            "b_exit": (360_004, 360_203),
                            "engine_owner": "bm-a"}, "W156 row face drift"
assert pf.N1_BANDS[155] == {"a": (355_804, 357_803),
                            "b_exit": (357_804, 358_003),
                            "engine_owner": "bm-a"}, "W155 row survived (r560 no-replace law)"
print("post-edit structural assertions PASS: N1_BANDS 154 rows tail W156, "
      "W155 row intact")
''')

DST = r"results/_r771bma_w156_freeze_edits.py"
src = "".join(out)
io.open(DST, "w", encoding="utf-8", newline="\n").write(src)
py_compile.compile(DST, doraise=True)
print("built+compiled:", DST, len(src), "bytes")

json.dump({"transform_counts": counts,
           "expectation_failures": fails,
           "anchor_prechecks": "pf:a1=1 n1:a2=1 n1:a3=1 n1:a4=1",
           "output": DST, "output_bytes": len(src)},
          io.open(r"results/_r771bma_w156_editor_build_receipt.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("build receipt written")
