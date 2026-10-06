# -*- coding: utf-8 -*-
"""r769 bm-a generator: W156 freeze-edits driver from the r768 W155 template.
Order: anchor placeholders -> parity protection -> ordered value-map ->
post-valmap manual fixes -> global bare 155->156 -> live-anchor restore ->
parity restore + W155 row append. Output py_compiled."""
import py_compile

SRC = "results/_r768bma_w155_freeze_edits.py"
DST = "results/_r769bma_w156_freeze_edits.py"
src = open(SRC, encoding="utf-8", newline="").read()


def sub(old, new, n=1, tag="?"):
    global src
    c = src.count(old)
    assert c == n, f"{tag}: count={c} expect={n}: {old[:60]!r}"
    src = src.replace(old, new)
    print(f"  [{tag}] x{n} ok")


# --- 1. anchor placeholders ------------------------------------------------------
A1_FULL = ('    154: {"a": (353_604, 355_603), "b_exit": (355_604, 355_803),\\r\\n'
           '         "engine_owner": "bm-a"},\\r\\n'
           '}')
A1_PREFIX = A1_FULL[:-1]  # without trailing '}'
A2_FULL = ('"shard_subdir": "n1_w154", "out_name": "n1_w154_results.json",\\r\\n'
           '                            "engine_owner": "bm-a"},\\r\\n'
           '                       }')
A2_PREFIX = A2_FULL[:-len('\\r\\n                       }')]
A3 = ('    finally:\\r\\n        _set_wave(2)\\r\\n    # --- T-141 s2 lane face')
A4_FULL = ('"results/_r767bma_w154_band_gate.json, law sec.4 W154 row, "\\r\\n'
           '          "r767 bm-a] "\\r\\n'
           '          "+ T-141 s2 "')
A4_PREFIX = A4_FULL[:-len('          "+ T-141 s2 "')]

sub(A1_FULL, "@A1@", 1, "a1-def")
sub(A1_PREFIX, "@A1P@", 1, "a1-prefix")
sub(A2_FULL, "@A2@", 1, "a2-def")
sub(A2_PREFIX, "@A2P@", 1, "a2-prefix")
sub(A3, "@A3@", 1, "a3-def")
sub(A4_FULL, "@A4@", 1, "a4-def")
sub(A4_PREFIX, "@A4P@", 1, "a4-prefix")

# --- 2. parity block protection --------------------------------------------------
PSTART = "        # registered row parity (r307 pinned constants, recent estate)\\r\\n"
PEND = '            "registered W154 row parity drift (r307; bm-a r767)"\\r\\n'
i0 = src.find(PSTART)
i1 = src.find(PEND)
assert i0 > 0 and i1 > i0, (i0, i1)
parity_block = src[i0:i1 + len(PEND)]
src = src[:i0] + "@PARITY@" + src[i1 + len(PEND):]
print("  [parity] protected", len(parity_block), "bytes")

