# -*- coding: utf-8 -*-
import io, os
ROOT = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
def app(rel, text):
    p = os.path.join(ROOT, rel)
    with io.open(p, 'a', encoding='utf-8', newline='') as f:
        f.write(text)
    print('appended:', rel)

NL = '\n'

g = ('| N2U3_ALPHAGEN_RL_P1 | e16 census 幸存者语法空间（A158 底座 vendored loader sha16 814b7f7ab3d418ae·E16 §3 verbatim·本批=RL 反馈搜索机制首烧非新语法） '
     '| RL 训练搜索产出 top-K=32（4096 eps·checkpoint 断点续跑·n_unique=32·n_skip=0·n_excluded_dup=0） '
     '| judged 32 格 + batch-own scrnull nulls 32（t23 _permute_ranks_within_mask verbatim·μ=-0.2571/σ=0.6119） '
     '| seeds gen=20625000 scrnull=20625500 unc=20626000 '
     '| serialized r892 freeze（commit 8f49d6eea）+ consumed 2026-10-14 07:42:26（leg-3 autofill 01:06/05:02 两段·export-topk 05:01·judged r923c→r925 链·prereg bm-b r889 起草/r892 frozen / runner bm-b r891） '
     '| verdict judged_negative：0/32 registered（RL 反馈无增量·EXCLUSION_BOOK 收口）·same-grammar rerun FORBIDDEN (TRIAL_LABOR_LAW sec.4) |' + NL)
app(r'research\TRIAL_GRAMMAR_LEDGER.md', g)

e = (NL + '### 附录·新增类级负发现（2026-10-14 bm-b r933 首录·判决 finalize 类收口步）' + NL + NL +
     '- **RL 反馈搜索无增量（N2U3-ALPHAGEN-RL-P1·E17 judged 判负）**：E16 census 已证同一语法空间存在 |ICIR|>0.4 信号面，但 RL 反馈搜索'
     '（PPO+协同池边际 rank-IC 奖励·4096 eps 断点续跑）相对 E16 无反馈随机采样 **无可判读增量**——leg-2 边际 IC flat（Q0-Q3 均值 0.0001-0.0002 无上升信号）；'
     'judged top-32 全灭 0/32（G1\'v2 0 过〔best QTLD(low,60) SR 0.5435 vs skill_line 2.952 @ N_eff 940,821〕·M1 9/32·D6 拒 18·DSR max 0.2355·PBO 0.2714）；'
     'RL 收敛全部价格字段（close 13/high 7/open 6/low 3/vwap 3）而非先验量能/换手族=族向预测证伪。'
     '**撞号指纹**：同一语法空间内「反馈 vs 非反馈搜索机制对比」再开须新证据增量三选一声明（新机制族/新数据面/判线改革）；same-grammar rerun FORBIDDEN。'
     '证据=results/alphagen_rl_p1/JUDGED-2026-10-09.json+research/N2U3_ALPHAGEN_RL_P1.md §7/§8+attrition 双面行（r933）。' + NL)
app(r'research\EXCLUSION_BOOK_R1-20261006.md', e)

t = ('- 2026-10-14 13:5x bm-b r933 研究判决批收口单获（N2U3-ALPHAGEN-RL-P1 judged finalize 类·TREASURE_PROTECTION_LAW §1）：'
     '入册=**RL 反馈搜索无增量判负正面知识**（E16 语法空间 holds→RL 反馈 vs 无反馈基线 judged 0/32 全灭·leg-2 边际 flat·'
     'skill_line 2.952 @ N_eff 940,821 数据驱动门照常咬合=「连假阳性都没放进一条」门在百万格尺度正常工作再证）'
     '+批内自有 scrnull null 池机械（K=32 同码置换单源复用 t23 verbatim）'
     '【证据=results/alphagen_rl_p1/JUDGED-2026-10-09.json+research/N2U3_ALPHAGEN_RL_P1.md §7/§8+attrition 双面行】。' + NL)
app(r'knowledge\TREASURE_REGISTRY.md', t)

