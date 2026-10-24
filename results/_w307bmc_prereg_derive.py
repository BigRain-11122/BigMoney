# -*- coding: utf-8 -*-
"""W307 prereg derive (bm-c r1192).

Canon-clone of the frozen W306 pre-run face
(git 7ab2b459e2:research/PERPETUAL_N1_W306_PREREG.md, 25,643B / 63 newlines,
sha16 df988a1e28b48d75) -> research/PERPETUAL_N1_W307_PREREG.md.

Cumulative-history faces (A/B 1-hop chain, se_mu narrowing chain, own-turn
rotation list, RAM freeze chain, estate chain, timeline/seat/freeze-window
clauses) are parked behind pure-letter sentinels and EXTENDED by one entry
(never rolled) -- r1180/r1182/r1184 pit family.
Everything else rides ONE single-pass map: wave labels W>=301 +1, bands +2200,
ordinals +1, round labels +2, plus a printed literal-count table before any
replacement is written (r1171 law).

Usage: python results/_w307bmc_prereg_derive.py [--measure]
"""
import hashlib
import json
import re
import subprocess
import sys

SRC_REV = "7ab2b459e2"
SRC_PATH = "research/PERPETUAL_N1_W306_PREREG.md"
OUT = "research/PERPETUAL_N1_W307_PREREG.md"
EXPECT_SHA16 = "df988a1e28b48d75"
EXPECT_BYTES = 25643
SEAT_SHA = "d78f799608"
MEASURE = "--measure" in sys.argv

raw = subprocess.run(["git", "show", "%s:%s" % (SRC_REV, SRC_PATH)],
                     capture_output=True, check=True).stdout
assert len(raw) == EXPECT_BYTES, "src bytes %d != %d" % (len(raw), EXPECT_BYTES)
assert hashlib.sha256(raw).hexdigest()[:16] == EXPECT_SHA16, "src sha16 mismatch"
src = raw.decode("utf-8")
assert src.count("\n") == 63

# ---------------------------------------------------------------- facts (machine-read)
res = json.load(open("results/perpetual_faces/n1_w306_results.json", encoding="utf-8"))
led = res["science_gates"]["ledger"]
assert led["total"] == 1097541 and led["prev_total"] == 1095341, "ledger anchor drift"
cum = res["null_pool_cumulative"]
assert cum["merged"]["n_values"] == 671120, "merged K drift"
assert abs(cum["merged"]["mu"] + 0.09284763902133747) < 1e-12
assert abs(cum["merged"]["sigma"] - 0.2451266254234313) < 1e-12
assert cum["se_mu_at_k671120"] == 0.000299
assert abs(cum["w306_only"]["mu"] + 0.08964145454545454) < 1e-12
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_671120"] == 1.1999 and kl["n_eff_held_equal"] == 1095341
assert abs(res["families"]["A_random_engine_exit"]["full_sharpe_p95"] - 0.309) < 1e-12
seed = json.load(open("results/_w307bmc_20261024_probe_receipt.json", encoding="utf-8"))
assert seed["verdict"] == "ADMIT"
l1 = seed["legs"]["leg1"]
assert l1["A"] == [690701, 692700] and l1["B"] == [692701, 692900]
assert l1["hops_A"] == 1 and l1["hops_B"] == 1
assert seed["legs"]["leg0"]["owner_rows"] == 296
assert seed["legs"]["leg0"]["bmc_rows"] == 125

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
    print("PARK %-10s hits=%d old=%r" % (label, len(ms), olds[0][:110]))
    print("     %-10s new=%r" % ("", news[0][:110]))
    return olds, news


def tl1(old):
    o = "（r1189/r1189/r1190 W305 全周期先例实时间线："
    n = "（r1191/r1191/r1191 W306 全周期先例实时间线："
    assert o in old
    return old.replace(o, n)


def tl2(old):
    o = ("prereg 5f2c19de83 落于 r1189 窗·splice 318e263ee0 落于 r1189 执行窗 09:0x"
         "——**W306 freeze 面：W305 own-wave finalize 已落地=席位时即解锁——席位 r1191 窗+prereg r1191 窗落地")
    n = ("prereg 7ab2b459e2 落于 r1191 窗·splice aa8e2a8f1f 落于 r1191 执行窗 09:5x"
         "——**W307 freeze 面：W306 own-wave finalize 已落地=席位时即解锁——席位 r1192 窗+prereg r1192 窗落地")
    assert o in old, old
    return old.replace(o, n)


def fwin(old):
    o = "bm-c 循环班 r1191 冻结窗 2026-10-24 09:5x"
    n = "bm-c 循环班 r1192 冻结窗 2026-10-24 10:5x"
    assert o in old, old
    return old.replace(o, n)


def ab(old):
    o = "/W305/W306=A/B 双 1-hop 形态第五十三波"
    n = "/W306/W307=A/B 双 1-hop 形态第五十四波"
    assert o in old, old
    return old.replace(o, n)


