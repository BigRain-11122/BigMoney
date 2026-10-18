# -*- coding: utf-8 -*-
# r1091 diagnostic: replay the derive transform, dump post-phase3 'W266' contexts
import io, subprocess

CANON = "results/_w267bmc_freeze_edits.py"
blob_wt = subprocess.run(["git", "hash-object", CANON], capture_output=True, text=True).stdout.strip()
assert blob_wt.startswith("05ae8eeb2c8a0e2d"), blob_wt[:16]
t = io.open(CANON, encoding="utf-8", newline="").read()

def rep(old, new, expect, tag):
    global t
    n = t.count(old)
    assert n == expect, f"[{tag}] count {n} != {expect}: {old[:100]!r}"
    t = t.replace(old, new)

# phase 1
for old, new, e, tag in [
    ("W268p", "W269p", 13, "a"), ("W268", "W269", 13, "b"),
    ("604_701", "606_901", 5, "c"), ("604_900", "607_100", 4, "d"),
    ("602_701", "604_901", 8, "e"), ("604_700", "606_900", 9, "f"),
    ("602_900", "605_100", 2, "g"), ("604_500", "606_700", 2, "h"),
    ("602_501", "604_701", 4, "i"), ("602_700", "604_900", 6, "j"),
    ("1,009,535", "1,011,735", 6, "k"), ("583,120", "585,320", 6, "l"),
    ("1_009_535", "1_011_735", 1, "m"), ("583_120", "585_320", 1, "n"),
    ("n1_w267", "n1_w268", 4, "o"), ("n1w267-", "n1w268-", 2, "p"),
    ("w267_", "w268_", 10, "q"), ("n1_w266", "n1_w267", 4, "r"),
    ("w266_", "w267_", 89, "s"), ("_w267bmc_", "_w268bmc_", 11, "t"),
    ("MSG-20261018-1025-bmc-w267-seat", "MSG-20261018-1229-bmc-w268-seat", 7, "u"),
    ("942ebd5885 r1086", "b9ad2f1119 r1089", 1, "v"),
    ('SEAT_ORIGIN = "942ebd5885"', 'SEAT_ORIGIN = "b9ad2f1119"', 1, "w"),
    ("dc71ecc3f9", "7b9e9377", 1, "x"), ("df55e3fab9", "f1ec8231c7", 1, "y"),
    ('"wave": 266', '"wave": 267', 1, "z"),
    ("2026-10-18 11:2x bm-c r1088 freeze window", "2026-10-18 13:4x bm-c r1091 freeze window", 1, "aa"),
]:
    rep(old, new, e, tag)
