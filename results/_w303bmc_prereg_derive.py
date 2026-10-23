# -*- coding: utf-8 -*-
"""W303 prereg derive (bm-c r1186).

Canon-clone of the frozen W302 pre-run face (git 184e056533:research/PERPETUAL_N1_W302_PREREG.md,
25,302B / 63 lines, sha256-16 a282049a16b3f511) -> research/PERPETUAL_N1_W303_PREREG.md.

Cumulative-history faces (A/B 1-hop chain, se_mu narrowing chain, own-turn rotation list,
RAM freeze chain, estate chain, seat/timeline clauses) are parked behind pure-letter sentinels
(carried verbatim and EXTENDED by one entry, never rolled) -- r1180/r1182/r1184 pit family.
Everything else rides ONE single-pass map: wave labels W>=300 +1, bands +2200, ordinals +1,
plus a printed literal-count table before any replacement is written (r1171 law).

Usage: python results/_w303bmc_prereg_derive.py [--measure]
"""
import hashlib
import json
import re
import subprocess
import sys

SRC_REV = "184e056533"
SRC_PATH = "research/PERPETUAL_N1_W302_PREREG.md"
OUT = "research/PERPETUAL_N1_W303_PREREG.md"
EXPECT_SHA16 = "a282049a16b3f511"
EXPECT_BYTES = 25302
MEASURE = "--measure" in sys.argv

raw = subprocess.run(["git", "show", "%s:%s" % (SRC_REV, SRC_PATH)],
                     capture_output=True, check=True).stdout
assert len(raw) == EXPECT_BYTES, "src bytes %d != %d" % (len(raw), EXPECT_BYTES)
assert hashlib.sha256(raw).hexdigest()[:16] == EXPECT_SHA16, "src sha16 mismatch"
src = raw.decode("utf-8")
assert src.count("\n") == 63

# ---------------------------------------------------------------- facts (machine-read)
res = json.load(open("results/perpetual_faces/n1_w302_results.json", encoding="utf-8"))
led = res["science_gates"]["ledger"]
assert led["total"] == 1088741 and led["prev_total"] == 1086541, "ledger anchor drift"
cum = res["null_pool_cumulative"]
assert cum["merged"]["n_values"] == 662320, "merged K drift"
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_662320"] == 1.1995 and kl["line_pre_w302"] == 1.1995
seed = json.load(open("results/_w303bmc_20261024_probe_receipt.json", encoding="utf-8"))
assert seed["verdict"] == "ADMIT"
l1 = seed["legs"]["leg1"]
assert l1["A"] == [681901, 683900] and l1["B"] == [683901, 684100]
assert l1["hops_A"] == 1 and l1["hops_B"] == 1
assert seed["legs"]["leg0"]["owner_rows"] == 292
assert seed["legs"]["leg0"]["bmc_rows"] == 121

# ---------------------------------------------------------------- 1. park cumulative history
S_AB = "ZZCUMAB"
S_SE = "ZZCUMSE"
S_ROT = "ZZCUMROT"
S_RAM = "ZZCUMRAM"
S_EST = "ZZCUMEST"
S_SEAT = "ZZSEAT"
S_TL = "ZZTIMELINE"
S_TL2 = "ZZTLBODY"

out = src
stash = {}


def swap(old, new, sent, label):
    global out
    n = out.count(old)
    assert n >= 1, "zero-hit: %s" % label
    stash[sent] = new
    out = out.replace(old, sent)
    return n


# --- parked explicit rewrites (their W/r numerals must not ride the blanket map)
TL1_OLD = "splice 执行窗派生落地（r1184/r1184/r1184 W301 全周期先例实时间线："
TL1_NEW = "splice 执行窗派生落地（r1185/r1185/r1185 W302 全周期先例实时间线："
TL2_OLD = ("prereg 1d821e224c 落于 r1184 窗·splice 59f0515c12 落于 r1184 执行窗 05:1x——"
           "**W302 freeze 面：W301 own-wave finalize 已落地=席位时即解锁——席位 r1185 窗+"
           "prereg r1185 窗落地")
