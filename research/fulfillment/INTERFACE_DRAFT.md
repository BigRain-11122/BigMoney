# BigMoney 履约引擎接口草案 v0.1（INTERFACE_DRAFT）

> **状态：DESIGN ONLY · 非约束性设计草案，待 GM+HQ 审后升 v0.2**（J18 式纪律：
> 本件不构成任何判据/引擎/运行时变更）。
> 出处：T-2026-09-24-38（P1 · GM 署名=集团决策 D-20260924-10 BigMoney 腿 ·
> bm-a r104 开票）；起草=bm-b r122（dept:工程+交易部接口面 · 研究部 consult
> SCIENCE 披露字段）；**本票零引擎/运行时代码改动**（验收 d）。
> 业务框定：BigDomain 观测付费产品（19.9 算力验证包形态）需要 BigMoney 引擎供给；
> 收款出口=BigCompute（随 D-09）；分账三面=产品 BigDomain 大头 / 引擎 BigMoney
> 服务费 / 出口 BigCompute 通道费（D-10 定案）。

## §0 合规死红线（D-10 定案 · 全文置顶 · 一切节次于本节）

1. **9.9/19.9 卖的是「算力验证服务」，不是荐股**。输出语义恒为
   verification-service（算力验证服务）：交付物=回测/纸面**观测数据**+证据指针
   （evidence_cutoff / 试验数 N / 判定门状态），**永不**交付直播荐股。
2. **输出物零买卖建议字段**：出口 JSON schema 中不得出现 buy/sell/signal/
   advice/recommend 类字段（§3 schema 以 `advice_fields: []` 空数组自证）；
   逐股实时建议=禁区；输出为历史观测+统计口径。
3. 实盘/真金面零触碰：T0 实盘开闸门、iron_rules 三红线+熔断（AI 自动复盘）
   仍为全部合规边界；本接口只服务「观测验证」，不接任何交易执行路径。
4. 引擎侧数据铁律不因商业化放松：禁未来数据 · 样本外恒盲 · 成本恒开
   （26bp+T+1 冻结）· 预注册先行 · 随机基线+试验数 N 全记（BACKTEST_PLAN 三铁律）。

## §1 输入契约（一份「观测付费请求」携带什么）

```json
{
  "request_id": "<BigCompute 出口签发的请求号，引擎侧不解读>",
  "target": {
    "universe": "STRATEGY_LIBRARY | ASTYLE_ZOO",
    "id": "<注册交易员号（如 NEEDLE-DE-01）| 动物园条目号（如 zoo#41）| 引擎因子 id>",
    "variant": "default | CE（注册员的出场机；库内冻结预设，禁自由参数）",
    "params_preset": "<只许引用库内冻结预设键；无 ad-hoc 调参=反 snooping 设计>"
  },
  "observation_window": {
    "as_of": "<观测截止日，必须 <= 当前 evidence_cutoff>",
    "lookback": "<回看窗规格（预设模板：全史/近N年/指定政体窗）>"
  },
  "virtual_capital": {
    "initial_cash": "<虚拟资金（观测口径；t35 纸盘先例：CNY 记账面）>",
    "cost_model": "on-frozen-26bp-T+1（不可协商关闭）",
    "risk_rows": "iron_rules 只读镜像（单标的≤10%/总仓≤80% 等）"
  },
  "channel_auth": "<BigCompute 出口通道签名（D-09 收款出口对齐）>"
}
```

校验门（引擎侧拒绝行，reject 即回执不计费争议）：id 必须在
STRATEGY_LIBRARY/ASTYLE_ZOO 在册面且属**允许观测集合**（注册员/G1' 候选/判负
归档皆可观测——诚实负结果也是可交付观测）；窗口不得越 evidence_cutoff
（禁未来数据）；params 只取冻结预设。**未知 id/越窗/自由参数=拒绝行**。

## §2 引擎执行契约（BigMoney 跑什么、只返回什么）

- 跑=**预注册策略计算**：在自有面板数据（core48/Money02 深史）上确定性重放，
  注册员类目标附随机信号基线对照+试验数 N 记账；一切观测跑批走既有预注册/
  判据面（禁为出货另立判线）。
- 返回=**观测输出且仅观测输出**：回测/纸面观测数据（净值曲线、成交账本、
  聚合统计）+ evidence_cutoff + trial-count N + 该目标在库内门禁链上的
  **判定状态原文**（含诚实判负：FAIL/收线状态如实交付，禁止只报喜）。
