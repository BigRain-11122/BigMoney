# -*- coding: utf-8 -*-
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
G = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"

def git(*a):
    r = subprocess.run(["git", "-C", G] + list(a), capture_output=True)
    return r.stdout.decode("utf-8", errors="replace").strip()

subprocess.run(["git", "-C", G, "fetch", "origin"], capture_output=True)
probe = json.load(open(r"results/_r900bma_w193_probe_receipt.json",
                      encoding="utf-8"))
assert probe["verdict"] == "ADMIT" and probe["bands"] == {
    "A": "439404_441403", "B": "441404_441603"}, probe
leg0 = probe["legs"]["leg0"]
assert leg0["rows"] == 190 and leg0["tail"] == "W192" and \
    leg0["w191_ledger_head"] == 833536, leg0
assert leg0["ordinal"] == 183 and leg0["bma_ordinal"] == 108, leg0
res = json.load(open(r"results/perpetual_faces/n1_w191_results.json",
                     encoding="utf-8"))
assert res["null_pool_cumulative"]["merged"]["n_values"] == 418120
assert res["science_gates"]["ledger"]["total"] == 833536
_vac = git("log", "origin/main", "--format=%h", "-n", "1", "-S",
           '193: {"a": (439_404', "--", "scripts/perpetual_faces.py")
assert _vac == "", "W193 five-face already on origin?!"
_fin = git("ls-tree", "origin/main",
           "results/perpetual_faces/n1_w192_results.json")
assert _fin == "", "W192 finalize landed -- anchor must roll to W192 (r590)!"

sys.path.insert(0, "scripts")
sys.path.insert(0, ".")
import science_gates as _sg  # noqa: E402
REG_N = len(_sg.SEED_REGISTRY)
assert REG_N == 191, "SEED_REGISTRY count drift: %d" % REG_N