TL2_NEW = ("prereg 184e056533 落于 r1185 窗·splice 78b4b1ce5c 落于 r1185 执行窗 06:1x——"
           "**W303 freeze 面：W302 own-wave finalize 已落地=席位时即解锁——席位 r1186 窗+"
           "prereg r1186 窗落地")
AB_OLD = "W299/W300/W301/W302=A/B 双 1-hop 形态第四十九波"
AB_NEW = "W299/W300/W301/W302/W303=A/B 双 1-hop 形态第五十波"
SE_OLD = "W300 **0.000302**→W302 投影 0.000302"
SE_NEW = "W300 **0.000302**→W302 **0.000301**→W303 投影 0.000301"
ROT_OLD = ("W288 bm-c→W293 bm-c→W294 bm-c→W295 bm-c→W296 bm-c→W297 bm-c→W298 bm-c→"
           "W299 bm-c→W300 bm-c→W301 bm-c→W302 bm-c own-turn rotation")
ROT_NEW = ("W288 bm-c→W293 bm-c→W294 bm-c→W295 bm-c→W296 bm-c→W297 bm-c→W298 bm-c→"
           "W299 bm-c→W300 bm-c→W301 bm-c→W302 bm-c→W303 bm-c own-turn rotation")
RAM_OLD = "W300 冻结窗 ~2.6G bm-c 实锚·W301 冻结窗 ~6.8G bm-c 实锚·本窗冻结窗 ~3.3G bm-c 实锚"
RAM_NEW = ("W300 冻结窗 ~2.6G bm-c 实锚·W301 冻结窗 ~6.8G bm-c 实锚·"
           "W302 冻结窗 ~3.3G bm-c 实锚·本窗冻结窗 ~1.8G bm-c 实锚")
EST_OLD = "estate chain r1184/r1184/r1184 W301 全周期 1d821e224c+59f0515c12+3bf8978aed"
EST_NEW = "estate chain r1185/r1185/r1185 W302 全周期 184e056533+78b4b1ce5c+070ba903cf"
SEAT_OLD = ("席面 own-seat face（bm-c r1185 席位 MSG-20261024-0550-bmc-w302-seat 已推 origin "
            "6a5e62e6bb·probe receipt _w302bmc_20261024 机证·bands ADMIT verbatim·"
            "queue-head seat-first lane）")
SEAT_NEW = ("席面 own-seat face（bm-c r1186 席位 MSG-20261024-0640-bmc-w303-seat 已推 origin "
            "f09ad33571·probe receipt _w303bmc_20261024 机证·bands ADMIT verbatim·"
            "queue-head seat-first lane）")

parked_hits = {}
for sent, old, new, label in (
        (S_TL, TL1_OLD, TL1_NEW, "timeline-1"), (S_TL2, TL2_OLD, TL2_NEW, "timeline-2"),
        (S_AB, AB_OLD, AB_NEW, "AB-chain"), (S_SE, SE_OLD, SE_NEW, "se_mu-chain"),
        (S_ROT, ROT_OLD, ROT_NEW, "rotation-chain"), (S_RAM, RAM_OLD, RAM_NEW, "RAM-chain"),
        (S_EST, EST_OLD, EST_NEW, "estate-chain"), (S_SEAT, SEAT_OLD, SEAT_NEW, "seat-face")):
    parked_hits[label] = swap(old, new, sent, label)

# ---------------------------------------------------------------- 2. wave labels +1 (W>=300)
out = re.sub(r"W(\d{3})", lambda m: "W%03d" % (int(m.group(1)) + 1)
             if int(m.group(1)) >= 300 else m.group(0), out)

