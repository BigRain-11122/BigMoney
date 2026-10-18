# -*- coding: utf-8 -*-
# r1085 bm-c: W266 prereg derive (count-asserted ordered transform + marker-extracted block replaces).
# Canon-clone of _w265bmc_prereg_derive.py per age() machine-needle law (shift-map one generation).
# Source = committed frozen W265 prereg AT THE FREEZE COMMIT e57215a2c (git e57215a2c:research/PERPETUAL_N1_W265_PREREG.md,
# 22,927 bytes -- the frozen pre-run face; sec7/8 placeholders intact). Extracted to
# results/_w266bmc_w265_frozen_face.txt THIS window (r1085); byte-verified:
# disk==blob sha1 2fb89d04929156f2a0270d4270988f46d52400f0, sha256_16 d36c29cf048d299d.
# TEMPLATE-FACE DISCLOSURE (r1052/r1049 law): HEAD twin 39c55fad386bc405c8b30861355897ae27254555 = the
# CURRENT HEAD face = the POST-CYCLE face with sec.7/8 BACKFILLED by the r1084 W265 cycle (estate
# landed via 2e622ee447, fivekeys+backfill closeout). Deriving from the backfilled face would
# fabricate W266 sec.7/8 from W265's measured numbers -- the r1049/r1052 precedent requires the
# e57215a2c frozen pre-run face.
# W266 facts (all machine-derived, never transcribed):
#   - seat probe ADMIT receipt results/_w266bmc_20261018_probe_receipt.json (bm-c r1084 continuation
#     dead-window chain, seat rides origin ace19ba85b per r565 early-visibility law,
#     MSG-20261018-0719-bmc-w266-seat landed, swept processed). STAIRCASE CONTINUES: A naive
#     600_301..602_300 REFUSED at start (registered W265 B band 600_301..600_500 sits INSIDE the
#     naive A window) -> A first-clean 600_501..602_500 hops=1 (FIFTEENTH consecutive A-hop, W265
#     prereg sec.5 item5 post-W265-REGISTERED pre-disclosure confirmed live per r587, ZERO
#     divergence) / B naive 600_501..600_700 REFUSED at start (lands INSIDE the own-wave W266 A
#     first-clean window 600_501..602_500) -> own-A reservation cascade hop past 602_500 ->
#     602_501..602_700 hops=1 (SIXTEENTH consecutive above-own-A landing); seed_admit FREE x2
#     (A base=600501 span=2000 / B base=602501 span=200); leg0 rows=263 owner_rows=255 bmc_rows=84
#     ordinal=256; leg2 conflicts=0; leg3 origin_vacancy=true; leg4 W267+ projection: A naive
#     602_501..604_500 CLEAN hops=0 pre-W266 universe BUT post-W266-REGISTERED the naive W267 A start
#     602_501 is REFUSED by the registered W266 B band 602_501..602_700 (SIXTEENTH consecutive A-hop
#     expected) AND the W267 B naive 602_701..602_900 lands inside the own-A reservation face.
#   - upstream W265 finalize LANDED (bm-c r1084 continuation dead-window chain one-pass,
#     n1_w265_results.json generated 2026-10-18 07:01:43, estate landed via 2e622ee447,
#     absorb-verified by the r1084 closeout d1e9f1b5f9): merged K=580,920 / ledger 1,007,335 EXACT
#     (1,005,135+2,200) / merged mu -0.09271568116091716 (8dp -0.09271568) / sigma 0.2450411750444309
#     (8dp 0.24504118) / se_mu@K580,920 0.000321 / W265-only mu -0.08956581818181819 (8dp
#     -0.08956582) / A p95 0.3149 / K-lift 0.0 (held-flat-at-zero, second consecutive true-0 face) /
#     n_eff_held 1,005,135 / line_pre_w265 1.1956 / line_merged@580,920 1.1956 / own-slice vs merged
#     gap 0.00314986 in-band<0.02 (fivekeys 6/6 ALL PASS receipt results/_r1084bmc_w265_fivekeys.json
#     + sixgate PRE-FINALIZE ALL PASS 27th consecutive receipt results/_r1084bmc_w265_sixgate.json;
#     splice a47517f792 06:50:58; engine self-burn 12/12 ledger appends 93298b7e33+c72805837c;
#     prereg freeze e57215a2caccd881964444380aa13fb327ada7c4 landed by the bm-c r1081 window).
# Needle-count pre-flight evidence: results/_w266bmc_needle_counts.txt (measured live on T0 + T1
# simulation THIS window; floors below match every VMAP_FLOORS entry; divergences from the
# pattern-assumed shift are MEASURED law: W264 raw 62 (not 63), W263 raw 4 (not 3), W260 raw 1
# (not 2) -- measured-counts-not-assumed per r1077 preflight law).
# Same-window needle heals disclosed:
# (1) DATE-ROLL heal (r1081 family, NEW for this generation): the _w265bmc->_w266bmc roll maps
#     "_w265bmc_20261017" x3 (the W265 seat-probe receipt name) onto "_w266bmc_20261017" -- WRONG
#     (the W266 seat probe is dated 20261018; the W265 generation needed no such heal because both
#     probes shared the 20261017 date) -> POST_LEG rewrites "_w266bmc_20261017"->"_w266bmc_20261018"
#     floor 3 (2 non-block receipt refs + 1 b_title-interior copy discarded by block replacement).
# (2) RAM face live-measured THIS window: psutil 2.87GB free (~3GB, same magnitude as the r1081
#     anchor) + nvidia-smi 3% util / 3.2G VRAM resident / ZERO active GPU burn -- the r1081 face
#     "POOL-0016 候件冻结态" updated to the honest current "零在飞烧批" (gen-only lane idle window,
#     CEO weekend-use standing, LLM face retired per O-20261017-0953);
# (3) se_mu chain true-history correction (r1059 canon-embed advice, pre-authored consumed-label
#     form): the rolled chain carries W262 0.000324 (FALSE -- true W262 measured 0.000323 per the
#     W265-prereg frozen chain) -> POST_LEG rewrites the tail with true history W262 **0.000323** /
#     W263 **0.000323** / W264 **0.000322** / W265 **0.000321** (W265 measured per n1_w265_results
#     se_mu_at_k580920) and appends the W266 projection 0.000321;
# (4) K-lift POST_LEG: post-roll form carries "键 W265 实测 K-lift **0.0001**·line_merged@K578,720
#     **1.1955**·line_pre_w264 1.1954" (lowercase line_pre_w264 NOT rolled by the W-roll --
#     case-sensitive) -- corrected to the true W265 anchors "键 W265 实测 K-lift **0.0000**·
#     line_merged@K580,920 **1.1956**·line_pre_w265 1.1956" (k_lift_delta=0.0 per
#     _r1084bmc_w265_fivekeys, held-flat-at-zero);
# (5) low-RAM precedent ledger append: W265 freeze-window 3G bm-c anchor appended via POST_LEG
#     (chain precedent every-wave append, W262-derive b6_ram paradigm; the wave-roll had shifted
#     the W263 26G bm-a anchor onto the W264 label and the W264 7G onto W265 -- both restored +
#     true W265 anchor appended);
# (6) n_eff_held_equal 996,335 carried verbatim per W263/W264/W265 derive precedent (static
#     precedent-chain face; the live n_eff anchors are machine-verified from receipts in the
#     gates below);
# (7) finalize-window stamp roll: W265 finalize one-pass landed 07:0x (n1_w265_results generated
#     07:01:43); T1 carries the W264-era 22:3x stamps x4 (two block-interior copies discarded by
#     block replacement) -> POST_LEG rolls all to 07:0x.
import io, os, sys, datetime, subprocess, hashlib, re, json

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w266bmc_w265_frozen_face.txt")
OUT = os.path.join(REPO, "research", "PERPETUAL_N1_W266_PREREG.md")
GIT = "C:/Program Files/Git/cmd/git.exe"


