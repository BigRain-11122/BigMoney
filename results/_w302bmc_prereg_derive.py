# -*- coding: utf-8 -*-
"""W302 prereg derive (bm-c r1185).

Canon-clone of the frozen W301 pre-run face (git 1d821e224c:research/PERPETUAL_N1_W301_PREREG.md,
25,253B / 63 lines, sha256-16 67660cf60627132e) -> research/PERPETUAL_N1_W302_PREREG.md.

Cumulative-history faces (A/B 1-hop chain, se_mu narrowing chain, own-turn rotation list,
RAM freeze chain, estate chain, seat/timeline clauses) are parked behind pure-letter sentinels
(carried verbatim and EXTENDED by one entry, never rolled) -- r1180/r1182/r1184 pit family.
Everything else rides ONE single-pass map: wave labels W>=300 +1, bands +2200, ordinals +1.
"""
import hashlib
import json
import re
import subprocess

SRC_REV = "1d821e224c"
SRC_PATH = "research/PERPETUAL_N1_W301_PREREG.md"
OUT = "research/PERPETUAL_N1_W302_PREREG.md"
EXPECT_SHA16 = "67660cf60627132e"
EXPECT_BYTES = 25253

raw = subprocess.run(["git", "show", "%s:%s" % (SRC_REV, SRC_PATH)],
                     capture_output=True, check=True).stdout
assert len(raw) == EXPECT_BYTES, "src bytes %d != %d" % (len(raw), EXPECT_BYTES)
assert hashlib.sha256(raw).hexdigest()[:16] == EXPECT_SHA16, "src sha16 mismatch"
src = raw.decode("utf-8")
assert src.count("\n") == 63

# ---------------------------------------------------------------- facts (machine-read)
res = json.load(open("results/perpetual_faces/n1_w301_results.json", encoding="utf-8"))
led = res["science_gates"]["ledger"]
assert led["total"] == 1086541 and led["prev_total"] == 1084341
cum = res["null_pool_cumulative"]
assert cum["merged"]["n_values"] == 660120
seed = json.load(open("results/_w302bmc_20261024_probe_receipt.json", encoding="utf-8"))
assert seed["verdict"] == "ADMIT"
l1 = seed["legs"]["leg1"]
assert l1["A"] == [679701, 681700] and l1["B"] == [681701, 681900]
assert l1["hops_A"] == 1 and l1["hops_B"] == 1
assert seed["legs"]["leg0"]["owner_rows"] == 291
assert seed["legs"]["leg0"]["bmc_rows"] == 120

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


def swap(old, new, label):
    global out
    n = out.count(old)
    assert n >= 1, "zero-hit: %s" % label
    out = out.replace(old, new)
    return n


def park_span(head, tail, sent, build):
    global out
    assert out.count(head) == 1, "head not unique: %r" % head[:40]
    i = out.find(head)
    j = out.find(tail, i)
    assert j >= 0, "zero-hit tail: %r" % tail[:30]
    j += len(tail)
    stash[sent] = build(out[i:j])
    out = out[:i] + sent + out[j:]


# --- parked explicit rewrites (their W/r numerals must not ride the blanket map)
TL1_OLD = "splice 执行窗派生落地（r1183/r1183/r1183 W300 全周期先例实时间线："
TL1_NEW = "splice 执行窗派生落地（r1184/r1184/r1184 W301 全周期先例实时间线："
TL2_OLD = ("prereg 5973d8625a 落于 r1183 窗·splice 921ff28882 落于 r1183 执行窗 04:4x——"
           "**W301 freeze 面：W300 own-wave finalize 已落地=席位时即解锁——席位 r1184 窗+"
           "prereg r1184 窗落地")
TL2_NEW = ("prereg 1d821e224c 落于 r1184 窗·splice 59f0515c12 落于 r1184 执行窗 05:1x——"
           "**W302 freeze 面：W301 own-wave finalize 已落地=席位时即解锁——席位 r1185 窗+"
           "prereg r1185 窗落地")
EST_OLD = "estate chain r1183/r1183/r1183 W300 全周期 921ff28882+c9ee1346b1+dad95fe359"
EST_NEW = "estate chain r1184/r1184/r1184 W301 全周期 1d821e224c+59f0515c12+3bf8978aed"
SEAT_OLD = ("席面 own-seat face（bm-c r1183 席位 MSG-20261024-0455-bmc-w301-seat 已推 origin "
            "57d4e8526d·probe receipt _w301bmc_20261024 机证·bands ADMIT verbatim·"
            "queue-head seat-first lane）")
SEAT_NEW = ("席面 own-seat face（bm-c r1185 席位 MSG-20261024-0550-bmc-w302-seat 已推 origin "
            "6a5e62e6bb·probe receipt _w302bmc_20261024 机证·bands ADMIT verbatim·"
            "queue-head seat-first lane）")

for sent, old, new in ((S_TL, TL1_OLD, TL1_NEW), (S_TL2, TL2_OLD, TL2_NEW),
                       (S_EST, EST_OLD, EST_NEW), (S_SEAT, SEAT_OLD, SEAT_NEW)):
    n = out.count(old)
    assert n >= 1, "zero-hit swap: %r" % old[:50]
    stash[sent] = new
    out = out.replace(old, sent)

# --- parked cumulative-history spans (extended by one row, never rolled)
park_span("W252/W253/W254/W255/W256/W257/W259/W260/W261", "第四十八波", S_AB,
          lambda s: s.replace("W301=A/B", "W301/W302=A/B").replace("第四十八波", "第四十九波"))
park_span("→W299 **0.000303**→W300 **0.000302**→W301 投影 0.000302", "0.000302", S_SE,
          lambda s: s.replace("W301 投影 0.000302", "W301 **0.000302**→W302 投影 0.000302"))
