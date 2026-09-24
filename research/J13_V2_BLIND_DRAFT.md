# J13 v2 盲测预检（blind-draft qualification probe）spec — 跑前冻结

- 日期: 2026-09-24 · 认领: bm-a round 64 (MSG-20260924-0935) · 车道来源: R61 RD-Agent
  深读开放池候选#2 / R63 next_pointer #3
- 性质: **L2 能力预检，非研究批**。零引擎跑、零试验账本、零注册、零因子池入册。
  机械合格率 ≠ α；任何真实因子测试仍须另开预注册 IC 批（PREREG_TEMPLATE+null 校准+账本）。

## 0. 背景与动机

R61 RD-Agent 深读定案：我方 OS 循环与 RD-Agent(Q) R&D 环已同构；真增量之一 =
J13 v2「7B 出因子公式草稿 → L1 IC harness 判定」迷你环。但 qwen2.5:7b 与论文
o1/o3 级模型能力差距大，开工前须先盲测公式草稿合格率（R61 原文条款）。

## 1. 冻结协议（跑前写死，跑后禁改）

### 1.1 生成侧
- 模型: qwen2.5:7b-instruct（J13 常驻 Ollama serve，复用 `scripts.llm_assist.chat()`，
  零新传输代码；不碰 keepwarm.pause 阀=单次短推理）。
- 参数: temperature=0.7、num_predict 上限 512、num_ctx=4096（提示词 ~500 tokens）。
- N=10 次独立生成，同一固定 prompt（盲测：不给示例、不给评估标准、不给已知好因子提示）。
- 用户 prompt 逐字冻结（英文，代码生成对 qwen 更稳）:

```
Write ONE alpha factor formula for Chinese A-share ETF daily bars.

Available inputs are pandas DataFrames with DatetimeIndex (rows=trading days)
and columns = 6-digit ETF codes:
  open, high, low, close, volume, amount

Rules:
1. Use only past and current-day data. No future data (never use negative
   shifts or reference future rows).
2. The result must be assigned to a variable named `factor`, a DataFrame with
   the same index and columns as the inputs.
3. Cross-sectionally comparable values are preferred, but raw per-symbol
   values are acceptable.
4. At most 8 lines of code.

Respond with EXACTLY one fenced python code block, then one final line of the
form: NAME: <short_factor_name>
```

- system prompt = J13 现行 SYSTEM_PROMPT（公司铁律内建）。

### 1.2 判定侧（L1 机械门，逐字冻结）
每份草稿依次过五门，任一门败即记败因：
- **E1 extract**: 从回复中提取 fenced code block；须含 `factor =` 赋值；
  须含 `NAME:` 行（提取失败记 extract_fail）。
- **E2 syntax**: `compile()` 通过（失败记 syntax_fail）。
- **E3 lookahead-static**: 禁 `shift(-`（唯一无歧义的前瞻原语；失败记
  lookahead_static_fail）。
- **E4 compute**: 在命名空间 `open/high/low/close/volume/amount`（core48 裸码
  面板，全部历史）上 `exec`，30s 超时；异常记 compute_fail。面板只读，
  exec 沙箱=受限命名空间（无 import 走私：`__builtins__` 白名单未做——诚实注记：
  本探针跑在可信本地 7B 输出上，非外部内容）。
- **E5 validity**: `factor` 为 DataFrame 且 reindex 对齐面板后——非全 NaN
  （≥50% 交易日有 ≥5 个有限值，5=公司横截面下限先例）、无 inf 主导
  （有限值占比≥50%）、有横截面方差（≥30% 交易日截面 std>0）。失败记
  invalid_output_*。

### 1.3 判据条（跑前冻结）
- mechanically_valid_rate = 过 E1-E5 草稿数 / 10。
- **≥0.3 → draft-mill viable**（J13 v2 迷你环可进入下一步：预注册 IC 判定协议设计）；
- **0.1-0.2 → marginal**（prompt 工程后再测，不进入实现）；
- **0.0 → park J13 v2**（7B 判定不适合该岗位）。
- 合格草稿**不入任何池**（7B 主张非指令；留档 JSON 仅供后续预注册参考）。

### 1.4 预测（跑前写死）
- qwen2.5:7b 对结构化代码任务输出格式遵循度尚可：E1 提取率 ≥60%。
- pandas 语义错误（对齐/链式）会杀一批：E4+E5 综合合格率预测 [30%, 60%]。
- 最常见死因预测：因子名重名（`open/close` 覆盖输入——被 E4 崩或 E5 掩码暴露）。

## 2. 产物
- `scripts/j13_draft_probe.py`（run/selftest 两子命令）
- `results/shortline/j13_draft_probe.json`（逐草稿记录+汇总+audit 段）
- `research/digests/DIGEST-20260924-j13-blind-draft.md`（一页纪要）

## 3. 边界与诚实声明
- 本探针不产出任何有效性主张；合格率是 L2 岗位能力读数。
- 判定权恒在 L1 门禁+预注册（R61 条款原文精神）。
- 引擎零跑、账本 N 双线不动。
