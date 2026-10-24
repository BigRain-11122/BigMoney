# -*- coding: utf-8 -*-
"""W308 prereg derive (bm-c r1194, resumed window).

Canon-clone of the frozen W307 pre-run face
(git 2131c78e84:research/PERPETUAL_N1_W307_PREREG.md, 25,690B / 63 newlines,
sha16 3f335b23cc464c1e) -> research/PERPETUAL_N1_W308_PREREG.md.

Cumulative-history faces (A/B 1-hop chain, se_mu narrowing chain, own-turn
rotation list, RAM freeze chain, estate chain, timeline/seat/freeze-window
clauses) are parked behind pure-letter sentinels and EXTENDED by one entry
(never rolled) -- r1180/r1182/r1184 pit family.
Everything else rides ONE single-pass map: wave labels W>=301 +1, bands +2200,
ordinals +1, round labels +2, plus a printed literal-count table written to a
receipt before any replacement (r1171 law; ASCII-only prints).

Usage: python results/_w308bmc_prereg_derive.py [--measure]
"""
import hashlib
import json
import re
import subprocess
import sys

SRC_REV = "2131c78e84"
SRC_PATH = "research/PERPETUAL_N1_W307_PREREG.md"
OUT = "research/PERPETUAL_N1_W308_PREREG.md"
EXPECT_SHA16 = "3f335b23cc464c1e"
EXPECT_BYTES = 25690
SEAT_SHA = "3e1ecb3110"
SEAT_MSG = "MSG-20261024-1325-bmc-w308-seat"
MEASURE = "--measure" in sys.argv

raw = subprocess.run(["git", "show", "%s:%s" % (SRC_REV, SRC_PATH)],
                     capture_output=True, check=True).stdout
assert len(raw) == EXPECT_BYTES, "src bytes %d != %d" % (len(raw), EXPECT_BYTES)
assert hashlib.sha256(raw).hexdigest()[:16] == EXPECT_SHA16, "src sha16 mismatch"
src = raw.decode("utf-8")
assert src.count("\n") == 63

# ---------------------------------------------------------------- facts (machine-read)
res = json.load(open("results/perpetual_faces/n1_w307_results.json", encoding="utf-8"))
led = res["science_gates"]["ledger"]
assert led["total"] == 1099741 and led["prev_total"] == 1097541, "ledger anchor drift"
cum = res["null_pool_cumulative"]
assert cum["merged"]["n_values"] == 673320, "merged K drift"
assert abs(cum["merged"]["mu"] + 0.09283045387037367) < 1e-12
assert abs(cum["merged"]["sigma"] - 0.24512009026497977) < 1e-12
assert cum["se_mu_at_k673320"] == 0.000299
assert abs(cum["w307_only"]["mu"] + 0.08758804545454546) < 1e-12
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_673320"] == 1.2 and kl["n_eff_held_equal"] == 1097541
assert abs(res["families"]["A_random_engine_exit"]["full_sharpe_p95"] - 0.3153) < 1e-12
seed = json.load(open("results/_w308bmc_20261024_probe_receipt.json", encoding="utf-8"))
assert seed["verdict"] == "ADMIT"
l1 = seed["legs"]["leg1"]
assert l1["A"] == [692901, 694900] and l1["B"] == [694901, 695100]
assert l1["hops_A"] == 1 and l1["hops_B"] == 1
assert seed["legs"]["leg0"]["owner_rows"] == 297
assert seed["legs"]["leg0"]["bmc_rows"] == 126
print("facts OK: ledger 1,099,741 / K 673,320 / W307-only mu -0.08758805 / p95 0.3153")

# ---------------------------------------------------------------- 1. park cumulative history
out = src
stash = {}


def park(pattern, fn, label, expect=1):
    global out
    ms = list(re.finditer(pattern, out))
    assert len(ms) == expect, "%s: %d hits (expect %d)" % (label, len(ms), expect)
    olds = [m.group(0) for m in ms]
    news = [fn(o) for o in olds]
    for o, n in zip(olds, news):
        assert n != o, "%s: transform was a no-op" % label
    sent = "ZZ" + re.sub(r"[^A-Z]", "", label.upper())
    stash[sent] = news[0]
    for o in olds:
        out = out.replace(o, sent, 1)
    print("PARK %-10s hits=%d ascii_ok=%s" % (label, len(ms), olds[0].isascii()))
    return olds, news


