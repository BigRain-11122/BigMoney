# OH-20260929-bigmoney — 开源收获轮·BigMoney 切片 1（首窗）

- **窗**：首窗 2026-09-26 21:40 → 2026-09-29 21:40；本切片=2026-09-29 02:0x（BigMoney 实体首片·补齐窗内落地·正典=cph4/oss-harvest.md v1.0·T2 否决窗至 10-03）。本实体业务面=量化子公司（策略工厂/判决台/纸盘/数据采集链/算力池）；判据基面=firm/LOCAL_FIRST.md 本地化路由（L1 确定性零 token/L2 本地 LLM/L3 云端关键面）——提效候选以「本地可跑+省真资源+一句话映射业务线」为纲。
- **反重复门基线（先查后采·三面）**：①cph4/README.md 能力注册表 grep optuna/qlib/polars=零命中（开源采用 3 例在册无撞）；②仓内面：requirements.txt 零命中·PLAN.md 既有「Optuna 贝叶斯调参骨架」排队 J 件（=本采的消费面·采库不重复建管线）·scripts/Tools 零 import·T-110/O-1716 工具栈验证集（22 real：backtrader/backtesting/vectorbt/rqalpha/akshare/baostock/tushare/easyquotation/quantstats/stockstats/alphalens-reloaded/duckdb/pyqlib/pandas-ta 等）无 optuna=净新增；③姊妹 OH 六件 grep 本窗候选词零命中。
- **实搜面（7 处网页读取·4 成 3 死·采时 2026-09-29 02:0x·零登录墙）**：①api.github.com/repos/optuna/optuna=14,857★·1,398 forks·pushed 2026-09-25·非归档·open_issues=18·license=MIT（API 判定）；②api.github.com/repos/optuna/optuna/license=LICENSE 原文 base64 逐字解码=「MIT License / Copyright (c) 2018 Preferred Networks, Inc.」全文在验（许可门原文证据）；③api.github.com/repos/microsoft/qlib=49,009★·7,747 forks·pushed 2026-09-22·非归档·open_issues=481·license=MIT；④pypi.org/pypi/optuna/json=113,676B 超内联限（截读弃用·非死面）；⑤raw…/optuna/LICENSE.md=404（文件名猜测失败·真名=LICENSE 无扩展——失败面实录）；⑥raw…/optuna/LICENSE=abort 超时（网络面·后经 license API 绕道补全原文=③号面）；⑦web_search 原生通道=410 Gone（2026-09-27 死面复验仍死·legacy 端点下线·不硬闯）。
- **候选（2 件逐件五门：1 过 1 parked）**：Optuna（github.com/optuna/optuna·MIT·超参优化框架=贝叶斯调参骨架执行库）；Qlib（github.com/microsoft/qlib·MIT·AI 量化平台=parked 平台重叠）。
- **采用→落点**：**Optuna 5.0.0 实装入 bm-c 隔离 venv**（C:\Users\Dasheng\.bm-tools\venv·O-1716 隔离律=零触碰系统 python/OS 循环环境）+双烟测 PASS（import OK+seeded RandomSampler 迷你优化 5 trials best 22.847）；消费面=PLAN.md 排队件「Optuna 贝叶斯调参骨架」定库（淬炼轴/REFINE_BENCH 手段轴网格扫描的贝叶斯替代面——同 CPU 预算更高搜索效率·L1 本地零 token）；集团登记=cph4/README.md 开源采用第五例行（本 commit）。
- **parked+理由**：Qlib——①平台件与自有 engine/science_gates/池调度重叠（禁双建律·反重复门不过）；②其 Alpha158 因子定义知识面已由 O-20260928-1815 ① GM 供料批收割在烧（学实现不搬件·借力律正形）；③pyqlib 包已在 O-1716 验证集、按 O-1750 needs-based 律待消费线触发再装——三面叠加=不采平台只续收知识面。
- **下窗指针**：下一窗=2026-09-29 21:40 → 10-02 21:40；候选苗=polars（L1 确定性因子普查批提速面·许可待验）/vectorbt 许可原文逐字验（bm-b 已装·O-1716 verified real 但 LICENSE 原文未验）/pandas-ta 信号语料（O-1716 验证集内·许可验后可用）。

## 结论应用表（research-protocol §结论应用律强制·无表=未交付）

| 候选 | 五门判定 | 落点（改了什么） | 消费面（谁吃产出） | 状态 |
|---|---|---|---|---|
| Optuna 5.0.0 | 契合✓（贝叶斯调参骨架执行库·替手写网格）/反重复✓（注册表+仓内+T-110 集三面零撞）/许可✓（MIT 原文逐字验）/健康✓（14.9k★·pushed 09-25·非归档）/成本安全✓（纯 Python·本地零 token·venv 隔离·in-memory study 零数据外发·依赖面=alembic/colorlog/numpy/packaging/sqlalchemy/tqdm/PyYAML 无红旗） | bm-c venv 实装+双烟测 PASS+注册表第五例行 | PLAN.md「Optuna 贝叶斯调参骨架」排队 J 件·淬炼轴扫描面 | **adopted** |
| Qlib | 契合✓/反重复✗（平台撞自有引擎）/许可✓（MIT）/健康✓（49k★）/成本△（重平台依赖面大） | 无落点=不采（Alpha158 知识面已由 GM 供料批收割） | 知识面续收（O-1815 ① 普查批在烧） | parked |
