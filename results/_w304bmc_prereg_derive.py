# -*- coding: utf-8 -*-
"""W304 prereg derive (bm-c r1187).

Canon-clone of the frozen W303 pre-run face (git 886e88787a:research/PERPETUAL_N1_W303_PREREG.md,
25,374B / 63 newlines, sha16 ffbe3df0115a9d60) -> research/PERPETUAL_N1_W304_PREREG.md.

Cumulative-history faces (A/B 1-hop chain, se_mu narrowing chain, own-turn rotation list,
RAM freeze chain, estate chain, seat/timeline clauses) are parked behind pure-letter sentinels
and EXTENDED by one entry (never rolled) -- r1180/r1182/r1184 pit family.
Everything else rides ONE single-pass map: wave labels W>=300 +1, bands +2200, ordinals +1,
plus a printed literal-count table before any replacement is written (r1171 law).

Unlike the W303 script this one LOCATES each parked face by regex on the frozen text
(never transcribes the old literal) -- r1171 literal-count family.

Usage: python results/_w304bmc_prereg_derive.py [--measure]
"""
import hashlib
import json
import re
import subprocess
import sys

SRC_REV = "886e88787a"
SRC_PATH = "research/PERPETUAL_N1_W303_PREREG.md"
OUT = "research/PERPETUAL_N1_W304_PREREG.md"
EXPECT_SHA16 = "ffbe3df0115a9d60"
EXPECT_BYTES = 25374
MEASURE = "--measure" in sys.argv

raw = subprocess.run(["git", "show", "%s:%s" % (SRC_REV, SRC_PATH)],
                     capture_output=True, check=True).stdout
assert len(raw) == EXPECT_BYTES, "src bytes %d != %d" % (len(raw), EXPECT_BYTES)
assert hashlib.sha256(raw).hexdigest()[:16] == EXPECT_SHA16, "src sha16 mismatch"
src = raw.decode("utf-8")
assert src.count("\n") == 63

# ---------------------------------------------------------------- facts (machine-read)
res = json.load(open("results/perpetual_faces/n1_w303_results.json", encoding="utf-8"))
led = res["science_gates"]["ledger"]
assert led["total"] == 1090941 and led["prev_total"] == 1088741, "ledger anchor drift"
cum = res["null_pool_cumulative"]
assert cum["merged"]["n_values"] == 664520, "merged K drift"
assert abs(cum["merged"]["mu"] + 0.09282371245410222) < 1e-12
assert abs(cum["merged"]["sigma"] - 0.2451257705050054) < 1e-12
assert cum["se_mu_at_k664520"] == 0.000301
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_664520"] == 1.1996 and kl["line_pre_w303"] == 1.1996
seed = json.load(open("results/_w304bmc_20261024_probe_receipt.json", encoding="utf-8"))
assert seed["verdict"] == "ADMIT"
l1 = seed["legs"]["leg1"]
assert l1["A"] == [684101, 686100] and l1["B"] == [686101, 686300]
assert l1["hops_A"] == 1 and l1["hops_B"] == 1
assert seed["legs"]["leg0"]["owner_rows"] == 293
assert seed["legs"]["leg0"]["bmc_rows"] == 122

# ---------------------------------------------------------------- 1. park cumulative history
out = src
stash = {}


def park(pattern, fn, label, expect=1):
    global out
    ms = list(re.finditer(pattern, out))
    assert len(ms) == expect, "%s: %d hits (expect %d)" % (label, len(ms), expect)
    m = ms[0]
    old = m.group(0)
    new = fn(old)
    assert new != old, "%s: transform was a no-op" % label
    sent = "ZZ" + re.sub(r"[^A-Z]", "", label.upper())
    stash[sent] = new
    out = out[:m.start()] + sent + out[m.end():]
    print("PARK %-10s hits=%d old=%r" % (label, len(ms), old[:110]))
    print("     %-10s new=%r" % ("", new[:110]))
    return old, new


def tl1(old):
    o = "r1185/r1185/r1185 W302 全周期先例实时间线："
    n = "r1186/r1186/r1186 W303 全周期先例实时间线："
    assert o in old
    return old.replace(o, n)


