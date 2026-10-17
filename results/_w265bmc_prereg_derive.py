# -*- coding: utf-8 -*-
# r1080 bm-c: W265 prereg derive (count-asserted ordered transform + marker-extracted block replaces).
# Canon-clone of _w264bmc_prereg_derive.py per age() machine-needle law (shift-map one generation).
# Source = committed frozen W264 prereg AT THE FREEZE COMMIT f4ffdb34e (git f4ffdb34e:research/PERPETUAL_N1_W264_PREREG.md,
# 22,819 bytes -- the frozen pre-run face; sec7/8 placeholders intact). Extracted to
# results/_w265bmc_w264_frozen_face.txt by the dead 02:03 prep window; byte-verified THIS window:
# disk==blob sha1 2ba4dbc1e1947ffa0ef7f5c0850bed73cc432277, sha256_16 4bf4079f686ab859.
# TEMPLATE-FACE DISCLOSURE (r1052/r1049 law): HEAD twin 96c037c4146ba1c4020604f6745961d47cf3d2db = the
# CURRENT HEAD face = the POST-CYCLE face with sec.7/8 BACKFILLED by the dead r1077 W264 cycle (estate
# landed via 7343e3650). Deriving from the backfilled face would fabricate W265 sec.7/8 from W264's
# measured numbers -- the r1049/r1052 precedent requires the f4ffdb34e frozen pre-run face.
# W265 facts (all machine-derived, never transcribed):
#   - seat probe ADMIT receipt results/_w265bmc_20261017_probe_receipt.json (bm-c r1077 dead-window cycle,
#     seat rides origin 7343e3650 per r565 early-visibility law, MSG-20261017-2241-bmc-w265-seat landed,
#     swept processed). STAIRCASE CONTINUES: A naive 598_101..600_100 REFUSED at start (registered W264 B
#     band 598_101..598_300 sits INSIDE the naive A window) -> A first-clean 598_301..600_300 hops=1
#     (FOURTEENTH consecutive A-hop, W264 prereg sec.5 item5 post-W264-REGISTERED pre-disclosure confirmed
#     live per r587, ZERO divergence) / B naive 598_301..598_500 REFUSED at start (lands INSIDE the
#     own-wave W265 A first-clean window 598_301..600_300) -> own-A reservation cascade hop past 600_300
#     -> 600_301..600_500 hops=1 (FIFTEENTH consecutive above-own-A landing); seed_admit FREE x2
#     (A base=598301 span=2000 / B base=600301 span=200); leg0 rows=262 owner_rows=254 bmc_rows=83
#     ordinal=255; leg2 conflicts=0; leg3 origin_vacancy=true; leg4 W266+ projection: A naive
#     600_301..602_300 CLEAN hops=0 pre-W265 universe BUT post-W265-REGISTERED the naive W266 A start
#     600_301 is REFUSED by the registered W265 B band 600_301..600_500 (FIFTEENTH consecutive A-hop
#     expected) AND the W266 B naive 600_501..600_700 lands inside the own-A reservation face.
#   - upstream W264 finalize LANDED (bm-c dead r1077 window one-pass, n1_w264_results.json generated
#     2026-10-17 22:37:45, estate landed via 7343e3650 22:43:34): merged K=578,720 / ledger 1,005,135
#     EXACT (1,002,935+2,200) / merged mu -0.09272765534282555 (8dp -0.09272766) / sigma
#     0.2450429696990889 (8dp 0.24504297) / se_mu@K578,720 0.000322 / W264-only mu
#     -0.08593818181818182 (8dp -0.08593818) / A p95 0.3046 / K-lift +0.0001 (first positive micro-move)
#     / n_eff_held 1,002,935 / line_pre_w264 1.1954 / line_merged@578,720 1.1955 / own-slice vs merged
#     gap 0.0067894735 in-band<0.02 (fivekeys 6/6 ALL PASS receipt results/_r1077bmc_w264_fivekeys.json
#     + sixgate PRE-FINALIZE ALL PASS 26th consecutive receipt results/_r1076bmc_w264_sixgate.json;
#     splice 216b578b0 21:21:08; engine self-burn 12/12 ledger appends 964148797 21:02:30 + 17dd06323
#     21:06:18 batched self-commits).
# Needle-count pre-flight evidence: results/_w265bmc_needle_counts.txt (this window, measured live on T0;
# floors below match every VMAP_FLOORS entry, divergences disclosed in header comments as same-window
# needle heals). Same-window needle heals disclosed:
# (1) finalize-window stamp roll 19:2x->22:3x (W263 finalize -> W264 finalize two-wave anchor jump; the
#     four T0 faces include two block-interior copies discarded by block replacement);
# (2) se_mu chain true-history correction (pre-authored consumed-label form per r1059 canon-embed advice):
#     the rolled chain carries W261 0.000325 (FALSE -- W261 measured 0.000324 per the W264-prereg frozen
#     chain) -> POST_LEG rewrites the tail with true history W261 **0.000324** / W262 **0.000323** /
#     W263 **0.000323** / W264 **0.000322** (W264 measured per n1_w264_results se_mu_at_k578720) and
#     appends the W265 projection 0.000322;
# (3) RAM face honest update: prior face "~7GB CEO gaming yield 让路态（MV 重烧在飞合法占用）" -> THIS window
#     live-measures ~3GB (psutil 2.83GB free 03:1x, bm-c 24G chassis) with GPU gen-only lane idle face
#     (nvidia-smi 3% util / 3.2G VRAM resident / POOL-0016 candidate frozen) -- CEO weekend-use machine
#     state, LLM face retired per O-20261017-0953;
# (4) K-lift POST_LEG: post-roll form carries "键 W263 实测 K-lift **0.0000**" -- corrected to the true
#     anchor "键 W264 实测 K-lift **0.0001**" (line_delta_k_lift=0.0001 per _r1077bmc_w264_fivekeys, first
#     positive micro-move disclosed);
# (5) low-RAM precedent ledger append: W264 freeze-window anchor 7G bm-c appended via POST_LEG (chain
#     precedent every-wave append, W262-derive b6_ram paradigm; the wave-roll had shifted the W263 26G
#     bm-a anchor onto the W264 label -- restored + true W264 anchor appended);
# (6) n_eff_held_equal 996,335 carried verbatim per W263/W264 derive precedent (static precedent-chain
#     face; the live n_eff anchors are machine-verified from receipts in the gates below).
import io, os, sys, datetime, subprocess, hashlib, re, json

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w265bmc_w264_frozen_face.txt")
OUT = os.path.join(REPO, "research", "PERPETUAL_N1_W265_PREREG.md")
GIT = "C:/Program Files/Git/cmd/git.exe"


