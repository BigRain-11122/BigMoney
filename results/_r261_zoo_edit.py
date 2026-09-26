# -*- coding: utf-8 -*-
# r261 T-76 wave-10 face (c) second-sweep: ASTYLE_ZOO #95/#96 rows + wave-10 adjudication bullet
# byte-face: LF-only, UTF-8 no BOM (probed r261); field-level insert only
import io

P = 'research/shortline/ASTYLE_ZOO.md'
raw = open(P, 'rb').read()
assert b'\xef\xbb\xbf' != raw[:3], 'BOM present - face drift'
assert b'\r\n' not in raw, 'CRLF present - face drift'
txt = raw.decode('utf-8')

row94_end = '+**冻结卡=DIGEST-20260926-zoo-paramfreeze-92-94.md** |\n\n- 波-9 判定消费裁定补遗'
assert txt.count(row94_end) == 1, 'anchor not unique: %d' % txt.count(row94_end)

row95 = ('| 95 | 指数高阶矩择时 `index_higher_mom_timing` | **通道级登记（r261 二扫·未深读——窗与阈值深读冻结时定）**：'
         '指数日收益滚动窗三/四阶矩（偏度/峰度）状态读数，矩读数越过阈值转择时信号（2015 广发原文框架级描述；'
         '高偏度=彩票需求过热·高峰度=尾部风险集聚两腿读数面） | B（择时族·矩状态新读数·二阶矩外的矩阶扩展） | '
         '新写（波-10 face (c) 二扫·2026-09-26·T-76·bm-b r261）；D6=行为偏差（彩票偏好与尾部风险规避——'
         '高偏度截面=彩票型收益需求拥挤=回落先验，高峰度=尾部风险集聚=防御先验）；黑名单四路径全非✓'
         '（单读数=滚动矩量·非背离构造·择时低换手预算条款必列·510300/core48 日线原生在册）；'
         '反重复=与 VOLATILITY-CE-01（二阶矩）不同矩阶、与 REGIME_GUARD 状态面近邻不同读数——'
         '批测面 D6 corr≥0.7 合并条款先查（与 vol 族为高危对·合并条款必查）；'
         '参数冻结纪律=窗宽与阈值跑前 prereg 冻结（原文阈值=研报调参面不作冻结基·clean-room）；'
         '消费位=T-34 快线候选池；源=广发 2015-05-20《交易性择时策略研究之八：指数高阶矩择时策略》【未实证】'
         '·QuantsPlaybook 无 license=禁抄码 clean-room；证据卡=DIGEST-20260926-wave10-qp-catalog-sweep2 §五 #95 |\n')
row96 = ('| 96 | 特征成交量状态机 `volume_regime_bimodal` | **通道级登记（r261 二扫·未深读——分布拟合腿与窗宽深读冻结时定）**：'
         '全市场成交量能指标 AMA5/AMA100 比率型读数+√型分布 bimodal 状态机（华创特征分布系列之二——'
         '系列一 #94 LHB 面同作者方法论迁移至量能面；「巧妙做空」=研报叙述非实现·中段空仓与 #94 同判定先例） | '
         'B（择时族·量能状态面·#94「系列之二=另一主题」延期议题兑现） | '
         '新写（波-10 face (c) 二扫·2026-09-26·T-76·bm-b r261）；D6=行为偏差（量能拥挤/出清物极必反——'
         '参与度极值=拥挤外部性先验，系列一 V 型两端正中段负先验的量能面姊妹篇）；黑名单四路径全非✓'
         '（单读数=量能比率+分布状态·非背离构造·择时低换手·全市场日成交量 P-1c 面板 amount/vol 原生在册）；'
         '反重复=与 #94 同作者不同数据面（全市场量能 vs LHB 席位）、与聪明钱因子同 volume 域不同用法'
         '（择时状态机 vs 截面因子）、与 REGIME_GUARD/市场时钟热度复合面近邻不同读数——批测面 D6 corr≥0.7 合并条款先查；'
         '参数冻结纪律=原文 skopt 调参=研报调参面不作冻结基·跑前 prereg 冻结·分布拟合腿复杂度随窗宽评估（构造简单解优先律）；'
         '消费位=T-34 快线候选池；源=华创 2022-08-05《特征分布建模择时系列之二：物极必反，巧妙做空，特征成交量，模型终完备》【未实证】'
         '·QuantsPlaybook 无 license=禁抄码 clean-room；证据卡=DIGEST-20260926-wave10-qp-catalog-sweep2 §五 #96 |\n')

