# REGIME_GUARD 深窗回放 HAND-OFF PACK —— T-2026-09-24-13 deliverable-3

> 状态：**DELIVERED（r122 bm-b）**。性质=纯转写件：**100% 派生自 FROZEN 批产物**
> （`results/regime_deep_replay_v2.json` GATES_OK + `results/regime_deep_replay_episodes.csv`
> 15 段，prereg `research/REGIME_GUARD_DEEP_REPLAY_V2.md` FROZEN r106），零新测量、
> 零判据、零引擎，trials=0。数字逐字取自产物，派生仅限加法计数。

## §1 交付问题与答案（deliverable-3 原文）

「v1/v2 双 FAIL（61.6% residenced / 26.53% vs 25% 目标）是否为 episode 稀缺所驱动？」

**答案：否——稀缺假说被 21 年深窗（2005-04-08→2026-09-22，5216 行，15 个 dd250
episode）证伪，两代失败均为结构性：**

- **v1**：深窗 R+O=53.49%（vs 核心窗 61.6%）→ 「结构性稀缺族」；ORANGE FA=0.6875
  → 结构性坏。核心窗 FAIL 非窗artifact，深窗同判。
- **v2**：深窗 R+O=28.60% ≥ 核心 26.53%（`window_driven_breach: false`）→
  越窗复现=结构坏非窗驱动；ORANGE FA=0.6176。
- **v3**：深窗 R+O=18.36%、ORANGE FA=0.0（episode 内 0、episode 外 0，
  j4_summary）、`robust_out_of_window: true` → 核心窗 PASS（12.01%）后深窗
  复验稳健，**首个跨窗稳健防线**。

推论：v1/v2 的失败源在状态机定义本身（掩蔽面/确认结构），不随样本窗扩容消失；
v3 拧法 B+C 在两窗同过。**enforce 裁决可据此排除「等更多 episode 也许 v1/v2 就
过了」的辩护路径。**

## §2 per-episode 校准统计表（deliverable-3 主交付物）

**正典载体=`results/regime_deep_replay_episodes.csv`**（15 段×三矩阵
G/Y/O/R 计数 + RO share + orange rounds/FA（段内））。逐段读数示例（零派生）：

| episode（窗） | v1 RO% | v2 RO% | v3 RO% |
|---|---|---|---|
| #4 2008 GFC 2008-01-22→2009-06-18（342d） | 84.21 | 80.70 | 78.65 |
| #8 2011-05 机械段→2013-01（402d） | 95.02 | 21.89 | 0.00 |
| #11 2018-05 机械段→2019-03（204d） | 85.78 | 50.49 | 0.00 |
| #13 2021-22 熊 2021-03-24→2023-08-04（576d） | 80.21 | 30.38 | 11.98 |

段内/段外拆分（j4_summary）：v1 R+O 段内 2328d/段外 462d，FA 段内 17/段外 16；
v2 1152/340，FA 8/13；v3 780/178，FA 0/0（段外 orange 回合仅 1 且零 FA）。
→ v3 掩蔽高度向真实危机段收紧（长熊段 RO 压到 0-12%），v1 则全段高烧。

## §3 消费面（谁在何时读）

- **主消费者=`research/ENFORCE_PROPOSAL_REGIME_GUARD_V3.md`**（FILED·否决窗至
  2026-10-01）：其必呈条款 1 的 G2 低统计力注记（核心窗 ORANGE 回合=1 样本）可
  追加本 pack 深窗读数——21 年窗 v3 ORANGE FA 恒 0（段内段外）、R+O 18.36%
  稳健，缓解单回合小样本疑虑但不替代核心窗判据（判据面零改动，只是证据引用）。
- T-10（done，r94/r95）先于 V2 批（r106）收线——本 pack 即票面 deliverable-3
  的补齐件；P-44 过拟合相位后续件（cph4 item5）如启动可复用同一 episodes CSV。

## §4 deliverable-4 基础（数据完整性面，随 V2 批已闭）

D-A PASS（5216 行严格单调零 NaN）+ D-B PASS（10444 bars=5222 parquet 锚全等）
+ D-C v2_b PASS（median 9.792bp≤15 / p99.9 348.87bp≤400，41 危机日，
非危机 max 422.06bp 无界纯披露，超 p99.9 豁免 3 日全微观结构归因）。
**面板缺口诚实披露**（dim_availability）：2005-2015 仅指数面（ETF 宇宙前薄，
prereg s1）；breadth 维度 2020-02-06 起算；FOMC 事件 2020-2026 历法内才可触发
（2020 前不触发=已披露非缺陷）；MA200 首可算 2006-02-08。

## §5 未启项如实披露（cph4 item5）

T-13 分段政体扩检（P-44 后腿，spec=`R-20260924-infra-4-overfit.md` §3）
**本仓/本机不可达=未认领未启动**（r104/r106 双披露，投递请求已递 cph4 层）。
spec 到仓前零启动；到仓后按「纯诊断批·预注册先行·零判据改动」另开认领。

—— bm-b r122（dept:研究+数据）
