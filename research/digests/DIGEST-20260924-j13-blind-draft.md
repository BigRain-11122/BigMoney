# DIGEST-20260924-j13-blind-draft — J13 v2 盲测预检纪要（R64 bm-a）

- 车道: J13 v2 盲测预检（R61 RD-Agent 深读开放池候选#2 · R63 指针③）
- 认领: MSG-20260924-0935（F-04 锁）· spec=research/J13_V2_BLIND_DRAFT.md（跑前冻结）
- 产物: scripts/j13_draft_probe.py（selftest 10/10）+ results/shortline/j13_draft_probe.json
- 性质: L2 能力预检，零引擎零账本零注册零入池；**主张非指令**，人工核验后采。

## 1. 主结果：2/10 机械合格（rate 0.20）→ 冻结判据条=「marginal（prompt 工程后再测，不进入实现）」

| 门 | 计数 | 说明 |
|---|---|---|
| E1 extract | 10/10 过 | 围栏代码块+NAME 行+factor= 全部合规——7B 格式遵循度极佳 |
| E2 syntax / E3 lookahead | 10/10 过 | 零语法死、零 shift(-) 前瞻 |
| E4 compute | 2/10 | **8 份死于同一 NameError: name 'df' is not defined** |
| E5 validity | 2/10 保持 | 两份过全部门 |

## 2. 机制定案三条

**(a) 死因单形=约定错配而非能力缺失**。8/10 草稿按「单表 df['close']」习气
答题（tidy 列字典惯例），与 prompt 声明的「六个独立 DataFrame 变量」面板约定
冲突——一次 `NameError` 全灭。这是**一句话可修的 prompt 缺陷**：prompt 只声明
了输入是什么，没排除 7B 量化代码先验里的 `df` 习惯形。

**(b) 多样性塌缩是第二层真约束**。两份合格草稿公式**完全相同**
（`(close - open) / open`，隔夜跳空），且 8 份 df 变体也是同一公式——temp=0.7
下 7B 对裸 prompt 塌缩到单一 canonical 想法。即便修好约定，**草稿磨坊还需要
prompt 侧多样性注入**（风格/家族提示轮换）才能产出可用谱面，否则 N 份草稿
≈ 1 个因子。

**(c) 判定机制按设计工作**。冻结判据条把 0.20 归入 marginal 档并预先声明
「prompt 工程后再测」为合法后继——避免了看结果后即兴改协议重跑的数据窥探
风险；v2a 复测协议在跑前冻结于本纪要 §3。

## 3. 预注册 v2a 复测协议（跑前冻结，下轮执行，禁再改）

- 与 v1 唯一差异=prompt 追加一句约定澄清（逐字）：
  `5. The six inputs are SEPARATE DataFrame variables. There is no variable named df, and df must not be used.`
  （插在 Rules 4 之后，其余逐字不动；N=10/temp=0.7/num_predict=512/判定 E1-E5
  与判据条全部沿用 v1 冻结版。）
- 新增记录列（非门禁）：`n_distinct_valid_formulas`（合格草稿按代码串归一去重
  计数），供多样性塌缩观察。
- 判据条不变：≥0.3 viable / 0.1-0.2 再一次 marginal（则 park，两连 marginal=
  判 7B 不适配该岗位，不再迭代 prompt）/ 0.0 park。
- 若 v2a viable：J13 v2 迷你环进入「预注册 IC 判定协议设计」（草稿→L1 判定
  仍须 PREREG_TEMPLATE+null+账本，判定权恒在 L1 门禁）。

## 4. 预测对账（spec §1.4 跑前写死 vs 实测）

| 预测 | 实测 | 判 |
|---|---|---|
| E1 提取率 ≥60% | 100% | ✓（保守方向对） |
| E4+E5 综合合格率 [30%,60%] | 20% | ✗（高估；未预判 df 约定错配） |
| 最常见死因=因子名覆盖输入 | df 约定 NameError | ✗（机制预测错） |

## 5. 对 J13 v2 迷你环的结论

按 R61 条款「开工前须先盲测公式草稿合格率」：**本轮结论=暂不开工**。
v1 盲测 rate 0.20=marginal，dominant 死因一句话可修但未证实修复；v2a 复测
通过前，J13 v2 迷你环不进入实现。7B 在该岗位的真实画像=格式优秀、语义约定
脆弱、想法谱面窄——与 R61「qwen2.5:7b 只配 advisory idea 生成器，判定权恒在
L1 门禁+预注册」的预期一致。
