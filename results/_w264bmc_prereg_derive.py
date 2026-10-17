# -*- coding: utf-8 -*-
# r1076 bm-c: W264 prereg derive (count-asserted ordered transform + marker-extracted block replaces).
# Canon-clone of _w262bmc_prereg_derive.py per age() machine-needle law (shift-map one generation);
# bloodline note: the W263 tpl below is bm-a-authored compact format (22,725B/64 lines) -- the b1
# giant-chain-tail blocks of the bm-c format DO NOT EXIST in this template; the chain face rides the
# title parenthetical (block-replaced here), so no HIST_B1/HIST_B6 extraction is needed this generation.
# Source = committed frozen W263 prereg AT THE FREEZE COMMIT b32f6bf1c (git b32f6bf1c:research/PERPETUAL_N1_W263_PREREG.md,
# 22,725 bytes -- the frozen pre-run face; sec7/8 placeholders intact). Extracted to
# results/_w264bmc_w263_frozen_face.txt THIS window (byte-verified: disk==blob 4b6f791dd50f085738292257a40f7b1c408411e0,
# sha256_16 5b26e6d31b7a21a8 == hash-object == rev-parse @ b32f6bf1c).
# TEMPLATE-FACE DISCLOSURE (r1052/r1049 law): HEAD twin 56cdbd3376acc0dda3e8b320a3e2fea2990c1c6f = the
# CURRENT HEAD face = the POST-CYCLE face with sec.7/8 BACKFILLED by the bm-a W263 cycle (estate landed
# via bm-a r1040 absorb 91da16c86). Deriving from the backfilled face would fabricate W264 sec.7/8 from
# W263's measured numbers -- the r1049/r1052 precedent requires the b32f6bf1c frozen pre-run face.
# W264 facts (all machine-derived, never transcribed):
#   - seat probe ADMIT receipt results/_w264bmc_20261017_probe_receipt.json (bm-c r1075 window, seat rides
#     origin dd5fd438e per r565 early-visibility law, MSG-20261017-1950-bmc-w264-seat landed in fleet/inbox/).
#     STAIRCASE CONTINUES: A naive 595_901..597_900 REFUSED at start (registered W263 B band 595_901..596_100
#     sits INSIDE the naive A window) -> A first-clean 596_101..598_100 hops=1 (THIRTEENTH consecutive A-hop,
#     W263 prereg sec.5 item5 post-W263-REGISTERED pre-disclosure confirmed live per r587, ZERO divergence) /
#     B naive 596_101..596_300 REFUSED at start (lands INSIDE the own-wave W264 A first-clean window
#     596_101..598_100) -> own-A reservation cascade hop past 598_100 -> 598_101..598_300 hops=1 (FOURTEENTH
#     consecutive above-own-A landing); seed_admit FREE x2 (A base=596101 span=2000 / B base=598101 span=200);
#     leg0 rows=261 owner_rows=253 bmc_rows=82 ordinal=254; leg2 conflicts=0; leg3 origin_vacancy=true;
#     leg4 W265+ projection: A naive 598_101..600_100 CLEAN hops=0 BUT post-W264-REGISTERED the naive W265 A
#     start 598_101 is REFUSED by the registered W264 B band 598_101..598_300 (FOURTEENTH consecutive A-hop
#     expected) AND the W265 B naive 598_301..598_500 lands inside the own-A reservation face.
#   - upstream W263 finalize LANDED (bm-a r1039 window 19:2x one-pass, n1_w263_results.json generated
#     19:27:33, estate landed via bm-a r1040 absorb 91da16c86): merged K=576,520 / ledger 1,002,935 EXACT
#     (1,000,735+2,200) / merged mu -0.09275356397002706 (8dp -0.09275356) / sigma 0.2450370389545185
#     (8dp 0.24503704) / se_mu@K576,520 0.000323 / W263-only mu -0.09496454545454545 (8dp -0.09496455) /
#     A p95 0.3208 / K-lift 0.0 (held-flat-zero face) / n_eff_held 1,000,735 / line_pre_w263 1.1953 /
#     line_merged@576,520 1.1953 / own-slice vs merged gap 0.00221098 in-band<0.02 (fivekeys 6/6 ALL PASS
#     receipt results/_r1039bma_w263_fivekeys.json + sixgate PRE-FINALIZE ALL PASS 25th consecutive
#     receipt results/_r1039bma_w263_sixgate.json; splice f499817fa 18:27:45; engine self-burn 12/12
#     ledger append 355c716b7).
#   - W263 chain: seat MSG-20261017-1740-bma-w263-seat origin fb0c962b5 -> prereg b32f6bf1c (17:42:09) ->
#     splice f499817fa (bm-a r1038, 18:27:45) -> engine self-burn 12/12 (355c716b7) -> sixgate 25th ->
#     finalize one-pass 19:27:33 -> fivekeys 6/6 -> estate absorb bm-a r1040 91da16c86.
# Needle-count pre-flight evidence: results/_w264bmc_needle_counts.txt (this window, measured live on T0;
# floors below match every VMAP_FLOORS entry, divergences disclosed in header comments as same-window
# needle heals). Same-window needle heals disclosed:
# (1) two-round jump faces: seat window rolls r1037->r1075 (FIVE rounds: the W263 seat sat in the bm-a
#     r1037 window; the W264 seat sat in the bm-c r1075 window -- live-read legs carry the true stamps);
#     finalize window rolls 14:1x->19:2x (W261 finalize -> W263 finalize two-wave anchor jump disclosed);
# (2) se_mu chain true-value correction (pre-authored consumed-label form per r1059 canon-embed advice):
#     the rolled chain carried W262 0.000324 (FALSE -- W262 measured 0.000323 per n1_w262_results
#     se_mu_at_k574320) -> POST_LEG rewrites the tail with true history W262 **0.000323** / W263 **0.000323**
#     and appends the W264 projection 0.000323;
# (3) RAM face honest update: prior face "~26GB bm-a 94G CEO-weekend" -> THIS window live-measures
#     ~7GB (psutil 7.40GB / Win32 7.39GB free, 20:2x) -- bm-c 24G chassis, CEO gaming-yield standing,
#     GPU=gen-only lane, LLM face retired per O-20261017-0953 gen-only lane;
# (4) K-lift POST_LEG: post-roll form would carry "键 W262 实测 K-lift **−0.0001**" -- corrected to the
#     true anchor "键 W263 实测 K-lift **0.0000**" (line_delta_k_lift=0.0 per n1_w263_results);
# (5) low-RAM precedent ledger append: W263 freeze-window anchor 26G bm-a appended via POST_LEG (chain
#     precedent every-wave append, W262-derive b6_ram paradigm).
import io, os, sys, datetime, subprocess, hashlib, re, json

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w264bmc_w263_frozen_face.txt")
OUT = os.path.join(REPO, "research", "PERPETUAL_N1_W264_PREREG.md")
GIT = "C:/Program Files/Git/cmd/git.exe"


