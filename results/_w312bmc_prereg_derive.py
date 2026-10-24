# -*- coding: utf-8 -*-
"""W312 prereg derive (bm-c r1202).

Canon-clone of the frozen W311 pre-run face
(git ea873c77d0:research/PERPETUAL_N1_W311_PREREG.md, 28,402B / 75 newlines,
sha16 5c98fc219bad6863) -> research/PERPETUAL_N1_W312_PREREG.md.

Cumulative-history chains (se_mu narrowing, A/B 1-hop wave list, own-turn
rotation list, RAM freeze chain) are parked behind pure-letter sentinels and
EXTENDED by one entry (never rolled) -- r1180/r1182/r1184 pit family.
Everything else rides ONE single-pass map: wave labels W>=301 +1, band tokens
+2200, ordinals +1, round labels +2, artifact names +1.

Usage: python results/_w312bmc_prereg_derive.py [--measure]
"""
import hashlib
import json
import re
import subprocess
import sys

SRC_REV = "ea873c77d0"
SRC_PATH = "research/PERPETUAL_N1_W311_PREREG.md"
OUT = "research/PERPETUAL_N1_W312_PREREG.md"
EXPECT_SHA16 = "5c98fc219bad6863"
EXPECT_BYTES = 28402
SEAT_SHA = "831cbe0a27"
SEAT_MSG = "MSG-20261024-1639-bmc-w312-seat"
FREE_RAM = "1.6"
MEASURE = "--measure" in sys.argv

raw = subprocess.run(["git", "show", "%s:%s" % (SRC_REV, SRC_PATH)],
                     capture_output=True, check=True).stdout
assert len(raw) == EXPECT_BYTES, "src bytes %d != %d" % (len(raw), EXPECT_BYTES)
assert hashlib.sha256(raw).hexdigest()[:16] == EXPECT_SHA16, "src sha16 mismatch"
src = raw.decode("utf-8")
assert src.count("\n") == 75, "src line count %d" % src.count("\n")

# ---------------------------------------------------------------- facts (machine-read)
res = json.load(open("results/perpetual_faces/n1_w311_results.json", encoding="utf-8"))
led = res["science_gates"]["ledger"]
assert led["total"] == 1108541 and led["prev_total"] == 1106341, "ledger anchor drift"
cum = res["null_pool_cumulative"]
assert cum["merged"]["n_values"] == 682120, "merged K drift"
assert abs(cum["merged"]["mu"] + 0.0928223394710608) < 1e-12
assert abs(cum["merged"]["sigma"] - 0.24514828848747955) < 1e-12
assert cum["se_mu_at_k682120"] == 0.000297
assert abs(cum["w311_only"]["mu"] + 0.10195040909090909) < 1e-12
assert abs(cum["w311_only"]["sigma"] - 0.24739515059200357) < 1e-12
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_682120"] == 1.2005 and kl["line_pre_w311"] == 1.2005
assert kl["line_delta_k_lift"] == 0.0
assert kl["n_eff_held_equal"] == 1106341
assert (abs(res["families"]["A_random_engine_exit"]["full_sharpe_p95"] - 0.3213) < 1e-12
        and abs(res["families"]["A_random_engine_exit"]["full_sharpe_p99"] - 0.4435) < 1e-12)
seed = json.load(open("results/_w312bmc_20261024_probe_receipt.json", encoding="utf-8"))
assert seed["verdict"] == "ADMIT"
l1 = seed["legs"]["leg1"]
assert l1["A"] == [701701, 703700] and l1["B"] == [703701, 703900]
assert l1["hops_A"] == 1 and l1["hops_B"] == 1
assert seed["legs"]["leg0"]["owner_rows"] == 301
assert seed["legs"]["leg0"]["bmc_rows"] == 130
print("facts OK: ledger 1,108,541 / K 682,120 / W311-only mu -0.10195041 / p95 0.3213")

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


PROJ = "\u6295\u5f71"          # 投影


def se(old):
    idx = old.rfind("\u2192W310")   # ->W310
    assert idx > 0, "se chain tail not found"
    tail = old[idx:]
    body = old[:idx]
    assert "0.000298" in tail
    assert "\u2192W311 " + PROJ + " 0.000297" in tail, "W311 projection tail not the expected shape"
    return (body + "\u2192W310 **0.000298**\u2192W311 **0.000297**\u2192W312 "
            + PROJ + " 0.000296")


