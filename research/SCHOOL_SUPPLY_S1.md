# T-87 流派补给批 s1 枚举（O-20260926-2320 §三·T-2026-09-26-87）

- 依据=票 spec（anti-dup hard law）+ T-73 s1 调研正典 `research/digests/DIGEST-20260926-t73-cn-schools-s1.md` §一 16 行表（**零发明：只引用调研原文行名与判定**）。
- 判负族不重开律：judged-closed 面只有新证据+新预注册才可再入（判负族不重开）。

## 一、16 流派总账（survey §一 原行号）

| 行 | 流派 | 状态判定 | 依据 |
|---|---|---|---|
| 1 | 游资打板/敢死队 | **judged-closed**（WILD-S1 25 臂 0 幸存，P01 打板 −2.08 等） | WILD_ROUTE_PREREG_S1 §8；T-57 |
| 2 | 低吸半路首板 | **judged-closed 同族面**（WILD-S1 P03a/b 断板低吸/反包 −0.85/−0.82 DEAD；P01 首板族） | 同上 |
| 3 | 龙头战法 | **部分 consumed**：涨停龙头面（P11 龙字辈/全名、P09 高度跟风）judged DEAD；**板块龙头非涨停面=新面候选**（板块垄断溢价≠涨停事件流，D6 披露后可入新 prereg） | WILD-S1 §8 表 |
| 4 | 题材概念轮动 | **PENDING**（survey 可建模性原文「低——事件面日线建模弱」；待事件/题材数据面，暂不 prereg） | survey 行 4 |
| 5 | 跟庄牛散 | **不可行域**（survey §四：庄股跟风=合规禁；照登不建模） | survey funnel 行 |
| 6 | 动量族 | converged 在册（T-47 供给线；短期反转/动量律 s2 slice-A 已判） | survey 行 6 仓内证据 |
| 7 | 红利低波高股息 | **judged-closed**（CN-DIV-LOWVOL-ROT R252 判负 0/4） | CN_COMBO_VERDICTS |
| 8 | 中特估/国家队风格 | **未建模=新 prereg 候选 #1**（survey 可建模性「高」；央企 ETF/指数成分跟随；data/daily 央企类 ETF 面可用） | survey 行 8 |
| 9 | 价值投资 | **data-gated PENDING**（survey「中（基本面数据面依赖）」；仓内 fundamental 仅 eligibility/b_layer_mask，无 PB/估值史面——先数据审计后 prereg，禁无米之炊） | survey 行 9 |
| 10 | 成长投资 | **data-gated PENDING**（同上，财报滞后面） | survey 行 10 |
| 11 | 双低转债 | converged 在飞（T-60 转债线在飞批） | survey 行 11 仓内证据 |
| 12 | 配置β/ETF 轮动 | **judged-closed**（CN-REGIME-POLICY R256 负 + CN-CORE-SATELLITE R261 负 + CN-CORE-DDCTL R263 负；T-59 ALLOC 前向观察线照飞） | CN_COMBO_VERDICTS |
| 13 | K 线技术/波段 | **部分 consumed**：网格腿=GRID-SLEEVE-P1 判负不重开；**形态识别面=候选 #3**（社区共识五要素 folklore 门未过=先外源考后 prereg，RESEARCH_MECHANISM v1.1 律） | survey 行 13 |
| 14 | 趋势跟踪 | **未建模=新 prereg 候选 #2**（survey 可建模性「高」；时序趋势≠行 6 截面动量=不同机制面；均线/突破跟随；ETF 日线面板直用） | survey 行 14 |
| 15 | 多因子/指数增强 | **converged→T-86**（因子融合普查线即本面，禁双开：s2 prereg 不另立，消费 T-86 census 候选） | survey 行 15 |
| 16 | 市场中性/微盘/T0 | 微盘=2024 崩塌判负禁翻案；T0=红线外；中性=**候选 #4**（股指期货 IC/IF/IH 在库+对冲腿数据面成立；「融券面依赖如实低」注记；期货 CTA 判负×3 禁翻案边界=本面非 CTA 趋势是股票多空对冲，需 prereg 内显式机制区分披露） | survey 行 16 |

## 二、s2 prereg 供给队列（认领顺序=可建模性×零判负重叠）

1. **#1 行 14 趋势跟踪**（时序趋势·均线/突破·ETF 面）——最高可建模性、机制面与全部判负族零重叠；T-47 是截面动量不同面。
2. **#2 行 8 中特估/国家队**（央企 ETF/成分跟随）——高可建模性；与红利低波判负面做 D6 同族检查（红利低波袖同 ETF 域，须 max|corr| 披露）。
3. **#3 行 13 K 线形态面**（网格腿除外）——folklore 门先行（外源社区共识考），过门再 prereg。
4. **#4 行 3 板块龙头非涨停面**——WILD-S1 涨停面判负披露+D6；板块相对强弱龙头定义冻结后方可入。
5. **#5 行 16 市场中性**——工程量最重（期货保证金/移仓成本模型）；CTA 禁翻案边界机制披露。
6. 行 9/10 价值/成长=数据审计先行批（估值/财报史面缺）后才入队列；行 4 题材概念=待事件数据面；行 5 合规禁永不入。

## 三、纪律

- 每流派 s2=设计决策+prereg 冻结先行（R99 律）→全史回测 G1'v2 judged cells x1+x2+分段；判负照报、slot 关闭注记。
- 幸存者 → STRATEGY_LIBRARY 入册 → 供给 T-85 s4 融合候选池（票面 cross-ref）。
- 三态标注（立法/生效/验收）+ post_review 面照 O-2115。

—— bm-a R277 开票即 s1 收口；s2 首两个 prereg（趋势跟踪/中特估）下一批落地，精确续作点=本文件 §二 队列。