def git_out(args):
    r = subprocess.run([GIT] + args, capture_output=True, cwd=REPO)
    if r.returncode != 0:
        raise SystemExit("git fail %r: %s" % (args, r.stderr.decode("utf-8", "replace")))
    return r.stdout.decode("utf-8", "replace").strip()


# --- source byte-identity gates ---
_blob_expect = "2ba4dbc1e1947ffa0ef7f5c0850bed73cc432277"   # freeze-commit face @ f4ffdb34e
_ho = git_out(["hash-object", SRC])
assert _ho == _blob_expect, "SRC blob mismatch: got %s expect %s" % (_ho, _blob_expect)
_fc = git_out(["rev-parse", "f4ffdb34e:research/PERPETUAL_N1_W264_PREREG.md"])
assert _fc == _blob_expect, "freeze-commit blob mismatch: %s" % _fc
_hb = git_out(["rev-parse", "HEAD:research/PERPETUAL_N1_W264_PREREG.md"])
assert _hb == "96c037c4146ba1c4020604f6745961d47cf3d2db", "HEAD tpl twin face drifted: %s" % _hb

T0 = io.open(SRC, encoding="utf-8", newline="").read()
assert len(T0.encode("utf-8")) == 22819, "SRC size drift: %d" % len(T0.encode("utf-8"))
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "4bf4079f686ab859", "SRC sha mismatch"

# --- chain-fact existence gates (zero transcription) ---
for sha in ("f4ffdb34e", "216b578b0", "964148797", "17dd06323", "7343e3650", "dd5fd438e"):
    git_out(["cat-file", "-e", sha + "^{commit}"])
_ci = git_out(["show", "-s", "--format=%ci", "216b578b0"])   # 2026-10-17 21:21:08 +0800
_m = re.match(r"2026-10-17 (\d{2}):(\d{2})", _ci)
assert _m, "splice commit ts unexpected: %r" % _ci
SPLICE_T = "%s:%sx" % (_m.group(1), _m.group(2)[0])           # 21:2x

# --- finalize-anchor machine-verify gates (fivekeys receipt + results json, live) ---
with open(os.path.join(REPO, "results", "_r1077bmc_w264_fivekeys.json"), encoding="utf-8") as f:
    fk = json.load(f)
assert round(fk["merged"]["mu"], 8) == -0.09272766, "merged mu drift: %r" % fk["merged"]["mu"]
assert round(fk["merged"]["sigma"], 8) == 0.24504297, "sigma drift: %r" % fk["merged"]["sigma"]
assert round(fk["merged"]["se_mu_k578720"], 6) == 0.000322, "se_mu drift: %r" % fk["merged"]["se_mu_k578720"]
assert round(fk["w264_only"]["mu"], 8) == -0.08593818, "w264-only mu drift: %r" % fk["w264_only"]["mu"]
assert round(fk["a_band"]["full_sharpe_p95"], 4) == 0.3046, "p95 drift: %r" % fk["a_band"]["full_sharpe_p95"]
assert round(fk["skill_line"]["k_lift_delta"], 4) == 0.0001, "k-lift drift: %r" % fk["skill_line"]["k_lift_delta"]
assert fk["skill_line"]["n_eff_held"] == 1002935, "n_eff_held drift: %r" % fk["skill_line"]["n_eff_held"]
assert fk["merged"]["k"] == 578720, "K drift: %r" % fk["merged"]["k"]
assert fk["ledger_identity"]["total"] == 1005135 and fk["ledger_identity"]["exact"], "ledger identity drift"
with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w264_results.json"), encoding="utf-8") as f:
    res = json.load(f)
assert res["skill_line_v2_k_lift"]["n_eff_held_equal"] == 1002935
assert round(res["skill_line_v2_k_lift"]["line_pre_w264"], 4) == 1.1954
assert round(res["skill_line_v2_k_lift"]["line_merged_578720"], 4) == 1.1955
assert round(res["null_pool_cumulative"]["se_mu_at_k578720"], 6) == 0.000322
with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w263_results.json"), encoding="utf-8") as f:
    res3 = json.load(f)
assert round(res3["null_pool_cumulative"]["se_mu_at_k576520"], 6) == 0.000323, "W263 se_mu heal verify"
with open(os.path.join(REPO, "results", "_w265bmc_20261017_probe_receipt.json"), encoding="utf-8") as f:
    pr = json.load(f)