TOK = [
    ('W118=bm-b r678 freeze（565e5b0b4）；W119=bm-a r701 freeze（907e1e187）；W120=bm-a r725 freeze；W121=bm-a r726 freeze（8dcb2e60c）；W122=bm-a r727 freeze（69466f13）；W123=bm-a r728 freeze（d049a2ab）；W124=bm-a r729 freeze（bebad2e18）；W125=bm-a r730 freeze（7cd1f6ee）；W126=bm-a r731 freeze（db9da0e92）；W127=bm-a r732 freeze（b70372381）；W128=bm-a r733 freeze（6ce3f5d6）；W129=bm-a r734 freeze（e8d140ef）；W130=bm-a r735 freeze（b8b308db）；W131=bm-a r736 freeze（cd6667e8）；W136=bm-a r741 freeze（cafbc7ab）；W137=bm-a r742 freeze（f9e4ec5d2）；W138=bm-a r743 freeze（798a1e5f）；W139=bm-a r744 freeze（4e3a018c7）；W140=bm-a r745 freeze（5e3984200）；W141=bm-a r747 freeze（7ffadab65）；W144=bm-a r752 freeze（ff6d2f918）；W145=bm-a r754 freeze（98c661f8f）；W146=bm-a r755 freeze（8f06f6910）；W147=bm-a r757 freeze（3961555de）；W148=bm-a r759 freeze（92c5ab03c）；W149=bm-a r761 freeze（0cef02a00）；W150=bm-a r762 freeze（fedebeb32）；W151=bm-a r763 freeze（bd4cd7159）；W155=bm-a r768 freeze（dde679c63）；W156=bm-a r771 freeze（13c989ba0）；W157=bm-a r772 freeze（aed41df3e）；W158=bm-a r775 freeze（6957f509e）；W159=bm-a r781 freeze（6ee1207bb）；W160=bm-a r783 freeze（ee04482a2）；W161=bm-a r785 freeze（678a07d4f）；W162=bm-a r787 freeze（764cd882a）；W163=bm-a r789 freeze（18231a529）；W165=bm-a r792 freeze（f7d34e5a7）；W165=bm-a r795 freeze（aebb94d2d）；W166=bm-a r799 freeze（c2d6c5e14）；W167=bm-a r805 freeze（f61835690）；W168=bm-a r809 freeze（8d8842b61）；W169=bm-a r811 freeze（9c2271baf）；W170=bm-a r813 freeze（cb7314d64）；W171=bm-a r815 freeze（456f3affc）；W172=bm-a r819 freeze（59fde9319）；W173=bm-a r822 freeze（04e95748a）；W174=bm-a r826 freeze（db42a0d46）；W175=bm-a r830 freeze（f3fca4055）；W176=bm-a r834 freeze（15ec44ea6）；W177=bm-a r843 freeze（c06cc230f）；W178=bm-a r845 freeze（de4716da2）；W179=bm-a r849 freeze（ef540bf8f）；W180=bm-a r852 freeze（568848aa4）；W181=bm-a r863 freeze（de699e8cd）；W182=bm-a r867 freeze（385dbafd8）；W183=bm-a r869 freeze（481da4d78）；W184=bm-a r874 freeze（7e791a87f）；W185=bm-a r878 freeze（beb4b5abd）；W186=bm-a r882 freeze（14177b161）；W187=bm-a r886 freeze（79c9a567c）；W188=bm-a r888 freeze（b66117659）；W189=bm-a r890 freeze（8addea3eb）；W190=bm-a r892 freeze（0cce3c47e）；W191=bm-a r892 席位+r893 prereg freeze（ea42ee94a）', '@CHAIN@'),
    ('# PERPETUAL-N1-W192 预注册 · N1 nulls-deepening 泵第 190 枚（never-dry 常供给例波·波序号连续·机面 derive：engine_owner 行 180 注册在册+W191 五面在飞+本候选=bm-c 第三十五枚自有波【bm-c 交互窗 2026-10-08 23:5x·CEO 领单直令】）', '@TITLE@'),
    ('引擎核=self 仓单源脚本·本机 bm-c 实例=**live daemon mtime-watch 热重载架构**——冻结编辑落工作栈后引擎下一 cycle n1_bands() mtime 复读自见新行自烧【r535 律·D-20261002-03 fix ①】·点火验证唯一证据=2 cycle 内产物增长面【r325 律·state queue 面不修】）→ **never-dry 常供给例波**：**O-20261001-2355 CEO 去节流令 §二**【每机自烧连续系列不等等待·down-series 续跑】+ O-20260929-2355 同窗同律共引+ **本窗领取令=CEO 直令 2026-10-08 ~23:5x「你的机器CPU算力闲置严重，自己去领回测任务！排满」**【bm-c 交互窗直执·O-20260924-1730 认领即开动同轮律·本机引擎队列自 wave-115 时代空转实测（saturation_engine_state.bm-c.json queue_next 空·py_cpu 0.23% 实读）】。', '@INST@'),
    ('【本冻结窗 fetch 实核表尾时 W192 号位空档·rg 行 WAVE_CONFIGS+prereg 路径三查+origin ls-tree vacancy 机证（本窗 probe leg3 实跑）；全 inbox/processed/ W192 席位零外机命中；**W191=bm-a r892 席位 MSG-2026-10-08-2130+r893 prereg freeze（ea42ee94a）在册·五面 band row 在飞未落 origin 如实注记——本波注册宇宙=W191 声明带注入（W191 prereg 原文 origin 文本验证·probe leg0 机证）·r892 W191 probe leg4 强制令兑现**；本机席位公示=MSG-20261008-2351-bmc-w192-seat 已推 origin 1abe1a57f 先于本冻结【r565 律·§6.1.4 API 直构零本地 commit 通道如实注记】】', '@SEATBLOCK@'),
    ('本波 **A-ext seed=437_204..439_203**（**A 面=FIRST-CLEAN past prior-wave B 阶梯第五十二例**：A 面算术继续带 437_004..439_003 在其起点即被 W191 声明 B 带 437_004..437_203 **拒**（W191 §5.5 投影+r892 probe leg4+W191 席位 W192+ 投影散文所预言+强制）→ 诚实前向走 **1 hop** 落 **437_204..439_203**·**A base==前波 B 尾+1（437_203+1）机检关系**=**A-hops-prior-B 阶梯几何第五十二例（E36 卡）**·非轮转 r587 前向单调断言在走册；序数面如实披露：W191 §5.5 投影预告第五十二例·本窗 probe 回执 A_semantics 机读序数=FIFTY-SECOND（第五十二例）·本件按回执序数面记载非转抄（r587）·投影与回执两读法恒同）', '@AFACE@'),
    ('**B-ext exit seed=439_204..439_403**（**B 面=FIRST-CLEAN past own-wave A**：B 面算术继续带 437_204..437_403 在声明宇宙上 CLEAN 但**落在本波 A 窗 437_204..439_203 内**（**同窗互斥面 leg2 律·W141 先例**：A 与 B 同一冻结 commit 双注册·互斥断言强制 B 越过本波 A 窗）→ B 带本波 A 窗保留走 **1 hop** 落 **439_204..439_403**·**B base==本波 A 尾+1（439_203+1）机检关系**·hop 链逐跳在 probe 回执；**W191 §5.5 投影+r892 probe leg4 承接面注记三面兑现**：投影预言 W192 须在 post-W191 注册宇宙重 derive 且 derive B 时预留本波 A 窗——本窗双面兑现·A 被拒+阶梯越带如投影所期·B 同窗互斥保留=投影所期·已如实披露非分叉）', '@BFACE@'),
    ('扫描面=pre-W192 全一百八十八行注册 N1 带表（表尾 W190 行·leg0 机证 188 行）+W191 声明带两条注入（origin 文本验证）', '@SCANFACE@'),
    ('R250：W192 带从未指派·测量面零结果可锁', '@R250@'),
    ('results/_w192bmc_20261009_probe_receipt.json', '@PRCR@'),
    ('W2..W191 落地 runner 的 wave 参数化复用', '@RUNNERW@'),
    ('引擎侧 `scripts/saturation_engine.py`【本机 bm-c 实例·live daemon mtime-watch 热重载架构】只做队列点火台账处理面·runner 零改写。**本冻结=交互窗直笔+探针机证（无 buildgen emission 链——extraction-from-emission 律 N/A 诚实注记·五腿探针回执在场为准·selftest W192 face 将随五面冻结落地验证）。**', '@ENGNOTE@'),
    ('批名=**PERPETUAL-N1-W192**', '@BATCHNAME@'),
    ('起稿窗实况：**W1..W190 N1 finalize 已全部落地**【净账本锚头 **825,328**·K=415,920 合并池·n1_w190_results.json 机读】；**W191=bm-a 席位+prereg 冻结在册·五面 band row 在飞未落 origin（dead-tail adoption in flight）——本波上游在飞席注记=W191·「零在飞上游链前」断言不适用改如实注记**', '@ANCHOR0@'),
    ('累计 null 池=415,920+2,200（W191 投影）+2,200（本波）=**420,320 投影**', '@POOL@'),
    ('- 认领：never-dry 常供给例波（TRIAL_LABOR_LAW §4·板空/池饿/无在飞判决批=默认续跑下一波——本机引擎队列空转+池 408 条全 done 实读；**CEO 直令 2026-10-08 ~23:5x 领单**（本机席位 MSG-20261008-2351-bmc-w192-seat 已推 origin 1abe1a57f r565 律·probe W193+ 投影 A 439_204..441_203 / B 439_404..439_603 **naive-B-inside-naive-A re-derive 强制注记+同窗互斥预披露**（投影 B 落投影 A 窗内·W192 B 带 439_204..439_403 注册后将拒 naive W193 A 窗=阶梯 A-hops-prior-B 继承第五十三例待 W193 注册宇宙复核））；O-20260924-1730 CEO 即时律（认领与开动同轮·禁排未来轮次）；T-2026-10-01-141 s1 引擎线第 182 波【bm-c 第三十五枚自有波【机面 derive：engine_owner==bm-c 行 34+本候选以 probe leg0 机证为准】】。（波号=注册表 W191 席后首个自由号·单态零席位空档；中位公示 MSG-20261008-2351-bmc-w192-seat 先推 origin 1abe1a57f r565 律；lane-free；dept:研究）。', '@CLAIM@'),
    ('（N1_BANDS 单源 derive·engine_owner==bm-c 波的未烧分片=本地队列项；per-wave prereg 在场=物化前置条件）；池面 supply 生成器对 engine_owner 波群跳过物化【cmd_supply owner 跳过闸防零号双烧面】；**引擎实况注记（本机 bm-c 实例=live daemon mtime-watch 热重载——五面冻结编辑落工作栈后引擎下一 cycle n1_bands() mtime 复读自见 W192 行并点火自烧【r535 律·D-20261002-03 fix ①·r325/r330 kill-restart 序免做】。**点火验证唯一证据=产物增长面**【r325 律·2 cycle 窗】·RAM face 随 cycle 上报。', '@MATCOND@'),
    ('--prereg research/PERPETUAL_N1_W192_PREREG.md', '@GATECMD@'),
    ('v2..W190 落地）的种子带扩展重测', '@V2W@'),
    ('entry rng seed=**437_204+j**（法典 §4 W192 行 A=437_204..439_203·**FIRST-CLEAN past prior-wave B 阶梯第五十二例**：算术续带 437_004..439_003 起点即被 W191 声明 B 带拒→1 hop 落 437_204..439_203·A base==前波 B 尾+1 机检关系·E36 卡·hops=1·ADMIT 回执在场）', '@ASEED@'),
    ('entry rng=**437_204+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）', '@BENTRY@'),
    ('exit rng=**439_204+j**（法典 §4 W192 行 B=439_204..439_403·**FIRST-CLEAN past own-wave A**：B 算术续带 437_204..437_403 在声明宇宙上 CLEAN 但落在本波 A 窗 437_204..439_203 内→**同窗互斥面 leg2 律·W141 先例**强制 B 越本波 A 窗→保留走落 439_204..439_403·hops=1·**B base==本波 A 尾+1 机检关系**·非轮转 r587·hop 链逐跳在 probe 回执·与 W191 §5.5 投影+r892 probe leg4 承接面注记兑现收敛·ADMIT 回执在场）', '@BSEED@'),
    ('本波设计=W2..W191 逐字复用', '@PROBEW@'),
    ('W192 带与 v1 在用带（10_000..10_099/20_000..20_019）、W1 ext 带（10_100..12_099/20_100..20_299）、W2..W191 带（**全注册单态+W191 声明带注入**）', '@DISJ@'),
    ('本波机验 ADMIT 回执在场=_w192bmc_20261009 探针窗（pre-seat probe 单窗·gate 腿合并结构承袭 r812/r820/r823 先例·parity N/A 诚实注记）；selftest W192 face（A=first-clean past prior-wave B 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W191 行 parity 腿【r735 测量-实现分叉族防护面：A/B 窗 set-range 针在场】）随五面冻结落地', '@GATEW2@'),
    ('已落账净值（起草窗实流 W1..W190 已落账 415,920 实测·derive 禁手抄）+W191 2,200（在飞）+本波 2,200', '@POOL4@'),
    ('batch_name="PERPETUAL-N1-W192", batch_trials=2200, file_name="results/perpetual_faces/n1_w192_results.json"', '@LEDGER@'),
    ('（起草窗实况注记：**W1..W190 N1 finalize 已全部落地**——净账本锚头 825,328·**K=415,920 合并池**·**W191 在飞上游席注记（bm-a·prereg 冻结·五面在飞未落）——本波 §5 预测键=**W190 实测值**【results/perpetual_faces/n1_w190_results.json·N1 面最新已落账键·W191 落账后属上游先决非本键面】', '@S5ANCH@'),
    ('1. W192-only mu 与累计池 merged mu（W190 实测键 **−0.0929**·K=415,920 合并池·W190-only 实测 **−0.0986**）差异 **|Δ|<0.02**（W2..W190 共一百八十九面实测 mu 稳定先例·单波跨键微）', '@S51@'),
    ('2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.245150**=W190 合并池实测 0.245150）', '@S52@'),
    ('3. A 档 full_sharpe_p95 与 W190 A 档 p95（**0.3068** 实测锚）差 **<0.05**（门标注法 W5..W190 先例', '@S53@'),
    ('4. K-lift 线移动幅度 **≤±0.02**（累计池加深零 se_mu 收窄线自 mu/sigma 微调面非质变——W136..W190 先例链披露【W186 −0.0001/W187 +0.0002/W188 +0.0000/W189 +0.0003/W190 −0.0001·键 W190 实测 K-lift **−0.0001**·line_merged@K415,920 **1.1866**·line_pre 1.1867·n_eff 823,128；se_mu 收窄链 W188 0.000382→W189 0.000381→W190 **0.000380**】）', '@S54@'),
    ('5. **W193+ 投影（probe 机证·下波冻结方复核非转抄 r587 律）**：A first-clean 439_204..441_203 **CLEAN**（hops=0）；B first-clean **439_404..439_603 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W193：W193 冻结方必须在 post-W192 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W192 B 带 439_204..439_403 注册后将拒 naive W193 A 窗**——W193 A 重 derive 同强制（越过 W192 B 带·阶梯 A-hops-prior-B 继承第五十三例）；verify at W193 prereg，hop 链逐跳在 probe 回执', '@S55@'),
    ('--wave 192/finalize --wave 192', '@CLI@'),
    ('点火面 `scripts/saturation_engine.py`（本机 bm-c 实例·**live daemon mtime-watch 热重载**·本地队列→PreIgnitionChecks→分离子进程点火→完成→台账处理【runner_args --lane engine 车道闸同 r523 律】）；**点火验证=2 cycle 内产物增长面**【n1_w192/ 分片计数增长·唯一点火证据·r325 律】', '@ENG6@'),
    ('results/p2cal_ext/n1_w192/shard-<k>-of-12.json', '@SHARD@'),
    ('results/perpetual_faces/n1_w192_results.json', '@RFN@'),
    ('finalize 键序前置=**起草窗在飞上游席 W191（bm-a·prereg 冻结）**——跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态例恒在', '@FINPRE@'),
    ('引擎台账：bm-c live daemon 架构=engine ledger jsonl+state/face/history 以 git 交付（engine_owner==bm-c 34 行注册 + 本候选——以 probe leg0 机证为准）', '@EOBD@'),
    ('待 W192 finalize 窗】\n- （占位·finalize one-pass 后机械回填：账本恒等式+合并池 K+merged mu/w-only mu/mu_delta+sigma+se_mu+skill_line_v2 K-lift+A 档 p95+§5 四预键机证+canon flip 态+audit.finalize_only+voids_applied。）', '@S7@'),
    ('【finalize 同窗回填·待 W192 finalize 窗】\n- （占位·§5.5 W193+ 投影承接+宝藏/方法论捕获问+诚实披露面·finalize 收口窗机械回填。）', '@S8@'),
    ('波号 192=注册表 W191 席后首个自由号', '@WAVEFREE@'),
]
BACK = {
    '@CHAIN@': 'W118=bm-b r678 freeze（565e5b0b4）；W119=bm-a r701 freeze（907e1e187）；W120=bm-a r725 freeze；W121=bm-a r726 freeze（8dcb2e60c）；W122=bm-a r727 freeze（69466f13）；W123=bm-a r728 freeze（d049a2ab）；W124=bm-a r729 freeze（bebad2e18）；W125=bm-a r730 freeze（7cd1f6ee）；W126=bm-a r731 freeze（db9da0e92）；W127=bm-a r732 freeze（b70372381）；W128=bm-a r733 freeze（6ce3f5d6）；W129=bm-a r734 freeze（e8d140ef）；W130=bm-a r735 freeze（b8b308db）；W131=bm-a r736 freeze（cd6667e8）；W136=bm-a r741 freeze（cafbc7ab）；W137=bm-a r742 freeze（f9e4ec5d2）；W138=bm-a r743 freeze（798a1e5f）；W139=bm-a r744 freeze（4e3a018c7）；W140=bm-a r745 freeze（5e3984200）；W141=bm-a r747 freeze（7ffadab65）；W144=bm-a r752 freeze（ff6d2f918）；W145=bm-a r754 freeze（98c661f8f）；W146=bm-a r755 freeze（8f06f6910）；W147=bm-a r757 freeze（3961555de）；W148=bm-a r759 freeze（92c5ab03c）；W149=bm-a r761 freeze（0cef02a00）；W150=bm-a r762 freeze（fedebeb32）；W151=bm-a r763 freeze（bd4cd7159）；W155=bm-a r768 freeze（dde679c63）；W156=bm-a r771 freeze（13c989ba0）；W157=bm-a r772 freeze（aed41df3e）；W158=bm-a r775 freeze（6957f509e）；W159=bm-a r781 freeze（6ee1207bb）；W160=bm-a r783 freeze（ee04482a2）；W161=bm-a r785 freeze（678a07d4f）；W162=bm-a r787 freeze（764cd882a）；W163=bm-a r789 freeze（18231a529）；W165=bm-a r792 freeze（f7d34e5a7）；W165=bm-a r795 freeze（aebb94d2d）；W166=bm-a r799 freeze（c2d6c5e14）；W167=bm-a r805 freeze（f61835690）；W168=bm-a r809 freeze（8d8842b61）；W169=bm-a r811 freeze（9c2271baf）；W170=bm-a r813 freeze（cb7314d64）；W171=bm-a r815 freeze（456f3affc）；W172=bm-a r819 freeze（59fde9319）；W173=bm-a r822 freeze（04e95748a）；W174=bm-a r826 freeze（db42a0d46）；W175=bm-a r830 freeze（f3fca4055）；W176=bm-a r834 freeze（15ec44ea6）；W177=bm-a r843 freeze（c06cc230f）；W178=bm-a r845 freeze（de4716da2）；W179=bm-a r849 freeze（ef540bf8f）；W180=bm-a r852 freeze（568848aa4）；W181=bm-a r863 freeze（de699e8cd）；W182=bm-a r867 freeze（385dbafd8）；W183=bm-a r869 freeze（481da4d78）；W184=bm-a r874 freeze（7e791a87f）；W185=bm-a r878 freeze（beb4b5abd）；W186=bm-a r882 freeze（14177b161）；W187=bm-a r886 freeze（79c9a567c）；W188=bm-a r888 freeze（b66117659）；W189=bm-a r890 freeze（8addea3eb）；W190=bm-a r892 freeze（0cce3c47e）；W191=bm-a r894 freeze（e5e4af81b）；W192=bm-c r787 freeze（f8703842c）',
    '@TITLE@': '# PERPETUAL-N1-W193 预注册 · N1 nulls-deepening 泵第 191 枚（never-dry 常供给例波·波序号连续·机面 derive：engine_owner 行 182 注册在册+W192 finalize 在飞+本候选=bm-a 第一百零八枚自有波【bm-a r901·buildgen 血统 r830/r833/r877 承袭】）',
    '@INST@': '引擎核=self 仓单源脚本·本机 bm-a 实例=**tick 架构**——冻结编辑落工作栈后下一 tick 新进程读活栈自见新行自烧【r535 律】·点火验证唯一证据=2 tick 内产物增长面【r325 律·state queue 面不修】）→ **never-dry 常供给例波**：**O-20261001-2355 CEO 去节流令 §二**【每机自烧连续系列不等等待·down-series 续跑】。',
    '@SEATBLOCK@': '【本冻结窗 fetch 实核表尾时 W193 号位空档·rg 行 WAVE_CONFIGS+prereg 路径三查+origin ls-tree vacancy 机证（本窗 probe leg3 实跑）；全 inbox/processed/ W193 席位零外机命中；**W192=bm-c r787 五面冻结 f8703842c 在册·finalize 在飞未落 origin 如实注记——本波注册宇宙=W192 注册带在册（N1_BANDS 注册行机器读·probe leg0 机证 190 行表尾 W192）·r900 W193 probe 全腿机证**；本机席位公示=MSG-2026-10-09-0458-bma-w193-seat 已推 origin 9df3078c5 先于本冻结【r565 律·推送窗=r900 seat push 直接快进送达 9df3078c5（payload=seat MSG+W193 pre-seat probe 脚本+回执同推）；self-ack inbox→processed 移位随五面冻结窗收口归档（如实注记）】】',
    '@AFACE@': '本波 **A-ext seed=439_404..441_403**（**A 面=FIRST-CLEAN past prior-wave B 阶梯第五十三例**：A 面算术继续带 439_204..441_203 在其起点即被 W192 注册 B 带 439_204..439_403 **拒**（W192 §5.5 投影+bm-c r787 probe leg4+W192 认领投影散文所预言+强制）→ 诚实前向走 **1 hop** 落 **439_404..441_403**·**A base==前波 B 尾+1（439_403+1）机检关系**=**A-hops-prior-B 阶梯几何第五十三例（E36 卡）**·非轮转 r587 前向单调断言在走册；序数面如实披露：W192 §5.5 投影预告第五十三例·本窗 probe 回执 A_semantics 机读序数=FIFTY-THIRD（第五十三例）·本件按回执序数面记载非转抄（r587）·投影与回执两读法恒同）',
    '@BFACE@': '**B-ext exit seed=441_404..441_603**（**B 面=FIRST-CLEAN past own-wave A**：B 面算术继续带 439_404..439_603 在声明宇宙上 CLEAN 但**落在本波 A 窗 439_404..441_403 内**（**同窗互斥面 leg2 律·W141 先例**：A 与 B 同一冻结 commit 双注册·互斥断言强制 B 越过本波 A 窗）→ B 带本波 A 窗保留走 **1 hop** 落 **441_404..441_603**·**B base==本波 A 尾+1（441_403+1）机检关系**·hop 链逐跳在 probe 回执；**W192 §5.5 投影+bm-c r787 probe leg4 承接面注记三面兑现**：投影预言 W193 须在 post-W192 注册宇宙重 derive 且 derive B 时预留本波 A 窗——本窗双面兑现·A 被拒+阶梯越带如投影所期·B 同窗互斥保留=投影所期·已如实披露非分叉）',
    '@SCANFACE@': '扫描面=pre-W193 全一百九十行注册 N1 带表（表尾 W192 行·leg0 机证 190 行）',
    '@R250@': 'R250：W193 带从未指派·测量面零结果可锁',
    '@PRCR@': 'results/_r900bma_w193_probe_receipt.json',
    '@RUNNERW@': 'W2..W192 落地 runner 的 wave 参数化复用',
    '@ENGNOTE@': '引擎侧 `scripts/saturation_engine.py`【本机 bm-a 实例·tick 架构】只做队列点火台账处理面·runner 零改写。**本冻结=buildgen emission 链（r830/r833/r877 血统承袭·TOK 两相 vmap+DRY 全文件门零写入先行+U+2212 显示形·五腿探针回执在场为准·selftest W193 face 将随五面冻结落地验证）。**',
    '@BATCHNAME@': '批名=**PERPETUAL-N1-W193**',
    '@ANCHOR0@': '起稿窗实况：**W1..W191 N1 finalize 已全部落地**【净账本锚头 **833,536**·K=418,120 合并池·n1_w191_results.json 机读】；**W192=bm-c 五面冻结在册（f8703842c）·finalize 在飞未落 origin——本波上游在飞席注记=W192·「零在飞上游链前」断言不适用改如实注记**',
    '@POOL@': '累计 null 池=418,120+2,200（W192 投影）+2,200（本波）=**422,520 投影**',
    '@CLAIM@': '- 认领：never-dry 常供给例波（TRIAL_LABOR_LAW §4·板空/池饿/无在飞判决批=默认续跑下一波——本机 r900 席位 MSG-2026-10-09-0458-bma-w193-seat 已推 origin 9df3078c5（r900 seat push·r565 律）·probe W194+ 投影 A 441_404..443_403 / B 441_604..441_803 **naive-B-inside-naive-A re-derive 强制注记+同窗互斥预披露**（投影 B 落投影 A 窗内·W193 B 带 441_404..441_603 注册后将拒 naive W194 A 窗=阶梯 A-hops-prior-B 继承第五十四例待 W194 注册宇宙复核）。表尾后新首个自由号自领·r900 probe 单跑兑现注记（本窗冻结消费）；O-20260924-1730 CEO 即时律（认领与开动同轮·禁排未来轮次）；T-2026-10-01-141 s1 引擎线第 183 波【bm-a 第一百零八枚自有波【机面 derive：engine_owner==bm-a 行 107+本候选以 probe leg0 机证为准】】。（波号=注册表 W192 席后首个自由号·单态零席位空档；中位公示 MSG-2026-10-09-0458-bma-w193-seat 先推 origin 9df3078c5 r565 律；lane-free；dept:研究）。',
    '@MATCOND@': '（N1_BANDS 单源 derive·engine_owner==bm-a 波的未烧分片=本地队列项；per-wave prereg 在场=物化前置条件）；池面 supply 生成器对 engine_owner 波群跳过物化【cmd_supply owner 跳过闸防零号双烧面】；**引擎实况注记（本机 bm-a 实例=**tick 架构**——五面冻结编辑落工作栈后引擎下一 tick 新进程读活栈自见 W193 行并点火自烧【r535 律·r325/r330 kill-restart 序免做】。**点火验证唯一证据=产物增长面**【r325 律·tick 窗】·RAM floor gate 机器例在场=自点火当 RAM 清】。',
    '@GATECMD@': '--prereg research/PERPETUAL_N1_W193_PREREG.md',
    '@V2W@': 'v2..W191 落地）的种子带扩展重测',
    '@ASEED@': 'entry rng seed=**439_404+j**（法典 §4 W193 行 A=439_404..441_403·**FIRST-CLEAN past prior-wave B 阶梯第五十三例**：算术续带 439_204..441_203 起点即被 W192 注册 B 带拒→1 hop 落 439_404..441_403·A base==前波 B 尾+1 机检关系·E36 卡·hops=1·ADMIT 回执在场）',
    '@BENTRY@': 'entry rng=**439_404+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）',
    '@BSEED@': 'exit rng=**441_404+j**（法典 §4 W193 行 B=441_404..441_603·**FIRST-CLEAN past own-wave A**：B 算术续带 439_404..439_603 在声明宇宙上 CLEAN 但落在本波 A 窗 439_404..441_403 内→**同窗互斥面 leg2 律·W141 先例**强制 B 越本波 A 窗→保留走落 441_404..441_603·hops=1·**B base==本波 A 尾+1 机检关系**·非轮转 r587·hop 链逐跳在 probe 回执·与 W192 §5.5 投影+bm-c r787 probe leg4 承接面注记兑现收敛·ADMIT 回执在场）',
    '@PROBEW@': '本波设计=W2..W192 逐字复用',
    '@DISJ@': 'W193 带与 v1 在用带（10_000..10_099/20_000..20_019）、W1 ext 带（10_100..12_099/20_100..20_299）、W2..W192 带（**全注册单态**）',
    '@GATEW2@': '本波机验 ADMIT 回执在场=_r900bma_w193 探针窗（pre-seat probe 单窗·gate 腿合并结构承袭 r812/r820/r823 先例·parity N/A 诚实注记）；selftest W193 face（A=first-clean past prior-wave B 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W192 行 parity 腿【r735 测量-实现分叉族防护面：A/B 窗 set-range 针在场】）随五面冻结落地',
    '@POOL4@': '已落账净值（起草窗实流 W1..W191 已落账 418,120 实测·derive 禁手抄）+W192 2,200（在飞）+本波 2,200',
    '@LEDGER@': 'batch_name="PERPETUAL-N1-W193", batch_trials=2200, file_name="results/perpetual_faces/n1_w193_results.json"',
    '@S5ANCH@': '（起草窗实况注记：**W1..W191 N1 finalize 已全部落地**——净账本锚头 833,536·**K=418,120 合并池**·**W192 在飞上游席注记（bm-c·五面冻结在册·finalize 在飞未落）——本波 §5 预测键=**W191 实测值**【results/perpetual_faces/n1_w191_results.json·N1 面最新已落账键·W192 落账后属上游先决非本键面】',
    '@S51@': '1. W193-only mu 与累计池 merged mu（W191 实测键 **−0.0929**·K=418,120 合并池·W191-only 实测 **−0.0898**）差异 **|Δ|<0.02**（W2..W191 共一百九十面实测 mu 稳定先例·单波跨键微）',
    '@S52@': '2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.245166**=W191 合并池实测 0.245166）',
    '@S53@': '3. A 档 full_sharpe_p95 与 W191 A 档 p95（**0.3049** 实测锚）差 **<0.05**（门标注法 W5..W191 先例',
    '@S54@': '4. K-lift 线移动幅度 **≤±0.02**（累计池加深零 se_mu 收窄线自 mu/sigma 微调面非质变——W136..W191 先例链披露【W187 +0.0002/W188 +0.0000/W189 +0.0003/W190 −0.0001/W191 **+0.0001**·键 W191 实测 K-lift **+0.0001**·line_merged@K418,120 **1.1872**·line_pre 1.1871·n_eff 831,336；se_mu 收窄链 W189 0.000381→W190 0.000380→W191 **0.000379**】）',
    '@S55@': '5. **W194+ 投影（probe 机证·下波冻结方复核非转抄 r587 律）**：A first-clean 441_404..443_403 **CLEAN**（hops=0）；B first-clean **441_604..441_803 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W194：W194 冻结方必须在 post-W193 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W193 B 带 441_404..441_603 注册后将拒 naive W194 A 窗**——W194 A 重 derive 同强制（越过 W193 B 带·阶梯 A-hops-prior-B 继承第五十四例）；verify at W194 prereg，hop 链逐跳在 probe 回执',
    '@CLI@': '--wave 193/finalize --wave 193',
    '@ENG6@': '点火面 `scripts/saturation_engine.py`（本机 bm-a 实例·**tick 架构**·本地队列→PreIgnitionChecks→分离子进程点火→完成→台账处理【runner_args --lane engine 车道闸同 r523 律】）；**点火验证=2 tick 内产物增长面**【n1_w193/ 分片计数增长·唯一点火证据·r325 律】',
    '@SHARD@': 'results/p2cal_ext/n1_w193/shard-<k>-of-12.json',
    '@RFN@': 'results/perpetual_faces/n1_w193_results.json',
    '@FINPRE@': 'finalize 键序前置=**起草窗在飞上游席 W192（bm-c·五面冻结在册）**——跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态例恒在',
    '@EOBD@': '引擎台账：bm-a tick 架构=engine ledger jsonl+state/face/history 以 git 交付（engine_owner==bm-a 107 行注册 + 本候选——以 probe leg0 机证为准）',
    '@S7@': '待 W193 finalize 窗】\n- （占位·finalize one-pass 后机械回填：账本恒等式+合并池 K+merged mu/w-only mu/mu_delta+sigma+se_mu+skill_line_v2 K-lift+A 档 p95+§5 四预键机证+canon flip 态+audit.finalize_only+voids_applied。）',
    '@S8@': '【finalize 同窗回填·待 W193 finalize 窗】\n- （占位·§5.5 W194+ 投影承接+宝藏/方法论捕获问+诚实披露面·finalize 收口窗机械回填。）',
    '@WAVEFREE@': '波号 193=注册表 W192 席后首个自由号'
}

