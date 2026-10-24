# -*- coding: utf-8 -*-
"""W305 prereg derive (bm-c r1189).

Canon-clone of the frozen W304 pre-run face (git 92f5041c27:research/PERPETUAL_N1_W304_PREREG.md,
25,448B / 63 newlines, sha16 b0a64a27779a66aa) -> research/PERPETUAL_N1_W305_PREREG.md.

Cumulative-history faces (A/B 1-hop chain, se_mu narrowing chain, own-turn rotation list,
RAM freeze chain, estate chain, seat/timeline/freeze-window clauses) are parked behind
pure-letter sentinels and EXTENDED by one entry (never rolled) -- r1180/r1182/r1184 pit family.
Everything else rides ONE single-pass map: wave labels W>=301 +1, bands +2200, ordinals +1,
plus a printed literal-count table before any replacement is written (r1171 law).

Usage: python results/_w305bmc_prereg_derive.py [--measure]
"""
import hashlib
import json
import re
import subprocess
import sys

SRC_REV = "92f5041c27"
SRC_PATH = "research/PERPETUAL_N1_W304_PREREG.md"
OUT = "research/PERPETUAL_N1_W305_PREREG.md"
EXPECT_SHA16 = "b0a64a27779a66aa"
EXPECT_BYTES = 25448
MEASURE = "--measure" in sys.argv

raw = subprocess.run(["git", "show", "%s:%s" % (SRC_REV, SRC_PATH)],
                     capture_output=True, check=True).stdout
assert len(raw) == EXPECT_BYTES, "src bytes %d != %d" % (len(raw), EXPECT_BYTES)
assert hashlib.sha256(raw).hexdigest()[:16] == EXPECT_SHA16, "src sha16 mismatch"
src = raw.decode("utf-8")
assert src.count("\n") == 63

# ---------------------------------------------------------------- facts (machine-read)
res = json.load(open("results/perpetual_faces/n1_w304_results.json", encoding="utf-8"))
led = res["science_gates"]["ledger"]
assert led["total"] == 1093141 and led["prev_total"] == 1090941, "ledger anchor drift"
cum = res["null_pool_cumulative"]
assert cum["merged"]["n_values"] == 666720, "merged K drift"
assert abs(cum["merged"]["mu"] + 0.09283733231341493) < 1e-12
assert abs(cum["merged"]["sigma"] - 0.24513614234161132) < 1e-12
assert cum["se_mu_at_k666720"] == 0.0003
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_666720"] == 1.1998 and kl["line_pre_w304"] == 1.1997
seed = json.load(open("results/_w305bmc_20261024_probe_receipt.json", encoding="utf-8"))
assert seed["verdict"] == "ADMIT"
l1 = seed["legs"]["leg1"]
assert l1["A"] == [686301, 688300] and l1["B"] == [688301, 688500]
assert l1["hops_A"] == 1 and l1["hops_B"] == 1
assert seed["legs"]["leg0"]["owner_rows"] == 294
assert seed["legs"]["leg0"]["bmc_rows"] == 123

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
    o = "（r1186/r1186/r1186 W303 全周期先例实时间线："
    n = "（r1187/r1187/r1188 W304 全周期先例实时间线："
    assert o in old
    return old.replace(o, n)


def tl2(old):
    o = ("prereg 886e88787a 落于 r1186 窗·splice f8a956c17c 落于 r1186 执行窗 07:0x"
         "——**W304 freeze 面：W303 own-wave finalize 已落地=席位时即解锁——席位 r1187 窗+prereg r1187 窗落地")
    n = ("prereg 92f5041c27 落于 r1187 窗·splice c7b6ecd7ba 落于 r1187 执行窗 08:0x"
         "——**W305 freeze 面：W304 own-wave finalize 已落地=席位时即解锁——席位 r1189 窗+prereg r1189 窗落地")
    assert o in old, old
    return old.replace(o, n)