def git_out(args):
    r = subprocess.run([GIT] + args, capture_output=True, cwd=REPO)
    if r.returncode != 0:
        raise SystemExit("git fail %r: %s" % (args, r.stderr.decode("utf-8", "replace")))
    return r.stdout.decode("utf-8", "replace").strip()


# --- source byte-identity gates ---
_blob_expect = "2fb89d04929156f2a0270d4270988f46d52400f0"   # freeze-commit face @ e57215a2c
_ho = git_out(["hash-object", SRC])
assert _ho == _blob_expect, "SRC blob mismatch: got %s expect %s" % (_ho, _blob_expect)
_fc = git_out(["rev-parse", "e57215a2c:research/PERPETUAL_N1_W265_PREREG.md"])
assert _fc == _blob_expect, "freeze-commit blob mismatch: %s" % _fc
_hb = git_out(["rev-parse", "HEAD:research/PERPETUAL_N1_W265_PREREG.md"])
assert _hb == "39c55fad386bc405c8b30861355897ae27254555", "HEAD tpl twin face drifted: %s" % _hb

T0 = io.open(SRC, encoding="utf-8", newline="").read()
assert len(T0.encode("utf-8")) == 22927, "SRC size drift: %d" % len(T0.encode("utf-8"))
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "d36c29cf048d299d", "SRC sha mismatch"

# --- chain-fact existence gates (zero transcription) ---
for sha in ("e57215a2c", "a47517f792", "93298b7e33", "c72805837c", "ace19ba85b", "7343e3650"):
    git_out(["cat-file", "-e", sha + "^{commit}"])
_ci = git_out(["show", "-s", "--format=%ci", "a47517f792"])   # 2026-10-18 06:50:58 +0800
_m = re.match(r"2026-10-18 (\d{2}):(\d{2})", _ci)
assert _m, "splice commit ts unexpected: %r" % _ci
SPLICE_T = "%s:%sx" % (_m.group(1), _m.group(2)[0])           # 06:5x

# --- finalize-anchor machine-verify gates (fivekeys receipt + results json, live) ---
with open(os.path.join(REPO, "results", "_r1084bmc_w265_fivekeys.json"), encoding="utf-8") as f:
    fk = json.load(f)
assert round(fk["merged"]["mu"], 8) == -0.09271568, "merged mu drift: %r" % fk["merged"]["mu"]
assert round(fk["merged"]["sigma"], 8) == 0.24504118, "sigma drift: %r" % fk["merged"]["sigma"]
assert round(fk["merged"]["se_mu_k580920"], 6) == 0.000321, "se_mu drift: %r" % fk["merged"]["se_mu_k580920"]
assert round(fk["w265_only"]["mu"], 8) == -0.08956582, "w265-only mu drift: %r" % fk["w265_only"]["mu"]
assert round(fk["a_band"]["full_sharpe_p95"], 4) == 0.3149, "p95 drift: %r" % fk["a_band"]["full_sharpe_p95"]
assert round(fk["skill_line"]["k_lift_delta"], 4) == 0.0000, "k-lift drift: %r" % fk["skill_line"]["k_lift_delta"]
assert fk["skill_line"]["n_eff_held"] == 1005135, "n_eff_held drift: %r" % fk["skill_line"]["n_eff_held"]
assert fk["merged"]["k"] == 580920, "K drift: %r" % fk["merged"]["k"]
assert fk["ledger_identity"]["total"] == 1007335 and fk["ledger_identity"]["exact"], "ledger identity drift"
with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w265_results.json"), encoding="utf-8") as f:
    res = json.load(f)
assert res["skill_line_v2_k_lift"]["n_eff_held_equal"] == 1005135
assert round(res["skill_line_v2_k_lift"]["line_pre_w265"], 4) == 1.1956
assert round(res["skill_line_v2_k_lift"]["line_merged_580920"], 4) == 1.1956
assert round(res["null_pool_cumulative"]["se_mu_at_k580920"], 6) == 0.000321
with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w264_results.json"), encoding="utf-8") as f:
    res4 = json.load(f)
