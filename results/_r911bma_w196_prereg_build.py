# -*- coding: utf-8 -*-
"""r911 bm-a W196 per-wave prereg build (EMITTED by
results/_r911bma_w196_buildgen.py; pairs baked; live facts re-asserted
at run time per r587).  Src = results/_r911bma_w196_prereg_src.txt
(W195 prereg freeze-time blob b9b962672, byte-verbatim binary extract,
r877 law 4).  Output CRLF (r370 law)."""
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SRC = "results/_r911bma_w196_prereg_src.txt"
OUT = "research/PERPETUAL_N1_W196_PREREG.md"
G = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
GIT = r"C:\Program Files\Git\cmd\git.exe"

def git(*a):
    r = subprocess.run([GIT, "-C", G] + list(a), capture_output=True)
    return r.stdout.decode("utf-8", errors="replace").strip()

subprocess.run([GIT, "-C", G, "fetch", "origin"], capture_output=True)
probe = json.load(open(r"results/_r910bma_w196_probe_receipt.json",
                      encoding="utf-8"))
assert probe["verdict"] == "ADMIT" and probe["bands"] == {
    "A": "446004_448003", "B": "448004_448203"}, probe
leg0 = probe["legs"]["leg0"]
assert leg0["rows"] == 193 and leg0["tail"] == "W195", leg0
assert leg0["ordinal"] == 186 and leg0["bma_ordinal"] == 111, leg0
res = json.load(open(r"results/perpetual_faces/n1_w195_results.json",
                     encoding="utf-8"))
assert res["null_pool_cumulative"]["merged"]["n_values"] == 426920
assert res["science_gates"]["ledger"]["total"] == 843345
assert res["skill_line_v2_k_lift"]["n_eff_held_equal"] == 841145
_vac = git("log", "origin/main", "--format=%h", "-n", "1", "-S",
           '196: {"a": (446_004', "--", "scripts/perpetual_faces.py")
assert _vac == "", "W196 five-face already on origin?!"
_fin194 = git("ls-tree", "origin/main",
              "results/perpetual_faces/n1_w194_results.json")
assert _fin194 != "", "W194 finalize NOT landed -- key-order face broken!"
_fin195 = git("ls-tree", "origin/main",
              "results/perpetual_faces/n1_w195_results.json")
assert _fin195 != "", "W195 finalize NOT landed -- anchor must roll r590!"
_seat = git("log", "origin/main", "--format=%h", "-n", "1",
            "--diff-filter=A", "--",
            "fleet/inbox/MSG-2026-10-09-1007-bma-w196-seat.md")
assert _seat == "01992cd42", _seat

sys.path.insert(0, "scripts")
sys.path.insert(0, ".")
import science_gates as _sg  # noqa: E402
REG_N = len(_sg.SEED_REGISTRY)
assert REG_N >= 194, "SEED_REGISTRY below freeze face: %d" % REG_N
_ws = [int(x) for x in _sg.SEED_REGISTRY.values()
       if isinstance(x, int)]
assert not [s for s in _ws if 446004 <= s <= 448203], "band overlap"