def git_out(args):
    r = subprocess.run([GIT] + args, capture_output=True, cwd=REPO)
    if r.returncode != 0:
        raise SystemExit("git fail %r: %s" % (args, r.stderr.decode("utf-8", "replace")))
    return r.stdout.decode("utf-8", "replace").strip()


# --- source byte-identity gates ---
_blob_expect = "4b6f791dd50f085738292257a40f7b1c408411e0"   # freeze-commit face @ b32f6bf1c
_ho = git_out(["hash-object", SRC])
assert _ho == _blob_expect, "SRC blob mismatch: got %s expect %s" % (_ho, _blob_expect)
_fc = git_out(["rev-parse", "b32f6bf1c:research/PERPETUAL_N1_W263_PREREG.md"])
assert _fc == _blob_expect, "freeze-commit blob mismatch: %s" % _fc
_hb = git_out(["rev-parse", "HEAD:research/PERPETUAL_N1_W263_PREREG.md"])
assert _hb == "56cdbd3376acc0dda3e8b320a3e2fea2990c1c6f", "HEAD tpl twin face drifted: %s" % _hb

T0 = io.open(SRC, encoding="utf-8", newline="").read()
assert len(T0.encode("utf-8")) == 22725, "SRC size drift: %d" % len(T0.encode("utf-8"))
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "5b26e6d31b7a21a8", "SRC sha mismatch"

# --- chain-fact existence gates (zero transcription) ---
for sha in ("f499817fa", "355c716b7", "91da16c86", "dd5fd438e", "b32f6bf1c"):
    git_out(["cat-file", "-e", sha + "^{commit}"])
_ci = git_out(["show", "-s", "--format=%ci", "f499817fa"])   # 2026-10-17 18:27:45 +0800
_m = re.match(r"2026-10-17 (\d{2}):(\d{2})", _ci)
assert _m, "splice commit ts unexpected: %r" % _ci
SPLICE_T = "%s:%sx" % (_m.group(1), _m.group(2)[0])           # 18:2x

# --- finalize-anchor machine-verify gates (fivekeys receipt + results json, live) ---
with open(os.path.join(REPO, "results", "_r1039bma_w263_fivekeys.json"), encoding="utf-8") as f:
    fk = json.load(f)
assert round(fk["merged"]["mu"], 8) == -0.09275356, "merged mu drift: %r" % fk["merged"]["mu"]
assert round(fk["merged"]["sigma"], 8) == 0.24503704, "sigma drift: %r" % fk["merged"]["sigma"]
assert round(fk["merged"]["se_mu_k576520"], 6) == 0.000323, "se_mu drift: %r" % fk["merged"]["se_mu_k576520"]
assert round(fk["w263_only"]["mu"], 8) == -0.09496455, "w263-only mu drift: %r" % fk["w263_only"]["mu"]
assert round(fk["a_band"]["full_sharpe_p95"], 4) == 0.3208, "p95 drift: %r" % fk["a_band"]["full_sharpe_p95"]
assert round(fk["skill_line"]["k_lift_delta"], 4) == 0.0, "k-lift drift: %r" % fk["skill_line"]["k_lift_delta"]
assert fk["skill_line"]["n_eff_held"] == 1000735, "n_eff_held drift: %r" % fk["skill_line"]["n_eff_held"]
assert fk["merged"]["k"] == 576520, "K drift: %r" % fk["merged"]["k"]
with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w263_results.json"), encoding="utf-8") as f:
    res = json.load(f)
assert res["skill_line_v2_k_lift"]["n_eff_held_equal"] == 1000735
assert round(res["skill_line_v2_k_lift"]["line_pre_w263"], 4) == 1.1953
assert round(res["skill_line_v2_k_lift"]["line_merged_576520"], 4) == 1.1953
assert round(res["null_pool_cumulative"]["se_mu_at_k576520"], 6) == 0.000323
with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w262_results.json"), encoding="utf-8") as f:
    res2 = json.load(f)
assert round(res2["null_pool_cumulative"]["se_mu_at_k574320"], 6) == 0.000323, "W262 se_mu heal verify"
with open(os.path.join(REPO, "results", "_w264bmc_20261017_probe_receipt.json"), encoding="utf-8") as f:
    pr = json.load(f)
