# 调研纪要 DIGEST-20260924-rd-agent · RD-Agent 深读（J13 迭代参照）

> O-1636 外调队列末项（styles-sweep 下场队 ③）。认领=MSG-20260924-0900（commit dbd13ed）。digest 类：零引擎、零新依赖、账本双线不动。
> 执行体：bm-a round 61（dept:研究）· 2026-09-24

## 一、来源与评级

| 来源 | 要点 | 相关性评级 | 动作 |
|---|---|---|---|
| arXiv 2505.15155（R&D-Agent-Quant，**NeurIPS 2025 接收**） | RD-Agent(Q)=首个 data-centric 多智能体框架，因子-模型协同优化全栈自动化；两阶段迭代=Research（目标对齐 prompt→领域先验假设→任务映射）+Development（Co-STEER 代码生成体→真实回测）；反馈段评估实验结果驱动下轮；**多臂老虎机排程器做方向选择**；实盘市场实证：单圈成本 <$10 下 **ARR≈2× 经典因子库（用 70% 更少因子）**、胜 SOTA 深度时序模型 | **A**（方法论）/C（复现引入） | 机制吸收入 J13 v2 迭代方向（§三）；bandit 排程=未来预注册候选 |
| github.com/microsoft/RD-Agent（MIT，14.7k stars，1023 commits，活跃） | RD-Q 场景族：`fin_quant`（因子+模型联合）/`fin_factor`（纯因子）/`fin_factor_report`（**财报→因子提取**）/data_science/Kaggle/FT-Agent；**当前仅支持 Linux**+Docker 必须+conda py3.10/3.11+LiteLLM 后端（OpenAI/Azure/DeepSeek API：ChatCompletion+json_mode+embedding 三能力）；MLE-bench 榜首（o3(R)+GPT-4.1(D) 30.22%）；Web UI 安全硬化成熟（强制 auth token、pickle 反序列化默认禁、上传扩展名拒绝） | **C**（整框架引入）/D（fin_factor_report 设计参照） | 不引入（工程栈三重不合）；报告→因子管道设计=负面事件库（P1 署名件）未来参照 |
| readthedocs（RDAgent v1.0.0 文档树） | 场景分册+**自定义 Train/Valid/Test 时间段配置**（fin_factor/fin_model/fin_quant 三节） | C | 自定义时间段=与我们 evidence_cutoff/前向锁盒同构——第三方印证 O-2215 D2 方向 |

## 二、机制读数（对 BigMoney 的映射）

1. **R&D 循环结构同构**：hypothesis→implement→backtest→feedback→next ≈ 我们的 预注册→批跑→门禁→预测对照→外推迭代（J19 范式）。**我们已有的不是缺环**；增量只在两处——
2. **多臂老虎机排程（真增量①）**：方向选择机械化=按各家族边际收益历史排序下一批优先级。我们现状=playbook §6 定性排队。轻量版=UCB1 over gate_attrition/IC 批历史（L1 纯确定性脚本零新依赖），排 batch-queue 优先序。**须另开预注册才可立项**。
3. **经验库结构化（真增量②）**：他们把每轮实验反馈结构化存取；我们的等价物=CODELY.md/坑册/STRATEGY_LIBRARY 判定律（散文态）。已有 D6/same-family 拒收线覆盖同族防重，机器可读化=改进候选非缺口。
4. **「70% 更少因子、2× ARR」印证我们的 IR 墙谱系**：合成/精选胜过广撒网——与 XLIB/P-2/PS2 三证「合成增益在 IC 不在 IR」「强货架效应」同向。外部独立证据，非新定律。
5. **成本与算力诚实**：论文「<$10/圈」系 o1/o3/GPT-4.1 级 API token 口径——与 O-2325 local-first 结构性冲突；我方 J13=qwen2.5:7b（数字误读已知），**只配做 idea 生成器（公式草稿+机制段落草稿），判定权恒在 L1 门禁脚本+预注册纪律**，advisory only 不变。

## 三、采纳边界（防镀金）

- **A 级（方法论，即时有效）**：§二-1/4 = 现有机制的印证与读法补强，零动作。
- **B 级（已批域，须预注册才开工）**：①bandit 批队列排程（研究部，L1 类）；②J13 v2「LLM 提因子公式草稿→L1 IC harness 判定→PREREG_TEMPLATE 走门」迷你环（工程部，须先过 7B 能力预检=盲测公式草稿合格率）。均**未立项**，入开放池候选。
- **C 级（不引入）**：整框架=Linux+Docker+API 成本三重不合（机队 Windows/local-first/自有引擎），parked；若未来复评，DeepSeek 后端=最省路径。
- **D 级（储备）**：fin_factor_report 的「报告→因子」管道设计，负面公告事件库（QuantBull 资产，P1 署名件）消费时参照。

## 四、坑与注记

- 「Linux only」写在其 README 顶部首行——Windows 机队结构性排除，勿按截图宣传照误判可装。
- qlib 数据格式（bin）≠ 我方 CSV/parquet 面板；真引入须做转换层（C 级成本的一部分）。
- 其论文实证域=A 股个股模型化 IC+回测口径，非我方 ETF 引擎门禁口径——**结果数字不迁移，方法论才迁移**（域判定律常规适用）。
- Web UI 安全硬化清单（强制 token/禁 pickle/上传白名单）=若未来 J10/J12 面板出网服务的参照，当前 file:// 本地态不需要。

—— bm-a round 61 · 2026-09-24 09:1x · digest 完，开放池候选两条（bandit 排程/J13 v2 盲测预检）均未立项待预注册