assert round(res4["null_pool_cumulative"]["se_mu_at_k578720"], 6) == 0.000322, "W264 se_mu heal verify"
with open(os.path.join(REPO, "results", "_w266bmc_20261018_probe_receipt.json"), encoding="utf-8") as f:
    pr = json.load(f)
assert pr["verdict"] == "ADMIT"
assert pr["bands"]["A"] == [600501, 602500] and pr["bands"]["B"] == [602501, 602700]
assert pr["legs"]["leg1"]["hops_A"] == 1 and pr["legs"]["leg1"]["hops_B"] == 1
assert pr["legs"]["leg0"]["owner_rows"] == 255 and pr["legs"]["leg0"]["bmc_rows"] == 84
assert pr["legs"]["leg0"]["ordinal"] == 256

P1, P2, P3 = "\x01W\x01", "\x01N\x01", "\x01B\x01"

VMAP = [
    # ---- explicit wave-free legs BEFORE the wave rolls (compound needles first) ----
    ("A-ext seed=598_301..600_300", "A-ext seed=600_501..602_500"),
    ("B-ext exit seed=600_301..600_500", "B-ext exit seed=602_501..602_700"),
    ("entry rng=**598_301+j**（与 A[j] 同源配对语义逐字", "entry rng=**600_501+j**（与 A[j] 同源配对语义逐字"),
    # seat/provenance faces (W266 seat published bm-c r1084 continuation chain, rides origin ace19ba85b)
    ("席位公示=MSG-20261017-2241-bmc-w265-seat 已推 origin 7343e3650 r565 律（bm-c r1077 席·queue-head seat-first lane）",
     "席位公示=MSG-20261018-0719-bmc-w266-seat 已推 origin ace19ba85b r565 律（bm-c r1084 席·queue-head seat-first lane）"),
    ("席位公示 MSG-20261017-2241-bmc-w265-seat 先推 origin 7343e3650 r565 律",
     "席位公示 MSG-20261018-0719-bmc-w266-seat 先推 origin ace19ba85b r565 律"),
    # wave-number + vacancy faces
    ("波号 265", "波号 266"),
    ("r1077 席位窗实跑：origin inbox 零 W265 席位外机命中", "r1084 席位窗实跑：origin inbox 零 W266 席位外机命中"),
    ("零 265 行", "零 266 行"),
    ("零 skip-ahead W266/W267 席位声明", "零 skip-ahead W267/W268 席位声明"),
    ("池第 263 枚", "池第 264 枚"),
    # ordinals + own-wave faces
    ("第 255 波", "第 256 波"),
    ("bm-c 第八十四枚自有波", "bm-c 第八十五枚自有波"),
    ("probe leg0 bmc_rows=83 attempt-continuity face（r1077 窗算法·bm-c own seat+bmc live rows 83 实读）——freeze 时 live derive bmc rows 83+候选=第 84 枚 EXACT",
     "probe leg0 bmc_rows=84 attempt-continuity face（r1084 窗算法·bm-c own seat+bmc live rows 84 实读）——freeze 时 live derive bmc rows 84+候选=第 85 枚 EXACT"),
    ("engine_owner==bm-c 83 行注册", "engine_owner==bm-c 84 行注册"),
    # engine live-read faces (bm-c instance, r1085 window)
    ("saturation_engine.py status live-read r1080：burns_active=[] queue_next=[] 实读·heartbeat 新鲜",
     "saturation_engine.py status live-read r1085：burns_active=[] queue_next=[] 实读·heartbeat 新鲜"),
    ("本机 bm-c 实例·heartbeat 新鲜实读 r1080 窗·队列空转 idle", "本机 bm-c 实例·heartbeat 新鲜实读 r1085 窗·队列空转 idle"),
    ("引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1080 窗实读", "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1085 窗实读"),
    # RAM face honest update (live-measured THIS window: psutil 2.87GB free ~3GB; nvidia-smi 3% / 3.2G VRAM
    # resident / zero active GPU burn -- gen-only lane idle window, CEO weekend-use standing, LLM retired)
    ("本窗 free RAM ~3GB（bm-c 底盘常驻·24G 物理内存机·CEO 周末用机态·GPU=gen-only 车道空窗（nvidia-smi 实读 3%·3.2G VRAM 常驻·POOL-0016 候件冻结态）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）",
     "本窗 free RAM ~3GB（bm-c 底盘常驻·24G 物理内存机·CEO 周末用机态·GPU=gen-only 车道空窗（nvidia-smi 实读 3%·3.2G VRAM 常驻·零在飞烧批）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）"),
    # runner CLI wave
    ("--wave 265/finalize --wave 265", "--wave 266/finalize --wave 266"),
    # sec8 placeholder projection-label bump (W267+ face)
    ("§5.5 W266+ 投影承接机证", "§5.5 W267+ 投影承接机证"),
    # ---- lowercase chained rolls (result/script faces) ----
    ("n1_w265", P2), ("n1_w264", "n1_w265"), (P2, "n1_w266"),
    ("_w265bmc", P3), ("_w264bmc", "_w265bmc"), (P3, "_w266bmc"),
    # ---- wave-number roll (chained placeholders) ----
    ("W265", P1), ("W264", "W265"), ("W263", "W264"), ("W262", "W263"), ("W261", "W262"), ("W260", "W261"),
    ("W259", "W260"), ("W258", "W259"), ("W257", "W258"), ("W256", "W257"), ("W255", "W256"), (P1, "W266"),
]