assert pr["verdict"] == "ADMIT"
assert pr["bands"]["A"] == [598301, 600300] and pr["bands"]["B"] == [600301, 600500]
assert pr["legs"]["leg1"]["hops_A"] == 1 and pr["legs"]["leg1"]["hops_B"] == 1
assert pr["legs"]["leg0"]["owner_rows"] == 254 and pr["legs"]["leg0"]["bmc_rows"] == 83
assert pr["legs"]["leg0"]["ordinal"] == 255

P1, P2, P3 = "\x01W\x01", "\x01N\x01", "\x01B\x01"

VMAP = [
    # ---- explicit wave-free legs BEFORE the wave rolls (compound needles first) ----
    ("A-ext seed=596_101..598_100", "A-ext seed=598_301..600_300"),
    ("B-ext exit seed=598_101..598_300", "B-ext exit seed=600_301..600_500"),
    ("entry rng=**596_101+j**（与 A[j] 同源配对语义逐字", "entry rng=**598_301+j**（与 A[j] 同源配对语义逐字"),
    # seat/provenance faces (W265 seat published bm-c r1077 dead-window cycle, rides origin 7343e3650)
    ("席位公示=MSG-20261017-1950-bmc-w264-seat 已推 origin dd5fd438e r565 律（bm-c r1075 席·queue-head seat-first lane）",
     "席位公示=MSG-20261017-2241-bmc-w265-seat 已推 origin 7343e3650 r565 律（bm-c r1077 席·queue-head seat-first lane）"),
    ("席位公示 MSG-20261017-1950-bmc-w264-seat 先推 origin dd5fd438e r565 律",
     "席位公示 MSG-20261017-2241-bmc-w265-seat 先推 origin 7343e3650 r565 律"),
    # wave-number + vacancy faces
    ("波号 264", "波号 265"),
    ("r1075 席位窗实跑：origin inbox 零 W264 席位外机命中", "r1077 席位窗实跑：origin inbox 零 W265 席位外机命中"),
    ("零 264 行", "零 265 行"),
    ("零 skip-ahead W265/W266 席位声明", "零 skip-ahead W266/W267 席位声明"),
    ("池第 262 枚", "池第 263 枚"),
    # ordinals + own-wave faces
    ("第 254 波", "第 255 波"),
    ("bm-c 第八十三枚自有波", "bm-c 第八十四枚自有波"),
    ("probe leg0 bmc_rows=82 attempt-continuity face（r1075 窗算法·bm-c own seat+bmc live rows 82 实读）——freeze 时 live derive bmc rows 82+候选=第 83 枚 EXACT",
     "probe leg0 bmc_rows=83 attempt-continuity face（r1077 窗算法·bm-c own seat+bmc live rows 83 实读）——freeze 时 live derive bmc rows 83+候选=第 84 枚 EXACT"),
    ("engine_owner==bm-c 82 行注册", "engine_owner==bm-c 83 行注册"),
    # engine live-read faces (bm-c instance, r1080 window)
    ("saturation_engine.py status live-read r1076：burns_active=[] queue_next=[] 实读·heartbeat 新鲜",
     "saturation_engine.py status live-read r1080：burns_active=[] queue_next=[] 实读·heartbeat 新鲜"),
    ("本机 bm-c 实例·heartbeat 新鲜实读 r1076 窗·队列空转 idle", "本机 bm-c 实例·heartbeat 新鲜实读 r1080 窗·队列空转 idle"),
    ("引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1076 窗实读", "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1080 窗实读"),
    # RAM face honest update (live-measured THIS window ~3GB, GPU gen-only lane idle)
    ("本窗 free RAM ~7GB（bm-c 底盘常驻·24G 物理内存机·CEO gaming yield 让路态·GPU=gen-only 车道（MV 重烧在飞合法占用）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）",
     "本窗 free RAM ~3GB（bm-c 底盘常驻·24G 物理内存机·CEO 周末用机态·GPU=gen-only 车道空窗（nvidia-smi 实读 3%·3.2G VRAM 常驻·POOL-0016 候件冻结态）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）"),
    # runner CLI wave
    ("--wave 264/finalize --wave 264", "--wave 265/finalize --wave 265"),
    # sec8 placeholder projection-label bump (W266+ face)
    ("§5.5 W265+ 投影承接机证", "§5.5 W266+ 投影承接机证"),
    # ---- lowercase chained rolls (result/script faces) ----
    ("n1_w264", P2), ("n1_w263", "n1_w264"), (P2, "n1_w265"),
    ("_w264bmc", P3), ("_w263bma", "_w264bmc"), (P3, "_w265bmc"),
    # ---- wave-number roll (chained placeholders) ----
    ("W264", P1), ("W263", "W264"), ("W262", "W263"), ("W261", "W262"), ("W260", "W261"), ("W259", "W260"),
    ("W258", "W259"), ("W257", "W258"), ("W256", "W257"), ("W255", "W256"), (P1, "W265"),
]