# phase 2
rep("W267", "W268", 92, "p2own")
rep("W266", "W267", 163, "p2up")
# phase 3 (same list as the editor)
for old, new, e, tag in [
    ("W264_W265_W267_bands_respected", "W265_W266_W267_bands_respected", 2, "p3a"),
    ("W211..W265 legs (55)", "W211..W266 legs (56)", 1, "p3b"),
    ("W211..W265 fifty-five legs", "W211..W266 fifty-six legs", 1, "p3c"),
    ("range(211, 266)", "range(211, 267)", 1, "p3d"),
    ("own W248..W265 legs (18)", "own W248..W266 legs (19)", 4, "p3e"),
    ("own W248..W265", "own W248..W266", 1, "p3f"),
    ("W248..W265 eighteen legs", "W248..W266 nineteen legs", 1, "p3g"),
    ('N1_BANDS[") == 18', 'N1_BANDS[") == 19', 1, "p3h"),
    ("W211..W267 legs 55", "W211..W267 legs 56", 1, "p3i"),
    ("W248..W267 legs (19", "W248..W267 legs (20", 4, "p3j"),
    ("block = 125 rows", "block = 126 rows", 1, "p3k"),
    ("125 parity rows", "126 parity rows", 1, "p3l"),
    ('N1_BANDS[") == 124,', 'N1_BANDS[") == 125,', 1, "p3m"),
    ('!= 124', '!= 125', 1, "p3n"),
    ('N1_BANDS[") == 55', 'N1_BANDS[") == 56', 1, "p3o"),
    ('"fresh_legs_row_asserts": 19', '"fresh_legs_row_asserts": 20', 1, "p3p"),
    ('+ 19,', '+ 20,', 1, "p3q"),
    ("block parity = 121 rows", "block parity = 126 rows", 1, "p3r"),
    ("range(248, 267)", "range(248, 268)", 2, "p3s"),
    ("range(248, 266)", "range(248, 267)", 1, "p3t"),
    ("range(16, 267)", "range(16, 268)", 2, "p3u"),
    ("range(17, 267)", "range(17, 268)", 3, "p3v"),
    ("range(209, 268)", "range(209, 269)", 2, "p3w"),
    ("if w < 267)", "if w < 268)", 5, "p3x"),
    ("if w < 266)", "if w < 267)", 1, "p3y"),
    ("267 - _lw", "268 - _lw", 2, "p3z"),
    ("WAVE_CONFIGS[267]", "WAVE_CONFIGS[268]", 2, "c1"),
    ("WAVE_CONFIGS[266]", "WAVE_CONFIGS[267]", 3, "c2"),
    ("N1_BANDS[266]", "N1_BANDS[267]", 5, "c3"),
    ("get(266)", "get(267)", 1, "c4"),
    ("_c266", "_c267", 5, "c5"),
    ('267: {"batch"', '268: {"batch"', 2, "c6"),
    ('267: {{"batch"', '268: {{"batch"', 1, "c7"),
    ('267: {"a"', '268: {"a"', 1, "c8"),
    ('267: {{"a"', '268: {{"a"', 2, "c9"),
    ('266: {"batch"', '267: {"batch"', 2, "c10"),
    ('266: {"a"', '267: {"a"', 3, "c11"),
    ("arith_a267", "arith_a268", 6, "c12"),
    ("arith_b267", "arith_b268", 6, "c13"),
    ("(263, 262, 261, 260, 259, 258, 257, 256, 255, 254)",
     "(264, 263, 262, 261, 260, 259, 258, 257, 256, 255)", 2, "c14"),
    ("W254..W263", "W255..W264", 1, "c15"),
    ("len(owner_rows_live) == 256 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 85",
     "len(owner_rows_live) == 257 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 86", 1, "c16"),
    ("256/130/85", "257/130/86", 1, "c17"),
    ("owner_rows=256 / bma_rows=130 / bmc_rows=85", "owner_rows=257 / bma_rows=130 / bmc_rows=86", 1, "c18"),
    ("rows 256 + candidate = 257th", "rows 257 + candidate = 258th", 2, "c19"),
    ("; bm-c rows 85 +", "; bm-c rows 86 +", 1, "c20"),
    ("bm-c rows 85 + candidate = 86th owned", "bm-c rows 86 + candidate = 87th owned", 1, "c21"),
    ("# candidate = 86th EXACT", "# candidate = 87th EXACT", 1, "c22"),
    ("engine_owner==bm-c rows 85 + candidate", "engine_owner==bm-c rows 86 + candidate", 1, "c23"),
    ("bm-c rows {len(bmc_rows_live)} + candidate (86th own wave",
     "bm-c rows {len(bmc_rows_live)} + candidate (87th own wave", 1, "c24"),
    ("bm-c's 86th own wave", "bm-c's 87th own wave", 2, "c25"),
    ("EIGHTY-SIXTH owned", "EIGHTY-SEVENTH owned", 3, "c26"),
    ("TWO HUNDRED AND SIXTY-SEVENTH", "TWO HUNDRED AND SIXTY-EIGHTH", 3, "c27"),
    ("bmc_rows=85", "bmc_rows=86", 6, "c28"),
    ('"probe_receipt_bmc_ordinal_face": 85', '"probe_receipt_bmc_ordinal_face": 86', 1, "c29"),
    ("SEVENTEENTH", "EIGHTEENTH", 7, "c30"),
    ("SIXTEENTH", "SEVENTEENTH", 15, "c31"),
    ("seventeenth", "eighteenth", 4, "c32"),
    ("sixteenth", "seventeenth", 3, "c33"),
    ("fifty-fifth", "fifty-sixth", 2, "c34"),
    ("wave 267 engine_owner=bm-c", "wave 268 engine_owner=bm-c", 1, "c35"),
    ('"wave 267: "', '"wave 268: "', 1, "c36"),
    ("wave 267 = first free number", "wave 268 = first free number", 1, "c37"),
    ("cycle COMPLETE bm-c r1085+r1086 closeout 10:5x", "cycle COMPLETE bm-c r1088+r1089 closeout 12:3x", 1, "c38"),
    ("the bm-c r1086 splice window", "the bm-c r1088 splice window", 2, "c39"),
    ("own-wave full cycle r1086", "own-wave full cycle r1088+r1089", 1, "c40"),
    ("bm-c splice generation r1086 window", "bm-c splice generation r1088 window", 1, "c41"),
    ("verified r1087", "verified r1089", 1, "c42"),
    ("# r1086 splice window", "# r1088 splice window", 1, "c43"),
    ("(bm-c r1086", "(bm-c r1088", 1, "c44"),
    ("finalize one-pass bm-c r1086 closeout, ledger", "finalize one-pass bm-c r1089 closeout, ledger", 1, "c45"),
    ("finalize one-pass bm-c r1086 closeout ledger", "finalize one-pass bm-c r1089 closeout ledger", 1, "c46"),
    ("(r1086 MSG-", "(r1089 MSG-", 1, "c47"),
    ("r1086 BEFORE this freeze", "r1089 BEFORE this freeze", 1, "c48"),
    ("seat itself r1086; queue-head", "seat itself r1089; queue-head", 1, "c49"),
    ("(r1086, queue-head seat-first supply", "(r1089, queue-head seat-first supply", 1, "c50"),
    ("bm-c r1087 window", "bm-c r1090 window", 4, "c51"),
    ("# r1087 window", "# r1090 window", 1, "c52"),
    ("r1087 commit", "r1090 commit", 1, "c53"),
    ("derived by the bm-a", "derived by the bm-c", 1, "c54"),
    ("authored 10:5x", "authored 13:1x", 2, "c55"),
    ("_w266bmc_freeze_edits.py template", "_w267bmc_freeze_edits.py template", 1, "c56"),
    ("(R266: ", "(R267: ", 1, "c57"),
    ("_w == 266", "_w == 267", 1, "c58"),
    ("_set_wave(267)", "_set_wave(268)", 1, "c59"),
]:
    rep(old, new, e, tag)

print("post-phase3 W266 count:", t.count("W266"))
print("post-phase3 'W268 block' count:", t.count("W268 block"))
for i, ln in enumerate(t.split("\n"), 1):
    if "W268 block" in ln:
        print("BLK L%d: %s" % (i, ln.strip()[:180]))
for i, ln in enumerate(t.split("\n"), 1):
    if "W266" in ln:
        print("L%d: %s" % (i, ln.strip()[:180]))