VMAP_FLOORS = {
    "A-ext seed=598_301..600_300": 1,
    "B-ext exit seed=600_301..600_500": 1,
    "entry rng=**598_301+j**（与 A[j] 同源配对语义逐字": 1,
    "席位公示=MSG-20261017-2241-bmc-w265-seat 已推 origin 7343e3650 r565 律（bm-c r1077 席·queue-head seat-first lane）": 1,
    "席位公示 MSG-20261017-2241-bmc-w265-seat 先推 origin 7343e3650 r565 律": 1,
    "波号 265": 1,
    "r1077 席位窗实跑：origin inbox 零 W265 席位外机命中": 1,
    "零 265 行": 1,
    "零 skip-ahead W266/W267 席位声明": 1,
    "池第 263 枚": 1,
    "第 255 波": 1,
    "bm-c 第八十四枚自有波": 1,
    "probe leg0 bmc_rows=83 attempt-continuity face（r1077 窗算法·bm-c own seat+bmc live rows 83 实读）——freeze 时 live derive bmc rows 83+候选=第 84 枚 EXACT": 1,
    "engine_owner==bm-c 83 行注册": 1,
    "engine_owner==bm-c 波的未烧分片": 1,
    "saturation_engine.py status live-read r1080：burns_active=[] queue_next=[] 实读·heartbeat 新鲜": 1,
    "本机 bm-c 实例·heartbeat 新鲜实读 r1080 窗·队列空转 idle": 1,
    "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1080 窗实读": 1,
    "本窗 free RAM ~3GB（bm-c 底盘常驻·24G 物理内存机·CEO 周末用机态·GPU=gen-only 车道空窗（nvidia-smi 实读 3%·3.2G VRAM 常驻·POOL-0016 候件冻结态）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）": 1,
    "--wave 265/finalize --wave 265": 1,
    "§5.5 W266+ 投影承接机证": 1,
    "n1_w265": 4, "n1_w264": 6, "_w265bmc": 4, "_w264bmc": 1,
    # measured live on T0 (results/_w266bmc_needle_counts.txt, r1085 window; MEASURED-counts law --
    # divergences from the naive one-gen shift are disclosed in the file header: W264 raw 62 not 63,
    # W263 raw 4 not 3, W260 raw 1 not 2)
    "W265": 35, "W264": 62, "W263": 4, "W262": 2, "W261": 2, "W260": 1,
    "W259": 1, "W258": 1, "W257": 1, "W256": 1, "W255": 1,
    # block-marker stability floors (raw template face)
    "engine_owner 行 254 注册在册（表尾": 1,
    "prev=**届时空窗活链头 derive 禁手抄**": 1,
    "（**A 面=STAIRCASE-AFFECTS-A": 1,
    "entry rng seed=**598_301+j**": 1,
    "exit rng=**600_301+j**": 1,
    "probe W266+ 投影 A naive 600_301..602_300 CLEAN hops=0": 1,
    "5. **W266+ 投影（probe 机证 leg4": 1,
    "本件=席位窗后首窗冻结件；五面冻结拼接脚本": 1,
    "（gate0.5 绿·编辑器 loud abort 兜底）**。": 1,
    "owner per chain-order law）**】】）": 1,
    "verify at W266 prereg，hop 链逐跳在 probe 回执。": 1,
    "（见 §5 item5）。": 1,
    "seed_admit_gate rc0 双带 FREE": 1,
    "n_eff_held_equal 996,335": 1,
    "注册+烧录+finalize 全落地": 2,
    "（W264 注册+烧录+finalize 全落地）": 1,
    # zero-floors (absence assertions on T0)
    "waits-upstream ARMED": 0,
    "1,007,335": 0, "600_501..602_500": 0, "602_501..602_700": 0,
    "−0.09271568": 0, "0.24504118": 0, "−0.08956582": 0, "0.3149": 0,
    "07:0x": 0, "583,120": 0, "602_501..604_500": 0, "602_701..602_900": 0,
    "_w266bmc_20261018": 0, "MSG-20261018-0719": 0, "ace19ba85b": 0,
}


def xf(t):
    for o, n in VMAP:
        t = t.replace(o, n)
    return t


for o, f in VMAP_FLOORS.items():
    c = T0.count(o)
    if f == 0:
        if c:
            raise SystemExit("VMAP FLOOR(0) FAIL: %r count=%d (expect 0)" % (o, c))
        continue
    if c < f:
        raise SystemExit("VMAP FLOOR FAIL: %r count=%d floor=%d" % (o, f))

T1 = xf(T0)