- 观测跑批与账本 N 记账同口径：验证服务跑批同样入试验账本（零假设记账律，
  防商业化面成为账外后门）。

## §3 出口通道交接（output JSON schema v0.1 · 交 BigCompute 收款出口）

```json
{
  "request_id": "<回显>",
  "target": { "universe": "...", "id": "...", "variant": "..." },
  "observation_window": { "as_of": "...", "lookback": "..." },
  "results": {
    "equity_series_ref": "<聚合/截断行数引用（原始面板不出司，见 §5）>",
    "trades_n": 0, "sharpe": 0.0, "annual_return": 0.0, "max_dd": 0.0,
    "oos_four_mandatory": { "oos_trades_n": 0, "years_covered": 0.0,
      "regime_windows_n": 0, "ci95_width": 0.0 }
  },
  "provenance": {
    "engine_version": "<引擎版本指纹>", "evidence_cutoff": "YYYY-MM-DD",
    "n_trials": 0, "cost_model": "on(26bp+T+1, frozen)",
    "random_baseline": { "mu": 0.0, "sigma": 0.0, "n": 0 },
    "prereg_ref": "<预注册文件指针（在库状态原文）>"
  },
  "verdict": { "library_status": "<库内判定状态原文（含诚实判负）>" },
  "metering": { "...见 §4..." },
  "compliance": { "output_class": "verification-service", "advice_fields": [] }
}
```

provenance 字段=SCIENCE 披露律法定面：`evidence_cutoff` 顶层必带（science_audit
C2 合法键）、`n_trials`、`cost_model` 恒 on、注册员类观测附**四必报**
（OOS 笔数/覆盖年数/独立政体窗数/CI 宽度）。

## §4 分账接口注记（D-10 三面分账 · 引擎只出计量事实、零计费逻辑）

引擎侧只发**计量字段**，计费逻辑全在 BigCompute：

- `compute_units`：引擎侧可测事实=面板-日数（panel-days touched）+ 试验数
  n_trials + 运行墙钟；
- `data_authorization_rows`：本次交付中属 §5「可计费授权行」的行数（独立于
  compute_units 单列——见 §5 保留点处置）；
- `service_class`：9.9 / 19.9 档位回显；
- `product_ref`：BigDomain 产品方指针。

三面分账（产品/引擎/通道）比例与结算=BigCompute 侧规则，引擎不实现不存储。

## §5 数据授权行（D-09 BigMoney 数据授权行 · D-10 本地 7b 保留点处置）

**可出司边界（=可计费授权行）**：聚合观测统计（净值/回撤/Sharpe 等聚合面）、
成交笔数与匿名化聚合账本、门禁判定状态、provenance 元数据、预注册指针、
公开知识行（库内已披露口径）。以上行为 BigCompute 计量
`data_authorization_rows` 的对象——**数据授权费挂在「验证输出行」上**。

**永不出司（internal-only · 不可计费）**：原始面板行（core48/股票池原始
OHLCV）、Money02 前代档案内部件、C2 锁盒/前向锁盒累积数据、成员持仓文件
（paper export 的 CNY 持仓面=司内只读消费面）、SEED_REGISTRY 内部账、
逐股实时行情级数据、任何可再生成原始面板的充分细粒度导出。

**保留点处置（D-10 本地 7b 审「平台公司收不到数据授权费」风险）**：若出口
只按 compute_units 计费，数据授权收入面恒为空。本草案的处置=`data_
authorization_rows` **独立计量字段**（§4），使授权腿可计费；同时坚持原始
数据永不出司（授权计费对象=聚合验证输出行，非原始数据本身）。该处置为
接口层方案，分账归属裁决归 GM+HQ 审（v0.2 议题）。

## §6 验收自检与后续

- (a) 非约束声明：本文件 v0.1 DESIGN ONLY，待 GM+HQ 审；禁据此实施。
- (b) smoke 23/23 不变（r122 轮内实证）。
- (c) 五节齐备+合规死红线显式置顶 ✓（§0-§5）。
- (d) 零引擎/运行时代码改动（本文件为唯一产物）✓。
- 后续：GM+HQ 审 → 意见回注升 v0.2 → BigDomain/BigCompute 跨组织交接走
  各自台账（本票只产草案，不代对方开票）。

—— bm-b r122（dept:工程+交易部+研究 consult）
