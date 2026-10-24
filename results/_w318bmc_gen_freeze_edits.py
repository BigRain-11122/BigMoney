# -*- coding: utf-8 -*-
# 2026-10-24 23:2x bm-c r1217 splice window: W318 five-face freeze splice editor generator.
# Canon-clone of results/_w317bmc_freeze_edits.py with THREE distinct literal faces kept
# on their own shift tracks (r1168/r1171/r1182/r1184 family):
#   1. W-tokens (W316/W317/W318 + lowercase w314..w317)  -> single descending cascade
#   2. seed-band literals                                -> parked to pure-alpha sentinels
#                                                           BEFORE mapping (no double shift)
#   3. ordinals / row-number literals / MSG timestamps   -> explicit, count-asserted
# The engine-owned-wave ordinal is re-anchored to the REGISTERED COUNT (r1170 body-chain
# law): the prereg body chain reads 306 / 307 / 308 for W316 / W317 / W318, while the
# W316/W317 freeze PROSE carried a stale 313/314 commit-chain value -- disclosed, not
# silently smoothed (see the receipt's ordinal_face field).
import io, re, sys

SRC = "results/_w317bmc_freeze_edits.py"
DST = "results/_w318bmc_freeze_edits.py"

t = io.open(SRC, encoding="utf-8").read()
orig_len = len(t)


def rep(text, old, new, expect):
    c = text.count(old)
    assert c == expect, f"count {old!r}: {c} != {expect}"
    return text.replace(old, new)


# ---------- face 1: W-tokens (descending cascade) ----------
for old, new, n in (("W318", "W319", 10), ("W317", "W318", 47), ("W316", "W317", 31),
                    ("w317", "w318", 15), ("w316", "w317", 2), ("w315", "w318", 12),
                    ("w314", "w317", 74)):
    t = rep(t, old, new, n)

# ---------- face 2: seed bands parked to alpha sentinels, then mapped ----------
PARK = [("712_501", "@@BA@@", 4), ("712_700", "@@BB@@", 2), ("712_701", "@@BC@@", 4),
        ("712_900", "@@BD@@", 2), ("714_500", "@@BE@@", 2), ("714_700", "@@BF@@", 2),
        ("714_701", "@@BG@@", 2), ("714_900", "@@BH@@", 2)]
for lit, tok, n in PARK:
    t = rep(t, lit, tok, n)
BANDS = {"@@BA@@": "714_701",   # W317 naive-A refuser band start  -> W318 naive-A refuser start
         "@@BB@@": "714_900",   # W317 registered B band tail      -> W318 naive-A refuser tail
         "@@BC@@": "714_901",   # W317 A band base                 -> W318 A base
         "@@BD@@": "715_100",   # W317 naive-B refuser band tail   -> W318 naive-B tail
         "@@BE@@": "716_700",   # W317 naive-A arithmetic tail     -> W318 naive-A arithmetic tail
         "@@BF@@": "716_900",   # W317 A band tail                 -> W318 A tail
         "@@BG@@": "716_901",   # W317 B band base                 -> W318 B base
         "@@BH@@": "717_100"}   # W317 B band tail                 -> W318 B tail
for tok, lit in BANDS.items():
    t = rep(t, tok, lit, None if False else t.count(tok))

# ---------- face 3: explicit literals ----------
t = rep(t, "MSG-20261024-2215-bmc-w318-seat", "MSG-20261024-2259-bmc-w318-seat", 4)  # noqa: E501
t = rep(t, "r1214", "r1217", 6)
# upstream anchor literals read off the W317 finalize product
t = rep(t, "1_119_541", "1_121_741", 1)
t = rep(t, "693_120", "695_320", 1)
# registry row literal (two waves before, kept once) + pickaxe needle (prior wave row)
t = rep(t, '315: {"a"', '316: {"a"', 2)
t = rep(t, "== 306 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 135",
        "== 307 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 136", 1)
# ordinals: B-face first (the pre-existing SEVENTY-FIRST is the above-own-A face),
# then the A-hop face, then the re-anchored engine-owned / owned-claim words.
t = rep(t, "SEVENTY-FIRST", "SEVENTY-SECOND", 7)
t = rep(t, "SEVENTIETH", "SEVENTY-FIRST", 8)
t = rep(t, "THREE HUNDRED AND FOURTEENTH", "THREE HUNDRED AND EIGHTH", 2)
t = rep(t, "HUNDRED-AND-THIRTY-THIRD", "HUNDRED-AND-THIRTY-SEVENTH", 2)
# header provenance line
t = rep(t, "# Lineage = results/_w318bmc_freeze_edits.py",
        "# Lineage = results/_w317bmc_freeze_edits.py", 1)
t = rep(t, "# 2026-10-24 22:5x bm-c r1217", "# 2026-10-24 23:2x bm-c r1217", 1)
t = rep(t, "# block's own w<312> boundary is a legitimate prior-wave boundary: it moves from",
        "# block's own w<318> boundary is a legitimate prior-wave boundary: it moves from", 1)
t = rep(t, "# the template's w<311> by exactly one).",
        "# the template's w<317> by exactly one).", 1)

# ---------- face 4: bare wave NUMBERS (outside the W-token cascade) ----------
NUM = [
    ("NEW_W = 317          # the wave being spliced", "NEW_W = 318          # the wave being spliced", 1),
    ("PREV_W = 316         # the last REGISTERED wave", "PREV_W = 317         # the last REGISTERED wave", 1),
    ("PRIOR_W = 315        # prior band face", "PRIOR_W = 316        # prior band face", 1),
    ("317: {{\"a\": ({fmt(a_lo)}", "318: {{\"a\": ({fmt(a_lo)}", 2),
    ("317: {{\"batch\": \"PERPETUAL-N1-W318\"", "318: {{\"batch\": \"PERPETUAL-N1-W318\"", 1),
    ("\"wave 317: \",", "\"wave 318: \",", 1),
    ("'317: {\"batch\": \"PERPETUAL-N1-W318\"'", "'318: {\"batch\": \"PERPETUAL-N1-W318\"'", 2),
    ("\"machine\": \"bm-c\", \"wave\": 316,", "\"machine\": \"bm-c\", \"wave\": 317,", 1),
]
for old, new, n in NUM:
    t = rep(t, old, new, n)

# ---------- post-checks ----------
assert "712_" not in t and "714_500" not in t, "stale seed-band literal leaked"
assert not re.search(r"@@B[A-H]@@", t), "band sentinel leaked"
assert "SEVENTIETH" not in t and "SEVENTY-FIRST consecutive" in t
assert "HUNDRED-AND-THIRTY-THIRD" not in t
assert t.count("MSG-20261024-2259-bmc-w318-seat") == 4
assert t.count('"_w318bmc_freeze_receipt.json"') >= 1

io.open(DST, "w", encoding="utf-8", newline="\n").write(t)
print(f"generated {DST}: {len(t)} bytes (src {orig_len})")
print("counts:", {k: t.count(k) for k in ("W318", "W317", "W319", "w318", "w317",
                                          "714_901", "716_900", "716_901", "717_100",
                                          "THREE HUNDRED AND EIGHTH")})