# --- 3. ordered value-map --------------------------------------------------------
VM = [
    ("355_804..357_803", "@ABAND@"), ("357_804..358_003", "@BBAND@"),
    ("355_604..357_603", "@NABAND@"), ("355_804..356_003", "@NBBAND@"),
    ("355_604..355_803", "@PBBAND@"),
    ("range(355_804, 357_804)", "@RA@"), ("range(357_804, 358_004)", "@RB@"),
    ("(355_804, 357_803)", "@TA@"), ("(357_804, 358_003)", "@TB@"),
    ("355_803+1", "@ABASE@"), ("357_803+1", "@BBASE@"),
    ("355_804", "@ABA@"), ("357_804", "@BBA@"),
    ("734,811", "@LEDG@"), ("336,720", "@K1@"),
    ("1fedffbe4", "@SHA@"), ("3095cb47e", "@PSHA@"),
    ("MSG-2026-10-06-0943", "@SEATTS@"),
    ("ONE HUNDRED-AND-FORTY-FIFTH", "@ORDA@"), ("seventy-first", "@ORDB@"),
    ("fourteenth", "@ORDC@"), ("rows 144", "@ROWSC@"), ("rows 70", "@ROWSB@"),
    ("_r767bma", "@OLDRDIR@"), ("_r768bma", "@RDIR@"),
    ("r767", "@PRW@"), ("r768", "@RW@"),
    ("W155", "@WN@"), ("W154", "@WP@"), ("w155", "@wn@"), ("w154", "@wp@"),
    ("len(pf.N1_BANDS) == 153", "@LEN153@"), ("N1_BANDS 153 rows", "@ROWS153@"),
]
BACK = [
    ("@ABAND@", "358_004..360_003"), ("@BBAND@", "360_004..360_203"),
    ("@NABAND@", "357_804..359_803"), ("@NBBAND@", "358_004..358_203"),
    ("@PBBAND@", "357_804..358_003"),
    ("@RA@", "range(358_004, 360_004)"), ("@RB@", "range(360_004, 360_204)"),
    ("@TA@", "(358_004, 360_003)"), ("@TB@", "(360_004, 360_203)"),
    ("@ABASE@", "358_003+1"), ("@BBASE@", "360_003+1"),
    ("@ABA@", "358_004"), ("@BBA@", "360_004"),
    ("@LEDG@", "737,011"), ("@K1@", "338,920"),
    ("@SHA@", "ffce2936f"), ("@PSHA@", "dde679c63"),
    ("@SEATTS@", "MSG-2026-10-06-1009"),
    ("@ORDA@", "ONE HUNDRED-AND-FORTY-SIXTH"), ("@ORDB@", "seventy-second"),
    ("@ORDC@", "fifteenth"), ("@ROWSC@", "rows 145"), ("@ROWSB@", "rows 71"),
    ("@OLDRDIR@", "_r768bma"), ("@RDIR@", "_r769bma"),
    ("@PRW@", "r768"), ("@RW@", "r769"),
    ("@WN@", "W156"), ("@WP@", "W155"), ("@wn@", "w156"), ("@wp@", "w155"),
    ("@LEN153@", "len(pf.N1_BANDS) == 154"), ("@ROWS153@", "N1_BANDS 154 rows"),
]
for a, b in VM:
    src = src.replace(a, b)
for a, b in BACK:
    src = src.replace(a, b)
print("  [valmap] applied")

# --- 4. post-valmap manual fixes ---------------------------------------------------
sub("(r761 Rev.B lesson + r762/r763/r764/r766/r768\nprecedent)",
    "(r761 Rev.B lesson + r762/r763/r764/r766/r767/r768\nprecedent)",
    1, "docstring-precedent")
sub('assert pf.N1_BANDS[155] == {"a": (353_604, 355_603),\\r\\n'
    '                            "b_exit": (355_604, 355_803),\\r\\n'
    '                            "engine_owner": "bm-a"}, "W155 row survived (r560 no-replace law)"',
    'assert pf.N1_BANDS[155] == {"a": (355_804, 357_803),\\r\\n'
    '                            "b_exit": (357_804, 358_003),\\r\\n'
    '                            "engine_owner": "bm-a"}, "W155 row survived (r560 no-replace law)"',
    1, "post-survived")
sub("r768 gate leg3 + r768 sec8 succession", "r768 gate leg3 + r769 sec8 succession",
    3, "sec8-split")
sub("+ r768 gate\\r\\n    # leg3 + r768 sec8 succession",
    "+ r768 gate\\r\\n    # leg3 + r769 sec8 succession",
    1, "sec8-split-broken")
sub("probe receipt +\\r\\n"
    "    # W155 finalize products; deletion-set EMPTY; delivery window\\r\\n"
    "    # absorbed a behind-2 bm-c r610 guard-round peer commit via\\r\\n"
    "    # merge, zero --no-verify; same-window self-ack inbox->processed\\r\\n"
    "    # move r769;",
    "probe receipt +\\r\\n"
    "    # W156 arc generator; deletion-set EMPTY; delivery window\\r\\n"
    "    # = direct fast-forward behind-0 at fetch (r769 pre-seat\\r\\n"
    "    # push), zero merge, zero --no-verify; self-ack inbox->processed\\r\\n"
    "    # move deferred to the W156 finalize window;",
    1, "deliv-edit1")