def sub(text, pairs):
    """Single-pass token map (no cascades)."""
    keys = sorted(pairs, key=len, reverse=True)
    pat = re.compile("|".join(re.escape(k) for k in keys))
    return pat.sub(lambda m: pairs[m.group(0)], text)


def wave_bump(text, floor=301):
    return re.sub(r"W(\d{3})", lambda m: "W%03d" % (int(m.group(1)) + 1)
                  if int(m.group(1)) >= floor else m.group(0), text)


def tl1(old):
    t = sub(old, {"r1191": "r1193", "W306": "W307"})
    assert "r1193/r1193/r1193" in t and "W307" in t
    return t


def tl2(old):
    t = sub(old, {"7ab2b459e2": "2131c78e84", "aa8e2a8f1f": "897b31fc83",
                  "09:5x": "11:5x", "W307": "W308", "W306": "W307",
                  "r1191": "r1193", "r1192": "r1194"})
    assert "2131c78e84" in t and "897b31fc83" in t
    return t


def fwin(old):
    t = sub(old, {"r1192": "r1194", "10:5x": "13:0x"})
    assert "r1194" in t and "13:0x" in t
    return t


def ab(old):
    t = old.replace("/W307=A/B", "/W307/W308=A/B", 1)
    assert "/W307/W308=A/B" in t, "A/B chain tail not the expected /W307=A/B"
    o_ord = "\u7b2c\u4e94\u5341\u56db\u6ce2"   # 54th wave
    n_ord = "\u7b2c\u4e94\u5341\u4e94\u6ce2"   # 55th wave
    assert o_ord in t, "A/B chain ordinal not the expected 54th"
    t = t.replace(o_ord, n_ord)
    return t


def se(old):
    t = old.replace("\u2192W307 \u6295\u5f71 0.000299",
                    "\u2192W307 **0.000299**\u2192W308 \u6295\u5f71 0.000299", 1)
    assert "W308 \u6295\u5f71 0.000299" in t and "\u2192W307 **0.000299**" in t
    return t


def rot(old):
    t = old.replace("\u2192W307 bm-c own-turn rotation",
                    "\u2192W307 bm-c\u2192W308 bm-c own-turn rotation", 1)
    assert "W308 bm-c own-turn rotation" in t, "own-turn chain tail not the expected W307"
    return t


def ram(old):
    pat = (r"\u00b7W306 \u51bb\u7ed3\u7a97 ~([\d.]+)G bm-c (\u5b9e\u951a)"
           r"\u00b7\u672c\u7a97\u51bb\u7ed3\u7a97 ~([\d.]+)G bm-c (\u5b9e\u951a)")
    m = re.search(pat, old)
    assert m, "RAM chain tail not found"
    w306_val, word, cur_val = m.group(1), m.group(2), m.group(3)
    new_tail = ("\u00b7W306 \u51bb\u7ed3\u7a97 ~%sG bm-c %s"
                "\u00b7W307 \u51bb\u7ed3\u7a97 ~%sG bm-c %s"
                "\u00b7\u672c\u7a97\u51bb\u7ed3\u7a97 ~0.3G bm-c %s"
                % (w306_val, word, cur_val, word, word))
    return old[:m.start()] + new_tail + old[m.end():]


def fin(old):
    t = sub(old, {"W306": "W307", "r1191": "r1193", "10:3x": "11:5x"})
    assert "W307 finalize one-pass" in t
    return t


def est(old):
    t = sub(old, {"r1191": "r1193", "W306": "W307", "7ab2b459e2": "2131c78e84",
                  "aa8e2a8f1f": "897b31fc83", "fd6b75028e": "5270a15dd8"})
    assert "5270a15dd8" in t
    return t