def se(old):
    o = "→W305 **0.000300**→W306 投影 0.000300"
    n = "→W305 **0.000300**→W306 **0.000299**→W307 投影 0.000299"
    assert o in old, old
    return old.replace(o, n)


def rot(old):
    o = "→W305 bm-c→W306 bm-c own-turn rotation"
    n = "→W305 bm-c→W306 bm-c→W307 bm-c own-turn rotation"
    assert o in old, old
    return old.replace(o, n)


def ram(old):
    o = "·W305 冻结窗 ~1.0G bm-c 实锚·本窗冻结窗 ~0.1G bm-c 实锚"
    n = "·W305 冻结窗 ~1.0G bm-c 实锚·W306 冻结窗 ~0.1G bm-c 实锚·本窗冻结窗 ~1.3G bm-c 实锚"
    assert o in old, old
    return old.replace(o, n)


def fin(old):
    o = "W305 finalize one-pass bm-c r1190 窗 09:3x"
    n = "W306 finalize one-pass bm-c r1191 窗 10:3x"
    assert o in old, old
    return old.replace(o, n)


def est(old):
    o = "estate chain r1189/r1189/r1190 W305 全周期 5f2c19de83+318e263ee0+426c570e01"
    n = "estate chain r1191/r1191/r1191 W306 全周期 7ab2b459e2+aa8e2a8f1f+fd6b75028e"
    assert o in old, old
    return old.replace(o, n)


def seat(old):
    o = ("bm-c r1191 席位 MSG-20261024-0950-bmc-w306-seat 已推 origin 9da7091894"
         "·probe receipt _w306bmc_20261024 机证·bands ADMIT verbatim")
    n = ("bm-c r1192 席位 MSG-20261024-1047-bmc-w307-seat 已推 origin %s"
         "·probe receipt _w307bmc_20261024 机证·bands ADMIT verbatim" % SEAT_SHA)
    assert o in old, old
    return old.replace(o, n)


park(r"（r1189/r1189/r1190[^（\n]*?先例实时间线：", tl1, "TLWINDOW")
park(r"prereg 5f2c19de83[^\n]*?prereg r1191 窗落地", tl2, "TLPAIR")
park(r"bm-c 循环班 r1191 冻结窗[^\n]*?09:5x", fwin, "FREEZEWIN")
park(r"W252/W253[^\n]*?第五十三波", ab, "ABCHAIN")
park(r"se_mu 收窄链 …[^\n]*?→W306 投影 0\.000300", se, "SECH")
park(r"W288 bm-c[^\n]*?own-turn rotation", rot, "ROTCH")
park(r"W300 冻结窗[^\n]*?本窗冻结窗 ~[\d.]+G bm-c 实锚", ram, "RAMCH")
park(r"W305 finalize one-pass bm-c r1190 窗 09:3x", fin, "FINFACE", expect=2)
park(r"estate chain r1189/r1189/r1190[^\n]*?426c570e01", est, "ESTCH")
park(r"bm-c r1191 席位 MSG-20261024-0950-bmc-w306-seat[^\n]*?bands ADMIT verbatim",
     seat, "SEATF")

# ---------------------------------------------------------------- 2. wave labels +1 (W>=301)
out = re.sub(r"W(\d{3})", lambda m: "W%03d" % (int(m.group(1)) + 1)
             if int(m.group(1)) >= 301 else m.group(0), out)

# ---------------------------------------------------------------- 3. numeric / ordinal / artifact maps
NUM = [
    ("1,095,341", "1,097,541"), ("1,093,141", "1,095,341"),
    ("668,920", "671,120"), ("671,120", "673,320"),
    ("−0.09285818", "−0.09284764"), ("−0.09917732", "−0.08964145"),
    ("0.24513696", "0.24512663"),
    ("0.3009", "0.3090"),
    ("0.0063", "0.0032"),
    ("line_pre_w306", "line_pre_w307"),
    ("行 295 注册在册", "行 296 注册在册"),
    ("池第 304 枚", "池第 305 枚"),
    ("第 125 枚", "第 126 枚"),
    ("第五十九次", "第六十次"),
    ("第六十次", "第六十一次"),
    ("第 296 波", "第 297 波"),
    ("CLEAN-AT-BIRTH 37th gen", "CLEAN-AT-BIRTH 38th gen"),
    ("MSG-20261024-0950-bmc-w306-seat", "MSG-20261024-1047-bmc-w307-seat"),
    ("9da7091894", SEAT_SHA),
    ("318e263ee0", "aa8e2a8f1f"),
    ("_w306bmc_20261024", "_w307bmc_20261024"),
    ("_w306bmc_freeze_edits.py", "_w307bmc_freeze_edits.py"),
    ("_w305bmc_freeze_edits.py", "_w306bmc_freeze_edits.py"),
    ("--wave 306", "--wave 307"),
    ("n1_w305", "n1_w306"), ("n1_w306", "n1_w307"),
    ("bmc_rows=124", "bmc_rows=125"),
    ("bmc live rows 124", "bmc live rows 125"),
    ("bmc rows 124", "bmc rows 125"),
    ("R307", "R308"),
    ("09:0x", "10:3x"), ("09:1x", "09:5x"),
    ("r1189", "r1191"), ("r1190", "r1191"),
]