# ---------------- post-roll correction legs (needles exist only in T1 after the rolls) ----------------
VMAP_POST_LEGS = [
    # finalize-window stamp roll (heal (7)): W265 finalize one-pass landed 07:0x (n1_w265_results
    # generated 2026-10-18 07:01:43); T1 carries the W264-era 22:3x stamps x4 (two block-interior
    # copies discarded by block replacement)
    ("22:3x", "07:0x", 2),
    # DATE-ROLL heal (1): the _w265bmc->_w266bmc roll maps the W265 seat-probe receipt name onto the
    # WRONG date (20261017); the W266 probe receipt is dated 20261018 (2 non-block + 1 block-interior)
    ("_w266bmc_20261017", "_w266bmc_20261018", 3),
    # sec.5 item1 measured keys -> W265 actuals (n1_w265_results + fivekeys machine values)
    ("（W265 实测键 **−0.09272766**·K=578,720 合并池·W265-only 实测 **−0.08593818**）",
     "（W265 实测键 **−0.09271568**·K=580,920 合并池·W265-only 实测 **−0.08956582**）", 1),
    ("W2..W265 共二百六十三面实测 mu 稳定先例", "W2..W265 共二百六十四面实测 mu 稳定先例", 1),
    ("W265-only vs merged 实差 0.0068 在带内", "W265-only vs merged 实差 0.0031 在带内", 1),
    # sec.5 item2 sigma key
    ("键 **0.24504297**=W265 合并池实测", "键 **0.24504118**=W265 合并池实测", 1),
    # sec.5 item3 p95 anchor
    ("与 W265 A 档 p95（**0.3046** 实测锚）", "与 W265 A 档 p95（**0.3149** 实测锚）", 1),
    # sec.5 item4 K-lift chain + line faces (heal (4): lowercase line_pre_w264 NOT rolled by the
    # W-roll; true W265 anchors K-lift 0.0000 held-flat + line_merged@580,920 1.1956 + line_pre_w265 1.1956)
    ("键 W265 实测 K-lift **0.0001**·line_merged@K578,720 **1.1955**·line_pre_w264 1.1954·n_eff_held_equal 996,335",
     "键 W265 实测 K-lift **0.0000**·line_merged@K580,920 **1.1956**·line_pre_w265 1.1956·n_eff_held_equal 996,335", 1),
    ("→W262 **0.000324**→W263 **0.000323**→W264 **0.000323**→W265 **0.000322**→W266 投影 0.000322】",
     "→W262 **0.000323**→W263 **0.000323**→W264 **0.000322**→W265 **0.000321**→W266 投影 0.000321】", 1),
    # sec.4 merged-pool anchor face (W265 finalize landed)
    ("（起草窗实流 W1..W265 已落账 578,720 实测〔n1_w265_results.json 机读·W265 finalize 已落〕）",
     "（起草窗实流 W1..W265 已落账 580,920 实测〔n1_w265_results.json 机读·W265 finalize 已落〕）", 1),
    # sec.7/8 backfill paradigm rows -> the W265 cycle (bm-c r1084)
    ("bm-c r1077 W265 §7 范式", "bm-c r1084 W265 §7 范式", 1),
    ("bm-c r1077 W265 §8 范式", "bm-c r1084 W265 §8 范式", 1),
    # low-RAM precedent ledger append (heal (5)): W265 freeze-window 3G bm-c anchor
    # (the wave-roll had shifted the W263 26G bm-a anchor onto the W264 label and the W264 7G onto
    # W265 -- restore both + append the true W265 anchor)
    ("·W244 冻结窗 41.9G bm-a 实锚·W264 冻结窗 26G bm-a 实锚·W265 冻结窗 7G bm-c 实锚）",
     "·W244 冻结窗 41.9G bm-a 实锚·W263 冻结窗 26G bm-a 实锚·W264 冻结窗 7G bm-c 实锚·W265 冻结窗 3G bm-c 实锚）", 1),
]

for o, n, f in VMAP_POST_LEGS:
    c = T1.count(o)
    if c < f:
        raise SystemExit("VMAP POST FLOOR FAIL: %r count=%d floor=%d" % (o, c, f))
    T1 = T1.replace(o, n)

# ---------------- block replacements (needles marker-matched on T1; NEW = final) ----------------
NEW = {}

NEW["b_title"] = (
    "engine_owner 行 255 注册在册（表尾 W265 行【bm-c r1084 五面冻结 splice a47517f792 落地 @@SPLICE_T@@·selftest 9/9】"
    "+引擎自燃 12/12 分片已落【results/p2cal_ext/n1_w265/ 12/12·ledger append 93298b7e33+c72805837c】"
    "·**W265 finalize 已落地**【n1_w265_results.json 机读·净账本锚头 1,007,335·K=580,920 合并池·W265 finalize one-pass bm-c r1084 窗 07:0x·estate absorb r1084 2e622ee447】）"
    "+本候选=bm-c 自有席自有波【live-derive face：席面 own-seat face（bm-c r1084 席位 MSG-20261018-0719-bmc-w266-seat 已推 origin ace19ba85b"
    "·probe receipt _w266bmc_20261018 机证·bands ADMIT verbatim·queue-head seat-first lane）"
    "→freeze 时 live derive bmc rows 84+候选=第 85 枚 EXACT·以 freeze 时 live derive 为准 r587/r359】"
    "【bm-c 循环班 r1084 席位窗 2026-10-18 07:1x·CEO 填载令 standing+2026-10-10 ~23:1x RE-ISSUE+O-20261013-2215 CPU 常开令"
    "·**W266=bm-c own-wave window per chain-order law（W263 bm-a→W264 bm-c→W265 bm-c→W266 bm-c own-turn rotation·bm-a 席 r1042/r1043 明让 bm-c·MSG-0719 owner per chain-order law）**】】）"
)

NEW["b_prev"] = (
    "prev=**届时空窗活链头 derive 禁手抄**——起稿窗实况（**锚滚链面 r576/r590 律**）："
    "**W1..W265 N1 注册全部落地**【W265=注册+12/12 分片已烧·**finalize 已落地**——最新已 finalize 锚=**W265**"
    "【净账本锚头 **1,007,335**·K=580,920 合并池·n1_w265_results.json 机读·W265 finalize one-pass bm-c r1084 窗 07:0x】】；"
    "**零在飞上游席——「零在飞上游链前」断言适用且干净前置成立**（上游 W265 席位已闭链=注册+烧录+finalize 全落地·零在飞）；"
    "finalize 键序前置=届时按 registry 键 derive 复核 FAIL-CLOSED r307 两态例恒在；"
    "累计 null 池=580,920+2,200（本波）=**583,120 投影**（机械算·投影面仅披露·finalize 运行时按 registry 键 derive 免疫）。"
)