m = (NL + '- **E65 外采生成式方法最小承诺主考法（census-holds→license-question→judged 全链·RL 反馈 vs 无反馈 A/B 内建）**：proven，研究面。'
     '外采生成式方法（alphagen RL 公式因子范式）落地正法五步：①先廉价 census 钉「语法空间有无信号面」（E16 范式·obs family vs null family p95）；'
     '②census holds 才开最小承诺主考（top-K 格 judged·全判据门+批内自有 scrnull null 池）；'
     '③**license 问题显式预注册**（P3：RL 边际曲线是否优于无反馈基线=负即止整条线·EXCLUSION_BOOK 收口）；'
     '④RL 搜索面与 nulls 校准不入试验账本（trial_budget_law 同例）·judged K 格才计；'
     '⑤预测面五条冻结（族向/判线/边际/极端日/唯一性）跑后逐条对账。'
     'live 实证：N2U3-ALPHAGEN-RL-P1 0/32 registered 判负（best SR 0.5435 vs skill_line 2.952·DSR max 0.2355·PBO 0.2714·leg-2 边际 flat）——'
     '「负即止」单窗收口零重烧。证据=results/alphagen_rl_p1/JUDGED-2026-10-09.json+research/N2U3_ALPHAGEN_RL_P1.md §7/§8（r933 bm-b）。' + NL)
app(r'knowledge\METHODOLOGY_ASSETS.md', m)

d = ('# DIGEST-20261014-e17-alphagen-rl-judged —— N2U3-ALPHAGEN-RL-P1 判决批收口' + NL + NL +
     '- **批件**：N2 U3 通道①「全新语法」alphagen RL 公式因子主考批（E16 census_holds=true 开窗承接·supply-floor chain leg-5·prereg FROZEN r892 commit 8f49d6eea·judged 面 evidence_cutoff 2026-10-09）' + NL +
     '- **链条**：leg-1 runner r891（selftest 46/46）→leg-2 训练探针（256 eps·marginal flat 0.0001-0.0002）→leg-3 完整训练（4096 eps·autofill 01:06/05:02 断点续跑）→export-topk（n_unique=32·n_skip=0）→judged（r923c→r925 链·07:42:26 JUDGED-2026-10-09.json 落地 114KB）→r933 判负收口（§7/§8 回填+attrition 双面行+EXCLUSION_BOOK+TRIAL_GRAMMAR_LEDGER+METHODOLOGY E65+本 digest）' + NL +
     '- **判决**：**0/32 registered 判负**——门禁链：D6 拒 18（max|corr| vs 在册 0.706-1.000）→M1 t≥3 过 9（t 10.416-13.227）→G1\'v2 过 0（best QTLD(low,60) sharpe_full_x1 0.5435 vs skill_line_v2 2.952 @ N_eff 940,821·批内 scrnull μ=-0.2571/σ=0.6119·CI95 下界 -0.1707≤0）→G2 0（DSR max 0.2355<0.95 且 family PBO 0.2714>0.25 双 fail）。账本 940,789→940,821（+32 EXACT·RL 搜索面与 nulls 不计=E16 trial_budget_law）' + NL +
     '- **预测对账**：P2 对（G1\' 0/32·差距巨大）/P1 错（RL 收敛价格字段 {close 13/high 7/open 6/low 3/vwap 3} 非量能/换手族；|ICIR| med 0.178·带内 14/32 部分）/P3 错（核心 license 面判负：RL 边际 flat=无反馈基线不可超越）/P4 过（极端日四日全 false·x2/x3 逐年稳定 32/32）/P5 过（n_unique=32·n_skip=0）' + NL +
     '- **全起点分布（best 格）**：fullstart_6m best +0.1753/p25 -0.0043/中位 +0.0193/p75 +0.0402/worst -0.1301；滚动最差 3y -0.0201/5y +0.0228；beat 3m 0.5708/6m 0.5337/12m 0.4906；max_dd_x1 -13.71%' + NL +
     '- **一句话定谳**：RL 反馈搜索在该语法空间不产生高于无反馈采样的可注册信号——负即止 RL 线（EXCLUSION_BOOK 收口·G2 fallback 学术引用面·same-grammar rerun FORBIDDEN）' + NL +
     '- **证据**：results/alphagen_rl_p1/JUDGED-2026-10-09.json + TOPK-2026-10-09.json + research/N2U3_ALPHAGEN_RL_P1.md §7/§8 + gate_attrition 双面行（r933 bm-b）' + NL)
app(r'research\digests\DIGEST-20261014-e17-alphagen-rl-judged.md', d)
print('ALL APPENDS DONE')