counts = {}
for a, b in NUM:
    counts[a] = out.count(a)
print("COUNT TABLE (key -> occurrences):")
for a, _ in sorted(NUM, key=lambda kv: -len(kv[0])):
    print("  %-42r %d" % (a, counts[a]))
zero = [a for a in counts if counts[a] == 0]
assert not zero, "zero-hit keys: %r" % zero
if MEASURE:
    print("MEASURE ok, zero=%r" % (zero,))
    for s, t in stash.items():
        print("STASH", s, "len", len(t))
    sys.exit(0)

table = dict(NUM)
alt = "|".join(re.escape(a) for a, _ in sorted(NUM, key=lambda kv: -len(kv[0])))
out = re.sub(alt, lambda m: table[m.group(0)], out)

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
    ("本窗 free RAM 0.1GB", "本窗 free RAM 1.3GB"),
    ("GPU=gen-only 车道 idle（外部 MV i2v 车道已停·util 2% 实读·非本波占用；"
     "nvidia-smi 实读 10.4G VRAM 占用·GPU 零在烧工件〔ComfyUI 双 python 常驻显存·util 2% 实读·非本波占用·",
     "GPU=gen-only 车道 busy（外部 MV i2v 车道在烧·util 100% 实读·非本波占用；"
     "nvidia-smi 实读 15.6G VRAM 占用·GPU 在烧件属外部 MV 车道〔util 100% 实读·非本波占用·"),
    # round labels: references to THIS window's own operations advance to r1192
    # (the +2 map above only rewrote the W305/W306-era ones)
    ("波号 304=注册表 W308 席后首个自由号", "波号 305=注册表 W308 席后首个自由号"),
    ("live-read r1191：burns_active", "live-read r1192：burns_active"),
    ("（r1191 席位窗实跑：origin inbox 零 W307", "（r1192 席位窗实跑：origin inbox 零 W307"),
    ("attempt-continuity face（r1191 窗算法", "attempt-continuity face（r1192 窗算法"),
    ("heartbeat 新鲜 r1191 窗实读·队列空转", "heartbeat 新鲜 r1192 窗实读·队列空转"),
    ("r565 律（bm-c r1191 席·queue-head", "r565 律（bm-c r1192 席·queue-head"),
]
for old, new in POST:
    n = out.count(old)
    assert n == 1, "post-fix %r hits=%d" % (old[:40], n)
    out = out.replace(old, new)
    print("post-fix %r ok" % old[:40])

# ---------------------------------------------------------------- 6. asserts
assert out.count("\n") == 63, "line count changed: %d" % out.count("\n")
assert out.count("688_501") == 0, "old band block leaked"
assert out.count("690_701") >= 4, "target A band missing"
for band in ("690_701..692_700", "692_701..692_900"):
    assert out.count(band) >= 2, "target band missing: %s" % band
assert out.count("W307") > 30 and out.count("W308") > 5
assert out.count("W300") == src.count("W300"), "W300 (cumulative) must not roll"
assert out.count("W301") == src.count("W301"), "W301 (cumulative chain) must not roll"
assert out.count("1,097,541") == src.count("1,095,341")
assert out.count("671,120") == src.count("668,920"), "668,920 roll mismatch"
assert out.count("673,320") == src.count("671,120"), "671,120 roll mismatch"
assert out.count("line_pre_w307") == 1
assert out.count("line_pre_w306") == 0, "line_pre double roll"
assert out.count("ZZ") == 0, "sentinel leaked"
assert out.count("n1_w306") >= 4 and "n1_w307" in out
assert out.count("n1_w305") == 0, "n1 double roll"
assert out.count("第五十九次") == 0 and out.count("第六十次") >= 3
assert out.count("第六十一次") >= 3
assert out.count("1.1999") >= 2
assert out.count(SEAT_SHA) >= 3
assert out.count("CLEAN-AT-BIRTH 38th gen") == 1

open("results/_w307bmc_derive_counts.json", "w", encoding="utf-8").write(
    json.dumps({"keys": counts, "band_tokens": nband,
                "bytes_src": len(raw), "bytes_out": len(out.encode("utf-8"))},
               ensure_ascii=False, indent=1))
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(out)
b = out.encode("utf-8")
print("WROTE %s bytes=%d lines=%d sha16=%s bands=%d keys=%d" % (
    OUT, len(b), out.count("\n"), hashlib.sha256(b).hexdigest()[:16], nband, len(NUM)))