def ab(old):
    t = old.replace("/W310/W311=A/B", "/W310/W311/W312=A/B", 1)
    assert "/W310/W311/W312=A/B" in t, "A/B chain tail not the expected /W310/W311=A/B"
    o_ord = "\u7b2c\u4e94\u5341\u516b\u6ce2"   # 58th wave
    n_ord = "\u7b2c\u4e94\u5341\u4e5d\u6ce2"   # 59th wave
    assert o_ord in t, "A/B chain ordinal not the expected 58th"
    t = t.replace(o_ord, n_ord)
    return t


def rot(old):
    t = old.replace("\u2192W311 bm-c own-turn rotation",
                    "\u2192W311 bm-c\u2192W312 bm-c own-turn rotation", 1)
    assert "W312 bm-c own-turn rotation" in t, "own-turn chain tail not expected W311"
    return t


def ram(old):
    m = re.search(r"\u00b7W310 \u51bb\u7ed3\u7a97 ~([\d.]+)G bm-c \u5b9e\u951a\u00b7\u672c\u7a97\u51bb\u7ed3\u7a97 ~([\d.]+)G bm-c \u5b9e\u951a\uff09", old)
    assert m, "RAM chain tail not found"
    word = "\u5b9e\u951a"   # 实锚
    new_tail = ("\u00b7W310 \u51bb\u7ed3\u7a97 ~" + m.group(1) + "G bm-c " + word +
                "\u00b7W311 \u51bb\u7ed3\u7a97 ~" + m.group(2) + "G bm-c " + word +
                "\u00b7\u672c\u7a97\u51bb\u7ed3\u7a97 ~" + FREE_RAM + "G bm-c " + word + "\uff09")
    return old[:m.start()] + new_tail + old[m.end():]


park(r"W277 \*\*0\.000314\*\*[^\n]*?\u6295\u5f71 0\.000297", se, "SECH")
park(r"W252/W253[^\n]*?\u7b2c\u4e94\u5341\u516b\u6ce2", ab, "ABCHAIN")
park(r"W288 bm-c[\s\S]{0,900}?own-turn rotation", rot, "ROTCH")
park(r"W206/W211[^\n]*?\u5b9e\u951a\uff09", ram, "RAMCH")

# ---------------------------------------------------------------- 2. wave labels +1 (W>=301)
out = wave_bump(out)

