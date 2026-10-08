# -*- coding: utf-8 -*-
"""r901 bm-a W193 per-wave prereg BUILDGEN (generator): constructs the
W192->W193 TOK/BACK pair map, runs the full preflight DRY gate (r787
preflight dry-run law, ZERO writes until all green), then EMITS
results/_r901bma_w193_prereg_build.py (the executable build script with
pairs baked).

Bloodline: r830 (E41 buildgen surgery) / r833 prereg-build three laws
(AST no-exec prior-gen / DRY full-file gate zero-write-first /
U+2212 display anchor forms) / r877 S83 roll (old side = physical src
POST-ROLL text; binary src extraction; TAIL %% escapes) / r893 W191
buildgen (two-phase vmap, whole-string composites, numerals LAST,
r735 substring-order law = pair list order preserved).

Src: research/PERPETUAL_N1_W192_PREREG.md freeze-time blob 66b3c64123
(commit de1ad11f9 == origin/main HEAD face, verified EQUAL this window;
W192 sec7/sec8 still placeholders = safe build src, no actuals leak).
Extracted byte-verbatim (binary) to results/_r901bma_w193_prereg_src.txt.

r587 machine-derived facts (live-asserted inside, zero transcribe):
  - r900 pre-seat probe results/_r900bma_w193_probe_receipt.json ADMIT:
    A 439_404..441_403 (staircase FIFTY-THIRD, E36; naive A 439_204..441_203
    REFUSED at own start by registered W192 B band 439_204..439_403,
    hops=1) / B 441_404..441_603 (own-wave A reservation, W141 leg2,
    hops=1; naive B 439_404..439_603 lands inside own-A);
    leg0 rows=190 tail W192 owner_rows=182 bma_rows=107 ordinal=183
    bma_ordinal=108 w191_ledger_head=833,536;
    leg4 W194+ projection A 441_404..443_403 hops=0 / B 441_604..441_803
    hops=0, B-inside-A True.
  - W191 finalize results/perpetual_faces/n1_w191_results.json:
    ledger 831,336+2,200=833,536 EXACT; K merged=418,120 EXACT;
    merged mu -0.09286652420357792 -> 4dp display -0.0929 HOLDS
    (four-wave display hold W189/W190/W191/W193-key); w-only -0.0898
    ROLLS; sigma 0.245166 ROLLS; A p95 0.3049 ROLLS; K-lift +0.0001
    (sign-flip back positive); line 1.1871 -> 1.1872; n_eff 831,336;
    se_mu chain tail 0.000379.
  - shas: W191 five-face e5e4af81b (pf.py -S pick), W192 five-face
    f8703842c, W193 seat MSG add 9df3078c5; W193 five-face vacancy on
    origin (empty -S pick) and W192 finalize product ABSENT on origin
    (anchor stays W191 per r590 push-time re-derive; W192 = in-flight
    upstream seat disclosed honestly).

Structural disclosures vs the W192 physical src (bm-c direct-pen face):
  * authorship returns to bm-a buildgen lineage: the bm-c "交互窗直笔
    无 buildgen emission 链" note is replaced by the buildgen emission
    disclosure (r830/r833/r877 bloodline named);
  * engine instance prose rolls bm-c live-daemon -> bm-a tick (W191
    bm-a precedent wording);
  * the single-state chain W191 entry updates from its W192-era
    in-flight form ("r892 席位+r893 prereg freeze ea42ee94a") to the
    LANDED five-face commit (e5e4af81b) -- chain entries uniformly
    point at landed five-face commits (all other rows do); W192 row
    appended (f8703842c); disclosed here, not silently;
  * scan face: no declared-band injection this wave (W191/W192 five-
    faces both registered; leg0 190 rows tail W192 machine-read);
  * SEED_REGISTRY live count rolls 190 -> 191 (F1-BULL-COND-P1 seed
    94_200 registered 1b7e9e53d); machine-derived, masked pre-TOK like
    the r893 @@REGN@@ vestigial pattern;
  * claim context rolls to the r900 seat push (9df3078c5) with W194+
    projection (probe leg4 machine values); CEO fill-order quote (bm-c
    window-specific) not carried into the bm-a face -- the bm-a claim
    law = never-dry standing line + O-1730 same-round claim (W191
    precedent);
  * pool projection 418,120+2,200(W192 in-flight)+2,200(this)=422,520.

Output written CRLF (on-disk convention, r370 law) by the EMITTED
script; this generator writes nothing but the emitted script itself
(after its own DRY gate is fully green).
"""
import ast
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SRC = "results/_r901bma_w193_prereg_src.txt"
OUT = "research/PERPETUAL_N1_W193_PREREG.md"
EMIT = "results/_r901bma_w193_prereg_build.py"
G = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
M = "\u2212"  # U+2212 display minus


def git(*a):
    r = subprocess.run(["git", "-C", G] + list(a), capture_output=True)
    return r.stdout.decode("utf-8", errors="replace").strip()


# --- machine-derived facts (r587) --------------------------------------
subprocess.run(["git", "-C", G, "fetch", "origin"], capture_output=True)
probe = json.load(open(r"results/_r900bma_w193_probe_receipt.json",
                      encoding="utf-8"))
assert probe["verdict"] == "ADMIT", probe["verdict"]
assert probe["bands"] == {"A": "439404_441403", "B": "441404_441603"}, \
    probe["bands"]
leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]
leg4 = probe["legs"]["leg4"]
assert leg1["A"] == [439404, 441403] and leg1["B"] == [441404, 441603], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1
assert leg1["ARITH_A"] == [439204, 441203], leg1["ARITH_A"]
assert leg1["B_naive_first_clean"] == [439404, 439603], leg1
assert leg1["B_hop_chain"][0]["jump_to"] == 441404, leg1["B_hop_chain"]
assert leg0["rows"] == 190 and leg0["tail"] == "W192", leg0
assert leg0["ordinal"] == 183 and leg0["bma_ordinal"] == 108, leg0
assert leg0["owner_rows"] == 182 and leg0["bma_rows"] == 107, leg0
assert leg0["w191_ledger_head"] == 833536, leg0
assert probe["legs"]["leg2"]["conflicts"] == 0, probe["legs"]["leg2"]
assert probe["legs"]["leg3"]["origin_vacancy"] is True, probe["legs"]["leg3"]
assert leg4["W194p_A"] == "441404..443403" and \
    leg4["W194p_B"] == "441604..441803", leg4
assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0, leg4
assert leg4["W194p_B_lands_inside_W194p_A"] is True, leg4
assert "FIFTY-THIRD" in leg1["A_semantics"], leg1["A_semantics"]

res = json.load(open(r"results/perpetual_faces/n1_w191_results.json",
                     encoding="utf-8"))
npc = res["null_pool_cumulative"]
kl = res["skill_line_v2_k_lift"]
assert npc["merged"]["n_values"] == 418120, "K drift"
assert npc["pre_w191_cumulative"]["n_values"] == 415920, "pre-K drift"
assert res["science_gates"]["ledger"]["total"] == 833536, "ledger head"
assert res["science_gates"]["ledger"]["prev_total"] == 831336, "ledger prev"
assert npc["se_mu_at_k418120"] == 0.000379, "se_mu drift"
assert kl["n_eff_held_equal"] == 831336, kl
assert abs(kl["line_delta_k_lift"] - 0.0001) < 1e-12, kl
assert abs(kl["line_pre_w191"] - 1.1871) < 1e-9 and \
    abs(kl["line_merged_418120"] - 1.1872) < 1e-9, kl
assert res["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.3049
MU4 = ("%.4f" % npc["merged"]["mu"]).replace("-", M)
WONLY4 = ("%.4f" % npc["w191_only"]["mu"]).replace("-", M)
SIG6 = "%.6f" % npc["merged"]["sigma"]
assert MU4 == M + "0.0929" and WONLY4 == M + "0.0898" and SIG6 == "0.245166", \
    (MU4, WONLY4, SIG6)

W191_FF = git("log", "origin/main", "--format=%h", "-n", "1", "-S",
              '191: {"a": (435_004', "--", "scripts/perpetual_faces.py")
assert W191_FF == "e5e4af81b", W191_FF
W192_FF = git("log", "origin/main", "--format=%h", "-n", "1", "-S",
              '192: {"a": (437_204', "--", "scripts/perpetual_faces.py")
assert W192_FF == "f8703842c", W192_FF
SEAT = git("log", "origin/main", "--format=%h", "-n", "1", "--diff-filter=A",
           "--", "fleet/inbox/MSG-2026-10-09-0458-bma-w193-seat.md")
assert SEAT == "9df3078c5", SEAT
_vac = git("log", "origin/main", "--format=%h", "-n", "1", "-S",
           '193: {"a": (439_404', "--", "scripts/perpetual_faces.py")
assert _vac == "", "W193 five-face already on origin?!"
_fin = git("ls-tree", "origin/main", "results/perpetual_faces/n1_w192_results.json")
assert _fin == "", "W192 finalize landed -- anchor must roll to W192 (r590)!"
print("facts: ALL GREEN (anchor=W191, W192 five-face landed, W193 vacancy)")

# live SEED_REGISTRY count (rolls 190->191 this window, F1-BULL-COND-P1
# seed 94_200 registered 1b7e9e53d); masked pre-TOK like r893 @@REGN@@
sys.path.insert(0, "scripts")
sys.path.insert(0, ".")
import science_gates as _sg  # noqa: E402
REG_N = len(_sg.SEED_REGISTRY)
assert REG_N == 191, "SEED_REGISTRY count drift: %d" % REG_N

# --- src load -----------------------------------------------------------
src = io.open(SRC, encoding="utf-8").read()
assert src.count("\r\n") == 0, "src blob expected LF"
assert "PERPETUAL-N1-W192" in src and "437_204..439_203" in src, \
    "src face drift"
assert src.count("SEED_REGISTRY \u5168\u952e 190 \u503c") == 1, \
    "registry-count face not found in src (old live count)"
# pre-TOK registry mask (value rolls this generation 190->191)
src_t = src.replace("SEED_REGISTRY \u5168\u952e 190 \u503c",
                    "SEED_REGISTRY \u5168\u952e @@REGN@@ \u503c")

# --- pair construction (old side = physical src text, r877 law 1) -------
# chain: extract verbatim from src (r587 zero-transcribe)
_m = re.search(r"W118=bm-b r678 freeze（565e5b0b4）.*?"
               r"W191=bm-a r892 席位\+r893 prereg freeze（ea42ee94a）", src_t)
assert _m, "chain anchor not found"
CHAIN_OLD = _m.group()
CHAIN_NEW = (CHAIN_OLD
             .replace("W191=bm-a r892 席位+r893 prereg freeze（ea42ee94a）",
                      "W191=bm-a r894 freeze（e5e4af81b）")
             + "；W192=bm-c r787 freeze（f8703842c）")
assert "e5e4af81b" in CHAIN_NEW and CHAIN_NEW.endswith("f8703842c）")
assert "ea42ee94a" not in CHAIN_NEW

Aface_new = (
    "本波 **A-ext seed=439_404..441_403**（**A 面=FIRST-CLEAN past "
    "prior-wave B 阶梯第五十三例**：A 面算术继续带 439_204..441_203 在其"
    "起点即被 W192 注册 B 带 439_204..439_403 **拒**（W192 §5.5 投影+"
    "bm-c r787 probe leg4+W192 认领投影散文所预言+强制）→ 诚实前向走 "
    "**1 hop** 落 **439_404..441_403**·**A base==前波 B 尾+1（439_403+1）"
    "机检关系**=**A-hops-prior-B 阶梯几何第五十三例（E36 卡）**·非轮转 "
    "r587 前向单调断言在走册；序数面如实披露：W192 §5.5 投影预告第五十"
    "三例·本窗 probe 回执 A_semantics 机读序数=FIFTY-THIRD（第五十三例）"
    "·本件按回执序数面记载非转抄（r587）·投影与回执两读法恒同）")
Bface_new = (
    "**B-ext exit seed=441_404..441_603**（**B 面=FIRST-CLEAN past "
    "own-wave A**：B 面算术继续带 439_404..439_603 在声明宇宙上 CLEAN "
    "但**落在本波 A 窗 439_404..441_403 内**（**同窗互斥面 leg2 律·"
    "W141 先例**：A 与 B 同一冻结 commit 双注册·互斥断言强制 B 越过本波 "
    "A 窗）→ B 带本波 A 窗保留走 **1 hop** 落 **441_404..441_603**·"
    "**B base==本波 A 尾+1（441_403+1）机检关系**·hop 链逐跳在 probe 回"
    "执；**W192 §5.5 投影+bm-c r787 probe leg4 承接面注记三面兑现**：投"
    "影预言 W193 须在 post-W192 注册宇宙重 derive 且 derive B 时预留本"
    "波 A 窗——本窗双面兑现·A 被拒+阶梯越带如投影所期·B 同窗互斥保留="
    "投影所期·已如实披露非分叉）")

TOK = [
    # (old, token)  -- composites first, bare numerals LAST (r773/r775)
    (CHAIN_OLD, "@CHAIN@"),
    ("# PERPETUAL-N1-W192 预注册 · N1 nulls-deepening 泵第 190 枚"
     "（never-dry 常供给例波·波序号连续·机面 derive：engine_owner 行 "
     "180 注册在册+W191 五面在飞+本候选=bm-c 第三十五枚自有波"
     "【bm-c 交互窗 2026-10-08 23:5x·CEO 领单直令】）", "@TITLE@"),
    ("引擎核=self 仓单源脚本·本机 bm-c 实例=**live daemon mtime-watch "
     "热重载架构**——冻结编辑落工作栈后引擎下一 cycle n1_bands() mtime "
     "复读自见新行自烧【r535 律·D-20261002-03 fix ①】·点火验证唯一证据"
     "=2 cycle 内产物增长面【r325 律·state queue 面不修】）→ **never-dry "
     "常供给例波**：**O-20261001-2355 CEO 去节流令 §二**【每机自烧连续系"
     "列不等等待·down-series 续跑】+ O-20260929-2355 同窗同律共引+ **本窗"
     "领取令=CEO 直令 2026-10-08 ~23:5x「你的机器CPU算力闲置严重，自己去"
     "领回测任务！排满」**【bm-c 交互窗直执·O-20260924-1730 认领即开动同轮"
     "律·本机引擎队列自 wave-115 时代空转实测（saturation_engine_state."
     "bm-c.json queue_next 空·py_cpu 0.23% 实读）】。", "@INST@"),
    ("【本冻结窗 fetch 实核表尾时 W192 号位空档·rg 行 WAVE_CONFIGS+"
     "prereg 路径三查+origin ls-tree vacancy 机证（本窗 probe leg3 实跑）"
     "；全 inbox/processed/ W192 席位零外机命中；**W191=bm-a r892 席位 "
     "MSG-2026-10-08-2130+r893 prereg freeze（ea42ee94a）在册·五面 band "
     "row 在飞未落 origin 如实注记——本波注册宇宙=W191 声明带注入（W191 "
     "prereg 原文 origin 文本验证·probe leg0 机证）·r892 W191 probe leg4 "
     "强制令兑现**；本机席位公示=MSG-20261008-2351-bmc-w192-seat 已推 "
     "origin 1abe1a57f 先于本冻结【r565 律·§6.1.4 API 直构零本地 commit "
     "通道如实注记】】", "@SEATBLOCK@"),
    ("本波 **A-ext seed=437_204..439_203**（**A 面=FIRST-CLEAN past "
     "prior-wave B 阶梯第五十二例**：A 面算术继续带 437_004..439_003 在"
     "其起点即被 W191 声明 B 带 437_004..437_203 **拒**（W191 §5.5 投影+"
     "r892 probe leg4+W191 席位 W192+ 投影散文所预言+强制）→ 诚实前向走 "
     "**1 hop** 落 **437_204..439_203**·**A base==前波 B 尾+1（437_203+1）"
     "机检关系**=**A-hops-prior-B 阶梯几何第五十二例（E36 卡）**·非轮转 "
     "r587 前向单调断言在走册；序数面如实披露：W191 §5.5 投影预告第五十"
     "二例·本窗 probe 回执 A_semantics 机读序数=FIFTY-SECOND（第五十二"
     "例）·本件按回执序数面记载非转抄（r587）·投影与回执两读法恒同）",
     "@AFACE@"),
    ("**B-ext exit seed=439_204..439_403**（**B 面=FIRST-CLEAN past "
     "own-wave A**：B 面算术继续带 437_204..437_403 在声明宇宙上 CLEAN "
     "但**落在本波 A 窗 437_204..439_203 内**（**同窗互斥面 leg2 律·"
     "W141 先例**：A 与 B 同一冻结 commit 双注册·互斥断言强制 B 越过本波 "
     "A 窗）→ B 带本波 A 窗保留走 **1 hop** 落 **439_204..439_403**·"
     "**B base==本波 A 尾+1（439_203+1）机检关系**·hop 链逐跳在 probe 回"
     "执；**W191 §5.5 投影+r892 probe leg4 承接面注记三面兑现**：投影预"
     "言 W192 须在 post-W191 注册宇宙重 derive 且 derive B 时预留本波 A "
     "窗——本窗双面兑现·A 被拒+阶梯越带如投影所期·B 同窗互斥保留=投影所"
     "期·已如实披露非分叉）", "@BFACE@"),
    ("扫描面=pre-W192 全一百八十八行注册 N1 带表（表尾 W190 行·leg0 机证 "
     "188 行）+W191 声明带两条注入（origin 文本验证）", "@SCANFACE@"),
    ("R250：W192 带从未指派·测量面零结果可锁", "@R250@"),
    ("results/_w192bmc_20261009_probe_receipt.json", "@PRCR@"),
    ("W2..W191 落地 runner 的 wave 参数化复用", "@RUNNERW@"),
    ("引擎侧 `scripts/saturation_engine.py`【本机 bm-c 实例·live daemon "
     "mtime-watch 热重载架构】只做队列点火台账处理面·runner 零改写。"
     "**本冻结=交互窗直笔+探针机证（无 buildgen emission 链——"
     "extraction-from-emission 律 N/A 诚实注记·五腿探针回执在场为准·"
     "selftest W192 face 将随五面冻结落地验证）。**", "@ENGNOTE@"),
    ("批名=**PERPETUAL-N1-W192**", "@BATCHNAME@"),
    ("起稿窗实况：**W1..W190 N1 finalize 已全部落地**【净账本锚头 "
     "**825,328**·K=415,920 合并池·n1_w190_results.json 机读】；**W191="
     "bm-a 席位+prereg 冻结在册·五面 band row 在飞未落 origin（dead-tail "
     "adoption in flight）——本波上游在飞席注记=W191·「零在飞上游链前」"
     "断言不适用改如实注记**", "@ANCHOR0@"),
    ("累计 null 池=415,920+2,200（W191 投影）+2,200（本波）=**420,320 投"
     "影**", "@POOL@"),
    ("- 认领：never-dry 常供给例波（TRIAL_LABOR_LAW §4·板空/池饿/无在飞"
     "判决批=默认续跑下一波——本机引擎队列空转+池 408 条全 done 实读；"
     "**CEO 直令 2026-10-08 ~23:5x 领单**（本机席位 MSG-20261008-2351-"
     "bmc-w192-seat 已推 origin 1abe1a57f r565 律·probe W193+ 投影 A "
     "439_204..441_203 / B 439_404..439_603 **naive-B-inside-naive-A "
     "re-derive 强制注记+同窗互斥预披露**（投影 B 落投影 A 窗内·W192 B "
     "带 439_204..439_403 注册后将拒 naive W193 A 窗=阶梯 A-hops-prior-B "
     "继承第五十三例待 W193 注册宇宙复核））；O-20260924-1730 CEO 即时律"
     "（认领与开动同轮·禁排未来轮次）；T-2026-10-01-141 s1 引擎线第 182 "
     "波【bm-c 第三十五枚自有波【机面 derive：engine_owner==bm-c 行 34+"
     "本候选以 probe leg0 机证为准】】。（波号=注册表 W191 席后首个自由号"
     "·单态零席位空档；中位公示 MSG-20261008-2351-bmc-w192-seat 先推 "
     "origin 1abe1a57f r565 律；lane-free；dept:研究）。", "@CLAIM@"),
    ("（N1_BANDS 单源 derive·engine_owner==bm-c 波的未烧分片=本地队列项"
     "；per-wave prereg 在场=物化前置条件）；池面 supply 生成器对 "
     "engine_owner 波群跳过物化【cmd_supply owner 跳过闸防零号双烧面】；"
     "**引擎实况注记（本机 bm-c 实例=live daemon mtime-watch 热重载——五面"
     "冻结编辑落工作栈后引擎下一 cycle n1_bands() mtime 复读自见 W192 行"
     "并点火自烧【r535 律·D-20261002-03 fix ①·r325/r330 kill-restart 序"
     "免做】。**点火验证唯一证据=产物增长面**【r325 律·2 cycle 窗】·"
     "RAM face 随 cycle 上报。", "@MATCOND@"),
    ("--prereg research/PERPETUAL_N1_W192_PREREG.md", "@GATECMD@"),
    ("v2..W190 落地）的种子带扩展重测", "@V2W@"),
    ("entry rng seed=**437_204+j**（法典 §4 W192 行 A=437_204..439_203·"
     "**FIRST-CLEAN past prior-wave B 阶梯第五十二例**：算术续带 "
     "437_004..439_003 起点即被 W191 声明 B 带拒→1 hop 落 "
     "437_204..439_203·A base==前波 B 尾+1 机检关系·E36 卡·hops=1·"
     "ADMIT 回执在场）", "@ASEED@"),
    ("entry rng=**437_204+j**（与 A[j] 同源配对语义逐字·runner 实证 "
     "entry=A_SEED_BASE+j）", "@BENTRY@"),
    ("exit rng=**439_204+j**（法典 §4 W192 行 B=439_204..439_403·"
     "**FIRST-CLEAN past own-wave A**：B 算术续带 437_204..437_403 在声明"
     "宇宙上 CLEAN 但落在本波 A 窗 437_204..439_203 内→**同窗互斥面 leg2 "
     "律·W141 先例**强制 B 越本波 A 窗→保留走落 439_204..439_403·hops=1·"
     "**B base==本波 A 尾+1 机检关系**·非轮转 r587·hop 链逐跳在 probe 回"
     "执·与 W191 §5.5 投影+r892 probe leg4 承接面注记兑现收敛·ADMIT 回执"
     "在场）", "@BSEED@"),
    ("本波设计=W2..W191 逐字复用", "@PROBEW@"),
    ("W192 带与 v1 在用带（10_000..10_099/20_000..20_019）、W1 ext 带"
     "（10_100..12_099/20_100..20_299）、W2..W191 带（**全注册单态+W191 "
     "声明带注入**）", "@DISJ@"),
    ("本波机验 ADMIT 回执在场=_w192bmc_20261009 探针窗（pre-seat probe 单"
     "窗·gate 腿合并结构承袭 r812/r820/r823 先例·parity N/A 诚实注记）；"
     "selftest W192 face（A=first-clean past prior-wave B 恒等·B=first-"
     "clean past own-wave A 恒等+同窗互斥断言·W191 行 parity 腿"
     "【r735 测量-实现分叉族防护面：A/B 窗 set-range 针在场】）随五面冻结"
     "落地", "@GATEW2@"),
    ("已落账净值（起草窗实流 W1..W190 已落账 415,920 实测·derive 禁手抄）"
     "+W191 2,200（在飞）+本波 2,200", "@POOL4@"),
    ('batch_name="PERPETUAL-N1-W192", batch_trials=2200, file_name='
     '"results/perpetual_faces/n1_w192_results.json"', "@LEDGER@"),
    ("（起草窗实况注记：**W1..W190 N1 finalize 已全部落地**——净账本锚头 "
     "825,328·**K=415,920 合并池**·**W191 在飞上游席注记（bm-a·prereg 冻"
     "结·五面在飞未落）——本波 §5 预测键=**W190 实测值**【results/"
     "perpetual_faces/n1_w190_results.json·N1 面最新已落账键·W191 落账后属"
     "上游先决非本键面】", "@S5ANCH@"),
    ("1. W192-only mu 与累计池 merged mu（W190 实测键 **−0.0929**·K="
     "415,920 合并池·W190-only 实测 **−0.0986**）差异 **|Δ|<0.02**（W2.."
     "W190 共一百八十九面实测 mu 稳定先例·单波跨键微）", "@S51@"),
    ("2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.245150**"
     "=W190 合并池实测 0.245150）", "@S52@"),
    ("3. A 档 full_sharpe_p95 与 W190 A 档 p95（**0.3068** 实测锚）差 "
     "**<0.05**（门标注法 W5..W190 先例", "@S53@"),
    ("4. K-lift 线移动幅度 **≤±0.02**（累计池加深零 se_mu 收窄线自 mu/"
     "sigma 微调面非质变——W136..W190 先例链披露【W186 −0.0001/W187 "
     "+0.0002/W188 +0.0000/W189 +0.0003/W190 −0.0001·键 W190 实测 K-lift "
     "**−0.0001**·line_merged@K415,920 **1.1866**·line_pre 1.1867·"
     "n_eff 823,128；se_mu 收窄链 W188 0.000382→W189 0.000381→W190 "
     "**0.000380**】）", "@S54@"),
    ("5. **W193+ 投影（probe 机证·下波冻结方复核非转抄 r587 律）**：A "
     "first-clean 439_204..441_203 **CLEAN**（hops=0）；B first-clean "
     "**439_404..439_603 CLEAN**（hops=0）——**naive B 落在 naive A 窗"
     "内**（W141 同窗互斥先例适用于 W193：W193 冻结方必须在 post-W192 注"
     "册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；"
     "**W192 B 带 439_204..439_403 注册后将拒 naive W193 A 窗**——W193 A "
     "重 derive 同强制（越过 W192 B 带·阶梯 A-hops-prior-B 继承第五十三"
     "例）；verify at W193 prereg，hop 链逐跳在 probe 回执", "@S55@"),
    ("--wave 192/finalize --wave 192", "@CLI@"),
    ("点火面 `scripts/saturation_engine.py`（本机 bm-c 实例·**live daemon "
     "mtime-watch 热重载**·本地队列→PreIgnitionChecks→分离子进程点火→完"
     "成→台账处理【runner_args --lane engine 车道闸同 r523 律】）；**点火"
     "验证=2 cycle 内产物增长面**【n1_w192/ 分片计数增长·唯一点火证据·"
     "r325 律】", "@ENG6@"),
    ("results/p2cal_ext/n1_w192/shard-<k>-of-12.json", "@SHARD@"),
    ("results/perpetual_faces/n1_w192_results.json", "@RFN@"),
    ("finalize 键序前置=**起草窗在飞上游席 W191（bm-a·prereg 冻结）**——"
     "跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态例恒在",
     "@FINPRE@"),
    ("引擎台账：bm-c live daemon 架构=engine ledger jsonl+state/face/"
     "history 以 git 交付（engine_owner==bm-c 34 行注册 + 本候选——以 "
     "probe leg0 机证为准）", "@EOBD@"),
    ("待 W192 finalize 窗】\n- （占位·finalize one-pass 后机械回填：账本恒"
     "等式+合并池 K+merged mu/w-only mu/mu_delta+sigma+se_mu+"
     "skill_line_v2 K-lift+A 档 p95+§5 四预键机证+canon flip 态+audit."
     "finalize_only+voids_applied。）", "@S7@"),
    ("【finalize 同窗回填·待 W192 finalize 窗】\n- （占位·§5.5 W193+ 投影"
     "承接+宝藏/方法论捕获问+诚实披露面·finalize 收口窗机械回填。）",
     "@S8@"),
    # ---- numerals LAST ----
    ("波号 192=注册表 W191 席后首个自由号", "@WAVEFREE@"),
]

BACK = {
    "@CHAIN@": CHAIN_NEW,
    "@TITLE@": (
        "# PERPETUAL-N1-W193 预注册 · N1 nulls-deepening 泵第 191 枚"
        "（never-dry 常供给例波·波序号连续·机面 derive：engine_owner 行 "
        "182 注册在册+W192 finalize 在飞+本候选=bm-a 第一百零八枚自有波"
        "【bm-a r901·buildgen 血统 r830/r833/r877 承袭】）"),
    "@INST@": (
        "引擎核=self 仓单源脚本·本机 bm-a 实例=**tick 架构**——冻结编辑落"
        "工作栈后下一 tick 新进程读活栈自见新行自烧【r535 律】·点火验证唯"
        "一证据=2 tick 内产物增长面【r325 律·state queue 面不修】）→ "
        "**never-dry 常供给例波**：**O-20261001-2355 CEO 去节流令 §二**【每"
        "机自烧连续系列不等等待·down-series 续跑】。"),
    "@SEATBLOCK@": (
        "【本冻结窗 fetch 实核表尾时 W193 号位空档·rg 行 WAVE_CONFIGS+"
        "prereg 路径三查+origin ls-tree vacancy 机证（本窗 probe leg3 实"
        "跑）；全 inbox/processed/ W193 席位零外机命中；**W192=bm-c r787 "
        "五面冻结 f8703842c 在册·finalize 在飞未落 origin 如实注记——本波"
        "注册宇宙=W192 注册带在册（N1_BANDS 注册行机器读·probe leg0 机证 "
        "190 行表尾 W192）·r900 W193 probe 全腿机证**；本机席位公示="
        "MSG-2026-10-09-0458-bma-w193-seat 已推 origin 9df3078c5 先于本冻"
        "结【r565 律·推送窗=r900 seat push 直接快进送达 9df3078c5（payload"
        "=seat MSG+W193 pre-seat probe 脚本+回执同推）；self-ack inbox→"
        "processed 移位随五面冻结窗收口归档（如实注记）】】"),
    "@AFACE@": Aface_new,
    "@BFACE@": Bface_new,
    "@SCANFACE@": (
        "扫描面=pre-W193 全一百九十行注册 N1 带表（表尾 W192 行·leg0 机证 "
        "190 行）"),
    "@R250@": "R250：W193 带从未指派·测量面零结果可锁",
    "@PRCR@": "results/_r900bma_w193_probe_receipt.json",
    "@RUNNERW@": "W2..W192 落地 runner 的 wave 参数化复用",
    "@ENGNOTE@": (
        "引擎侧 `scripts/saturation_engine.py`【本机 bm-a 实例·tick 架构】"
        "只做队列点火台账处理面·runner 零改写。**本冻结=buildgen emission "
        "链（r830/r833/r877 血统承袭·TOK 两相 vmap+DRY 全文件门零写入先"
        "行+U+2212 显示形·五腿探针回执在场为准·selftest W193 face 将随五"
        "面冻结落地验证）。**"),
    "@BATCHNAME@": "批名=**PERPETUAL-N1-W193**",
    "@ANCHOR0@": (
        "起稿窗实况：**W1..W191 N1 finalize 已全部落地**【净账本锚头 "
        "**833,536**·K=418,120 合并池·n1_w191_results.json 机读】；**W192="
        "bm-c 五面冻结在册（f8703842c）·finalize 在飞未落 origin——本波上"
        "游在飞席注记=W192·「零在飞上游链前」断言不适用改如实注记**"),
    "@POOL@": (
        "累计 null 池=418,120+2,200（W192 投影）+2,200（本波）=**422,520 "
        "投影**"),
    "@CLAIM@": (
        "- 认领：never-dry 常供给例波（TRIAL_LABOR_LAW §4·板空/池饿/无在"
        "飞判决批=默认续跑下一波——本机 r900 席位 MSG-2026-10-09-0458-bma-"
        "w193-seat 已推 origin 9df3078c5（r900 seat push·r565 律）·probe "
        "W194+ 投影 A 441_404..443_403 / B 441_604..441_803 **naive-B-"
        "inside-naive-A re-derive 强制注记+同窗互斥预披露**（投影 B 落投影 "
        "A 窗内·W193 B 带 441_404..441_603 注册后将拒 naive W194 A 窗=阶梯 "
        "A-hops-prior-B 继承第五十四例待 W194 注册宇宙复核）。表尾后新首个"
        "自由号自领·r900 probe 单跑兑现注记（本窗冻结消费）；O-20260924-"
        "1730 CEO 即时律（认领与开动同轮·禁排未来轮次）；T-2026-10-01-141 "
        "s1 引擎线第 183 波【bm-a 第一百零八枚自有波【机面 derive："
        "engine_owner==bm-a 行 107+本候选以 probe leg0 机证为准】】。（波号"
        "=注册表 W192 席后首个自由号·单态零席位空档；中位公示 MSG-2026-10-"
        "09-0458-bma-w193-seat 先推 origin 9df3078c5 r565 律；lane-free；"
        "dept:研究）。"),
    "@MATCOND@": (
        "（N1_BANDS 单源 derive·engine_owner==bm-a 波的未烧分片=本地队列项"
        "；per-wave prereg 在场=物化前置条件）；池面 supply 生成器对 "
        "engine_owner 波群跳过物化【cmd_supply owner 跳过闸防零号双烧面】；"
        "**引擎实况注记（本机 bm-a 实例=**tick 架构**——五面冻结编辑落工作"
        "栈后引擎下一 tick 新进程读活栈自见 W193 行并点火自烧【r535 律·"
        "r325/r330 kill-restart 序免做】。**点火验证唯一证据=产物增长面**"
        "【r325 律·tick 窗】·RAM floor gate 机器例在场=自点火当 RAM 清】。"),
    "@GATECMD@": "--prereg research/PERPETUAL_N1_W193_PREREG.md",
    "@V2W@": "v2..W191 落地）的种子带扩展重测",
    "@ASEED@": (
        "entry rng seed=**439_404+j**（法典 §4 W193 行 A=439_404..441_403·"
        "**FIRST-CLEAN past prior-wave B 阶梯第五十三例**：算术续带 "
        "439_204..441_203 起点即被 W192 注册 B 带拒→1 hop 落 "
        "439_404..441_403·A base==前波 B 尾+1 机检关系·E36 卡·hops=1·"
        "ADMIT 回执在场）"),
    "@BENTRY@": (
        "entry rng=**439_404+j**（与 A[j] 同源配对语义逐字·runner 实证 "
        "entry=A_SEED_BASE+j）"),
    "@BSEED@": (
        "exit rng=**441_404+j**（法典 §4 W193 行 B=441_404..441_603·"
        "**FIRST-CLEAN past own-wave A**：B 算术续带 439_404..439_603 在声明"
        "宇宙上 CLEAN 但落在本波 A 窗 439_404..441_403 内→**同窗互斥面 leg2 "
        "律·W141 先例**强制 B 越本波 A 窗→保留走落 441_404..441_603·hops=1·"
        "**B base==本波 A 尾+1 机检关系**·非轮转 r587·hop 链逐跳在 probe 回"
        "执·与 W192 §5.5 投影+bm-c r787 probe leg4 承接面注记兑现收敛·"
        "ADMIT 回执在场）"),
    "@PROBEW@": "本波设计=W2..W192 逐字复用",
    "@DISJ@": (
        "W193 带与 v1 在用带（10_000..10_099/20_000..20_019）、W1 ext 带"
        "（10_100..12_099/20_100..20_299）、W2..W192 带（**全注册单态**）"),
    "@GATEW2@": (
        "本波机验 ADMIT 回执在场=_r900bma_w193 探针窗（pre-seat probe 单窗·"
        "gate 腿合并结构承袭 r812/r820/r823 先例·parity N/A 诚实注记）；"
        "selftest W193 face（A=first-clean past prior-wave B 恒等·B=first-"
        "clean past own-wave A 恒等+同窗互斥断言·W192 行 parity 腿"
        "【r735 测量-实现分叉族防护面：A/B 窗 set-range 针在场】）随五面冻"
        "结落地"),
    "@POOL4@": (
        "已落账净值（起草窗实流 W1..W191 已落账 418,120 实测·derive 禁手抄）"
        "+W192 2,200（在飞）+本波 2,200"),
    "@LEDGER@": (
        'batch_name="PERPETUAL-N1-W193", batch_trials=2200, file_name='
        '"results/perpetual_faces/n1_w193_results.json"'),
    "@S5ANCH@": (
        "（起草窗实况注记：**W1..W191 N1 finalize 已全部落地**——净账本锚头 "
        "833,536·**K=418,120 合并池**·**W192 在飞上游席注记（bm-c·五面冻"
        "结在册·finalize 在飞未落）——本波 §5 预测键=**W191 实测值**"
        "【results/perpetual_faces/n1_w191_results.json·N1 面最新已落账键·"
        "W192 落账后属上游先决非本键面】"),
    "@S51@": (
        "1. W193-only mu 与累计池 merged mu（W191 实测键 **" + MU4 + "**·K="
        "418,120 合并池·W191-only 实测 **" + WONLY4 + "**）差异 **|Δ|<0.02**"
        "（W2..W191 共一百九十面实测 mu 稳定先例·单波跨键微）"),
    "@S52@": (
        "2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **" + SIG6 +
        "**=W191 合并池实测 " + SIG6 + "）"),
    "@S53@": (
        "3. A 档 full_sharpe_p95 与 W191 A 档 p95（**0.3049** 实测锚）差 "
        "**<0.05**（门标注法 W5..W191 先例"),
    "@S54@": (
        "4. K-lift 线移动幅度 **≤±0.02**（累计池加深零 se_mu 收窄线自 mu/"
        "sigma 微调面非质变——W136..W191 先例链披露【W187 +0.0002/W188 "
        "+0.0000/W189 +0.0003/W190 " + M + "0.0001/W191 **+0.0001**·键 W191 "
        "实测 K-lift **+0.0001**·line_merged@K418,120 **1.1872**·line_pre "
        "1.1871·n_eff 831,336；se_mu 收窄链 W189 0.000381→W190 0.000380→"
        "W191 **0.000379**】）"),
    "@S55@": (
        "5. **W194+ 投影（probe 机证·下波冻结方复核非转抄 r587 律）**：A "
        "first-clean 441_404..443_403 **CLEAN**（hops=0）；B first-clean "
        "**441_604..441_803 CLEAN**（hops=0）——**naive B 落在 naive A 窗"
        "内**（W141 同窗互斥先例适用于 W194：W194 冻结方必须在 post-W193 "
        "注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；"
        "**W193 B 带 441_404..441_603 注册后将拒 naive W194 A 窗**——W194 A "
        "重 derive 同强制（越过 W193 B 带·阶梯 A-hops-prior-B 继承第五十四"
        "例）；verify at W194 prereg，hop 链逐跳在 probe 回执"),
    "@CLI@": "--wave 193/finalize --wave 193",
    "@ENG6@": (
        "点火面 `scripts/saturation_engine.py`（本机 bm-a 实例·**tick 架构"
        "**·本地队列→PreIgnitionChecks→分离子进程点火→完成→台账处理"
        "【runner_args --lane engine 车道闸同 r523 律】）；**点火验证=2 tick "
        "内产物增长面**【n1_w193/ 分片计数增长·唯一点火证据·r325 律】"),
    "@SHARD@": "results/p2cal_ext/n1_w193/shard-<k>-of-12.json",
    "@RFN@": "results/perpetual_faces/n1_w193_results.json",
    "@FINPRE@": (
        "finalize 键序前置=**起草窗在飞上游席 W192（bm-c·五面冻结在册）**——"
        "跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态例恒在"),
    "@EOBD@": (
        "引擎台账：bm-a tick 架构=engine ledger jsonl+state/face/history 以 "
        "git 交付（engine_owner==bm-a 107 行注册 + 本候选——以 probe leg0 "
        "机证为准）"),
    "@S7@": (
        "待 W193 finalize 窗】\n- （占位·finalize one-pass 后机械回填：账本恒"
        "等式+合并池 K+merged mu/w-only mu/mu_delta+sigma+se_mu+"
        "skill_line_v2 K-lift+A 档 p95+§5 四预键机证+canon flip 态+audit."
        "finalize_only+voids_applied。）"),
    "@S8@": (
        "【finalize 同窗回填·待 W193 finalize 窗】\n- （占位·§5.5 W194+ 投影"
        "承接+宝藏/方法论捕获问+诚实披露面·finalize 收口窗机械回填。）"),
    "@WAVEFREE@": "波号 193=注册表 W192 席后首个自由号",
}

# --- preflight DRY gate (r787 countcheck + r833 zero-write) -------------
print("DRY GATE: counting old sides in src (progressive, vmap-order) ...")
problems = []
out_t = src_t
for old, tok in TOK:
    n = out_t.count(old)
    if n != 1:
        problems.append((tok, n, old[:60]))
        continue
    out_t = out_t.replace(old, tok)
if problems:
    for tok, n, head in problems:
        print("  COUNT-FAIL %-14s count=%d head=%r" % (tok, n, head))
    raise SystemExit("DRY GATE red: %d pair(s) failed" % len(problems))
print("  all %d old sides count==1 (progressive vmap order)" % len(TOK))

# BACK phase on the tokenized text
for tok, new in BACK.items():
    out_t = out_t.replace(tok, new)
out_t = out_t.replace("SEED_REGISTRY \u5168\u952e @@REGN@@ \u503c",
                      "SEED_REGISTRY \u5168\u952e %d \u503c" % REG_N)
resid = re.findall(r"@[A-Z0-9]+@", out_t)
assert not resid, "residual tokens: %s" % resid[:6]
bad = [mm.group() for mm in
       re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", out_t)
       if int(mm.group(3)) < int(mm.group(1))]
assert not bad, "malformed windows: %s" % bad[:4]
# U+2212 display forms present, no ASCII minus in the four anchor keys
assert M + "0.0929" in out_t and M + "0.0898" in out_t, "U+2212 forms"
assert "0.245166" in out_t and "0.3049" in out_t and "0.000379" in out_t
# batch-id sanity (title + batchname + ledger = 3 hyphenated forms)
nb = out_t.count("PERPETUAL-N1-W193")
assert nb == 3, "batch id count=%d (expect 3: title+batchname+ledger)" % nb
# stale sweep: W192-era values that must have rolled
for stale in ("FIFTY-SECOND", "第五十二例", "0.245150", M + "0.0986",
              "**0.3068**", "825,328", "415,920", "823,128", "**1.1866**",
              "line_pre 1.1867", "n1_w190_results", "W190 实测键",
              "键 W190 实测", "**0.000380**", "ea42ee94a", "1abe1a57f",
              "MSG-20261008-2351", "bm-c 第三十五枚", "engine_owner==bm-c",
              "第 182 波", "W1..W190 ", "W2..W190 共一百八十九面",
              "泵第 190 枚", "437_204..439_203", "**B-ext exit seed=439_204..439_403**",
              "437_204+j", "439_204+j",
              "live daemon mtime-watch", "无 buildgen emission 链"):
    assert stale not in out_t, "stale survives: %r" % stale
# legal persistences (display-HOLD + chain mids)
assert M + "0.0929" in out_t, "merged-mu 4dp display hold missing"
assert out_t.count("W190 0.000380") == 1, "se_mu chain mid W190 missing"
assert out_t.count(M + "0.0001/W191") == 1, "K-lift chain mid missing"
assert "W191=bm-a r894 freeze（e5e4af81b）" in out_t, "chain W191 update missing"
assert "；W192=bm-c r787 freeze（f8703842c）。" in out_t, "chain W192 append missing"
print("  vmap simulation: residual-zero, malformed-zero, stale-sweep CLEAN")
print("DRY GATE: ALL GREEN (zero writes performed)")

# --- emit the build script ----------------------------------------------
def q(s):
    return repr(s)


tok_lit = "[\n" + ",\n".join("    (%s, %s)" % (q(o), q(t)) for o, t in TOK) + ",\n]"
back_lit = "{\n" + ",\n".join("    %s: %s" % (q(k), q(v))
            for k, v in BACK.items()) + "\n}"
emit_src = EMIT_TEMPLATE = '''# -*- coding: utf-8 -*-
"""r901 bm-a W193 per-wave prereg build (EMITTED by
results/_r901bma_w193_buildgen.py; pairs baked; live facts re-asserted
at run time per r587).  Src = results/_r901bma_w193_prereg_src.txt
(W192 prereg freeze-time blob 66b3c64123, byte-verbatim binary extract,
r877 law 4).  Output CRLF (r370 law)."""
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SRC = "results/_r901bma_w193_prereg_src.txt"
OUT = "research/PERPETUAL_N1_W193_PREREG.md"
G = r"%s"

def git(*a):
    r = subprocess.run(["git", "-C", G] + list(a), capture_output=True)
    return r.stdout.decode("utf-8", errors="replace").strip()

subprocess.run(["git", "-C", G, "fetch", "origin"], capture_output=True)
probe = json.load(open(r"results/_r900bma_w193_probe_receipt.json",
                      encoding="utf-8"))
assert probe["verdict"] == "ADMIT" and probe["bands"] == {
    "A": "439404_441403", "B": "441404_441603"}, probe
leg0 = probe["legs"]["leg0"]
assert leg0["rows"] == 190 and leg0["tail"] == "W192" and \\
    leg0["w191_ledger_head"] == 833536, leg0
assert leg0["ordinal"] == 183 and leg0["bma_ordinal"] == 108, leg0
res = json.load(open(r"results/perpetual_faces/n1_w191_results.json",
                     encoding="utf-8"))
assert res["null_pool_cumulative"]["merged"]["n_values"] == 418120
assert res["science_gates"]["ledger"]["total"] == 833536
_vac = git("log", "origin/main", "--format=%%h", "-n", "1", "-S",
           '193: {"a": (439_404', "--", "scripts/perpetual_faces.py")
assert _vac == "", "W193 five-face already on origin?!"
_fin = git("ls-tree", "origin/main",
           "results/perpetual_faces/n1_w192_results.json")
assert _fin == "", "W192 finalize landed -- anchor must roll to W192 (r590)!"

sys.path.insert(0, "scripts")
sys.path.insert(0, ".")
import science_gates as _sg  # noqa: E402
REG_N = len(_sg.SEED_REGISTRY)
assert REG_N == 191, "SEED_REGISTRY count drift: %%d" %% REG_N

TOK = %s
BACK = %s

src = io.open(SRC, encoding="utf-8").read()
assert src.count("\\r\\n") == 0, "src blob expected LF"
assert src.count("SEED_REGISTRY \\u5168\\u952e 190 \\u503c") == 1, \\
    "registry-count face not found in src"
src = src.replace("SEED_REGISTRY \\u5168\\u952e 190 \\u503c",
                  "SEED_REGISTRY \\u5168\\u952e @@REGN@@ \\u503c")
out_t = src
for old, tok in TOK:
    n = out_t.count(old)
    assert n == 1, "TOK %%s count=%%d" %% (tok, n)
    out_t = out_t.replace(old, tok)
for tok, new in BACK.items():
    out_t = out_t.replace(tok, new)
out_t = out_t.replace("SEED_REGISTRY \\u5168\\u952e @@REGN@@ \\u503c",
                      "SEED_REGISTRY \\u5168\\u952e %%d \\u503c" %% REG_N)
resid = re.findall(r"@[A-Z0-9]+@", out_t)
assert not resid, "unsubstituted tokens remain: %%s" %% resid[:5]
bad = [mm.group() for mm in
       re.finditer(r"(\\d{3})_(\\d{3})\\.(\\d{3})_(\\d{3})", out_t)
       if int(mm.group(3)) < int(mm.group(1))]
assert not bad, "malformed windows: %%s" %% bad[:4]
assert out_t.count("PERPETUAL-N1-W193") == 3, "batch id count drift"
M = "\\u2212"
for stale in ("FIFTY-SECOND", "第五十二例", "0.245150", M+"0.0986",
              "**0.3068**", "825,328", "415,920", "823,128", "**1.1866**",
              "line_pre 1.1867", "n1_w190_results", "W190 实测键",
              "键 W190 实测", "**0.000380**", "ea42ee94a", "1abe1a57f",
              "MSG-20261008-2351", "bm-c 第三十五枚", "engine_owner==bm-c",
              "第 182 波", "W1..W190 ", "W2..W190 共一百八十九面",
              "泵第 190 枚", "437_204..439_203", "**B-ext exit seed=439_204..439_403**",
              "437_204+j", "439_204+j",
              "live daemon mtime-watch", "无 buildgen emission 链"):
    assert stale not in out_t, "stale token survives: %%r" %% stale
assert M+"0.0929" in out_t and M+"0.0898" in out_t, "U+2212 forms"
assert out_t.count("W190 0.000380") == 1
assert "W191=bm-a r894 freeze（e5e4af81b）" in out_t
assert "；W192=bm-c r787 freeze（f8703842c）。" in out_t

open(OUT, "wb").write(out_t.replace("\\n", "\\r\\n").encode("utf-8"))
chk = io.open(OUT, encoding="utf-8", newline="").read()
assert chk == out_t.replace("\\n", "\\r\\n"), "CRLF roundtrip drift"
print("W193 prereg built: %%s bytes=%%d crlf=%%d" %%
      (OUT, len(chk.encode("utf-8")), chk.count("\\r\\n")))
print("post-transform asserts PASS (counts, residue-zero, "
      "malformed-zero, stale-sweep CLEAN, U+2212 forms)")
''' % (G, tok_lit, back_lit)
io.open(EMIT, "w", encoding="utf-8", newline="\n").write(emit_src)
print("EMITTED:", EMIT, len(emit_src), "bytes")
print("buildgen complete: DRY gate green -> emitted build script (run it next)")