VMAP_FLOORS = {
    "A-ext seed=596_101..598_100": 1,
    "B-ext exit seed=598_101..598_300": 1,
    "entry rng=**596_101+j**（与 A[j] 同源配对语义逐字": 1,
    "席位公示=MSG-20261017-1950-bmc-w264-seat 已推 origin dd5fd438e r565 律（bm-c r1075 席·queue-head seat-first lane）": 1,
    "席位公示 MSG-20261017-1950-bmc-w264-seat 先推 origin dd5fd438e r565 律": 1,
    "波号 264": 1,
    "r1075 席位窗实跑：origin inbox 零 W264 席位外机命中": 1,
    "零 264 行": 1,
    "零 skip-ahead W265/W266 席位声明": 1,
    "池第 262 枚": 1,
    "第 254 波": 1,
    "bm-c 第八十三枚自有波": 1,
    "probe leg0 bmc_rows=82 attempt-continuity face（r1075 窗算法·bm-c own seat+bmc live rows 82 实读）——freeze 时 live derive bmc rows 82+候选=第 83 枚 EXACT": 1,
    "engine_owner==bm-c 82 行注册": 1,
    "engine_owner==bm-c 波的未烧分片": 1,
    "saturation_engine.py status live-read r1076：burns_active=[] queue_next=[] 实读·heartbeat 新鲜": 1,
    "本机 bm-c 实例·heartbeat 新鲜实读 r1076 窗·队列空转 idle": 1,
    "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1076 窗实读": 1,
    "本窗 free RAM ~7GB（bm-c 底盘常驻·24G 物理内存机·CEO gaming yield 让路态·GPU=gen-only 车道（MV 重烧在飞合法占用）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）": 1,
    "--wave 264/finalize --wave 264": 1,
    "§5.5 W265+ 投影承接机证": 1,
    "n1_w264": 4, "n1_w263": 6, "_w264bmc": 4, "_w263bma": 1,
    # measured live on T0 (results/_w265bmc_needle_counts.txt; r1081 re-measure backs this face --
    # dead r1080 window authored floors but died pre-evidence; heal (7) r1081: "W259" 2->1 live-audit
    # correction [pattern-assumed floor; T0 holds 1 occurrence; chained roll consumes it; zero content
    # impact -- output still fully gated by MUST/MUST_NOT/pinned-counts below])
    "W264": 35, "W263": 63, "W262": 3, "W261": 2, "W260": 2, "W259": 1,
    "W258": 1, "W257": 1, "W256": 1, "W255": 1,
    # block-marker stability floors (raw template face)
    "engine_owner 行 253 注册在册（表尾": 1,
    "prev=**届时空窗活链头 derive 禁手抄**": 1,
    "（**A 面=STAIRCASE-AFFECTS-A": 1,
    "entry rng seed=**596_101+j**": 1,
    "exit rng=**598_101+j**": 1,
    "probe W265+ 投影 A naive 598_101..600_100 CLEAN hops=0": 1,
    "5. **W265+ 投影（probe 机证 leg4": 1,
    "本件=席位窗后首窗冻结件；五面冻结拼接脚本": 1,
    "（gate0.5 绿·编辑器 loud abort 兜底）**。": 1,
    # zero-floors (absence assertions on T0)
    "waits-upstream ARMED": 0,
    "1,005,135": 0, "598_301..600_300": 0, "600_301..600_500": 0,
    "−0.09272766": 0, "0.24504297": 0, "−0.08593818": 0, "0.3046": 0,
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
        raise SystemExit("VMAP FLOOR FAIL: %r count=%d floor=%d" % (o, c))

T1 = xf(T0)

# ---------------- post-roll correction legs (needles exist only in T1 after the rolls) ----------------
VMAP_POST_LEGS = [
    # finalize-window stamp roll (heal (1)): W264 finalize one-pass landed 22:3x (n1_w264_results
    # generated 22:37:45); T0 carried the W263 19:2x stamps (two block-interior copies discarded later)
    ("19:2x", "22:3x", 2),
    # sec.5 item1 measured keys -> W264 actuals (n1_w264_results + fivekeys machine values)
    ("（W264 实测键 **−0.09275356**·K=576,520 合并池·W264-only 实测 **−0.09496455**）",
     "（W264 实测键 **−0.09272766**·K=578,720 合并池·W264-only 实测 **−0.08593818**）", 1),
    ("W2..W264 共二百六十一面实测 mu 稳定先例", "W2..W264 共二百六十三面实测 mu 稳定先例", 1),
    ("W264-only vs merged 实差 0.0022 在带内", "W264-only vs merged 实差 0.0068 在带内", 1),
    # sec.5 item2 sigma key
    ("键 **0.24503704**=W264 合并池实测", "键 **0.24504297**=W264 合并池实测", 1),
    # sec.5 item3 p95 anchor
    ("与 W264 A 档 p95（**0.3208** 实测锚）", "与 W264 A 档 p95（**0.3046** 实测锚）", 1),
    # sec.5 item4 K-lift chain + line faces (heal (4): true W264 K-lift +0.0001 first positive move)
    ("键 W264 实测 K-lift **0.0000**·line_merged@K576,520 **1.1953**·line_pre_w263 1.1953·n_eff_held_equal 996,335",
     "键 W264 实测 K-lift **0.0001**·line_merged@K578,720 **1.1955**·line_pre_w264 1.1954·n_eff_held_equal 996,335", 1),
    ("→W261 **0.000325**→W262 **0.000324**→W263 **0.000323**→W264 **0.000323**→W265 投影 0.000323】",
     "→W261 **0.000324**→W262 **0.000323**→W263 **0.000323**→W264 **0.000322**→W265 投影 0.000322】", 1),
    # sec.4 merged-pool anchor face (W264 finalize landed)
    ("（起草窗实流 W1..W264 已落账 576,520 实测〔n1_w264_results.json 机读·W264 finalize 已落〕）",
     "（起草窗实流 W1..W264 已落账 578,720 实测〔n1_w264_results.json 机读·W264 finalize 已落〕）", 1),
    # r1081 heal (8): REMOVED duplicate K-face leg ("·K=576,520 合并池·W264-only 实测" -> 578,720) --
    # blanket-duplication defect (W255-gen disclosed family): the parenthetical leg above ALREADY
    # consumed the only "合并池·W-only 实测" occurrence in T0 (verified: T0 grep count=1, inside the
    # §5 item1 parenthetical); the standalone needle could never match post-leg-2 (count=0 fail-closed
    # as designed). W264-gen canon has NO such standalone leg. Zero content impact: K=578,720 lands
    # via the parenthetical leg; MUST "578,720" + MUST_NOT "576,520" both enforce.
    # sec.7/8 backfill paradigm rows -> the W264 cycle (bm-c r1077)
    ("bm-a r1039 W264 §7 范式", "bm-c r1077 W264 §7 范式", 1),
    ("bm-a r1039 W264 §8 范式", "bm-c r1077 W264 §8 范式", 1),
    # low-RAM precedent ledger append (heal (5)): W264 freeze-window 7G bm-c anchor
    # (the wave-roll shifted the W263 26G bm-a anchor onto the W264 label -- restore + append true face)
    ("·W244 冻结窗 41.9G bm-a 实锚·W264 冻结窗 26G bm-a 实锚）",
     "·W244 冻结窗 41.9G bm-a 实锚·W263 冻结窗 26G bm-a 实锚·W264 冻结窗 7G bm-c 实锚）", 1),
]

for o, n, f in VMAP_POST_LEGS:
    c = T1.count(o)
    if c < f:
        raise SystemExit("VMAP POST FLOOR FAIL: %r count=%d floor=%d" % (o, c, f))
    T1 = T1.replace(o, n)

# ---------------- block replacements (needles marker-matched on T1; NEW = final) ----------------
NEW = {}

NEW["b_title"] = (
    "engine_owner 行 254 注册在册（表尾 W264 行【bm-c r1076 五面冻结 splice 216b578b0 落地 @@SPLICE_T@@·selftest 9/9】"
    "+引擎自燃 12/12 分片已落【results/p2cal_ext/n1_w264/ 12/12·ledger append 964148797+17dd06323】"
    "·**W264 finalize 已落地**【n1_w264_results.json 机读·净账本锚头 1,005,135·K=578,720 合并池·W264 finalize one-pass bm-c r1077 窗 22:3x·estate absorb r1077 7343e3650】）"
    "+本候选=bm-c 自有席自有波【live-derive face：席面 own-seat face（bm-c r1077 席位 MSG-20261017-2241-bmc-w265-seat 已推 origin 7343e3650"
    "·probe receipt _w265bmc_20261017 机证·bands ADMIT verbatim·queue-head seat-first lane）"
    "→freeze 时 live derive bmc rows 83+候选=第 84 枚 EXACT·以 freeze 时 live derive 为准 r587/r359】"
    "【bm-c 循环班 r1077 席位窗 2026-10-17 22:4x·CEO 填载令 standing+2026-10-10 ~23:1x RE-ISSUE+O-20261013-2215 CPU 常开令"
    "·**W265=bm-c own-wave window per chain-order law（W263 bm-a→W264 bm-c→W265 bm-c own-turn rotation·bm-a 席 r1042/r1043 明让 bm-c·MSG-2241 owner per chain-order law）**】】）"
)

NEW["b_prev"] = (
    "prev=**届时空窗活链头 derive 禁手抄**——起稿窗实况（**锚滚链面 r576/r590 律**）："
    "**W1..W264 N1 注册全部落地**【W264=注册+12/12 分片已烧·**finalize 已落地**——最新已 finalize 锚=**W264**"
    "【净账本锚头 **1,005,135**·K=578,720 合并池·n1_w264_results.json 机读·W264 finalize one-pass bm-c r1077 窗 22:3x】】；"
    "**零在飞上游席——「零在飞上游链前」断言适用且干净前置成立**（上游 W264 席位已闭链=注册+烧录+finalize 全落地·零在飞）；"
    "finalize 键序前置=届时按 registry 键 derive 复核 FAIL-CLOSED r307 两态例恒在；"
    "累计 null 池=578,720+2,200（本波）=**580,920 投影**（机械算·投影面仅披露·finalize 运行时按 registry 键 derive 免疫）。"
)

NEW["b_band"] = (
    "（**A 面=STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第十四次连续 A-hop）**："
    "A 面算术续带 598_101..600_100（自注册 W264 A 尾 598_100 续）"
    "在席位窗宇宙（post-W264-REGISTERED 终态注册）起点即 REFUSED"
    "（注册 W264 B 带 598_101..598_300 落 naive A 窗内=staircase re-emergence affects A 承袭"
    "·W264 prereg §5 item5 post-W264-REGISTERED pre-disclosure 兑现 r587 如实披露）"
    "→walk 越注册 W264 B 尾 598_300→A first-clean **598_301..600_300**·**hops=1**·"
    "**A 落位 base==注册前波 B 尾+1（598_300+1）机检关系**"
    "（A_hop_chain 1 跳 verbatim leg1 机证〔window 598_101..600_100→jump 598_301·refuser band 598_101..598_300〕"
    "·A_clean_at_naive_start=false·A_staircase_hop_past_W264_B=true"
    "·A base>=registered prior-wave B tail+1 floor relation）·非转录 r587 前向单调断言在走册）；"
    "**B-ext exit seed=600_301..600_500**（**B 面=1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态（第十五次连续 above-own-A 落位）**："
    "B naive 续带 598_301..598_500（自注册 W264 B 尾 598_300+1 续）"
    "在席位窗宇宙（post-W264-REGISTERED 终态注册）起点即 REFUSED"
    "（naive B 窗 598_301..598_500 落本波 A first-clean 窗 598_301..600_300 内"
    "=own-A reservation cascade standard leg 强制·probe leg1 B_semantics 机证·B_naive_refused_at_start=true）"
    "——**own-A reservation standard leg 越本波 A 窗 598_301..600_300**（1 hop）"
    "→**1 hop** 落位 **600_301..600_500**·**B 落位 base==本波 A 窗尾+1（600_300+1）EXACT 机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执 leg1 机证"
    "·非转录 r587·AB 同窗互斥面 leg2 律在场）；"
    "**W264 prereg §5 item5 投影承接面注记兑现+落位一致如面**："
    "投影预言 W265 A naive 598_101..600_100 将被注册 W264 B 带拒（staircase affects A 承袭·第十四次连续 A-hop）"
    "与 B own-A reservation cascade 上移——本窗 live re-derive 与投影完全一致（零分歧如实注记·禁转录投影 r587 面在场）。"
    "R266：W265 带（A 598_301..600_300/B 600_301..600_500）注册后对 W266+ 的拒面影响=W265 冻结方 leg4 前瞻已机证（见 §5 item5）。"
)

NEW["b3_a"] = (
    "entry rng seed=**598_301+j**（法典 §4 W265 行 A=598_301..600_300·"
    "**STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第十四次连续 A-hop）**："
    "A 算术续带 598_101..600_100（自注册 W264 A 尾 598_100 续）"
    "在席位窗宇宙（post-W264-REGISTERED 终态注册）起点即 REFUSED"
    "（注册 W264 B 带 598_101..598_300 落 naive A 窗内=W264 prereg §5 item5 post-W264-REGISTERED pre-disclosure 兑现·r587 承袭披露）"
    "→walk 越注册 W264 B 尾 598_300→A first-clean 598_301..600_300·**hops=1**·"
    "**A 落位 base==注册前波 B 尾+1（598_300+1）机检关系**"
    "（A_hop_chain 1 跳 verbatim probe leg1 机证·A_clean_at_naive_start=false·A_staircase_hop_past_W264_B=true）"
    "·非转录 r587·ADMIT 回执在场）；p=`BASELINE_P"
)

NEW["b3_b"] = (
    "exit rng=**600_301+j**（法典 §4 W265 行 B=600_301..600_500·"
    "**1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态**："
    "B naive 续带 598_301..598_500（自注册 W264 B 尾 598_300+1 续）"
    "在席位窗宇宙（post-W264-REGISTERED 终态注册）起点即 REFUSED"
    "（naive B 窗落本波 A first-clean 窗 598_301..600_300 内=own-A reservation cascade standard leg·probe leg1 B_semantics 机证）"
    "→own-A reservation 越本波 A 窗 598_301..600_300→1 hop 落位 600_301..600_500·"
    "**B 落位 base==本波 A 窗尾+1（600_300+1）机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执"
    "·第十五次连续 above-own-A 落位如实注记）"
    "·非转录 r587·与 W264 prereg §5 item5 投影承接面注记兑现+落位零分歧披露收敛·ADMIT 回执在场）；p_exit=`P_EXIT=0.05`"
)

NEW["b_claim_proj"] = (
    "probe W266+ 投影 A naive 600_301..602_300 CLEAN hops=0（零 live refusers）/ B naive 600_501..600_700 CLEAN hops=0 "
    "**但落 naive W266 A 窗内**→own-A reservation cascade 下 staircase 级联上移 **staircase face 延续 live re-derive governs 预披露**"
    "（投影 A naive 600_301..602_300 CLEAN·hops=0——**post-W265-REGISTERED 预披露：naive W266 A 起点 600_301 将被注册 W265 B 带 600_301..600_500 拒=staircase affects A 第十五次连续 A-hop 预期**；"
    "投影 B naive 600_501..600_700 clean 但落 naive W266 A 窗 600_301..602_300 内——"
    "**above-own-A 承袭 face：W265 B 600_301..600_500 落本波 A 窗之上〔第十五次连续〕·W265 A 面 1-hop=staircase affects A〔第十四次连续〕·"
    "W266 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace·注册 W265 B 带将拒 naive W266 A 窗仅当重叠——"
    "**W266 freezer 承接面强制注记：须在 post-W265 宇宙重 derive 且 derive B 时预留本波 A 窗·W141 先例·never transcribe r587**）"
)

NEW["b5_projection"] = (
    "5. **W266+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 600_301..602_300 **CLEAN**（hops=0·pre-W265 宇宙零 live refusers）——"
    "**post-W265-REGISTERED 预披露：naive W266 A 起点 600_301 将被注册 W265 B 带 600_301..600_500 拒（staircase-affects-A 第十五次连续 A-hop 预期）**；"
    "B naive **600_501..600_700 CLEAN（hops=0）但落投影 A 窗 600_301..602_300 内**（W266p_B_lands_inside_W266p_A_naive=true——"
    "**staircase face 延续**：W265 A 598_301..600_300+B 600_301..600_500 注册后 naive W266 A 窗起点即被注册 W265 B 带拒（staircase affects A 承袭·第十五次连续 A-hop 预期）"
    "→A first-clean 将上移·B own-A reservation cascade 落位相应上移——post-W265 宇宙 live re-derive 必变·禁转录投影）；"
    "**W266 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace**"
    "（W251 起 staircase affects A·W252/W253/W254/W255/W256/W257/W258/W259/W260/W261/W262/W263/W264/W265=A/B 双 1-hop 形态连续十四波如实注记·seed-gap face 已于 W252 终结=A 首跳如实注记）"
    "——W266 冻结方必须在 post-W265 注册宇宙重 derive 且 derive B 时预留本波 A 窗 598_301..600_300+本波 B 带 600_301..600_500"
    "——leg2 律/E36 卡·W141 先例；verify at W266 prereg，hop 链逐跳在 probe 回执。"
)

NEW["b_gated"] = (
    "本件=席位窗后首窗冻结件；五面冻结拼接脚本 results/_w265bmc_freeze_edits.py"
    "（按 _w264bmc_freeze_edits.py 模板派生·gate0.5 自查 W264 行+W264 finalize 件在场=已绿·未落即 loud abort 兜底）"
    "=**splice 执行窗派生落地（r1076/r1077 W264 先例实时间线：prereg f4ffdb34e 落于 r1076 窗·splice 216b578b0 落于 r1076 absorb 执行窗 @@SPLICE_T@@——"
    "**W265 freeze 面：W264 own-wave finalize 已落地=席位时即解锁——席位+prereg 本窗落地 per seat-first law O-20261010-2350 §2·"
    "splice 执行窗开门（gate0.5 绿·编辑器 loud abort 兜底）**。"
)

# marker pairs: (block, start_marker, end_marker) -- needles matched on T1 (post-roll faces)
BLOCKS = [
    ("b_title", "engine_owner 行 253 注册在册（表尾", "已名此窗）**】】）"),
    ("b_prev", "prev=**届时空窗活链头 derive 禁手抄**", "（机械算·投影面仅披露·finalize 运行时按 registry 键 derive 免疫）。"),
    ("b_band", "（**A 面=STAIRCASE-AFFECTS-A", "（见 §5 item5）。"),
    ("b3_a", "entry rng seed=**596_101+j**", "；p=`BASELINE_P"),
    ("b3_b", "exit rng=**598_101+j**", "；p_exit=`P_EXIT=0.05`"),
    ("b_claim_proj", "probe W265+ 投影 A naive 598_101..600_100 CLEAN hops=0", "never transcribe r587**）"),
    ("b5_projection", "5. **W265+ 投影（probe 机证 leg4", "verify at W265 prereg，hop 链逐跳在 probe 回执。"),
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
    "PERPETUAL-N1-W265", "research/PERPETUAL_N1_W265_PREREG.md",
    "598_301..600_300", "600_301..600_500", "580,920", "1,005,135", "578,720",
    "n1_w265_results.json", "MSG-20261017-2241-bmc-w265-seat", "7343e3650",
    "池第 263 枚", "第八十四枚", "第 255 波", "第 84 枚",
    "STAIRCASE-AFFECTS-A", "第十四次连续 A-hop", "第十五次连续 above-own-A",
    "_w265bmc_20261017", "--wave 265/finalize --wave 265",
    "W264 finalize one-pass bm-c r1077", "n_eff_held_equal 996,335",
    "−0.09272766", "0.24504297", "−0.08593818", "（**0.3046** 实测锚）",
    "键 W264 实测 K-lift **0.0001**", "line_merged@K578,720 **1.1955**", "line_pre_w264 1.1954",
    "实差 0.0068 在带内", "共二百六十三面实测", "W2..W264",
    "engine_owner==bm-c 83 行注册", "engine_owner 行 254 注册在册",
    "probe leg0 bmc_rows=83 attempt-continuity face（r1077 窗算法·bm-c own seat+bmc live rows 83 实读）",
    "bm-c 循环班 r1077 席位窗", "本窗 free RAM ~3GB", "本机 bm-c 实例",
    "W265=bm-c own-wave window per chain-order law",
    # r1081 heal (9): "dd5fd438e" REMOVED from MUST (clone residue -- dead window left the W264-gen's
    # own-seat origin in MUST while the correctly-shifted MUST_NOT also demands its absence; the W265
    # seat rides origin 7343e3650 per the seat VMAP legs, T2 legitimately carries ZERO dd5fd438e).
    "f4ffdb34e", "216b578b0", "964148797", "17dd06323",
    "W266+ 投影", "W266p_B_lands_inside_W266p_A_naive", "verify at W266 prereg",
    "_w265bmc_freeze_edits.py", "_w264bmc_freeze_edits.py 模板派生",
    "bm-c r1077 W264 §7 范式", "bm-c r1077 W264 §8 范式",
    "（W264 注册+烧录+finalize 全落地）",
    "W206/W211..W264 低 RAM 实烧先例", "W263 冻结窗 26G bm-a 实锚", "W264 冻结窗 7G bm-c 实锚",
    "席位时即解锁", "（见 §5 item5）。", "R266：W265 带",
    "→W261 **0.000324**→W262 **0.000323**→W263 **0.000323**→W264 **0.000322**→W265 投影 0.000322】",
    "598_300+1", "600_300+1",
    "A_staircase_hop_past_W264_B=true", "B_lands_above_own_A=true",
    "seed_admit_gate rc0 双带 FREE",
    "波号 265", "零 265 行", "零 skip-ahead W266/W267 席位声明",
]
for s in MUST:
    assert s in T2, "MUST-HAVE missing: %r" % s

MUST_NOT = [
    "A-ext seed=596_101", "B-ext exit seed=598_101",
    "596_101..598_100", "598_101..600_100 CLEAN", "598_101..598_300**",
    "GATED on", "finalize PENDING", "pending 投影 derive",
    "576,520", "1,002,935", "**578,720 投影**", "line_merged@K576,520",
    "−0.09275356", "0.24503704", "−0.09496455", "**0.3208**", "实差 0.0022 在带内",
    "19:2x", "queue_depth",
    "MSG-20261017-1950", "dd5fd438e", "b32f6bf1c", "f499817fa", "355c716b7", "91da16c86",
    "bm-a r1039", "bm-a r1039 W263",
    "bmc_rows=82", "第 83 枚", "第 254 波", "第八十三枚",
    "engine_owner==bm-c 82 行注册",
    "r1075 席", "r1075 席位窗实跑", "r1075 窗算法",
    "本窗 free RAM ~7GB", "gaming yield 让路态",
    "W265p_", "W264p_",
    "line_pre_w263", "键 W262 实测 K-lift", "键 W263 实测 K-lift",
    "verify at W265 prereg",
    "W265+ 投影", "W264+ 投影",
    "第十三次连续 A-hop", "第十四次连续 above-own-A", "连续十三波", "共二百六十一面",
    "_w263bma", "_w264bmc_freeze_edits.py 模板派生·gate0.5 自查 W263",
    # r1081 heal (10): "n1_w264_results.json 机读·净账本锚头" REMOVED from MUST_NOT (dead-window
    # non-canon addition -- W264-gen MUST_NOT bans stale NUMBERS only, never this n1_ prefix; the
    # NEW b_title block legitimately carries it with true numbers 1,005,135; stale faces already
    # banned via the "1,002,935" + "576,520" entries below).
    "n1_w263_results.json",
    "W2..W263", "W136..W263",
]
for s in MUST_NOT:
    assert s not in T2, "MUST-NOT-HAVE present: %r (count=%d)" % (s, T2.count(s))

# pinned count gates
assert T2.count("W266+ 投影") == 3, "W266+ 投影 count=%d (expect 3 = b5 title + b6 claim + sec8 rolled)" % T2.count("W266+ 投影")
assert T2.count("W265+ 投影") == 0, "W265+ 投影 count=%d (expect 0)" % T2.count("W265+ 投影")
assert T2.count("hops=1") == 2, "hops=1 count=%d (expect 2 = 带位 A + §3 A)" % T2.count("hops=1")
assert T2.count("hops=0") == 5, "hops=0 count=%d (expect 5 = b5 x2 + b6 x3)" % T2.count("hops=0")
assert T2.count("第十四次连续 A-hop") == 3, "第十四次连续 A-hop count=%d (expect 3 = b_band x2 + b3_a x1)" % T2.count("第十四次连续 A-hop")
assert T2.count("第十五次连续 A-hop") == 3, "第十五次连续 A-hop count=%d (expect 3 = b5 x2 + b6 x1)" % T2.count("第十五次连续 A-hop")
assert T2.count("第十五次连续 above-own-A") == 2, "第十五次连续 above-own-A count=%d (expect 2 = b_band + b3_b)" % T2.count("第十五次连续 above-own-A")
assert T2.count("连续十四波") == 1, "连续十四波 count=%d (expect 1 = b5 NEW)" % T2.count("连续十四波")
assert T2.count("598_301..600_300") >= 5, "598_301..600_300 count=%d (expect >=5)" % T2.count("598_301..600_300")
assert T2.count("600_301..600_500") >= 4, "600_301..600_500 count=%d (expect >=4)" % T2.count("600_301..600_500")
assert T2.count("600_301..602_300") == 5, "600_301..602_300 count=%d (expect 5 = b6 x3 + b5 x2)" % T2.count("600_301..602_300")
assert T2.count("席位时即解锁") == 2, "席位时即解锁 count=%d (expect 2 = final line + b_gated)" % T2.count("席位时即解锁")

# residue scan: all X_Y..X_Y windows well-formed
for m in re.finditer(r"(\d{3}_\d{3})\.\.(\d{3}_\d{3})", T2):
    lo = int(m.group(1).replace("_", "")); hi = int(m.group(2).replace("_", ""))
    assert lo <= hi, "malformed window %s" % m.group(0)

io.open(OUT, "w", encoding="utf-8", newline="").write(T2)
print("W265 PREREG DERIVE OK -> %s (%d bytes, %d lines)" % (OUT, len(T2.encode("utf-8")), T2.count("\n") + 1))
print("splice commit face: 216b578b0 @ " + SPLICE_T)
print("blocks replaced: %s" % ", ".join(n for n, _, _ in BLOCKS))
print("vmap legs: %d floors: %d post-legs: %d MUST: %d MUST_NOT: %d" % (
    len(VMAP), len(VMAP_FLOORS), len(VMAP_POST_LEGS), len(MUST), len(MUST_NOT)))
print("src blob-verified == 2ba4dbc1e1947ffa0ef7f5c0850bed73cc432277 @ f4ffdb34e (frozen pre-run face; HEAD post-backfill twin 96c037c4 disclosed, NOT used)")
print("out sha256_16: %s" % hashlib.sha256(T2.encode("utf-8")).hexdigest()[:16])
