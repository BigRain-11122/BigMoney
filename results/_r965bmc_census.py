# -*- coding: utf-8 -*-
# r965 bm-c census: W230 freeze edits template face counts (for W231 derive editor calibration)
import io, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(HERE, "_w230bmc_freeze_edits.py")
t = io.open(T, encoding="utf-8", newline="").read()
faces = [
 "n1_w230", "n1_w230_results", "w230_", "n1w230", "W230", "W231+ projection",
 "naive W231 A window", "W231 freezer", "W231+ freezer", "downstream W231 seat",
 "_set_wave(230)", '"wave": 230,', "f'{CFG_I}230: ", "f'{ROW_I}230: ",
 "f'230: {{\"a\":", "ROW_I + '230: {\"a\"'", "'    230: {\"a\"'", "'230: {\"batch\"'", "'230: {\"a\"'",
 "WAVE_CONFIGS[230]", "N1_BANDS.get(230)", "wave 230 = first free number", "wave 230: ",
 "if w < 230)", "range(16, 230)", "range(17, 230)", "w<230 count", "below 230 composes",
 "below-230", "registered wave below 230",
 "NINETY-FIRST instance anticipated", "NINETY-SECOND",
 "TWO HUNDRED AND THIRTY-FIRST", "TWO HUNDRED AND THIRTIETH",
 "sixty-first", "sixtieth", "61st", "60th", "bmc_ordinal=60",
 "rows 59 + candidate", "rows 219 + candidate", "== 219 and len(bmc_rows_live) == 59",
 "expect 219/59", "precedent 218/58 pre-splice", "splice 219/59",
 "W229", "w229_", "n1_w229_results", "n1w229", "W228", "w228_", "n1_w228_results",
 "m227", "N1_BANDS\\[227\\]", "_c229", "arith_a230", "arith_b230", "n3r1_used230",
 "WAVE_CONFIGS[229]", "pf.N1_BANDS[229]", "pf.N1_BANDS[228]",
 "w229_out_path", "w228_out_path",
 "MSG-20261013-1155-bmc", "MSG-20261013-1000-bmc", "MSG-20261013-0855-bmc",
 "6638ddf9f", "6cfe285e3", "c9e9e83b8", "aebe0a5ac", "91de0ae83",
 "2ae8553e6", "24e12fa5e", "f4b24e865", "ce70c5808", "e3665b334", "b5d62792d",
 "0ef11a120", "aec41c57c",
 "927_589", "501_720", "929_789", "503_920", "(520_804, 522_803)", "(522_804, 523_003)",
 "(523_004, 525_003)", "(525_004, 525_203)",
 "r962 10:1x", "r963 11:5x", "r963 freeze window", "r964", "r965",
 "nineteenth consecutive", "twentieth consecutive", "fifth consecutive", "fourth consecutive",
 "FOURTEEN-level", "FIFTEEN-level", "88 rows", "89 rows",
 "w229_a_tail", "w229_b_tail", "w229_freeze_sha", "w229_prereg_sha",
 "w230_prereg_sha", "w230_receipt_sha", "w230_a_tail", "w230_b_tail", "w229_total",
 "w227_leg", "w228_leg", "w229_leg", "w230_leg",
 "EIGHTY-NINTH", "NINETIETH instance", "n1_w231",
 "221st", "220th", "hundred-and", "SEventy", "sixty-first",
 "msg-20261013", "e485a0b3f", "e1401e62", "1932f439",
]
cal = {f: t.count(f) for f in sorted(set(faces))}
io.open(os.path.join(HERE, "_r965bmc_census.json"), "w", encoding="utf-8").write(
    json.dumps(cal, indent=1, sort_keys=True))
print(json.dumps(cal, indent=1, sort_keys=True))
print("LEN", len(t))