assert pr["verdict"] == "ADMIT"
assert pr["bands"]["A"] == [596101, 598100] and pr["bands"]["B"] == [598101, 598300]
assert pr["legs"]["leg1"]["hops_A"] == 1 and pr["legs"]["leg1"]["hops_B"] == 1
assert pr["legs"]["leg0"]["owner_rows"] == 253 and pr["legs"]["leg0"]["bmc_rows"] == 82
assert pr["legs"]["leg0"]["ordinal"] == 254

P1, P2, P3 = "\x01W\x01", "\x01N\x01", "\x01B\x01"

VMAP = [
    # ---- explicit wave-free legs BEFORE the wave rolls (compound needles first) ----
    ("A-ext seed=593_901..595_900", "A-ext seed=596_101..598_100"),
    ("B-ext exit seed=595_901..596_100", "B-ext exit seed=598_101..598_300"),
    ("entry rng=**593_901+j**（与 A[j] 同源配对语义逐字", "entry rng=**596_101+j**（与 A[j] 同源配对语义逐字"),
    # seat/provenance faces (W264 seat published bm-c r1075 window, rides origin dd5fd438e)
    ("席位公示=MSG-20261017-1740-bma-w263-seat 已推 origin fb0c962b5 r565 律（bm-a r1037 席·queue-head seat-first lane）",
     "席位公示=MSG-20261017-1950-bmc-w264-seat 已推 origin dd5fd438e r565 律（bm-c r1075 席·queue-head seat-first lane）"),
    ("席位公示 MSG-20261017-1740-bma-w263-seat 先推 origin fb0c962b5 r565 律",
     "席位公示 MSG-20261017-1950-bmc-w264-seat 先推 origin dd5fd438e r565 律"),
    # wave-number + vacancy faces
    ("波号 263", "波号 264"),
    ("r1037 席位窗实跑：origin inbox/processed/ 零 W263 席位外机命中", "r1075 席位窗实跑：origin inbox 零 W264 席位外机命中"),
    ("零 263 行", "零 264 行"),
    ("零 skip-ahead W264/W265 席位声明", "零 skip-ahead W265/W266 席位声明"),
    ("池第 261 枚", "池第 262 枚"),
    # ordinals + own-wave faces
    ("第 253 波", "第 254 波"),
    ("bm-a 第一百三十枚自有波", "bm-c 第八十三枚自有波"),
    ("probe leg0 bma_rows=129 attempt-continuity face（r1037 窗算法·bm-a own seat+bma live rows 129 实读）——freeze 时 live derive bma rows 129+候选=第 130 枚 EXACT",
     "probe leg0 bmc_rows=82 attempt-continuity face（r1075 窗算法·bm-c own seat+bmc live rows 82 实读）——freeze 时 live derive bmc rows 82+候选=第 83 枚 EXACT"),
    ("engine_owner==bm-a 129 行注册", "engine_owner==bm-c 82 行注册"),
    ("engine_owner==bm-a 波的未烧分片", "engine_owner==bm-c 波的未烧分片"),
    # engine live-read faces (bm-c instance, r1076 window)
    ("saturation_engine.py status live-read r1037：burns_active=[] queue_depth=[] 实读·heartbeat 新鲜",
     "saturation_engine.py status live-read r1076：burns_active=[] queue_next=[] 实读·heartbeat 新鲜"),
    ("本机 bm-a 实例·heartbeat 新鲜实读 r1037 窗·队列空转 idle", "本机 bm-c 实例·heartbeat 新鲜实读 r1076 窗·队列空转 idle"),
    ("本机 bm-a 实例·heartbeat 新鲜实读", "本机 bm-c 实例·heartbeat 新鲜实读"),
    ("引擎实况注记（本机 bm-a 实例 heartbeat 新鲜 r1037 窗实读", "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1076 窗实读"),
    ("bm-a 实例=engine ledger", "bm-c 实例=engine ledger"),
    # RAM face honest update (live-measured THIS window ~7GB)
    ("本窗 free RAM ~26GB（bm-a 底盘常驻·94G 物理内存机·CEO 周末用机态+35B:8090 常驻 GPU-offload 共存·引擎队列空转·CPU 车道独立如实注记）",
     "本窗 free RAM ~7GB（bm-c 底盘常驻·24G 物理内存机·CEO gaming yield 让路态·GPU=gen-only 车道（MV 重烧在飞合法占用）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）"),
    # runner CLI wave
    ("--wave 263/finalize --wave 263", "--wave 264/finalize --wave 264"),
    # sec8 placeholder projection-label bump (W265+ face)
    ("§5.5 W264+ 投影承接机证", "§5.5 W265+ 投影承接机证"),
    # ---- lowercase chained rolls (result/script faces) ----
    ("n1_w263", P2), ("n1_w261", "n1_w263"), (P2, "n1_w264"),
    ("_w263bma", P3), ("_w262bmc", "_w263bma"), (P3, "_w264bmc"),
    # ---- wave-number roll (chained placeholders) ----
    ("W263", P1), ("W262", "W263"), ("W261", "W262"), ("W260", "W261"), ("W259", "W260"),
    ("W258", "W259"), ("W257", "W258"), ("W256", "W257"), ("W255", "W256"), (P1, "W264"),
]