txt = txt.replace(row94_end, '+**冻结卡=DIGEST-20260926-zoo-paramfreeze-92-94.md** |\n' + row95 + row96 + '\n- 波-9 判定消费裁定补遗')

bullet_anchor = '- §八日历季节系证据升级：#36-38 骨架不变；'
assert txt.count(bullet_anchor) == 1
w10 = ('- 波-10 face (c) 二扫裁定补遗（2026-09-26·T-76·bm-b r261·DIGEST-20260926-wave10-qp-catalog-sweep2）：'
       'QuantsPlaybook 目录首扫（r189）未判 27 条全档裁定——**14 条族并入**（QRS 择时=RSRS 族疑似变体·分位数回归斜率 vs OLS 未实证=深读复核位｜'
       '低延迟趋势线=MA 族参数化变体（#81/#86 律）｜单向波动差值=VOLATILITY 族择时变体｜时变夏普=动量+vol 族派生读数（derived index view）｜'
       '趋与势量化定义=slope 族原语组合｜点位效率理论=ER 动量族参数化变体｜技术指标形态识别+识别圆弧底=patterns 族（ma_converge 在册）扩展面｜'
       '另类价量共振=量价族择时变体（MF/资金流面近邻）｜CCK 羊群效应=REGIME_GUARD/breadth 族状态变量近邻（CSAD 离散度=拥挤读数·'
       'REGIME_GUARD 冻结面零触碰）｜反转之力微观来源=反转族（GTJA 070/081）微观构造变体｜高质量动量（Gray 图书）=动量族风险调整变体｜'
       '行业有效量价因子轮动=轮动族量价变体（MF_ROT_S1 负先验暴露在案·新 prereg 负先验担）｜隔夜日间 lead-lag 网络=并入 #11 网络族储备'
       '（同构 O(N²) 全史相关网络算力重条款））+ **1 条 ML 储备**（小波分析 SVM=ML 择时类·波-9 verdict 同）+ **3 条方法论/本体零新**'
       '（多因子指数增强/DE 进化算法=组合构建方法论非信号族·因子择时=T-81 profile cards+L3 activation 本体在产）+ **7 条 C/D 级**'
       '（北向资金交易能力=数据源死亡（实时披露停发）｜ETF 日内动量=分钟面未批域 P1 署名律｜基金经理超额收益=季频持仓面未批｜'
       '企业生命周期=季频基本面+IPCA 算力重｜分析师金股=外部订阅源缺位｜罗伯·瑞克现金流法则+FFScore=基本面价值域未批 P1 署名律）'
       '——funnel 27 收割/2 过闸（#95/#96 新行）。\n')
txt = txt.replace(bullet_anchor, w10 + bullet_anchor)

open(P, 'wb').write(txt.encode('utf-8'))
# self-verify: rows count, ids, byte faces
raw2 = open(P, 'rb').read()
assert b'\r\n' not in raw2 and raw2[:3] != b'\xef\xbb\xbf'
t2 = raw2.decode('utf-8')
import re
ids = sorted(int(m.group(1)) for m in re.finditer(r'^\|\s*(\d{1,3})\s*\|', t2, re.M))
print('PASS rows=%d max_id=%d tail_ids=%s' % (len(ids), max(ids), ids[-4:]))
print('95/96 present:', '| 95 |' in t2 and '| 96 |' in t2, '| wave-10 bullet:', '波-10 face (c) 二扫裁定补遗' in t2)