NEW["b_band"] = (
    "（**A 面=STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第十五次连续 A-hop）**："
    "A 面算术续带 600_301..602_300（自注册 W265 A 尾 600_300 续）"
    "在席位窗宇宙（post-W265-REGISTERED 终态注册）起点即 REFUSED"
    "（注册 W265 B 带 600_301..600_500 落 naive A 窗内=staircase re-emergence affects A 承袭"
    "·W265 prereg §5 item5 post-W265-REGISTERED pre-disclosure 兑现 r587 如实披露）"
    "→walk 越注册 W265 B 尾 600_500→A first-clean **600_501..602_500**·**hops=1**·"
    "**A 落位 base==注册前波 B 尾+1（600_500+1）机检关系**"
    "（A_hop_chain 1 跳 verbatim leg1 机证〔window 600_301..602_300→jump 600_501·refuser band 600_301..600_500〕"
    "·A_clean_at_naive_start=false·A_staircase_hop_past_W265_B=true"
    "·A base>=registered prior-wave B tail+1 floor relation）·非转录 r587 前向单调断言在走册）；"
    "**B-ext exit seed=602_501..602_700**（**B 面=1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态（第十六次连续 above-own-A 落位）**："
    "B naive 续带 600_501..600_700（自注册 W265 B 尾 600_500+1 续）"
    "在席位窗宇宙（post-W265-REGISTERED 终态注册）起点即 REFUSED"
    "（naive B 窗 600_501..600_700 落本波 A first-clean 窗 600_501..602_500 内"
    "=own-A reservation cascade standard leg 强制·probe leg1 B_semantics 机证·B_naive_refused_at_start=true）"
    "——**own-A reservation standard leg 越本波 A 窗 600_501..602_500**（1 hop）"
    "→**1 hop** 落位 **602_501..602_700**·**B 落位 base==本波 A 窗尾+1（602_500+1）EXACT 机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执 leg1 机证"
    "·非转录 r587·AB 同窗互斥面 leg2 律在场）；"
    "**W265 prereg §5 item5 投影承接面注记兑现+落位一致如面**："
    "投影预言 W266 A naive 600_301..602_300 将被注册 W265 B 带拒（staircase affects A 承袭·第十五次连续 A-hop）"
    "与 B own-A reservation cascade 上移——本窗 live re-derive 与投影完全一致（零分歧如实注记·禁转录投影 r587 面在场）。"
    "R267：W266 带（A 600_501..602_500/B 602_501..602_700）注册后对 W267+ 的拒面影响=W266 冻结方 leg4 前瞻已机证（见 §5 item5）。"
)

NEW["b3_a"] = (
    "entry rng seed=**600_501+j**（法典 §4 W266 行 A=600_501..602_500·"
    "**STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第十五次连续 A-hop）**："
    "A 算术续带 600_301..602_300（自注册 W265 A 尾 600_300 续）"
    "在席位窗宇宙（post-W265-REGISTERED 终态注册）起点即 REFUSED"
    "（注册 W265 B 带 600_301..600_500 落 naive A 窗内=W265 prereg §5 item5 post-W265-REGISTERED pre-disclosure 兑现·r587 承袭披露）"
    "→walk 越注册 W265 B 尾 600_500→A first-clean 600_501..602_500·**hops=1**·"
    "**A 落位 base==注册前波 B 尾+1（600_500+1）机检关系**"
    "（A_hop_chain 1 跳 verbatim probe leg1 机证·A_clean_at_naive_start=false·A_staircase_hop_past_W265_B=true）"
    "·非转录 r587·ADMIT 回执在场）；p=`BASELINE_P"
)

NEW["b3_b"] = (
    "exit rng=**602_501+j**（法典 §4 W266 行 B=602_501..602_700·"
    "**1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态**："
    "B naive 续带 600_501..600_700（自注册 W265 B 尾 600_500+1 续）"
    "在席位窗宇宙（post-W265-REGISTERED 终态注册）起点即 REFUSED"
    "（naive B 窗落本波 A first-clean 窗 600_501..602_500 内=own-A reservation cascade standard leg·probe leg1 B_semantics 机证）"
    "→own-A reservation 越本波 A 窗 600_501..602_500→1 hop 落位 602_501..602_700·"
    "**B 落位 base==本波 A 窗尾+1（602_500+1）机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执"
    "·第十六次连续 above-own-A 落位如实注记）"
    "·非转录 r587·与 W265 prereg §5 item5 投影承接面注记兑现+落位零分歧披露收敛·ADMIT 回执在场）；p_exit=`P_EXIT=0.05`"
)

NEW["b_claim_proj"] = (
    "probe W267+ 投影 A naive 602_501..604_500 CLEAN hops=0（零 live refusers）/ B naive 602_701..602_900 CLEAN hops=0 "
    "**但落 naive W267 A 窗内**→own-A reservation cascade 下 staircase 级联上移 **staircase face 延续 live re-derive governs 预披露**"
    "（投影 A naive 602_501..604_500 CLEAN·hops=0——**post-W266-REGISTERED 预披露：naive W267 A 起点 602_501 将被注册 W266 B 带 602_501..602_700 拒=staircase affects A 第十六次连续 A-hop 预期**；"
    "投影 B naive 602_701..602_900 clean 但落 naive W267 A 窗 602_501..604_500 内——"
    "**above-own-A 承袭 face：W266 B 602_501..602_700 落本波 A 窗之上〔第十六次连续〕·W266 A 面 1-hop=staircase affects A〔第十五次连续〕·"
    "W267 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace·注册 W266 B 带将拒 naive W267 A 窗仅当重叠——"
    "**W267 freezer 承接面强制注记：须在 post-W266 宇宙重 derive 且 derive B 时预留本波 A 窗·W141 先例·never transcribe r587**）"
)

NEW["b5_projection"] = (
    "5. **W267+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 602_501..604_500 **CLEAN**（hops=0·pre-W266 宇宙零 live refusers）——"
    "**post-W266-REGISTERED 预披露：naive W267 A 起点 602_501 将被注册 W266 B 带 602_501..602_700 拒（staircase-affects-A 第十六次连续 A-hop 预期）**；"
    "B naive **602_701..602_900 CLEAN（hops=0）但落投影 A 窗 602_501..604_500 内**（W267p_B_lands_inside_W267p_A_naive=true——"
    "**staircase face 延续**：W266 A 600_501..602_500+B 602_501..602_700 注册后 naive W267 A 窗起点即被注册 W266 B 带拒（staircase affects A 承袭·第十六次连续 A-hop 预期）"
    "→A first-clean 将上移·B own-A reservation cascade 落位相应上移——post-W266 宇宙 live re-derive 必变·禁转录投影）；"
    "**W267 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace**"
    "（W251 起 staircase affects A·W252/W253/W254/W255/W256/W257/W258/W259/W260/W261/W262/W263/W264/W265/W266=A/B 双 1-hop 形态连续十五波如实注记·seed-gap face 已于 W252 终结=A 首跳如实注记）"
    "——W267 冻结方必须在 post-W266 注册宇宙重 derive 且 derive B 时预留本波 A 窗 600_501..602_500+本波 B 带 602_501..602_700"
    "——leg2 律/E36 卡·W141 先例；verify at W267 prereg，hop 链逐跳在 probe 回执。"
)