park_span("W288 bm-c→W293 bm-c", "own-turn rotation", S_ROT,
          lambda s: s.replace("W301 bm-c own-turn rotation", "W301 bm-c→W302 bm-c own-turn rotation"))
park_span("W300 冻结窗 ~2.6G bm-c 实锚·本窗冻结窗 ~6.8G bm-c 实锚", "本窗冻结窗 ~6.8G bm-c 实锚", S_RAM,
          lambda s: s.replace("W300 冻结窗 ~2.6G bm-c 实锚·本窗冻结窗 ~6.8G bm-c 实锚",
                              "W300 冻结窗 ~2.6G bm-c 实锚·W301 冻结窗 ~6.8G bm-c 实锚·"
                              "本窗冻结窗 ~3.3G bm-c 实锚"))

# ---------------------------------------------------------------- 2. wave labels +1 (W>=300)
out = re.sub(r"W(\d{3})", lambda m: "W%03d" % (int(m.group(1)) + 1)
             if int(m.group(1)) >= 300 else m.group(0), out)

# ---------------------------------------------------------------- 3. numeric / ordinal / artifact maps
NUM = [
    ("1,084,341", "1,086,541"), ("1,082,141", "1,084,341"),
    ("657,920", "660,120"), ("660,120", "662,320"),
    ("0.09279368", "0.09281588"), ("0.09501695", "0.09945341"),
    ("0.24512089", "0.24511675"), ("0.3113", "0.3105"),
    ("实差 0.0022", "实差 0.0066"), ("**+0.0000**", "**−0.0001**"),
    ("line_pre_w301", "line_pre_w302"),
    ("第 291 波", "第 292 波"), ("波号 301", "波号 302"), ("第 299 枚", "第 300 枚"), ("第 120 枚", "第 121 枚"),
    ("行 290", "行 291"), ("bmc_rows=119", "bmc_rows=120"),
    ("bmc rows 119", "bmc rows 120"), ("live rows 119", "live rows 120"),
    ("bm-c 119 行注册", "bm-c 120 行注册"),
    ("第五十四次", "第五十五次"), ("第五十五次", "第五十六次"),
    ("第一百二十枚", "第一百二十一枚"),
    ("共二百九十九面", "共三百面"),
    ("CLEAN-AT-BIRTH 32nd gen", "CLEAN-AT-BIRTH 33rd gen"),
    ("MSG-20261024-0455-bmc-w301-seat", "MSG-20261024-0550-bmc-w302-seat"),
    ("57d4e8526d", "6a5e62e6bb"),
    ("921ff28882", "59f0515c12"),
    ("r1183", "r1184"), ("r1184", "r1185"),
    ("_w301bmc_20261024", "_w302bmc_20261024"),
    ("_w301bmc_freeze_edits.py", "_w302bmc_freeze_edits.py"),
    ("_w300bmc_freeze_edits.py", "_w301bmc_freeze_edits.py"),
    ("R302", "R303"),
    ("n1_w300", "n1_w301"), ("n1_w301", "n1_w302"),
    ("--wave 301", "--wave 302"),
    ("2026-10-24 05:1x", "2026-10-24 05:5x"),
    ("04:4x", "05:1x"), ("04:3x", "05:3x"),
    ("0.0066 在带内", "0.0066 在带内"),
]
NUM = [(a, b) for a, b in NUM if a != b]
counts = {}
for a, b in NUM:
    counts[a] = out.count(a)
    assert counts[a] > 0, "zero-hit key: %r" % a
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
    # vacancy face: replaced by a machine-checkable statement (no magic line number)
    ("origin perpetual_faces.py 零 297 行", "origin perpetual_faces.py 零 W302 行"),
    ("r1184 席位窗实跑", "r1185 席位窗实跑"),
    ("（r1184 窗算法", "（r1185 窗算法"),
    # VRAM face: nvidia-smi freeze-window read
    ("nvidia-smi 实读 1.9G VRAM 占用", "nvidia-smi 实读 14.3G VRAM 占用"),
    ("本窗 free RAM 6.8GB", "本窗 free RAM 3.3GB"),
]
for old, new in POST:
    n = out.count(old)
    assert n >= 1, "post-fix zero-hit: %r" % old
    out = out.replace(old, new)

# ---------------------------------------------------------------- 7. asserts
assert out.count("\n") == 63, "line count changed: %d" % out.count("\n")
assert out.count("677_") == 0, "old band block leaked"
for band in ("679_701..681_700", "681_701..681_900"):
    assert out.count(band) >= 2, "target band missing: %s" % band
assert out.count("W302") > 30 and out.count("W303") > 5
assert out.count("W299") == src.count("W299"), "W299 (cumulative) must not roll"
assert out.count("1,086,541") == src.count("1,084,341")
assert out.count("660,120") == src.count("657,920"), "657,920 roll mismatch"
assert out.count("662,320") == 1
assert out.count("line_pre_w302") == 1
assert out.count("ZZ") == 0, "sentinel leaked"
assert out.count("n1_w301") >= 4 and "n1_w302" in out

open("results/_w302bmc_derive_counts.json", "w", encoding="utf-8").write(
    json.dumps({"keys": counts, "band_tokens": nband, "bytes_src": len(raw),
                "bytes_out": len(out.encode("utf-8"))}, ensure_ascii=False, indent=1))
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(out)
b = out.encode("utf-8")
print("WROTE %s bytes=%d lines=%d sha16=%s bands=%d keys=%d" % (
    OUT, len(b), out.count("\n"), hashlib.sha256(b).hexdigest()[:16], nband, len(NUM)))