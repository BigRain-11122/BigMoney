# DIGEST 2026-09-26 wave-10 face(e)：arXiv 周度常设学术通道首扫（R153 配方）

> T-2026-09-26-76 wave-10 face (e) · bm-b r260 · O-1721 外源常态链 · RESEARCH_MECHANISM §二学术源
> 单写者=bm-b；串行 pacing（R109）；零登录零绕墙；fetch-fail 诚实记录；funnel 双列律照报。
> 通道=arXiv API `export.arxiv.org/api/query`（R153 实证开放正道）分类查询 q-fin.PM/q-fin.STR + submittedDate 窗。
> 机读面=scripts/arxiv_sweep.py（新常设脚本）→ results/harvest/arxiv_sweep_20260926.json（本周窗 2026-09-19..09-26）。

## §〇 通道实况

- 2 次分类查询（q-fin.PM / q-fin.STR）串行 3s pacing；PM totalResults=4 / STR totalResults=0（本窗慢周合法读数）。
- 通道坑与修（工程律）：①python 默认 SSL ctx 对 arxiv 链缺中间证书（CERTIFICATE_VERIFY_FAILED）→ certifi CA bundle 正解；②排序+过滤查询冷跑可 >30s → timeout 60s+单重试。两条坑已固化进脚本头注与 selftest 形态外（运维面）。
- fetch-fail：无（两次查询全中；SSL/超时坑当轮即修即过）。

## §一 窗内 4 件判定（标题+摘要级 triage，借力律：宣称≠验证）

| # | arXiv | 标题（缩） | 判定 | 映射 |
|---|---|---|---|---|
| 1 | 2609.27051 | Propose, Don't Judge: Anytime-Valid Referee for LLM Factor-Mining Agents | **A 级线索（方法论族）** | LLM 代理挖因子+冻结统计裁判（anytime-valid 打分、仅用提交后市场结果、十年 CSI500 walk-forward、泄漏裁判对照）——与我司「代理提案/冻结门判读」架构同构面（prereg+science_gates+OOS 恒盲+null 基线）；直接对话 C-arm（T-70/T-73 盲评轴）与门完整性律（R242「门被游戏」族的正式统计升级路径=anytime-valid 顺序检验替代固定阈值） |
| 2 | 2609.27113 | Active PM in Concentrated Equity Markets（SPT，EW vs cap-weight 制度依赖） | **B 级线索（既有族先验补强）** | EW 落后于「集中度上升+高相关」制度（泡面期）→ EW6_PORTFOLIO/alloc 组合线的经济先验+market_clock 集中度制度面候选读数；我司 CONC-TOP2/容量面（R259 constrained 11/20）同题材互证 |
| 3 | 2609.29887 | Cost-Sensitive Online Window Size Selection（窗口=experts 在线聚合、turnover 含损） | **C 级观察池** | 回看窗选择=我司 blend/锦标赛/时钟袖珍的活设计面；turnover-inclusive loss 与我司成本诚实同向；但在线学习 regret 数学重、落地需预注册，无近期拉力 |
| 4 | 2609.26349 | Integrated Variance Clocks（IVC-BSDE 最优投资消费） | **D 级 PASS** | 连续时间随机控制理论面，无日线可算落地脸，不入册 |

## §二 反重复与登记

- **零新族**：#1=既有族（科学门禁/评价体系族=T-63/T-02/science_gates 链）方法论补强；#2=既有族（EW6/alloc/市场时钟集中度面）经济先验；#3=既有族（blend/锦标赛窗选择面）远期观察。
- 登记（素材级，非采纳——一切采纳必过门禁链）：#1 进门禁方法论素材池（本 digest 在册，deep-read 候选首位）；#2 进 EW6/alloc 族经济先验素材池（本 digest 在册；消费面=未来 EW 系新预注册引用，EW6_PORTFOLIO 冻结件零触碰）；#3 观察池一行（本 digest 在册）。
- 拥挤标注：#1 LLM 挖因子=当红拥挤方向（采纳面照 folklore 五要素披露）；#2 SPT/EW tilt=业界成熟面。

## §三 funnel（双列律）

- 本片：faces 收割 **4** / 过闸 **0**（零采纳零接线——素材级登记不涉门禁）；新族 0；引擎接线 0。
- 采集≠入册，入册率低=正常诚实态（O-1721）。

## §四 续作指针

- **deep-read 候选**：#1 2609.27051（anytime-valid referee）——若 deep-read 证实其 e-process 配方可移植，消费路由=science_gates 方法论强化票（顺序检验面：我司 beat_rate_6m≥0.70 类固定门的多重偷看面正式化），属既有科学链工程面非新方向；deep-read 前按借力律维持 UNVERIFIED。
- 下周同窗 sweep=arxiv_sweep.py 幂等当日件、周窗自动滚动（next: 2026-10-03 窗）。
- face (a) 三通道（jisilu run-9/hibor run-5/guorn run-3）+jin-gong 开市假说=09-28 开市窗接力（date-gated）。