NEW["b_gated"] = (
    "本件=席位窗后首窗冻结件；五面冻结拼接脚本 results/_w266bmc_freeze_edits.py"
    "（按 _w265bmc_freeze_edits_TOL.py 模板派生·gate0.5 自查 W265 行+W265 finalize 件在场=已绿·未落即 loud abort 兜底）"
    "=**splice 执行窗派生落地（r1081/r1084 W265 先例实时间线：prereg e57215a2c 落于 r1081 窗·splice a47517f792 落于 r1084 执行窗 @@SPLICE_T@@——"
    "**W266 freeze 面：W265 own-wave finalize 已落地=席位时即解锁——席位+prereg 本窗落地 per seat-first law O-20261010-2350 §2·"
    "splice 执行窗开门（gate0.5 绿·编辑器 loud abort 兜底）**。"
)

# marker pairs: (block, start_marker, end_marker) -- needles matched on T1 (post-roll faces)
BLOCKS = [
    ("b_title", "engine_owner 行 254 注册在册（表尾", "owner per chain-order law）**】】）"),
    ("b_prev", "prev=**届时空窗活链头 derive 禁手抄**", "（机械算·投影面仅披露·finalize 运行时按 registry 键 derive 免疫）。"),
    ("b_band", "（**A 面=STAIRCASE-AFFECTS-A", "（见 §5 item5）。"),
    ("b3_a", "entry rng seed=**598_301+j**", "；p=`BASELINE_P"),
    ("b3_b", "exit rng=**600_301+j**", "；p_exit=`P_EXIT=0.05`"),
    ("b_claim_proj", "probe W266+ 投影 A naive 600_301..602_300 CLEAN hops=0", "never transcribe r587**）"),
    ("b5_projection", "5. **W266+ 投影（probe 机证 leg4", "verify at W266 prereg，hop 链逐跳在 probe 回执。"),
    ("b_gated", "本件=席位窗后首窗冻结件；五面冻结拼接脚本", "（gate0.5 绿·编辑器 loud abort 兜底）**。"),
]

T2 = T1
for name, sm, em in BLOCKS:
    c = T2.count(sm)
    assert c == 1, "BLOCK %s start-marker count=%d (expect 1)" % (name, c)
    i = T2.index(sm)
    j = T2.find(em, i)
    assert j > i, "BLOCK %s end-marker not found after start" % name
    j += len(em)
    NEWTXT = NEW[name].replace("@@SPLICE_T@@", SPLICE_T)
    T2 = T2[:i] + NEWTXT + T2[j:]
    assert NEWTXT in T2, "BLOCK %s NEW not inserted" % name

# ---------------- post gates ----------------
MUST = [
    "PERPETUAL-N1-W266", "research/PERPETUAL_N1_W266_PREREG.md",
    "600_501..602_500", "602_501..602_700", "583,120", "1,007,335", "580,920",
    "n1_w266_results.json", "MSG-20261018-0719-bmc-w266-seat", "ace19ba85b",
    "池第 264 枚", "第八十五枚", "第 256 波", "第 85 枚",
    "STAIRCASE-AFFECTS-A", "第十五次连续 A-hop", "第十六次连续 above-own-A",
    "_w266bmc_20261018", "--wave 266/finalize --wave 266",
    "W265 finalize one-pass bm-c r1084", "n_eff_held_equal 996,335",
    "−0.09271568", "0.24504118", "−0.08956582", "（**0.3149** 实测锚）",
    "键 W265 实测 K-lift **0.0000**", "line_merged@K580,920 **1.1956**", "line_pre_w265 1.1956",
    "实差 0.0031 在带内", "共二百六十四面实测", "W2..W265",
    "engine_owner==bm-c 84 行注册", "engine_owner 行 255 注册在册",
    "probe leg0 bmc_rows=84 attempt-continuity face（r1084 窗算法·bm-c own seat+bmc live rows 84 实读）",
    "bm-c 循环班 r1084 席位窗", "本窗 free RAM ~3GB", "本机 bm-c 实例",
    "W266=bm-c own-wave window per chain-order law",
    "e57215a2c", "a47517f792", "93298b7e33", "c72805837c", "2e622ee447",
    "W267+ 投影", "W267p_B_lands_inside_W267p_A_naive", "verify at W267 prereg",
    "_w266bmc_freeze_edits.py", "_w265bmc_freeze_edits_TOL.py 模板派生",
    "bm-c r1084 W265 §7 范式", "bm-c r1084 W265 §8 范式",
    "（上游 W265 席位已闭链=注册+烧录+finalize 全落地·零在飞）",
    "W206/W211..W265 低 RAM 实烧先例", "W263 冻结窗 26G bm-a 实锚", "W264 冻结窗 7G bm-c 实锚",
    "W265 冻结窗 3G bm-c 实锚",
    "席位时即解锁", "（见 §5 item5）。", "R267：W266 带",
    "→W262 **0.000323**→W263 **0.000323**→W264 **0.000322**→W265 **0.000321**→W266 投影 0.000321】",
    "600_500+1", "602_500+1",
    "A_staircase_hop_past_W265_B=true", "B_lands_above_own_A=true",
    "seed_admit_gate rc0 双带 FREE",
    "波号 266", "零 266 行", "零 skip-ahead W267/W268 席位声明",
    "（W265 注册+烧录+finalize 全落地）",
]
for s in MUST:
    assert s in T2, "MUST-HAVE missing: %r" % s