def tl2(old):
    o = "prereg 184e056533 落于 r1185 窗·splice 78b4b1ce5c 落于 r1185 执行窗 06:1x"
    n = "prereg 886e88787a 落于 r1186 窗·splice f8a956c17c 落于 r1186 执行窗 07:0x"
    assert o in old, old
    return old.replace(o, n)


def ab(old):
    o = "W303=A/B 双 1-hop 形态第五十波"
    n = "W303/W304=A/B 双 1-hop 形态第五十一波"
    assert o in old, old
    return old.replace(o, n)


def se(old):
    o = "→W303 投影 0.000301"
    n = "→W303 **0.000301**→W304 投影 0.000301"
    assert o in old, old
    return old.replace(o, n)


def rot(old):
    o = "W303 bm-c own-turn rotation"
    n = "W303 bm-c→W304 bm-c own-turn rotation"
    assert o in old, old
    return old.replace(o, n)


def ram(old):
    o = "·本窗冻结窗 ~1.8G bm-c 实锚"
    n = "·W303 冻结窗 ~1.8G bm-c 实锚·本窗冻结窗 ~1.6G bm-c 实锚"
    assert o in old, old
    return old.replace(o, n)


def est(old):
    o = "estate chain r1185/r1185/r1185 W302 全周期 184e056533+78b4b1ce5c+070ba903cf"
    n = "estate chain r1186/r1186/r1186 W303 全周期 886e88787a+f8a956c17c+774ef0c53f"
    assert o in old, old
    return old.replace(o, n)


def seat(old):
    o = ("bm-c r1186 席位 MSG-20261024-0640-bmc-w303-seat 已推 origin "
         "f09ad33571·probe receipt _w303bmc_20261024 机证·bands ADMIT verbatim")
    n = ("bm-c r1187 席位 MSG-20261024-0735-bmc-w304-seat 已推 origin "
         "098930328c·probe receipt _w304bmc_20261024 机证·bands ADMIT verbatim")
    assert o in old, old
    return old.replace(o, n)


park(r"splice 执行窗派生落地（r1185/r1185/r1185[^（\n]*?先例实时间线：", tl1, "TLWINDOW")
park(r"prereg 184e056533[^\n]*?06:1x", tl2, "TLPAIR")
park(r"W299/W300/W301/W302/W303=A/B[^\n]*?第五十波", ab, "ABCHAIN")
park(r"se_mu 收窄链[^\n]*?→W303 投影 0\.000301", se, "SECH")
park(r"W288 bm-c[^\n]*?own-turn rotation", rot, "ROTCH")
park(r"W300 冻结窗[^\n]*?本窗冻结窗 ~[\d.]+G bm-c 实锚", ram, "RAMCH")
park(r"estate chain r1185/r1185/r1185[^\n]*?070ba903cf", est, "ESTCH")
park(r"bm-c r1186 席位 MSG-20261024-0640-bmc-w303-seat[^\n]*?bands ADMIT verbatim",
     seat, "SEATF")

# ---------------------------------------------------------------- 2. wave labels +1 (W>=300)
out = re.sub(r"W(\d{3})", lambda m: "W%03d" % (int(m.group(1)) + 1)
             if int(m.group(1)) >= 300 else m.group(0), out)