def fwin(old):
    o = "bm-c 循环班 r1187 冻结窗 2026-10-24 07:3x"
    n = "bm-c 循环班 r1189 冻结窗 2026-10-24 08:4x"
    assert o in old, old
    return old.replace(o, n)


def ab(old):
    o = "/W304=A/B 双 1-hop 形态第五十一波"
    n = "/W304/W305=A/B 双 1-hop 形态第五十二波"
    assert o in old, old
    return old.replace(o, n)


def se(old):
    o = "→W303 **0.000301**→W304 投影 0.000301"
    n = "→W303 **0.000301**→W304 **0.000300**→W305 投影 0.000300"
    assert o in old, old
    return old.replace(o, n)


def rot(old):
    o = "→W304 bm-c own-turn rotation"
    n = "→W304 bm-c→W305 bm-c own-turn rotation"
    assert o in old, old
    return old.replace(o, n)


def ram(old):
    o = "·W303 冻结窗 ~1.8G bm-c 实锚·本窗冻结窗 ~1.6G bm-c 实锚"
    n = "·W303 冻结窗 ~1.8G bm-c 实锚·W304 冻结窗 ~1.6G bm-c 实锚·本窗冻结窗 ~1.0G bm-c 实锚"
    assert o in old, old
    return old.replace(o, n)


def fin(old):
    o = "W303 finalize one-pass bm-c r1186 窗 07:0x"
    n = "W304 finalize one-pass bm-c r1188 窗 08:1x"
    assert o in old, old
    return old.replace(o, n)


def est(old):
    o = "estate chain r1186/r1186/r1186 W303 全周期 886e88787a+f8a956c17c+774ef0c53f"
    n = "estate chain r1187/r1187/r1188 W304 全周期 92f5041c27+c7b6ecd7ba+77a117af38"
    assert o in old, old
    return old.replace(o, n)


def seat(old):
    o = ("bm-c r1187 席位 MSG-20261024-0735-bmc-w304-seat 已推 origin 098930328c"
         "·probe receipt _w304bmc_20261024 机证·bands ADMIT verbatim")
    n = ("bm-c r1189 席位 MSG-20261024-0845-bmc-w305-seat 已推 origin 871f187361"
         "·probe receipt _w305bmc_20261024 机证·bands ADMIT verbatim")
    assert o in old, old
    return old.replace(o, n)


park(r"（r1186/r1186/r1186[^（\n]*?先例实时间线：", tl1, "TLWINDOW")
park(r"prereg 886e88787a[^\n]*?prereg r1187 窗落地", tl2, "TLPAIR")
park(r"bm-c 循环班 r1187 冻结窗[^\n]*?07:3x", fwin, "FREEZEWIN")
park(r"W252/W253[^\n]*?第五十一波", ab, "ABCHAIN")
park(r"se_mu 收窄链 …[^\n]*?→W304 投影 0\.000301", se, "SECH")
park(r"W288 bm-c[^\n]*?own-turn rotation", rot, "ROTCH")
park(r"W300 冻结窗[^\n]*?本窗冻结窗 ~[\d.]+G bm-c 实锚", ram, "RAMCH")
park(r"W303 finalize one-pass bm-c r1186 窗 07:0x", fin, "FINFACE", expect=2)
park(r"estate chain r1186/r1186/r1186[^\n]*?774ef0c53f", est, "ESTCH")
park(r"bm-c r1187 席位 MSG-20261024-0735-bmc-w304-seat[^\n]*?bands ADMIT verbatim",
     seat, "SEATF")

# ---------------------------------------------------------------- 2. wave labels +1 (W>=301)
out = re.sub(r"W(\d{3})", lambda m: "W%03d" % (int(m.group(1)) + 1)
             if int(m.group(1)) >= 301 else m.group(0), out)

