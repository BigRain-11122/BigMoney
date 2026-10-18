# -*- coding: utf-8 -*-
# r1093 bm-c: final missing-needle measurement pass for the W269 editor
import io, json
t = io.open(r'results\_w268bmc_freeze_edits.py', encoding='utf-8', newline='').read()
faces = [
    # missed phase-3 needles
    'N1_BANDS[") == 19', 'N1_BANDS[") == 20', "W211..W266 fifty-six legs",
    "W211..W267 fifty-six legs", "W211..W266 legs (56)", "W211..W266 legs (57)",
    "W248..W268 legs (20", "W248..W269 legs (21",
    "seat itself r1089; queue-head", "seat itself r1091; queue-head",
    "(r1089, queue-head seat-first supply", "(r1091, queue-head seat-first supply",
    "bm-a own-seat continuity", "bm-c own-seat continuity",
    "bm-c five-face freeze upstream seat", "bm-c (upstream seat honored)",
    "owner=bm-c seat honored", "engine_owner=bm-a",
    "W268 FREEZE UNBLOCKED", "was published AFTER",
    "bm-c own seat executed at the bm-c r1088 splice window",
    "bm-c own seat executed at the bm-c r1091 splice window",
    "W267 materializer face", "W268 materializer face",
    "W267 finalize product", "W268 block", "post-W267-REGISTERED", "post-W268-REGISTERED",
    "PRE-W268-splice", "PRE-W269-splice", "post-W267 registration",
    "dual-window parity", "W269 walk",
    "anchors W267 1,011,735 / K=585,320 at draft",
    "anchors W268 1,013,935 / K=587,520 at draft",
    "fifty-sixth consecutive", "fifty-seventh consecutive",
    "expect 257/130/86", "expect 258/130/87",
    # gone-candidates (expect 0 in canon)
    "fourteen-wave", "bma_ordinal", "ONE HUNDRED AND THIRTIETH",
    "fifty-three", "FOURTEENTH", "fourteenth", "fifteenth", "FIFTEENTH",
    "m246", "m247", "N1_BANDS[246] ==", "N1_BANDS[247] ==",
    "rows 255 + candidate", "bmc_rows=84", "bmc_rows=85", "rows 254 + candidate",
    "254/130/83", "owner_rows=254", "len(owner_rows_live) == 254",
    "len(owner_rows_live) == 256", "256/130/85",
    "owner_rows=256 / bma_rows=130 / bmc_rows=85",
    "(R265: ", "(R266: ", "_w == 265", "_w == 266",
    "W263_W264_W265_bands_respected", "W264_W265_W267_bands_respected",
    "bm-a five-face freeze upstream seat", "bm-a (upstream seat honored)",
    "owner=bm-a seat honored", "(bm-a seat owner expected)",
    "18:2x", "19:2x", "20:5x", "22:4x", "10:2x", "11:2x",
    "authored 09:0x", "authored 10:5x", "editor template",
    "thirty-six", "W211..W246", "W211..W264", "W247..W264", "own W247..W264",
    "range(211, 247)", "range(211, 265)", "range(247, 265)", "range(247, 266)",
    "range(16, 266)", "range(17, 266)", "range(211, 266)", "range(248, 266)",
    "range(16, 267)", "range(17, 267)", "range(209, 268)",
    "if w < 265)", "if w < 266)", '"wave": 265', '"wave": 266',
    "N1_BANDS\\[246\\]", "N1_BANDS\\[247\\]", "N1_BANDS\\[248\\]",
    "SIXTEENTH", "sixteenth", "arith_a267", "arith_b267",
    "== 123", "!= 123", "== 124", 'N1_BANDS[") == 124,',
    "PENDING at seat", "waits-upstream face disclosed honest",
    "EIGHTY-FIFTH owned", "EIGHTY-SIXTH owned", "83rd", "84th",
    "TWO HUNDRED AND SIXTY-SIXTH", "TWO HUNDRED AND SIXTY-SEVENTH",
    "fifty-five legs", "own W248..W265", "W248..W265 eighteen legs",
    "W211..W265 legs (55)", "1,009,535", "583,120", "1_009_535", "583_120",
    "1,007,335", "580,920", "block = 125 rows", "125 parity rows",
    '"fresh_legs_row_asserts": 19', "+ 19,", "n1_w266", "n1w267-", "w266_",
    "602_501", "602_700", "602_701", "602_900", "604_500",
    "600_301", "600_500", "600_700", "602_300", "600_501", "602_500",
    "598_101", "598_300", "598_301", "600_300", "598_500", "600_100",
    "df55e3fab9", "942ebd5885", "dc71ecc3f9", "MSG-20261018-1025-bmc-w267-seat",
    "_w266bmc_", "20261017", "W267p", "W268p", "bma rows 128",
    "266: {\"batch\"", "265: {\"batch\"",
    "w244_a holds wave-262", "w244_a holds wave-263 bands",
    "registered wave below 262", "registered wave below 263 composes",
    "bma rows 129 + candidate 130th", "593901", "m211",
]
counts = {f: t.count(f) for f in faces}
nonzero = {k: v for k, v in counts.items() if v != 0}
zero = sorted(k for k in counts if counts[k] == 0)
print("NON-ZERO:", json.dumps(nonzero, indent=1))
print()
print("ZERO count:", len(zero))
print("ZERO faces:", json.dumps(zero, indent=1))