# ---------------------------------------------------------------- 3. numeric / ordinal / artifact maps
NUM = [
    ("1,086,541", "1,088,741"), ("1,084,341", "1,086,541"),
    ("662,320", "664,520"), ("660,120", "662,320"),
    ("0.09281588", "0.09281641"), ("0.09945341", "0.09297523"),
    ("0.24511675", "0.24511431"), ("0.3105", "0.3167"),
    ("实差 0.0066", "实差 0.0065"), ("**−0.0001**", "**+0.0000**"),
    ("1.1994", "1.1995"),
    ("line_pre_w302", "line_pre_w303"),
    ("第 292 波", "第 293 波"), ("波号 302", "波号 303"),
    ("第 300 枚", "第 301 枚"), ("第 121 枚", "第 122 枚"),
    ("第一百二十一枚", "第一百二十二枚"),
    ("行 291", "行 292"), ("bmc_rows=120", "bmc_rows=121"),
    ("bmc rows 120", "bmc rows 121"), ("live rows 120", "live rows 121"),
    ("bm-c 120 行注册", "bm-c 121 行注册"),
    ("第五十五次", "第五十六次"), ("第五十六次", "第五十七次"),
    ("共三百面", "共三百零一面"),
    ("CLEAN-AT-BIRTH 33rd gen", "CLEAN-AT-BIRTH 34th gen"),
    ("MSG-20261024-0550-bmc-w302-seat", "MSG-20261024-0640-bmc-w303-seat"),
    ("6a5e62e6bb", "f09ad33571"),
    ("59f0515c12", "78b4b1ce5c"),
    ("r1184", "r1185"), ("r1185", "r1186"),
    ("_w302bmc_20261024", "_w303bmc_20261024"),
    ("_w301bmc_freeze_edits.py", "_w302bmc_freeze_edits.py"),
    ("_w302bmc_freeze_edits.py", "_w303bmc_freeze_edits.py"),
    ("R303", "R304"),
    ("n1_w301", "n1_w302"), ("n1_w302", "n1_w303"),
    ("--wave 302", "--wave 303"),
    ("2026-10-24 05:5x", "2026-10-24 06:4x"),
    ("05:1x", "05:5x"), ("05:3x", "06:0x"), ("05:5x", "06:4x"),
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
    print("MEASURE: zero-hit keys=%r  parked=%r" % (zero, parked_hits))
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
    ("nvidia-smi 实读 14.3G VRAM 占用", "nvidia-smi 实读 15.2G VRAM 占用"),
    ("本窗 free RAM 3.3GB", "本窗 free RAM 1.8GB"),
]
for old, new in POST:
    n = out.count(old)
    if n:
        out = out.replace(old, new)
    print("post-fix %r -> %d hit(s)" % (old[:40], n))

# ---------------------------------------------------------------- 7. asserts
assert out.count("\n") == 63, "line count changed: %d" % out.count("\n")
assert out.count("679_") == 0, "old band block leaked"
for band in ("681_901..683_900", "683_901..684_100"):
    assert out.count(band) >= 2, "target band missing: %s" % band
assert out.count("W303") > 30 and out.count("W304") > 5
assert out.count("W300") == src.count("W300"), "W300 (cumulative) must not roll"
assert out.count("1,088,741") == src.count("1,086,541")
assert out.count("662,320") == src.count("660,120"), "660,120 roll mismatch"
assert out.count("664,520") == 1
assert out.count("line_pre_w303") == 1
assert out.count("ZZ") == 0, "sentinel leaked"
assert out.count("n1_w302") >= 4 and "n1_w303" in out
assert out.count("1.1995") >= 2

open("results/_w303bmc_derive_counts.json", "w", encoding="utf-8").write(
    json.dumps({"keys": counts, "parked": parked_hits, "band_tokens": nband,
                "bytes_src": len(raw), "bytes_out": len(out.encode("utf-8"))},
               ensure_ascii=False, indent=1))
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(out)
b = out.encode("utf-8")
print("WROTE %s bytes=%d lines=%d sha16=%s bands=%d keys=%d" % (
    OUT, len(b), out.count("\n"), hashlib.sha256(b).hexdigest()[:16], nband, len(NUM)))