TOK = [
    ('W118=bm-b r678 freeze（565e5b0b4）；W119=bm-a r701 freeze（907e1e187）；W120=bm-a r725 freeze；W121=bm-a r726 freeze（8dcb2e60c）；W122=bm-a r727 freeze（69466f13）；W123=bm-a r728 freeze（d049a2ab）；W124=bm-a r729 freeze（bebad2e18）；W125=bm-a r730 freeze（7cd1f6ee）；W126=bm-a r731 freeze（db9da0e92）；W127=bm-a r732 freeze（b70372381）；W128=bm-a r733 freeze（6ce3f5d6）；W129=bm-a r734 freeze（e8d140ef）；W130=bm-a r735 freeze（b8b308db）；W131=bm-a r736 freeze（cd6667e8）；W136=bm-a r741 freeze（cafbc7ab）；W137=bm-a r742 freeze（f9e4ec5d2）；W138=bm-a r743 freeze（798a1e5f）；W139=bm-a r744 freeze（4e3a018c7）；W140=bm-a r745 freeze（5e3984200）；W141=bm-a r747 freeze（7ffadab65）；W144=bm-a r752 freeze（ff6d2f918）；W145=bm-a r754 freeze（98c661f8f）；W146=bm-a r755 freeze（8f06f6910）；W147=bm-a r757 freeze（3961555de）；W148=bm-a r759 freeze（92c5ab03c）；W149=bm-a r761 freeze（0cef02a00）；W150=bm-a r762 freeze（fedebeb32）；W151=bm-a r763 freeze（bd4cd7159）；W155=bm-a r768 freeze（dde679c63）；W156=bm-a r771 freeze（13c989ba0）；W157=bm-a r772 freeze（aed41df3e）；W158=bm-a r775 freeze（6957f509e）；W159=bm-a r781 freeze（6ee1207bb）；W160=bm-a r783 freeze（ee04482a2）；W161=bm-a r785 freeze（678a07d4f）；W162=bm-a r787 freeze（764cd882a）；W163=bm-a r789 freeze（18231a529）；W165=bm-a r792 freeze（f7d34e5a7）；W165=bm-a r795 freeze（aebb94d2d）；W166=bm-a r799 freeze（c2d6c5e14）；W167=bm-a r805 freeze（f61835690）；W168=bm-a r809 freeze（8d8842b61）；W169=bm-a r811 freeze（9c2271baf）；W170=bm-a r813 freeze（cb7314d64）；W171=bm-a r815 freeze（456f3affc）；W172=bm-a r819 freeze（59fde9319）；W173=bm-a r822 freeze（04e95748a）；W174=bm-a r826 freeze（db42a0d46）；W175=bm-a r830 freeze（f3fca4055）；W176=bm-a r834 freeze（15ec44ea6）；W177=bm-a r843 freeze（c06cc230f）；W178=bm-a r845 freeze（de4716da2）；W179=bm-a r849 freeze（ef540bf8f）；W180=bm-a r852 freeze（568848aa4）；W181=bm-a r863 freeze（de699e8cd）；W182=bm-a r867 freeze（385dbafd8）；W183=bm-a r869 freeze（481da4d78）；W184=bm-a r874 freeze（7e791a87f）；W185=bm-a r878 freeze（beb4b5abd）；W186=bm-a r882 freeze（14177b161）；W187=bm-a r886 freeze（79c9a567c）；W188=bm-a r888 freeze（b66117659）；W189=bm-a r890 freeze（8addea3eb）；W190=bm-a r892 freeze（0cce3c47e）；W191=bm-a r894 freeze（e5e4af81b）；W192=bm-c r787 freeze（f8703842c）；W193=bm-a r901 freeze（5cf0d6175）；W194=bm-a r905 freeze（82670b0ba）', '@CHAIN@'),
    ('# PERPETUAL-N1-W195 预注册 · N1 nulls-deepening 泵第 193 枚（never-dry 常供给例波·波序号连续·机面 derive：engine_owner 行 184 注册在册+W193/W194 finalize 已落账·anchor 滚动已兑现（r590）+本候选=bm-a 第一百一十枚自有波【bm-a r908·buildgen 血统 r830/r833/r877/r904 承袭·干净窗 anchor=W194 实测 r590 滚动兑现】）', '@TITLE@'),
    ('【本冻结窗 fetch 实核表尾时 W195 号位空档·rg 行 WAVE_CONFIGS+prereg 路径三查+origin ls-tree vacancy 机证（本窗 probe leg3 实跑）；全 inbox/processed/ W195 席位零外机命中；**W193=bm-a r901 五面冻结 5cf0d6175 在册·finalize 已落 origin（r904 estate 收口 1316ab9e7）+W194=bm-a r905 五面冻结 82670b0ba 在册·finalize 已落 origin（r906 one-pass bd1f515f2·账本 841,145 EXACT 零偏离）——起稿窗注册宇宙=W193/W194 注册带在册+双 finalize 落账（N1_BANDS 注册行机器读·probe leg0 机证 192 行表尾 W194）·r907 W195 probe 全腿机证**；本机席位公示=MSG-2026-10-09-0844-bma-w195-seat 已推 origin eb81c0878 先于本冻结【r565 律·推送窗=r907 seat push 直接快进送达 eb81c0878（payload=seat MSG+W195 pre-seat probe 脚本+回执同推）；self-ack inbox→processed 移位随五面冻结窗收口归档（如实注记）】】', '@SEATBLOCK@'),
    ('本波 **A-ext seed=443_804..445_803**（**A 面=FIRST-CLEAN past prior-wave B 阶梯第五十五例**：A 面算术继续带 443_604..445_603 在其起点即被 W194 注册 B 带 443_604..443_803 **拒**（W194 §5.5 投影+r902 probe leg4 双源预言+强制·r907 probe 回执 A_semantics 机读双兑现）→ 诚实前向走 **1 hop** 落 **443_804..445_803**·**A base==前波 B 尾+1（443_803+1）机检关系**=**A-hops-prior-B 阶梯几何第五十五例（E36 卡）**·非轮转 r587 前向单调断言在走册；序数面如实披露：W194 §5.5 投影预告第五十五例·本窗 probe 回执 A_semantics 机读序数=FIFTY-FIFTH（第五十五例）·本件按回执序数面记载非转抄（r587）·投影与回执两读法恒同）', '@AFACE@'),
    ('**B-ext exit seed=445_804..446_003**（**B 面=FIRST-CLEAN past own-wave A**：B 面算术继续带 443_804..444_003 在声明宇宙上 CLEAN 但**落在本波 A 窗 443_804..445_803 内**（**同窗互斥面 leg2 律·W141 先例**：A 与 B 同一冻结 commit 双注册·互斥断言强制 B 越过本波 A 窗）→ B 带本波 A 窗保留走 **1 hop** 落 **445_804..446_003**·**B base==本波 A 尾+1（445_803+1）机检关系**·hop 链逐跳在 probe 回执；**W194 §5.5 投影+r904 prereg leg4 承接面注记兑现**：投影预言 W195 须在 post-W194 注册宇宙重 derive 且 derive B 时预留本波 A 窗——本窗双面兑现·A 被拒+阶梯越带如投影所期·B 同窗互斥保留=投影所期·已如实披露非分叉）', '@BFACE@'),
    ('起稿窗实况：**W1..W194 N1 finalize 已全部落地**【净账本锚头 **841,145**·K=424,720 合并池·n1_w194_results.json 机读（origin 在册）】；W195=本窗候选（席位已推 eb81c0878）——**零在飞上游席**·anchor=最新已落账键（W194 实测·r590 滚动已兑现：W194 finalize 已落 origin bd1f515f2（r906 one-pass·账本 841,145 EXACT 零偏离）·起稿窗干净窗零在飞上游席·r904 v2 同律·无 v1 自爆面）', '@ANCHOR0@'),
    ('（起草窗实况注记：**W1..W194 N1 finalize 已全部落地**——净账本锚头 841,145·**K=424,720 合并池**·**零在飞上游席（W193/W194 finalize 均已落 origin·ls-tree 机证）**——本波 §5 预测键=**W194 实测值**【results/perpetual_faces/n1_w194_results.json·N1 面最新已落账键·origin 在册机证】', '@S5ANCH@'),
    ('5. **W196+ 投影（probe 机证·下波冻结方复核非转抄 r587 律）**：A first-clean 445_804..447_803 **CLEAN**（hops=0）；B first-clean **446_004..446_203 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W196：W196 冻结方必须在 post-W195 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W195 B 带 445_804..446_003 注册后将拒 naive W196 A 窗**——W196 A 重 derive 同强制（越过 W195 B 带·阶梯 A-hops-prior-B 继承第五十六例）；verify at W196 prereg，hop 链逐跳在 probe 回执', '@S55@'),
    ('1. W195-only mu 与累计池 merged mu（W194 实测键 **−0.0928**·K=424,720 合并池·W194-only 实测 **−0.0881**）差异 **|Δ|<0.02**（W2..W194 共一百九十四面实测 mu 稳定先例·单波跨键微）', '@S51@'),
    ('2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.245098**=W194 合并池实测 0.245098）。', '@S52@'),
    ('3. A 档 full_sharpe_p95 与 W194 A 档 p95（**0.3135** 实测锚）差 **<0.05**（门标注法 W5..W194 先例：结果知情面仅作机器断言之用·测量面非注册利益）。', '@S53@'),
    ('4. K-lift 线移动幅度 **≤±0.02**（累计池加深零 se_mu 收窄线自 mu/sigma 微调面非质变——W136..W194 先例链披露【W189 +0.0003/W190 −0.0001/W191 +0.0001/W192 **−0.0002**/W193 **−0.0001**/W194 **+0.0000**·键 W194 实测 K-lift **+0.0000**·line_merged@K424,720 **1.1873**·line_pre 1.1873·n_eff 838,945；se_mu 收窄链 W191 0.000379→W192 0.000378→W193 0.000377→W194 **0.000376**】）。', '@S54@'),
    ('本波机验 ADMIT 回执在场=_r907bma_w195 探针窗（pre-seat probe 单窗·gate 腿合并结构承袭 r812/r820/r823 先例·parity N/A 诚实注记）；selftest W195 face（A=first-clean past prior-wave B 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W194 行 parity 腿【r735 测量-实现分叉族防护面：A/B 窗 set-range 针在场】）随五面冻结落地', '@GATEW2@'),
    ('entry rng seed=**443_804+j**（法典 §4 W195 行 A=443_804..445_803·**FIRST-CLEAN past prior-wave B 阶梯第五十五例**：算术续带 443_604..445_603 起点即被 W194 注册 B 带拒→1 hop 落 443_804..445_803·A base==前波 B 尾+1 机检关系·E36 卡·hops=1·ADMIT 回执在场）', '@ASEED@'),
    ('exit rng=**445_804+j**（法典 §4 W195 行 B=445_804..446_003·**FIRST-CLEAN past own-wave A**：B 算术续带 443_804..444_003 在声明宇宙上 CLEAN 但落在本波 A 窗 443_804..445_803 内→**同窗互斥面 leg2 律·W141 先例**强制 B 越本波 A 窗→保留走落 445_804..446_003·hops=1·**B base==本波 A 尾+1 机检关系**·非轮转 r587·hop 链逐跳在 probe 回执·与 W194 §5.5 投影+r904 prereg leg4 承接面注记兑现收敛·ADMIT 回执在场）', '@BSEED@'),
    ('**本冻结=buildgen emission 链（r830/r833/r877/r904 血统承袭·TOK 两相 vmap+DRY 全文件门零写入先行+U+2212 显示形·五腿探针回执在场为准·anchor=W194 实测 r590 滚动兑现·selftest W195 face 将随五面冻结落地验证）。**', '@ENGNOTE@'),
    ('- 认领：never-dry 常供给例波（TRIAL_LABOR_LAW §4·板空/池饱/无在飞判决批=默认续跑下一波——本机 r907 席位 MSG-2026-10-09-0844-bma-w195-seat 已推 origin eb81c0878（r907 seat push·r565 律）·probe W196+ 投影 A 445_804..447_803 / B 446_004..446_203 **naive-B-inside-naive-A re-derive 强制注记+同窗互斥预披露**（投影 B 落投影 A 窗内·W195 B 带 445_804..446_003 注册后将拒 naive W196 A 窗=阶梯 A-hops-prior-B 继承第五十六例待 W196 注册宇宙复核）。表尾后新首个自由号自领·r907 probe 单跑兑现注记（本窗冻结消费）；O-20260924-1730 CEO 即时律（认领与开动同轮·禁排未来轮次）；T-2026-10-01-141 s1 引擎线第 185 波【bm-a 第一百一十枚自有波【机面 derive：engine_owner==bm-a 行 109+本候选以 probe leg0 机证为准】】。（波号=注册表 W194 席后首个自由号·单态零席位空档；中位公示 MSG-2026-10-09-0844-bma-w195-seat 先推 origin eb81c0878 r565 律；lane-free；dept:研究）。', '@CLAIM@'),
    ('【finalize 同窗回填·待 W195 finalize 窗】\n- （占位·§5.5 W196+ 投影承接+宝藏/方法论捕获问+诚实披露面·finalize 收口窗机械回填。）', '@S8@'),
    ('待 W195 finalize 窗】\n- （占位·finalize one-pass 后机械回填：账本恒等式+合并池 K+merged mu/w-only mu/mu_delta+sigma+se_mu+skill_line_v2 K-lift+A 档 p95+§5 四预键机证+canon flip 态+audit.finalize_only+voids_applied。）', '@S7@'),
    ('扫描面=pre-W195 全一百九十二行注册 N1 带表（表尾 W194 行·leg0 机证 192 行）', '@SCANFACE@'),
    ('R250：W195 带从未指派·测量面零结果可锁', '@R250@'),
    ('results/_r907bma_w195_probe_receipt.json', '@PRCR@'),
    ('W2..W194 落地 runner 的 wave 参数化复用', '@RUNNERW@'),
    ('批名=**PERPETUAL-N1-W195**', '@BATCHNAME@'),
    ('累计 null 池=424,720（W194 落账实测）+2,200（本波）=**426,920 投影**', '@POOL@'),
    ('自见 W195 行并点火自烧', '@MATCOND@'),
    ('--prereg research/PERPETUAL_N1_W195_PREREG.md', '@GATECMD@'),
    ('entry rng=**443_804+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）', '@BENTRY@'),
    ('本波设计=W2..W194 逐字复用', '@PROBEW@'),
    ('W195 带与 v1 在用带（10_000..10_099/20_000..20_019）、W1 ext 带（10_100..12_099/20_100..20_299）、W2..W194 带（**全注册单态**）', '@DISJ@'),
    ('已落账净值（起稿窗实流 W1..W194 已落账 424,720 实测·derive 禁手抄）+本波 2,200', '@POOL4@'),
    ('batch_name="PERPETUAL-N1-W195", batch_trials=2200, file_name="results/perpetual_faces/n1_w195_results.json"', '@LEDGER@'),
    ('--wave 195/finalize --wave 195', '@CLI@'),
    ('【n1_w195/ 分片计数增长·唯一点火证据·r325 律】', '@ENG6@'),
    ('results/p2cal_ext/n1_w195/shard-<k>-of-12.json', '@SHARD@'),
    ('results/perpetual_faces/n1_w195_results.json', '@RFN@'),
    ('finalize 键序前置=**起草窗零在飞上游席（W193/W194 finalize 均已落 origin·ls-tree 机证）**——跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态例恒在）。', '@FINPRE@'),
    ('（engine_owner==bm-a 109 行注册 + 本候选——以 probe leg0 机证为准）', '@EOBD@'),
    ('（p2_calibration v1/v2 canon；v1 ext；v2..W194 落地）', '@BGATE@'),
    ('波号 195=注册表 W194 席后首个自由号', '@WAVEFREE@'),
]
BACK = {
    '@CHAIN@': 'W118=bm-b r678 freeze（565e5b0b4）；W119=bm-a r701 freeze（907e1e187）；W120=bm-a r725 freeze；W121=bm-a r726 freeze（8dcb2e60c）；W122=bm-a r727 freeze（69466f13）；W123=bm-a r728 freeze（d049a2ab）；W124=bm-a r729 freeze（bebad2e18）；W125=bm-a r730 freeze（7cd1f6ee）；W126=bm-a r731 freeze（db9da0e92）；W127=bm-a r732 freeze（b70372381）；W128=bm-a r733 freeze（6ce3f5d6）；W129=bm-a r734 freeze（e8d140ef）；W130=bm-a r735 freeze（b8b308db）；W131=bm-a r736 freeze（cd6667e8）；W136=bm-a r741 freeze（cafbc7ab）；W137=bm-a r742 freeze（f9e4ec5d2）；W138=bm-a r743 freeze（798a1e5f）；W139=bm-a r744 freeze（4e3a018c7）；W140=bm-a r745 freeze（5e3984200）；W141=bm-a r747 freeze（7ffadab65）；W144=bm-a r752 freeze（ff6d2f918）；W145=bm-a r754 freeze（98c661f8f）；W146=bm-a r755 freeze（8f06f6910）；W147=bm-a r757 freeze（3961555de）；W148=bm-a r759 freeze（92c5ab03c）；W149=bm-a r761 freeze（0cef02a00）；W150=bm-a r762 freeze（fedebeb32）；W151=bm-a r763 freeze（bd4cd7159）；W155=bm-a r768 freeze（dde679c63）；W156=bm-a r771 freeze（13c989ba0）；W157=bm-a r772 freeze（aed41df3e）；W158=bm-a r775 freeze（6957f509e）；W159=bm-a r781 freeze（6ee1207bb）；W160=bm-a r783 freeze（ee04482a2）；W161=bm-a r785 freeze（678a07d4f）；W162=bm-a r787 freeze（764cd882a）；W163=bm-a r789 freeze（18231a529）；W165=bm-a r792 freeze（f7d34e5a7）；W165=bm-a r795 freeze（aebb94d2d）；W166=bm-a r799 freeze（c2d6c5e14）；W167=bm-a r805 freeze（f61835690）；W168=bm-a r809 freeze（8d8842b61）；W169=bm-a r811 freeze（9c2271baf）；W170=bm-a r813 freeze（cb7314d64）；W171=bm-a r815 freeze（456f3affc）；W172=bm-a r819 freeze（59fde9319）；W173=bm-a r822 freeze（04e95748a）；W174=bm-a r826 freeze（db42a0d46）；W175=bm-a r830 freeze（f3fca4055）；W176=bm-a r834 freeze（15ec44ea6）；W177=bm-a r843 freeze（c06cc230f）；W178=bm-a r845 freeze（de4716da2）；W179=bm-a r849 freeze（ef540bf8f）；W180=bm-a r852 freeze（568848aa4）；W181=bm-a r863 freeze（de699e8cd）；W182=bm-a r867 freeze（385dbafd8）；W183=bm-a r869 freeze（481da4d78）；W184=bm-a r874 freeze（7e791a87f）；W185=bm-a r878 freeze（beb4b5abd）；W186=bm-a r882 freeze（14177b161）；W187=bm-a r886 freeze（79c9a567c）；W188=bm-a r888 freeze（b66117659）；W189=bm-a r890 freeze（8addea3eb）；W190=bm-a r892 freeze（0cce3c47e）；W191=bm-a r894 freeze（e5e4af81b）；W192=bm-c r787 freeze（f8703842c）；W193=bm-a r901 freeze（5cf0d6175）；W194=bm-a r905 freeze（82670b0ba）；W195=bm-a r909 freeze（b9b962672）',
    '@TITLE@': '# PERPETUAL-N1-W196 预注册 · N1 nulls-deepening 泵第 194 枚（never-dry 常供给例波·波序号连续·机面 derive：engine_owner 行 185 注册在册+W194/W195 finalize 已落账·anchor 滚动已兑现（r590）+本候选=bm-a 第一百一十一枚自有波【bm-a r911·buildgen 血统 r830/r833/r877/r908 承袭·干净窗 anchor=W195 实测 r590 滚动兑现】）',
    '@SEATBLOCK@': '【本冻结窗 fetch 实核表尾时 W196 号位空档·rg 行 WAVE_CONFIGS+prereg 路径三查+origin ls-tree vacancy 机证（本窗 probe leg3 实跑）；全 inbox/processed/ W196 席位零外机命中；**W194=bm-a r905 五面冻结 82670b0ba 在册·finalize 已落 origin（r906 one-pass bd1f515f2·账本 841,145 EXACT 零偏离）+W195=bm-a r909 五面冻结 b9b962672 在册·finalize 已落 origin（r910 one-pass a0b16d1d8·账本 843,345 EXACT 零偏离）——起稿窗注册宇宙=W194/W195 注册带在册+双 finalize 落账（N1_BANDS 注册行机器读·probe leg0 机证 193 行表尾 W195）·r910 W196 probe 全腿机证**；本机席位公示=MSG-2026-10-09-1007-bma-w196-seat 已推 origin 01992cd42 先于本冻结【r565 律·推送窗=r910 seat push 直接快进送达 01992cd42（payload=seat MSG+W196 pre-seat probe 脚本+回执同推）；self-ack inbox→processed 移位随五面冻结窗收口归档（如实注记）】】',
    '@AFACE@': '本波 **A-ext seed=446_004..448_003**（**A 面=FIRST-CLEAN past prior-wave B 阶梯第五十六例**：A 面算术继续带 445_804..447_803 在其起点即被 W195 注册 B 带 445_804..446_003 **拒**（W195 §5.5 投影+r907 probe leg4 双源预言+强制·r910 probe 回执 A_semantics 机读双兑现）→ 诚实前向走 **1 hop** 落 **446_004..448_003**·**A base==前波 B 尾+1（446_003+1）机检关系**=**A-hops-prior-B 阶梯几何第五十六例（E36 卡）**·非轮转 r587 前向单调断言在走册；序数面如实披露：W195 §5.5 投影预告第五十六例·本窗 probe 回执 A_semantics 机读序数=FIFTY-SIXTH（第五十六例）·本件按回执序数面记载非转抄（r587）·投影与回执两读法恒同）',
    '@BFACE@': '**B-ext exit seed=448_004..448_203**（**B 面=FIRST-CLEAN past own-wave A**：B 面算术继续带 446_004..446_203 在声明宇宙上 CLEAN 但**落在本波 A 窗 446_004..448_003 内**（**同窗互斥面 leg2 律·W141 先例**：A 与 B 同一冻结 commit 双注册·互斥断言强制 B 越过本波 A 窗）→ B 带本波 A 窗保留走 **1 hop** 落 **448_004..448_203**·**B base==本波 A 尾+1（448_003+1）机检关系**·hop 链逐跳在 probe 回执；**W195 §5.5 投影+r908 prereg leg4 承接面注记兑现**：投影预言 W196 须在 post-W195 注册宇宙重 derive 且 derive B 时预留本波 A 窗——本窗双面兑现·A 被拒+阶梯越带如投影所期·B 同窗互斥保留=投影所期·已如实披露非分叉）',
    '@ANCHOR0@': '起稿窗实况：**W1..W195 N1 finalize 已全部落地**【净账本锚头 **843,345**·K=426,920 合并池·n1_w195_results.json 机读（origin 在册）】；W196=本窗候选（席位已推 01992cd42）——**零在飞上游席**·anchor=最新已落账键（W195 实测·r590 滚动已兑现：W195 finalize 已落 origin a0b16d1d8（r910 one-pass·账本 843,345 EXACT 零偏离）·起稿窗干净窗零在飞上游席·r908 v2 同律·无 v1 自爆面）',
    '@S5ANCH@': '（起稿窗实况注记：**W1..W195 N1 finalize 已全部落地**——净账本锚头 843,345·**K=426,920 合并池**·**零在飞上游席（W194/W195 finalize 均已落 origin·ls-tree 机证）**——本波 §5 预测键=**W195 实测值**【results/perpetual_faces/n1_w195_results.json·N1 面最新已落账键·origin 在册机证】',
    '@S55@': '5. **W197+ 投影（probe 机证·下波冻结方复核非转抄 r587 律）**：A first-clean 448_004..450_003 **CLEAN**（hops=0）；B first-clean **448_204..448_403 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W197：W197 冻结方必须在 post-W196 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W196 B 带 448_004..448_203 注册后将拒 naive W197 A 窗**——W197 A 重 derive 同强制（越过 W196 B 带·阶梯 A-hops-prior-B 继承第五十七例）；verify at W197 prereg，hop 链逐跳在 probe 回执',
    '@S51@': '1. W196-only mu 与累计池 merged mu（W195 实测键 **−0.0929**·K=426,920 合并池·W195-only 实测 **−0.0970**）差异 **|Δ|<0.02**（W2..W195 共一百九十五面实测 mu 稳定先例·单波跨键微）',
    '@S52@': '2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.245069**=W195 合并池实测 0.245069）。',
    '@S53@': '3. A 档 full_sharpe_p95 与 W195 A 档 p95（**0.3078** 实测锚）差 **<0.05**（门标注法 W5..W195 先例：结果知情面仅作机器断言之用·测量面非注册利益）。',
    '@S54@': '4. K-lift 线移动幅度 **≤±0.02**（累计池加深零 se_mu 收窄线自 mu/sigma 微调面非质变——W136..W195 先例链披露【W189 +0.0003/W190 −0.0001/W191 +0.0001/W192 **−0.0002**/W193 **−0.0001**/W194 **+0.0000**/W195 **−0.0001**·键 W195 实测 K-lift **−0.0001**·line_merged@K426,920 **1.1873**·line_pre 1.1874·n_eff 841,145；se_mu 收窄链 W191 0.000379→W192 0.000378→W193 0.000377→W194 0.000376→W195 **0.000375**】）。',
    '@GATEW2@': '本波机验 ADMIT 回执在场=_r910bma_w196 探针窗（pre-seat probe 单窗·gate 腿合并结构承袭 r812/r820/r823 先例·parity N/A 诚实注记）；selftest W196 face（A=first-clean past prior-wave B 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W195 行 parity 腿【r735 测量-实现分叉族防护面：A/B 窗 set-range 针在场】）随五面冻结落地',
    '@ASEED@': 'entry rng seed=**446_004+j**（法典 §4 W196 行 A=446_004..448_003·**FIRST-CLEAN past prior-wave B 阶梯第五十六例**：算术续带 445_804..447_803 起点即被 W195 注册 B 带拒→1 hop 落 446_004..448_003·A base==前波 B 尾+1 机检关系·E36 卡·hops=1·ADMIT 回执在场）',
    '@BSEED@': 'exit rng=**448_004+j**（法典 §4 W196 行 B=448_004..448_203·**FIRST-CLEAN past own-wave A**：B 算术续带 446_004..446_203 在声明宇宙上 CLEAN 但落在本波 A 窗 446_004..448_003 内→**同窗互斥面 leg2 律·W141 先例**强制 B 越本波 A 窗→保留走落 448_004..448_203·hops=1·**B base==本波 A 尾+1 机检关系**·非轮转 r587·hop 链逐跳在 probe 回执·与 W195 §5.5 投影+r908 prereg leg4 承接面注记兑现收敛·ADMIT 回执在场）',
    '@ENGNOTE@': '**本冻结=buildgen emission 链（r830/r833/r877/r908 血统承袭·TOK 两相 vmap+DRY 全文件门零写入先行+U+2212 显示形·五腿探针回执在场为准·anchor=W195 实测 r590 滚动兑现·selftest W196 face 将随五面冻结落地验证）。**',
    '@CLAIM@': '- 认领：never-dry 常供给例波（TRIAL_LABOR_LAW §4·板空/池饱/无在飞判决批=默认续跑下一波——本机 r910 席位 MSG-2026-10-09-1007-bma-w196-seat 已推 origin 01992cd42（r910 seat push·r565 律）·probe W197+ 投影 A 448_004..450_003 / B 448_204..448_403 **naive-B-inside-naive-A re-derive 强制注记+同窗互斥预披露**（投影 B 落投影 A 窗内·W196 B 带 448_004..448_203 注册后将拒 naive W197 A 窗=阶梯 A-hops-prior-B 继承第五十七例待 W197 注册宇宙复核）。表尾后新首个自由号自领·r910 probe 单跑兑现注记（本窗冻结消费）；O-20260924-1730 CEO 即时律（认领与开动同轮·禁排未来轮次）；T-2026-10-01-141 s1 引擎线第 186 波【bm-a 第一百一十一枚自有波【机面 derive：engine_owner==bm-a 行 110+本候选以 probe leg0 机证为准】】。（波号=注册表 W195 席后首个自由号·单态零席位空档；中位公示 MSG-2026-10-09-1007-bma-w196-seat 先推 origin 01992cd42 r565 律；lane-free；dept:研究）。',
    '@SCANFACE@': '扫描面=pre-W196 全一百九十三行注册 N1 带表（表尾 W195 行·leg0 机证 193 行）',
    '@R250@': 'R250：W196 带从未指派·测量面零结果可锁',
    '@PRCR@': 'results/_r910bma_w196_probe_receipt.json',
    '@RUNNERW@': 'W2..W195 落地 runner 的 wave 参数化复用',
    '@BATCHNAME@': '批名=**PERPETUAL-N1-W196**',
    '@POOL@': '累计 null 池=426,920（W195 落账实测）+2,200（本波）=**429,120 投影**',
    '@MATCOND@': '自见 W196 行并点火自烧',
    '@GATECMD@': '--prereg research/PERPETUAL_N1_W196_PREREG.md',
    '@BENTRY@': 'entry rng=**446_004+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）',
    '@PROBEW@': '本波设计=W2..W195 逐字复用',
    '@DISJ@': 'W196 带与 v1 在用带（10_000..10_099/20_000..20_019）、W1 ext 带（10_100..12_099/20_100..20_299）、W2..W195 带（**全注册单态**）',
    '@POOL4@': '已落账净值（起稿窗实流 W1..W195 已落账 426,920 实测·derive 禁手抄）+本波 2,200',
    '@LEDGER@': 'batch_name="PERPETUAL-N1-W196", batch_trials=2200, file_name="results/perpetual_faces/n1_w196_results.json"',
    '@CLI@': '--wave 196/finalize --wave 196',
    '@ENG6@': '【n1_w196/ 分片计数增长·唯一点火证据·r325 律】',
    '@SHARD@': 'results/p2cal_ext/n1_w196/shard-<k>-of-12.json',
    '@RFN@': 'results/perpetual_faces/n1_w196_results.json',
    '@FINPRE@': 'finalize 键序前置=**起稿窗零在飞上游席（W194/W195 finalize 均已落 origin·ls-tree 机证）**——跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态例恒在）。',
    '@EOBD@': '（engine_owner==bm-a 110 行注册 + 本候选——以 probe leg0 机证为准）',
    '@BGATE@': '（p2_calibration v1/v2 canon；v1 ext；v2..W195 落地）',
    '@S7@': '待 W196 finalize 窗】\n- （占位·finalize one-pass 后机械回填：账本恒等式+合并池 K+merged mu/w-only mu/mu_delta+sigma+se_mu+skill_line_v2 K-lift+A 档 p95+§5 四预键机证+canon flip 态+audit.finalize_only+voids_applied。）',
    '@S8@': '【finalize 同窗回填·待 W196 finalize 窗】\n- （占位·§5.5 W197+ 投影承接+宝藏/方法论捕获问+诚实披露面·finalize 收口窗机械回填。）',
    '@WAVEFREE@': '波号 196=注册表 W195 席后首个自由号'
}