sub("probe receipt + W155 finalize products; deletion-set EMPTY; delivery window absorbed a behind-2 bm-c r610 guard-round peer commit via merge, zero --no-verify; same-window self-ack inbox->processed move r769;",
    "probe receipt + W156 arc generator; deletion-set EMPTY; delivery window = direct fast-forward behind-0 at fetch, zero merge, zero --no-verify; self-ack inbox->processed move deferred to the W156 finalize window;",
    1, "deliv-pre")
sub("probe receipt + W155 finalize\\r\\n"
    "    #     products; deletion-set EMPTY; delivery window absorbed a behind-2\\r\\n"
    "    #     bm-c r610 guard-round peer commit via merge;\\r\\n"
    "    #     zero --no-verify; same-window self-ack inbox->processed move\\r\\n"
    "    #     r769).",
    "probe receipt + W156 arc generator;\\r\\n"
    "    #     deletion-set EMPTY; delivery window = direct fast-forward\\r\\n"
    "    #     behind-0 at fetch, zero merge, zero --no-verify; self-ack\\r\\n"
    "    #     inbox->processed move deferred to the W156 finalize window).",
    1, "deliv-leg")

# --- 5. global bare 155->156 (variables, ranges, literals; anchors placeholdered) --
n155 = src.count("155")
src = src.replace("155", "156")
print(f"  [global] 155->156 x{n155}")
assert src.count("153") == 0 or "153" not in src.replace("353", ""), "bare 153 residue"

# --- 6. live-anchor restore -------------------------------------------------------
src = src.replace("@A1@", '    155: {"a": (355_804, 357_803), "b_exit": (357_804, 358_003),\\r\\n'
                   '         "engine_owner": "bm-a"},\\r\\n'
                   '}')
src = src.replace("@A1P@", '    155: {"a": (355_804, 357_803), "b_exit": (357_804, 358_003),\\r\\n'
                   '         "engine_owner": "bm-a"},\\r\\n')
src = src.replace("@A2@", '"shard_subdir": "n1_w155", "out_name": "n1_w155_results.json",\\r\\n'
                   '                            "engine_owner": "bm-a"},\\r\\n'
                   '                       }')
src = src.replace("@A2P@", '"shard_subdir": "n1_w155", "out_name": "n1_w155_results.json",\\r\\n'
                   '                            "engine_owner": "bm-a"},\\r\\n')
src = src.replace("@A3@", A3)
src = src.replace("@A4@", '"results/_r768bma_w155_band_gate.json, law sec.4 W155 row, "\\r\\n'
                   '          "r768 bm-a] "\\r\\n'
                   '          "+ T-141 s2 "')
src = src.replace("@A4P@", '"results/_r768bma_w155_band_gate.json, law sec.4 W155 row, "\\r\\n'
                   '          "r768 bm-a] "\\r\\n')
for tok in ("@A1", "@A2", "@A3", "@A4", "@PARITY@"):
    assert tok not in src, f"placeholder residue: {tok}"

# --- 7. parity restore + W155 row append --------------------------------------------
W155_PARITY = ('        assert pf.N1_BANDS[155] == {"a": (355_804, 357_803),\\r\\n'
               '                                    "b_exit": (357_804, 358_003),\\r\\n'
               '                                    "engine_owner": "bm-a"}, \\\\r\\n'
               '            "registered W155 row parity drift (r307; bm-a r768)"\\r\\n')
src = src.replace("@PARITY@", parity_block + W155_PARITY)
print("  [parity] restored + W155 row added")

open(DST, "w", encoding="utf-8", newline="\n").write(src)
py_compile.compile(DST, doraise=True)
print("built+compiled:", DST, len(src), "bytes")