src = io.open(SRC, encoding="utf-8").read()
assert src.count("\r\n") == 0, "src blob expected LF"
assert src.count("SEED_REGISTRY \u5168\u952e 190 \u503c") == 1, \
    "registry-count face not found in src"
src = src.replace("SEED_REGISTRY \u5168\u952e 190 \u503c",
                  "SEED_REGISTRY \u5168\u952e @@REGN@@ \u503c")
out_t = src
for old, tok in TOK:
    n = out_t.count(old)
    assert n == 1, "TOK %s count=%d" % (tok, n)
    out_t = out_t.replace(old, tok)
for tok, new in BACK.items():
    out_t = out_t.replace(tok, new)
out_t = out_t.replace("SEED_REGISTRY \u5168\u952e @@REGN@@ \u503c",
                      "SEED_REGISTRY \u5168\u952e %d \u503c" % REG_N)
resid = re.findall(r"@[A-Z0-9]+@", out_t)
assert not resid, "unsubstituted tokens remain: %s" % resid[:5]
bad = [mm.group() for mm in
       re.finditer(r"(\d{3})_(\d{3})\.(\d{3})_(\d{3})", out_t)
       if int(mm.group(3)) < int(mm.group(1))]
assert not bad, "malformed windows: %s" % bad[:4]
assert out_t.count("PERPETUAL-N1-W193") == 3, "batch id count drift"
M = "\u2212"
for stale in ("FIFTY-SECOND", "第五十二例", "0.245150", M+"0.0986",
              "**0.3068**", "825,328", "415,920", "823,128", "**1.1866**",
              "line_pre 1.1867", "n1_w190_results", "W190 实测键",
              "键 W190 实测", "**0.000380**", "ea42ee94a", "1abe1a57f",
              "MSG-20261008-2351", "bm-c 第三十五枚", "engine_owner==bm-c",
              "第 182 波", "W1..W190 ", "W2..W190 共一百八十九面",
              "泵第 190 枚", "437_204..439_203", "**B-ext exit seed=439_204..439_403**",
              "437_204+j", "439_204+j",
              "live daemon mtime-watch", "无 buildgen emission 链"):
    assert stale not in out_t, "stale token survives: %r" % stale
assert M+"0.0929" in out_t and M+"0.0898" in out_t, "U+2212 forms"
assert out_t.count("W190 0.000380") == 1
assert "W191=bm-a r894 freeze（e5e4af81b）" in out_t
assert "；W192=bm-c r787 freeze（f8703842c）。" in out_t

open(OUT, "wb").write(out_t.replace("\n", "\r\n").encode("utf-8"))
chk = io.open(OUT, encoding="utf-8", newline="").read()
assert chk == out_t.replace("\n", "\r\n"), "CRLF roundtrip drift"
print("W193 prereg built: %s bytes=%d crlf=%d" %
      (OUT, len(chk.encode("utf-8")), chk.count("\r\n")))
print("post-transform asserts PASS (counts, residue-zero, "
      "malformed-zero, stale-sweep CLEAN, U+2212 forms)")