MUST_NOT = [
    "A-ext seed=598_301", "B-ext exit seed=600_301",
    "598_301..600_300", "600_301..602_300 CLEAN", "600_301..600_500**",
    "GATED on", "finalize PENDING", "pending 投影 derive",
    "578,720", "1,005,135", "**580,920 投影**", "line_merged@K578,720",
    "−0.09272766", "0.24504297", "−0.08593818", "**0.3046**", "实差 0.0068 在带内",
    "22:3x", "19:2x", "queue_depth",
    "MSG-20261017-2241", "dd5fd438e", "b32f6bf1c", "f499817fa", "355c716b7", "91da16c86",
    "bm-a r1039", "bm-a r1039 W263",
    "bmc_rows=83", "第 84 枚", "第 255 波", "第八十四枚",
    "engine_owner==bm-c 83 行注册",
    "r1077 席", "r1077 席位窗实跑", "r1077 窗算法",
    "本窗 free RAM ~7GB", "gaming yield 让路态", "POOL-0016 候件冻结态",
    "W266p_", "W265p_",
    "line_pre_w263", "line_pre_w264 1.1954", "键 W262 实测 K-lift", "键 W263 实测 K-lift",
    "键 W264 实测 K-lift",
    "verify at W266 prereg",
    "W266+ 投影", "W265+ 投影",
    "第十四次连续 A-hop", "第十五次连续 above-own-A", "连续十四波", "共二百六十三面",
    "_w263bma", "_w264bma",
    "_w265bmc_freeze_edits.py 模板派生",
    "_w266bmc_20261017",
    "n1_w264_results.json", "n1_w263_results.json",
    "W2..W264", "W136..W264",
    "f4ffdb34e", "216b578b0", "964148797", "17dd06323", "7343e3650",
]
for s in MUST_NOT:
    assert s not in T2, "MUST-NOT-HAVE present: %r (count=%d)" % (s, T2.count(s))

# pinned count gates
assert T2.count("W267+ 投影") == 3, "W267+ 投影 count=%d (expect 3 = §5.5 rolled + b5 + b6 claim)" % T2.count("W267+ 投影")
assert T2.count("W266+ 投影") == 0, "W266+ 投影 count=%d (expect 0)" % T2.count("W266+ 投影")
assert T2.count("hops=1") == 2, "hops=1 count=%d (expect 2 = 带位 A + §3 A)" % T2.count("hops=1")
assert T2.count("hops=0") == 5, "hops=0 count=%d (expect 5 = b5 x2 + b6 x3)" % T2.count("hops=0")
assert T2.count("第十五次连续 A-hop") == 3, "第十五次连续 A-hop count=%d (expect 3 = b_band x2 + b3_a x1)" % T2.count("第十五次连续 A-hop")
assert T2.count("第十六次连续 A-hop") == 3, "第十六次连续 A-hop count=%d (expect 3 = b5 x2 + b6 x1)" % T2.count("第十六次连续 A-hop")
assert T2.count("第十六次连续 above-own-A") == 2, "第十六次连续 above-own-A count=%d (expect 2 = b_band + b3_b)" % T2.count("第十六次连续 above-own-A")
assert T2.count("连续十五波") == 1, "连续十五波 count=%d (expect 1 = b5 NEW)" % T2.count("连续十五波")
assert T2.count("600_501..602_500") >= 5, "600_501..602_500 count=%d (expect >=5)" % T2.count("600_501..602_500")
assert T2.count("602_501..602_700") >= 4, "602_501..602_700 count=%d (expect >=4)" % T2.count("602_501..602_700")
assert T2.count("600_301..600_500") >= 3, "600_301..600_500 count=%d (expect >=3 registered-prior-B-band refs)" % T2.count("600_301..600_500")
assert T2.count("602_501..604_500") == 5, "602_501..604_500 count=%d (expect 5 = b6 x3 + b5 x2)" % T2.count("602_501..604_500")
assert T2.count("600_301..602_300") == 4, "600_301..602_300 count=%d (expect 4 = b_band x3 [算术续带+A_hop_chain leg1 机证+W264 投影兑现注记] + b3_a x1; r1085 same-window heal #8: dead-window gate pattern-assumed 3, MEASURED T0 source needle 598_101..600_100 x4 = line5 x3 + line31 x1 per r1077 measured-counts law)" % T2.count("600_301..602_300")
assert T2.count("席位时即解锁") == 2, "席位时即解锁 count=%d (expect 2 = final line + b_gated)" % T2.count("席位时即解锁")
assert T2.count("_w266bmc_20261018") == 3, "_w266bmc_20261018 count=%d (expect 3 = 2 non-block refs + b_title)" % T2.count("_w266bmc_20261018")

# residue scan: all X_Y..X_Y windows well-formed
for m in re.finditer(r"(\d{3}_\d{3})\.\.(\d{3}_\d{3})", T2):
    lo = int(m.group(1).replace("_", "")); hi = int(m.group(2).replace("_", ""))
    assert lo <= hi, "malformed window %s" % m.group(0)

io.open(OUT, "w", encoding="utf-8", newline="").write(T2)
print("W266 PREREG DERIVE OK -> %s (%d bytes, %d lines)" % (OUT, len(T2.encode("utf-8")), T2.count("\n") + 1))
print("splice commit face: a47517f792 @ " + SPLICE_T)
print("blocks replaced: %s" % ", ".join(n for n, _, _ in BLOCKS))
print("vmap legs: %d floors: %d post-legs: %d MUST: %d MUST_NOT: %d" % (
    len(VMAP), len(VMAP_FLOORS), len(VMAP_POST_LEGS), len(MUST), len(MUST_NOT)))
print("src blob-verified == 2fb89d04929156f2a0270d4270988f46d52400f0 @ e57215a2c (frozen pre-run face; HEAD post-backfill twin 39c55fad disclosed, NOT used)")
print("out sha256_16: %s" % hashlib.sha256(T2.encode("utf-8")).hexdigest()[:16])