# ---------------------------------------------------------------- 3. numeric / ordinal / artifact maps
NUM = [
    ("1,106,341", "1,108,541"),
    ("1,104,141", "1,106,341"),
    ("679,920", "682,120"),
    ("682,120", "684,320"),
    ("0.302", "0.3213"),
    ("0.24514062", "0.24514829"),
    ("\u22120.09279280", "\u22120.09282234"),
    ("\u22120.08540905", "\u22120.10195041"),
    ("1.2004", "1.2005"),
    ("line_pre_w311", "line_pre_w312"),
    ("\u7b2c 309 \u679a", "\u7b2c 310 \u679a"),
    ("\u6ce2\u53f7 309=", "\u6ce2\u53f7 310="),
    ("\u884c 300 \u6ce8\u518c\u5728\u518c", "\u884c 301 \u6ce8\u518c\u5728\u518c"),
    ("bmc rows 129+\u5019\u9009=\u7b2c 130 \u679a", "bmc rows 130+\u5019\u9009=\u7b2c 131 \u679a"),
    ("bmc_rows=129", "bmc_rows=130"),
    ("bmc live rows 129", "bmc live rows 130"),
    ("\u7b2c\u4e00\u767e\u4e8c\u5341\u4e5d\u679a", "\u7b2c\u4e00\u767e\u4e09\u5341\u679a"),
    ("\u5f15\u64ce\u7ebf\u7b2c 301 \u6ce2", "\u5f15\u64ce\u7ebf\u7b2c 302 \u6ce2"),
    ("\u4e09\u767e\u96f6\u4e94\u9762", "\u4e09\u767e\u96f6\u516d\u9762"),
    ("CLEAN-AT-BIRTH 42nd gen", "CLEAN-AT-BIRTH 43rd gen"),
    ("--wave 311", "--wave 312"),
    ("n1_w310", "n1_w311"), ("n1_w311", "n1_w312"),
    ("_w310bmc_", "_w311bmc_"), ("_w311bmc_", "_w312bmc_"),
    ("MSG-20261024-1540-bmc-w311-seat", SEAT_MSG),
    ("442e881af8", "0b0265a62d"),
    ("d490186e9d", "2fdb496bb6"),
    ("5cbfce8417", SEAT_SHA),
    ("\u7b2c\u516d\u5341\u56db\u6b21", "\u7b2c\u516d\u5341\u4e94\u6b21"),
    ("\u7b2c\u516d\u5341\u4e94\u6b21", "\u7b2c\u516d\u5341\u516d\u6b21"),
    ("15:1x", "16:0x"),
    ("15:4x", "16:3x"),
    ("15:5x", "17:0x"),
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
    print("MEASURE ok")
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
    assert out.count(sent) == 1, "sentinel %s count %d" % (sent, out.count(sent))
    out = out.replace(sent, txt)

# ---------------------------------------------------------------- 5. round labels + post-fixes
# W310 window r1198/r1199 -> W311 window r1200/r1201; this window = r1202.
out = out.replace("r1198", "ZZRR1").replace("r1199", "ZZRR2").replace("r1200", "ZZRR3")
out = out.replace("ZZRR1", "r1200").replace("ZZRR2", "r1201").replace("ZZRR3", "r1202")

POST = [
    ("\u672c\u7a97 free RAM 2.1GB", "\u672c\u7a97 free RAM " + FREE_RAM + "GB"),
]
for old, new in POST:
    n = out.count(old)
    assert n >= 1, "post-fix %r hits=%d" % (old, n)
    out = out.replace(old, new)
    print("post-fix applied hits=%d" % n)

# ---------------------------------------------------------------- 6. asserts
if "--diag" in sys.argv:
    for tok in ("701_500", "699_501", "701_501", "703_700", "703_900"):
        print("DIAG", tok, out.count(tok))
        for m in re.finditer(re.escape(tok), out):
            print("   ...", out[max(0, m.start() - 90):m.start() + 40].replace("\n", "\\n"))
    sys.exit(0)
assert out.count("\n") == 75, "line count changed: %d" % out.count("\n")
assert out.count("699_501") == 0, "old A band leaked"
# 701_500 / 701_501..701_700 legitimately survive as the registered W311 A tail and
# W311 B refuser band quotes inside the probe-verbatim hop chain -- do not assert away.
for band in ("701_701..703_700", "703_701..703_900"):
    assert out.count(band) >= 2, "target band missing: %s" % band
assert out.count("W312") > 30 and out.count("W313") > 5
assert out.count("W300") == src.count("W300"), "W300 (cumulative) must not roll"
assert out.count("1,108,541") >= 3, "new ledger anchor missing"
assert out.count("682,120") >= src.count("679,920"), "prior-K roll mismatch"
assert out.count("line_pre_w312") >= 1 and out.count("line_pre_w311") == 0
assert out.count("ZZ") == 0, "sentinel leaked"
assert out.count("n1_w311") >= 4 and out.count("n1_w312") >= 1
assert out.count("n1_w310") == 0, "n1 double roll"
assert out.count(SEAT_SHA) >= 3
assert out.count(SEAT_MSG) >= 3
assert out.count("CLEAN-AT-BIRTH 43rd gen") == 1
assert out.count("r1200") >= 3 and out.count("r1202") >= 1

receipt = {"keys": counts, "band_tokens": nband,
           "bytes_src": len(raw), "bytes_out": len(out.encode("utf-8"))}
open("results/_w312bmc_derive_counts.json", "w", encoding="utf-8").write(
    json.dumps(receipt, ensure_ascii=False, indent=1))
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(out)
b = out.encode("utf-8")
print("WROTE %s bytes=%d lines=%d sha16=%s bands=%d keys=%d" % (
    OUT, len(b), out.count("\n"), hashlib.sha256(b).hexdigest()[:16], nband, len(NUM)))