src = io.open(SRC, encoding="utf-8").read()
assert src.count("\r\n") == 0, "src blob expected LF"
assert src.count("SEED_REGISTRY \u5168\u952e 194 \u503c") == 1, \
    "registry-count face not found in src"
src = src.replace("SEED_REGISTRY \u5168\u952e 194 \u503c",
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
assert out_t.count("PERPETUAL-N1-W196") == 3, "batch id count drift"
assert out_t.count("\n") == src.count("\n"), "line structure drift"
M = "\u2212"
for stale in ("FIFTY-FIFTH", "443_804..445_803", "443_604..443_803",
              "443_804+j", "445_804+j", "PERPETUAL-N1-W195",
              "PERPETUAL_N1_W195_PREREG", "n1_w195/",
              "n1_w194_results.json", "MSG-2026-10-09-0844", "eb81c0878",
              "5cca13637", "engine_owner==bm-a 109",
              "\u7b2c 185 \u6ce2", "\u7b2c\u4e00\u767e\u4e00\u5341"
              "\u679a", "\u6cf5\u7b2c 193 \u679a", "W2..W194",
              "\u5f85 W195 finalize \u7a97", "W196+ \u6295\u5f71",
              "K=424,720", "836,745", "422,520", "1.1872", "0.3135",
              "0.245098", "W194-only \u5b9e\u6d4b", "838,945",
              "line_pre 1.1873", "1316ab9e7"):
    assert stale not in out_t, "stale token survives: %r" % stale
assert M + "0.0929" in out_t and M + "0.0970" in out_t, "U+2212 forms"
assert out_t.count(M + "0.0001/W191") == 1
assert "W191=bm-a r894 freeze\uff08e5e4af81b\uff09" in out_t
assert "\uff1bW194=bm-a r905 freeze\uff0882670b0ba\uff09\uff1bW195=bm-a " \
    "r909 freeze\uff08b9b962672\uff09\u3002" in out_t
assert out_t.count("n1_w195_results.json") == 2
assert out_t.count("W1..W195 N1 finalize \u5df2\u5168\u90e8\u843d\u5730") \
    == 2
assert out_t.count("n1_w196") == 4
assert "FIFTY-SIXTH" in out_t
assert "W195-only \u5b9e\u6d4b" in out_t, "anchor w-only face missing"
assert "843,345" in out_t and "426,920" in out_t and "429,120" in out_t
assert "446_004..448_003" in out_t and "448_004..448_203" in out_t

open(OUT, "wb").write(out_t.replace("\n", "\r\n").encode("utf-8"))
chk = io.open(OUT, encoding="utf-8", newline="").read()
assert chk == out_t.replace("\n", "\r\n"), "CRLF roundtrip drift"
print("W196 prereg built: %s bytes=%d crlf=%d" %
      (OUT, len(chk.encode("utf-8")), chk.count("\r\n")))
print("post-transform asserts PASS (counts, residue-zero, "
      "malformed-zero, stale-sweep CLEAN, U+2212 forms, anchor=W195)")