def seat(old):
    t = sub(old, {"r1192": "r1194",
                  "MSG-20261024-1047-bmc-w307-seat": SEAT_MSG,
                  "d78f799608": SEAT_SHA, "_w307bmc_": "_w308bmc_"})
    assert SEAT_SHA in t and SEAT_MSG in t
    return t


park(r"r1191/r1191/r1191[^\n]{0,40}?\u5148\u4f8b\u5b9e\u65f6\u95f4\u7ebf\uff1a", tl1, "TLWINDOW")
park(r"prereg 7ab2b459e2[^\n]*?r1192 \u7a97\u843d\u5730", tl2, "TLPAIR")
park(r"bm-c \u5faa\u73af\u73ed r1192[^\n]*?10:5x", fwin, "FREEZEWIN")
park(r"W252/W253[^\n]*?\u7b2c[\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u5341]+\u6ce2",
     ab, "ABCHAIN")
park(r"\u2192W277 \*\*0\.000314\*\*[^\n]*?\u2192W307 \u6295\u5f71 0\.000299", se, "SECH")
park(r"W288 bm-c[^\n]*?own-turn rotation", rot, "ROTCH")
park(r"W300 \u51bb\u7ed3\u7a97[^\n]*?\u5b9e\u951a\u00b7\u672c\u7a97\u51bb\u7ed3\u7a97 ~[\d.]+G bm-c \u5b9e\u951a",
     ram, "RAMCH")
park(r"estate chain r1191/r1191/r1191[^\n]*?fd6b75028e", est, "ESTCH")
park(r"W306 finalize one-pass bm-c r1191 \u7a97 10:3x", fin, "FINFACE", expect=2)
park(r"bm-c r1192 \u5e2d\u4f4d MSG-20261024-1047-bmc-w307-seat[^\n]*?bands ADMIT verbatim",
     seat, "SEATF")

# ---------------------------------------------------------------- 2. wave labels +1 (W>=301)
out = wave_bump(out)

# ---------------------------------------------------------------- 3. numeric / ordinal / artifact maps
NUM = [
    ("1,095,341", "1,097,541"), ("1,097,541", "1,099,741"),
    ("671,120", "673,320"), ("673,320", "675,520"),
    ("0.3090", "0.3153"),
    ("0.24512663", "0.24512009"),
    ("\u22120.08964145", "\u22120.08758805"),
    ("0.0032", "0.0052"),
    ("1.1999", "1.2"),
    ("line_pre_w307", "line_pre_w308"),
    ("\u6c60\u7b2c 305 \u679a", "\u6c60\u7b2c 306 \u679a"),
    ("\u884c 296 \u6ce8\u518c\u5728\u518c", "\u884c 297 \u6ce8\u518c\u5728\u518c"),
    ("\u7b2c\u4e00\u767e\u4e8c\u5341\u4e94\u679a", "\u7b2c\u4e00\u767e\u4e8c\u5341\u516d\u679a"),
    ("\u7b2c 126 \u679a", "\u7b2c 127 \u679a"),
    ("\u7b2c\u516d\u5341\u4e00\u6b21", "\u7b2c\u516d\u5341\u4e8c\u6b21"),
    ("\u7b2c\u516d\u5341\u6b21", "\u7b2c\u516d\u5341\u4e00\u6b21"),
    ("\u5f15\u64ce\u7ebf\u7b2c 297 \u6ce2", "\u5f15\u64ce\u7ebf\u7b2c 298 \u6ce2"),
    ("\u6ce2\u53f7 305=", "\u6ce2\u53f7 306="),
    ("CLEAN-AT-BIRTH 38th gen", "CLEAN-AT-BIRTH 39th gen"),
    ("bmc_rows=125", "bmc_rows=126"),
    ("bmc live rows 125", "bmc live rows 126"),
    ("bmc rows 125+", "bmc rows 126+"),
    ("engine_owner==bm-c 124 \u884c", "engine_owner==bm-c 125 \u884c"),
    ("--wave 307", "--wave 308"),
    ("n1_w306", "n1_w307"), ("n1_w307", "n1_w308"),
    ("_w306bmc_", "_w307bmc_"), ("_w307bmc_", "_w308bmc_"),
    ("MSG-20261024-1047-bmc-w307-seat", SEAT_MSG),
    ("d78f799608", SEAT_SHA),
    ("aa8e2a8f1f", "897b31fc83"),
    ("09:5x", "11:5x"), ("r307", "r308"),
    ("r1191", "r1193"), ("r1192", "r1194"),
]