# ---------------------------------------------------------------- 3. numeric / ordinal / artifact maps
NUM = [
    ("1,088,741", "1,090,941"), ("1,086,541", "1,088,741"),
    ("662,320", "664,520"), ("664,520", "666,720"),
    ("0.09281641", "0.09282371"), ("0.09297523", "0.09502286"),
    ("0.24511431", "0.24512577"), ("0.3167", "0.3179"),
    ("1.1995", "1.1996"),
    ("line_pre_w303", "line_pre_w304"),
    ("行 292 注册在册", "行 293 注册在册"),
    ("池第 301 枚", "池第 302 枚"),
    ("线第 293 波", "线第 294 波"),
    ("第一百二十二枚", "第一百二十三枚"),
    ("第 122 枚", "第 123 枚"),
    ("第五十六次", "第五十七次"),
    ("第五十七次", "第五十八次"),
    ("CLEAN-AT-BIRTH 34th gen", "CLEAN-AT-BIRTH 35th gen"),
    ("MSG-20261024-0640-bmc-w303-seat", "MSG-20261024-0735-bmc-w304-seat"),
    ("f09ad33571", "098930328c"),
    ("78b4b1ce5c", "f8a956c17c"),
    ("r1185", "r1186"), ("r1186", "r1187"),
    ("_w303bmc_20261024", "_w304bmc_20261024"),
    ("_w302bmc_freeze_edits.py", "_w303bmc_freeze_edits.py"),
    ("_w303bmc_freeze_edits.py", "_w304bmc_freeze_edits.py"),
    ("R304", "R305"),
    ("n1_w302", "n1_w303"), ("n1_w303", "n1_w304"),
    ("--wave 303", "--wave 304"),
    ("bmc_rows=121", "bmc_rows=122"),
    ("bmc rows 121", "bmc rows 122"),
    ("live rows 121", "live rows 122"),
    ("bm-c 121 行注册", "bm-c 122 行注册"),
    ("2026-10-24 06:4x", "2026-10-24 07:3x"),
    ("06:0x", "07:0x"),
    ("06:1x", "07:1x"),
]
NUM = [(a, b) for a, b in NUM if a != b]
counts = {}
for a, b in NUM:
    counts[a] = out.count(a)
print("COUNT TABLE (key -> occurrences):")
for a, _ in sorted(NUM, key=lambda kv: -kv[0].__len__()):
    print("  %-42r %d" % (a, counts[a]))
zero = [a for a in counts if counts[a] == 0]
if MEASURE:
    print("MEASURE: zero-hit keys=%r" % (zero,))
    for s, t in stash.items():
        print("STASH", s, "len", len(t))
    sys.exit(0)
assert not zero, "zero-hit keys: %r" % zero

table = dict(NUM)
alt = "|".join(re.escape(a) for a, _ in sorted(NUM, key=lambda kv: -len(kv[0])))
out = re.sub(alt, lambda m: table[m.group(0)], out)

# ---------------------------------------------------------------- 4. bands +2200
def roll(m):
    v = int(m.group(1)) * 1000 + int(m.group(2)) + 2200
    return "%03d_%03d" % (v // 1000, v % 1000)


out, nband = re.subn(r"\b(\d{3})_(\d{3})\b", roll, out)
assert nband > 0

# ---------------------------------------------------------------- 5. restore sentinels
for sent, txt in stash.items():
    assert out.count(sent) >= 1, "sentinel %s missing" % sent
    out = out.replace(sent, txt)

# ---------------------------------------------------------------- 6. post-fixes
POST = [
    ("nvidia-smi 实读 15.2G VRAM 占用", "nvidia-smi 实读 10.4G VRAM 占用"),
    ("本窗 free RAM 1.8GB", "本窗 free RAM 1.6GB"),
]
for old, new in POST:
    n = out.count(old)
    if n:
        out = out.replace(old, new)
    print("post-fix %r -> %d hit(s)" % (old[:40], n))

# ---------------------------------------------------------------- 7. asserts
assert out.count("\n") == 63, "line count changed: %d" % out.count("\n")
assert out.count("681_") == 0, "old band block leaked"
for band in ("684_101..686_100", "686_101..686_300"):
    assert out.count(band) >= 2, "target band missing: %s" % band
assert out.count("W304") > 30 and out.count("W305") > 5
assert out.count("W300") == src.count("W300"), "W300 (cumulative) must not roll"
assert out.count("1,090,941") == src.count("1,088,741")
assert out.count("664,520") == src.count("662,320"), "662,320 roll mismatch"
assert out.count("666,720") == 1
assert out.count("line_pre_w304") == 1
assert out.count("ZZ") == 0, "sentinel leaked"
assert out.count("n1_w303") >= 4 and "n1_w304" in out
assert out.count("1.1996") >= 2

open("results/_w304bmc_derive_counts.json", "w", encoding="utf-8").write(
    json.dumps({"keys": counts, "band_tokens": nband,
                "bytes_src": len(raw), "bytes_out": len(out.encode("utf-8"))},
               ensure_ascii=False, indent=1))
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(out)
b = out.encode("utf-8")
print("WROTE %s bytes=%d lines=%d sha16=%s bands=%d keys=%d" % (
    OUT, len(b), out.count("\n"), hashlib.sha256(b).hexdigest()[:16], nband, len(NUM)))