VMAP_FLOORS = {
    "A-ext seed=593_901..595_900": 1,
    "B-ext exit seed=595_901..596_100": 1,
    "entry rng=**593_901+j**（与 A[j] 同源配对语义逐字": 1,
    "席位公示=MSG-20261017-1740-bma-w263-seat 已推 origin fb0c962b5 r565 律（bm-a r1037 席·queue-head seat-first lane）": 1,
    "席位公示 MSG-20261017-1740-bma-w263-seat 先推 origin fb0c962b5 r565 律": 1,
    "波号 263": 1,
    "r1037 席位窗实跑：origin inbox/processed/ 零 W263 席位外机命中": 1,
    "零 263 行": 1,
    "零 skip-ahead W264/W265 席位声明": 1,
    "池第 261 枚": 1,
    "第 253 波": 1,
    "bm-a 第一百三十枚自有波": 1,
    "probe leg0 bma_rows=129 attempt-continuity face（r1037 窗算法·bm-a own seat+bma live rows 129 实读）——freeze 时 live derive bma rows 129+候选=第 130 枚 EXACT": 1,
    "engine_owner==bm-a 129 行注册": 1,
    "engine_owner==bm-a 波的未烧分片": 1,
    "saturation_engine.py status live-read r1037：burns_active=[] queue_depth=[] 实读·heartbeat 新鲜": 1,
    "本机 bm-a 实例·heartbeat 新鲜实读 r1037 窗·队列空转 idle": 1,
    "本机 bm-a 实例·heartbeat 新鲜实读": 1,
    "引擎实况注记（本机 bm-a 实例 heartbeat 新鲜 r1037 窗实读": 1,
    "bm-a 实例=engine ledger": 1,
    "本窗 free RAM ~26GB（bm-a 底盘常驻·94G 物理内存机·CEO 周末用机态+35B:8090 常驻 GPU-offload 共存·引擎队列空转·CPU 车道独立如实注记）": 1,
    "--wave 263/finalize --wave 263": 1,
    "§5.5 W264+ 投影承接机证": 1,
    "n1_w263": 4, "n1_w261": 2, "_w263bma": 4, "_w262bmc": 1,
    "n1_w262": 1,
    # measured live on T0 (results/_w264bmc_needle_counts.txt, this window)
    "W263": 34, "W262": 49, "W261": 17, "W260": 2, "W259": 2,
    "W258": 1, "W257": 1, "W256": 1, "W255": 1,
    # block-marker stability floors (raw template face)
    "engine_owner 行 252 注册在册（表尾": 1,
    "prev=**届时空窗活链头 derive 禁手抄**": 1,
    "（**A 面=STAIRCASE-AFFECTS-A": 1,
    "entry rng seed=**593_901+j**": 1,
    "exit rng=**595_901+j**": 1,
    "probe W264+ 投影 A naive 595_901..597_900 CLEAN hops=0": 1,
    "5. **W264+ 投影（probe 机证 leg4": 1,
    "本件=席位窗冻结件；五面冻结拼接脚本": 1,
    # zero-floors (absence assertions on T0)
    "waits-upstream ARMED": 0,
    "578,720": 0, "1,002,935": 0, "596_101..598_100": 0, "598_101..598_300": 0,
    "−0.09275356": 0, "0.24503704": 0, "−0.09496455": 0, "0.3208": 0,
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
        raise SystemExit("VMAP FLOOR FAIL: %r count=%d floor=%d" % (o, c, f))

T1 = xf(T0)

# ---------------- post-roll correction legs (needles exist only in T1 after the rolls) ----------------
VMAP_POST_LEGS = [
    # sec.5 preamble: two-wave anchor jump (W261 key -> W263 key; W263 finalize landed 19:2x)
    ("（W263 finalize PENDING·分片 12/12 已烧）——**本波 §5 预测键=**W262 实测值**【results/perpetual_faces/n1_w263_results.json·N1 面最新已 finalize 键·14:1x finalize one-pass】（W263 finalize 落地后运行时按 registry 键 derive 免疫·本键为起草窗活链头如面）",
     "（W263 finalize 已落地 19:2x）——**本波 §5 预测键=**W263 实测值**【results/perpetual_faces/n1_w263_results.json·N1 面最新已 finalize 键·19:2x finalize one-pass】（运行时按 registry 键 derive 免疫·本键为起草窗活链头如面）", 1),
    # sec.5 item1 measured keys -> W263 actuals (n1_w263_results + fivekeys machine values)
    ("（W262 实测键 **−0.09273607**·K=572,120 合并池·W262-only 实测 **−0.09411977**）",
     "（W263 实测键 **−0.09275356**·K=576,520 合并池·W263-only 实测 **−0.09496455**）", 1),
    ("W2..W262 共二百五十九面实测 mu 稳定先例", "W2..W263 共二百六十一面实测 mu 稳定先例", 1),
    ("W262-only vs merged 实差 0.0014 在带内", "W263-only vs merged 实差 0.0022 在带内", 1),
    # sec.5 item2 sigma key
    ("键 **0.24503320**=W262 合并池实测", "键 **0.24503704**=W263 合并池实测", 1),
    # sec.5 item3 p95 anchor
    ("与 W262 A 档 p95（**0.2994** 实测锚）", "与 W263 A 档 p95（**0.3208** 实测锚）", 1),
    ("门标注法 W5..W262 先例", "门标注法 W5..W263 先例", 1),
    # sec.5 item4 K-lift chain + line faces
    ("W136..W262 先例链披露", "W136..W263 先例链披露", 1),
    ("键 W262 实测 K-lift **−0.0001**·line_merged@K572,120 **1.1951**·line_pre_w261 1.1952·n_eff_held_equal 996,335",
     "键 W263 实测 K-lift **0.0000**·line_merged@K576,520 **1.1953**·line_pre_w263 1.1953·n_eff_held_equal 996,335", 1),
    # se_mu narrowing chain true-history correction (heal (2)): rolled tail carried W262 0.000324 FALSE
    ("→W260 **0.000325**→W261 **0.000325**→W262 **0.000324**→W263 投影 0.000324】",
     "→W260 **0.000325**→W261 **0.000324**→W262 **0.000323**→W263 **0.000323**→W264 投影 0.000323】", 1),
    # sec.4 merged-pool anchor face (W263 finalize landed)
    ("（起草窗实流 W1..W262 已落账 572,120 实测+W263 2,200 分片已烧 finalize pending 投影 derive 禁手抄）",
     "（起草窗实流 W1..W263 已落账 576,520 实测〔n1_w263_results.json 机读·W263 finalize 已落〕）", 1),
    # sec.7/8 backfill paradigm rows -> the W263 cycle (bm-a r1039)
    ("bm-c r1067 W262 §7 范式", "bm-a r1039 W263 §7 范式", 1),
    ("bm-c r1067 W262 §8 范式", "bm-a r1039 W263 §8 范式", 1),
    # sec.6 finalize precondition (upstream complete)
    ("（W263 注册+烧录完成·finalize pending bm-c 收口）", "（W263 注册+烧录+finalize 全落地）", 1),
    # low-RAM precedent ledger append (heal (5)): W263 freeze-window 26G bm-a anchor
    ("W206/W211..W263 低 RAM 实烧先例·W247 冻结窗 60.8G bm-a 实锚·W244 冻结窗 41.9G bm-a 实锚）",
     "W206/W211..W263 低 RAM 实烧先例·W247 冻结窗 60.8G bm-a 实锚·W244 冻结窗 41.9G bm-a 实锚·W263 冻结窗 26G bm-a 实锚）", 1),
    # current-claim executor face (bm-c loop this wave; r1076 window)
    ("bm-a 循环班直执", "bm-c 循环班直执", 1),
    # final freeze line: GATED -> UNBLOCKED face (W263 finalize landed = seat-time unlock)
    ("**W264 五面 splice（法典 §4 注册行+WAVE_CONFIGS）GATED on W263 finalize 落地（gate0.5 loud abort 律）——splice 未执行前本件=候选冻结件·引擎不烧。**",
     "**W264 五面 splice（法典 §4 注册行+WAVE_CONFIGS）——W263 own-wave finalize 已落地=席位时即解锁（n1_w263_results.json 机读在场·gate0.5 绿）·splice 未执行前本件=候选冻结件·引擎不烧。**", 1),
]

for o, n, f in VMAP_POST_LEGS:
    c = T1.count(o)
    if c < f:
        raise SystemExit("VMAP POST FLOOR FAIL: %r count=%d floor=%d" % (o, c, f))
    T1 = T1.replace(o, n)

# ---------------- block replacements (needles marker-matched on T1; NEW = final) ----------------
NEW = {}

NEW["b_title"] = (
    "engine_owner 行 253 注册在册（表尾 W263 行【bm-a r1037/r1038 五面冻结 splice f499817fa 落地 @@SPLICE_T@@·selftest 9/9】"
    "+引擎自燃 12/12 分片已落【results/p2cal_ext/n1_w263/ 12/12·ledger append 355c716b7】"
    "·**W263 finalize 已落地**【n1_w263_results.json 机读·净账本锚头 1,002,935·K=576,520 合并池·W263 finalize one-pass bm-a r1039 窗 19:2x·estate absorb bm-a r1040 91da16c86】）"
    "+本候选=bm-c 自有席自有波【live-derive face：席面 own-seat face（bm-c r1075 席位 MSG-20261017-1950-bmc-w264-seat 已推 origin dd5fd438e"
    "·probe receipt _w264bmc_20261017 机证·bands ADMIT verbatim·queue-head seat-first lane）"
    "→freeze 时 live derive bmc rows 82+候选=第 83 枚 EXACT·以 freeze 时 live derive 为准 r587/r359】"
    "【bm-c 循环班 r1075 席位窗 2026-10-17 19:5x·CEO 填载令 standing+2026-10-10 ~23:1x RE-ISSUE+O-20261013-2215 CPU 常开令"
    "·**W264=bm-c own-wave window per chain-order law（W262 bm-c→W263 bm-a→W264 bm-c own-turn rotation·W263 席位 MSG forward face 已名此窗）**】】）"
)

NEW["b_prev"] = (
    "prev=**届时空窗活链头 derive 禁手抄**——起稿窗实况（**锚滚链面 r576/r590 律**）："
    "**W1..W263 N1 注册全部落地**【W263=注册+12/12 分片已烧·**finalize 已落地**——最新已 finalize 锚=**W263**"
    "【净账本锚头 **1,002,935**·K=576,520 合并池·n1_w263_results.json 机读·W263 finalize one-pass bm-a r1039 窗 19:2x】】；"
    "**零在飞上游席——「零在飞上游链前」断言适用且干净前置成立**（上游 W263 席位已闭链=注册+烧录+finalize 全落地·零在飞）；"
    "finalize 键序前置=届时按 registry 键 derive 复核 FAIL-CLOSED r307 两态例恒在；"
    "累计 null 池=576,520+2,200（本波）=**578,720 投影**（机械算·投影面仅披露·finalize 运行时按 registry 键 derive 免疫）。"
)

NEW["b_band"] = (
    "（**A 面=STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第十三次连续 A-hop）**："
    "A 面算术续带 595_901..597_900（自注册 W263 A 尾 595_900 续）"
    "在席位窗宇宙（post-W263-REGISTERED 终态注册）起点即 REFUSED"
    "（注册 W263 B 带 595_901..596_100 落 naive A 窗内=staircase re-emergence affects A 承袭"
    "·W263 prereg §5 item5 post-W263-REGISTERED pre-disclosure 兑现 r587 如实披露）"
    "→walk 越注册 W263 B 尾 596_100→A first-clean **596_101..598_100**·**hops=1**·"
    "**A 落位 base==注册前波 B 尾+1（596_100+1）机检关系**"
    "（A_hop_chain 1 跳 verbatim leg1 机证〔window 595_901..597_900→jump 596_101·refuser band 595_901..596_100〕"
    "·A_clean_at_naive_start=false·A_staircase_hop_past_W263_B=true"
    "·A base>=registered prior-wave B tail+1 floor relation）·非转录 r587 前向单调断言在走册）；"
    "**B-ext exit seed=598_101..598_300**（**B 面=1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态（第十四次连续 above-own-A 落位）**："
    "B naive 续带 596_101..596_300（自注册 W263 B 尾 596_100+1 续）"
    "在席位窗宇宙（post-W263-REGISTERED 终态注册）起点即 REFUSED"
    "（naive B 窗 596_101..596_300 落本波 A first-clean 窗 596_101..598_100 内"
    "=own-A reservation cascade standard leg 强制·probe leg1 B_semantics 机证·B_naive_refused_at_start=true）"
    "——**own-A reservation standard leg 越本波 A 窗 596_101..598_100**（1 hop）"
    "→**1 hop** 落位 **598_101..598_300**·**B 落位 base==本波 A 窗尾+1（598_100+1）EXACT 机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执 leg1 机证"
    "·非转录 r587·AB 同窗互斥面 leg2 律在场）；"
    "**W263 prereg §5 item5 投影承接面注记兑现+落位一致如面**："
    "投影预言 W264 A naive 595_901..597_900 将被注册 W263 B 带拒（staircase affects A 承袭·第十三次连续 A-hop）"
    "与 B own-A reservation cascade 上移——本窗 live re-derive 与投影完全一致（零分歧如实注记·禁转录投影 r587 面在场）。"
    "R265：W264 带（A 596_101..598_100/B 598_101..598_300）注册后对 W265+ 的拒面影响=W264 冻结方 leg4 前瞻已机证（见 §5 item5）。"
)

NEW["b3_a"] = (
    "entry rng seed=**596_101+j**（法典 §4 W264 行 A=596_101..598_100·"
    "**STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第十三次连续 A-hop）**："
    "A 算术续带 595_901..597_900（自注册 W263 A 尾 595_900 续）"
    "在席位窗宇宙（post-W263-REGISTERED 终态注册）起点即 REFUSED"
    "（注册 W263 B 带 595_901..596_100 落 naive A 窗内=W263 prereg §5 item5 post-W263-REGISTERED pre-disclosure 兑现·r587 承袭披露）"
    "→walk 越注册 W263 B 尾 596_100→A first-clean 596_101..598_100·**hops=1**·"
    "**A 落位 base==注册前波 B 尾+1（596_100+1）机检关系**"
    "（A_hop_chain 1 跳 verbatim probe leg1 机证·A_clean_at_naive_start=false·A_staircase_hop_past_W263_B=true）"
    "·非转录 r587·ADMIT 回执在场）；p=`BASELINE_P"
)

NEW["b3_b"] = (
    "exit rng=**598_101+j**（法典 §4 W264 行 B=598_101..598_300·"
    "**1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态**："
    "B naive 续带 596_101..596_300（自注册 W263 B 尾 596_100+1 续）"
    "在席位窗宇宙（post-W263-REGISTERED 终态注册）起点即 REFUSED"
    "（naive B 窗落本波 A first-clean 窗 596_101..598_100 内=own-A reservation cascade standard leg·probe leg1 B_semantics 机证）"
    "→own-A reservation 越本波 A 窗 596_101..598_100→1 hop 落位 598_101..598_300·"
    "**B 落位 base==本波 A 窗尾+1（598_100+1）机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执"
    "·第十四次连续 above-own-A 落位如实注记）"
    "·非转录 r587·与 W263 prereg §5 item5 投影承接面注记兑现+落位零分歧披露收敛·ADMIT 回执在场）；p_exit=`P_EXIT=0.05`"
)

NEW["b_claim_proj"] = (
    "probe W265+ 投影 A naive 598_101..600_100 CLEAN hops=0（零 live refusers）/ B naive 598_301..598_500 CLEAN hops=0 "
    "**但落 naive W265 A 窗内**→own-A reservation cascade 下 staircase 级联上移 **staircase face 延续 live re-derive governs 预披露**"
    "（投影 A naive 598_101..600_100 CLEAN·hops=0——**post-W264-REGISTERED 预披露：naive W265 A 起点 598_101 将被注册 W264 B 带 598_101..598_300 拒=staircase affects A 第十四次连续 A-hop 预期**；"
    "投影 B naive 598_301..598_500 clean 但落 naive W265 A 窗 598_101..600_100 内——"
    "**above-own-A 承袭 face：W264 B 598_101..598_300 落本波 A 窗之上〔第十四次连续〕·W264 A 面 1-hop=staircase affects A〔第十三次连续〕·"
    "W265 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace·注册 W264 B 带将拒 naive W265 A 窗仅当重叠——"
    "**W265 freezer 承接面强制注记：须在 post-W264 宇宙重 derive 且 derive B 时预留本波 A 窗·W141 先例·never transcribe r587**）"
)

NEW["b5_projection"] = (
    "5. **W265+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 598_101..600_100 **CLEAN**（hops=0·pre-W264 宇宙零 live refusers）——"
    "**post-W264-REGISTERED 预披露：naive W265 A 起点 598_101 将被注册 W264 B 带 598_101..598_300 拒（staircase-affects-A 第十四次连续 A-hop 预期）**；"
    "B naive **598_301..598_500 CLEAN（hops=0）但落投影 A 窗 598_101..600_100 内**（W265p_B_lands_inside_W265p_A_naive=true——"
    "**staircase face 延续**：W264 A 596_101..598_100+B 598_101..598_300 注册后 naive W265 A 窗起点即被注册 W264 B 带拒（staircase affects A 承袭·第十四次连续 A-hop 预期）"
    "→A first-clean 将上移·B own-A reservation cascade 落位相应上移——post-W264 宇宙 live re-derive 必变·禁转录投影）；"
    "**W265 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace**"
    "（W251 起 staircase affects A·W252/W253/W254/W255/W256/W257/W258/W259/W260/W261/W262/W263/W264=A/B 双 1-hop 形态连续十三波如实注记·seed-gap face 已于 W252 终结=A 首跳如实注记）"
    "——W265 冻结方必须在 post-W264 注册宇宙重 derive 且 derive B 时预留本波 A 窗 596_101..598_100+本波 B 带 598_101..598_300"
    "——leg2 律/E36 卡·W141 先例；verify at W265 prereg，hop 链逐跳在 probe 回执。"
)

NEW["b_gated"] = (
    "本件=席位窗后首窗冻结件；五面冻结拼接脚本 results/_w264bmc_freeze_edits.py"
    "（按 _w263bma_freeze_edits.py 模板派生·gate0.5 自查 W263 行+W263 finalize 件在场=已绿·未落即 loud abort 兜底）"
    "=**splice 执行窗派生落地（r1037/r1038 W263 先例实时间线：prereg b32f6bf1c 落于席位窗 r1037·splice f499817fa 落于执行窗 r1038——"
    "**W264 freeze 面：W263 own-wave finalize 已落地=席位时即解锁——席位+prereg 本窗落地 per seat-first law O-20261010-2350 §2·"
    "splice 执行窗开门（gate0.5 绿·编辑器 loud abort 兜底）**。"
)

# marker pairs: (block, start_marker, end_marker) -- needles matched on T1 (post-roll faces)
BLOCKS = [
    ("b_title", "engine_owner 行 252 注册在册（表尾", "后下窗归属=W264）**】）"),
    ("b_prev", "prev=**届时空窗活链头 derive 禁手抄**", "（机械算·投影面仅披露·finalize 运行时按 registry 键 derive 免疫）。"),
    ("b_band", "（**A 面=STAIRCASE-AFFECTS-A", "（见 §5 item5）。"),
    ("b3_a", "entry rng seed=**593_901+j**", "；p=`BASELINE_P"),
    ("b3_b", "exit rng=**595_901+j**", "；p_exit=`P_EXIT=0.05`"),
    ("b_claim_proj", "probe W264+ 投影 A naive 595_901..597_900 CLEAN hops=0", "never transcribe r587**）"),
    ("b5_projection", "5. **W264+ 投影（probe 机证 leg4", "verify at W264 prereg，hop 链逐跳在 probe 回执。"),
    ("b_gated", "本件=席位窗冻结件；五面冻结拼接脚本", "（gate0.5 未绿前禁 splice·编辑器 loud abort 兜底）**。"),
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
    "PERPETUAL-N1-W264", "research/PERPETUAL_N1_W264_PREREG.md",
    "596_101..598_100", "598_101..598_300", "578,720", "1,002,935", "576,520",
    "n1_w264_results.json", "MSG-20261017-1950-bmc-w264-seat", "dd5fd438e",
    "池第 262 枚", "第八十三枚", "第 254 波", "第 83 枚",
    "STAIRCASE-AFFECTS-A", "第十三次连续 A-hop", "第十四次连续 above-own-A",
    "_w264bmc_20261017", "--wave 264/finalize --wave 264",
    "W263 finalize one-pass bm-a r1039", "n_eff_held_equal 996,335",
    "−0.09275356", "0.24503704", "−0.09496455", "（**0.3208** 实测锚）",
    "键 W263 实测 K-lift **0.0000**", "line_merged@K576,520 **1.1953**", "line_pre_w263 1.1953",
    "实差 0.0022 在带内", "共二百六十一面实测", "W2..W263",
    "engine_owner==bm-c 82 行注册", "engine_owner 行 253 注册在册",
    "probe leg0 bmc_rows=82 attempt-continuity face（r1075 窗算法·bm-c own seat+bmc live rows 82 实读）",
    "bm-c 循环班 r1075 席位窗", "本窗 free RAM ~7GB", "本机 bm-c 实例",
    "W264=bm-c own-wave window per chain-order law",
    "f499817fa", "355c716b7", "91da16c86", "b32f6bf1c",
    "W265+ 投影", "W265p_B_lands_inside_W265p_A_naive", "verify at W265 prereg",
    "_w264bmc_freeze_edits.py", "_w263bma_freeze_edits.py 模板派生",
    "bm-a r1039 W263 §7 范式", "bm-a r1039 W263 §8 范式",
    "（W263 注册+烧录+finalize 全落地）",
    "W206/W211..W263 低 RAM 实烧先例", "W263 冻结窗 26G bm-a 实锚",
    "席位时即解锁", "（见 §5 item5）。", "R265：W264 带",
    "→W260 **0.000325**→W261 **0.000324**→W262 **0.000323**→W263 **0.000323**→W264 投影 0.000323】",
    "596_100+1", "598_100+1",
    "A_staircase_hop_past_W263_B=true", "B_lands_above_own_A=true",
    "seed_admit_gate rc0 双带 FREE",
    "波号 264", "零 264 行", "零 skip-ahead W265/W266 席位声明",
]
for s in MUST:
    assert s in T2, "MUST-HAVE missing: %r" % s

MUST_NOT = [
    "A-ext seed=593_901", "B-ext exit seed=595_901",
    "593_901..595_900", "595_901..596_100 CLEAN", "593_701..595_700",
    "GATED on", "finalize PENDING", "pending 投影 derive",
    "572,120", "998,535", "**576,520 投影**", "line_merged@K572,120",
    "−0.09273607", "0.24503320", "−0.09411977", "**0.2994**", "实差 0.0014 在带内",
    "14:1x", "15:5x", "17:4x", "queue_depth",
    "fb0c962b5", "MSG-20261017-1740", "e1a94b335", "32d28ffb3", "06dcd6c23", "b83318440",
    "bma rows 129", "bma_rows=129", "第 130 枚", "第一百三十枚", "第 253 波",
    "engine_owner==bm-a 129", "engine_owner==bm-a 波",
    "r1037 席位窗实跑", "r1037 窗算法", "bm-a r1037 席",
    "本窗 free RAM ~26GB", "94G 物理内存机", "CEO 周末用机态", "35B:8090",
    "本件=席位窗冻结件", "（bm-a r1035 席",
    "line_pre_w261", "键 W261 实测 K-lift", "键 W262 实测 K-lift",
    "W264p_B_lands_inside_W264p_A_naive", "verify at W264 prereg",
    "W264+ 投影", "W263p_",
    "第 261 枚", "第十二次连续 A-hop", "第十三次连续 above-own-A",
    "_w263bma_20261017",
]
for s in MUST_NOT:
    assert s not in T2, "MUST-NOT-HAVE present: %r (count=%d)" % (s, T2.count(s))

# pinned count gates
assert T2.count("W265+ 投影") == 3, "W265+ 投影 count=%d (expect 3 = b5 title + b6 claim + sec8 rolled)" % T2.count("W265+ 投影")
assert T2.count("W264+ 投影") == 0, "W264+ 投影 count=%d (expect 0)" % T2.count("W264+ 投影")
assert T2.count("hops=1") == 2, "hops=1 count=%d (expect 2 = 带位 A + §3 A)" % T2.count("hops=1")
assert T2.count("hops=0") == 5, "hops=0 count=%d (expect 5 = b5 x2 + b6 x3)" % T2.count("hops=0")
assert T2.count("第十三次连续 A-hop") == 3, "第十三次连续 A-hop count=%d (expect 3 = b_band x2 + b3_a x1)" % T2.count("第十三次连续 A-hop")
assert T2.count("第十四次连续 A-hop") == 3, "第十四次连续 A-hop count=%d (expect 3 = b5 x2 + b6 x1)" % T2.count("第十四次连续 A-hop")
assert T2.count("第十四次连续 above-own-A") == 2, "第十四次连续 above-own-A count=%d (expect 2 = b_band + b3_b)" % T2.count("第十四次连续 above-own-A")
assert T2.count("连续十三波") == 1, "连续十三波 count=%d (expect 1 = b5 NEW)" % T2.count("连续十三波")
assert T2.count("596_101..598_100") >= 5, "596_101..598_100 count=%d (expect >=5)" % T2.count("596_101..598_100")
assert T2.count("598_101..598_300") >= 4, "598_101..598_300 count=%d (expect >=4)" % T2.count("598_101..598_300")
assert T2.count("598_101..600_100") == 5, "598_101..600_100 count=%d (expect 5 = b6 x3 + b5 x2)" % T2.count("598_101..600_100")
assert T2.count("席位时即解锁") == 2, "席位时即解锁 count=%d (expect 2 = final line + b_gated)" % T2.count("席位时即解锁")

# residue scan: all X_Y..X_Y windows well-formed
for m in re.finditer(r"(\d{3}_\d{3})\.\.(\d{3}_\d{3})", T2):
    lo = int(m.group(1).replace("_", "")); hi = int(m.group(2).replace("_", ""))
    assert lo <= hi, "malformed window %s" % m.group(0)

io.open(OUT, "w", encoding="utf-8", newline="").write(T2)
print("W264 PREREG DERIVE OK -> %s (%d bytes, %d lines)" % (OUT, len(T2.encode("utf-8")), T2.count("\n") + 1))
print("splice commit face: f499817fa @ " + SPLICE_T)
print("blocks replaced: %s" % ", ".join(n for n, _, _ in BLOCKS))
print("vmap legs: %d floors: %d post-legs: %d MUST: %d MUST_NOT: %d" % (
    len(VMAP), len(VMAP_FLOORS), len(VMAP_POST_LEGS), len(MUST), len(MUST_NOT)))
print("src blob-verified == 4b6f791dd50f085738292257a40f7b1c408411e0 @ b32f6bf1c (frozen pre-run face; HEAD post-backfill twin 56cdbd337 disclosed, NOT used)")
print("out sha256_16: %s" % hashlib.sha256(T2.encode("utf-8")).hexdigest()[:16])