counts = {}
for a, b in NUM:
    counts[a] = out.count(a)
print("COUNT TABLE (key -> occurrences):")
for a, _ in sorted(NUM, key=lambda kv: -len(kv[0])):
    print("  key=%s -> %d" % (a.encode("ascii", "backslashreplace").decode(), counts[a]))
zero = [a for a in counts if counts[a] == 0]
assert not zero, "zero-hit keys: %r" % zero
if MEASURE:
    print("MEASURE ok, zero=%r" % (zero,))
    for s, t in stash.items():
        print("STASH", s, "len", len(t))
    sys.exit(0)

out = sub(out, dict(NUM))

# ---------------------------------------------------------------- 4. bands +2200
def roll(m):
    v = int(m.group(1)) * 1000 + int(m.group(2)) + 2200
    return "%03d_%03d" % (v // 1000, v % 1000)


out, nband = re.subn(r"\b(\d{3})_(\d{3})\b", roll, out)
assert nband > 0

for sent, txt in stash.items():
    assert out.count(sent) >= 1, "sentinel %s missing" % sent
    out = out.replace(sent, txt)

# ---------------------------------------------------------------- 5. post-fixes (live machine face)
POST = [
    ("\u672c\u7a97 free RAM 1.3GB", "\u672c\u7a97 free RAM 0.3GB"),
    ("W307 \u6c60\u6d4b\u8bd5", "W308 \u6c60\u6d4b\u8bd5"),
]
for old, new in POST:
    n = out.count(old)
    if n == 0:
        continue
    out = out.replace(old, new)
    print("post-fix applied hits=%d" % n)

# ---------------------------------------------------------------- 6. asserts
assert out.count("\n") == 63, "line count changed: %d" % out.count("\n")
assert out.count("690_701") == 0, "old band block leaked"
assert out.count("692_901") >= 3, "target A band missing"
for band in ("692_901..694_900", "694_901..695_100"):
    assert out.count(band) >= 2, "target band missing: %s" % band
assert out.count("W308") > 30 and out.count("W309") > 5
assert out.count("W300") == src.count("W300"), "W300 (cumulative) must not roll"
assert out.count("W301") == src.count("W301"), "W301 (cumulative chain) must not roll"
assert out.count("1,099,741") == src.count("1,097,541")
assert out.count("673,320") == src.count("671,120"), "671,120 roll mismatch"
assert out.count("675,520") == src.count("673,320"), "673,320 roll mismatch"
assert out.count("line_pre_w308") == 1
assert out.count("line_pre_w307") == 0, "line_pre double roll"
assert out.count("ZZ") == 0, "sentinel leaked"
assert out.count("n1_w307") >= 4 and "n1_w308" in out
assert out.count("n1_w306") == 0, "n1 double roll"
assert out.count(SEAT_SHA) >= 3
assert out.count(SEAT_MSG) >= 3
assert out.count("CLEAN-AT-BIRTH 39th gen") == 1
assert out.count("r1193") >= 3 and "r1194" in out

receipt = {"keys": counts, "band_tokens": nband,
           "bytes_src": len(raw), "bytes_out": len(out.encode("utf-8"))}
open("results/_w308bmc_derive_counts.json", "w", encoding="utf-8").write(
    json.dumps(receipt, ensure_ascii=False, indent=1))
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(out)
b = out.encode("utf-8")
print("WROTE %s bytes=%d lines=%d sha16=%s bands=%d keys=%d" % (
    OUT, len(b), out.count("\n"), hashlib.sha256(b).hexdigest()[:16], nband, len(NUM)))