# ---------------------------------------------------------------- 3. numeric / ordinal / artifact maps
NUM = [
    ("1,090,941", "1,093,141"), ("1,088,741", "1,090,941"),
    ("666,720", "668,920"), ("664,520", "666,720"),
    ("0.09282371", "0.09283733"), ("0.24512577", "0.24513614"),
    ("1.1996", "1.1997"),
    ("line_pre_w304", "line_pre_w305"),
    ("行 293 注册在册", "行 294 注册在册"),
    ("池第 302 枚", "池第 303 枚"),
    ("线第 294 波", "线第 295 波"),
    ("第一百二十三枚", "第一百二十四枚"),
    ("第 123 枚", "第 124 枚"),
    ("第五十七次", "第五十八次"),
    ("第五十八次", "第五十九次"),
    ("CLEAN-AT-BIRTH 35th gen", "CLEAN-AT-BIRTH 36th gen"),
    ("MSG-20261024-0735-bmc-w304-seat", "MSG-20261024-0845-bmc-w305-seat"),
    ("098930328c", "871f187361"),
    ("f8a956c17c", "c7b6ecd7ba"),
    ("r1186", "r1187"), ("r1187", "r1188"),
    ("_w305bmc_20261024", "_w305bmc_20261024"),
    ("_w304bmc_freeze_edits.py", "_w305bmc_freeze_edits.py"),
    ("_w303bmc_freeze_edits.py", "_w304bmc_freeze_edits.py"),
    ("R305", "R306"),
    ("n1_w303", "n1_w304"), ("n1_w304", "n1_w305"),
    ("--wave 304", "--wave 305"),
    ("bmc_rows=122", "bmc_rows=123"),
    ("bmc rows 122", "bmc rows 123"),
    ("live rows 122", "live rows 123"),
    ("bm-c 122 行注册", "bm-c 123 行注册"),
    ("07:0x", "08:0x"),
    ("07:1x", "08:1x"),
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
    ("nvidia-smi 实读 10.4G VRAM 占用", "nvidia-smi 实读 12.9G VRAM 占用"),
    ("本窗 free RAM 1.6GB", "本窗 free RAM 1.0GB"),
    ("GPU=gen-only 车道 idle（", "GPU=gen-only 车道 busy（外部 MV i2v 车道在烧·util 100% 实读·非本波占用；"),
    ("**1.1997**·line_pre_w305", "**1.1998**·line_pre_w305"),
]
for old, new in POST:
    n = out.count(old)
    if n:
        out = out.replace(old, new)
    print("post-fix %r -> %d hit(s)" % (old[:40], n))

# ---------------------------------------------------------------- 7. asserts
assert out.count("\n") == 63, "line count changed: %d" % out.count("\n")
assert out.count("684_") == 0, "old band block leaked"
for band in ("686_301..688_300", "688_301..688_500"):
    assert out.count(band) >= 2, "target band missing: %s" % band
assert out.count("W305") > 30 and out.count("W306") > 5
assert out.count("W300") == src.count("W300"), "W300 (cumulative) must not roll"
assert out.count("W301") == src.count("W301"), "W301 (cumulative chain) must not roll"
assert out.count("1,093,141") == src.count("1,090,941")
assert out.count("666,720") == src.count("664,520"), "664,520 roll mismatch"
assert out.count("668,920") == 1
assert out.count("line_pre_w305") == 1
assert out.count("ZZ") == 0, "sentinel leaked"
assert out.count("n1_w304") >= 4 and "n1_w305" in out
assert out.count("1.1998") >= 1 and out.count("1.1997") >= 1

open("results/_w305bmc_derive_counts.json", "w", encoding="utf-8").write(
    json.dumps({"keys": counts, "band_tokens": nband,
                "bytes_src": len(raw), "bytes_out": len(out.encode("utf-8"))},
               ensure_ascii=False, indent=1))
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(out)
b = out.encode("utf-8")
print("WROTE %s bytes=%d lines=%d sha16=%s bands=%d keys=%d" % (
    OUT, len(b), out.count("\n"), hashlib.sha256(b).hexdigest()[:16], nband, len(NUM)))