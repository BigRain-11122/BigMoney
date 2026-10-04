# OH-20261005-bigmoney — 开源收获轮·BigMoney 切片（D-20261005-05① 回执窗）

- **窗**：D-20261005-05① 派工回执窗（窗 10-06 00:00·点名→回执制首例·本司 10-05 00:4x 落片=窗内首片）。本实体业务面=量化子公司（策略工厂/判决台/纸盘/数据采集链/算力池）；本切片=上窗指针债清偿（OH-20260929-bigmoney 下窗指针三候选=polars 许可验/vectorbt 许可原文逐字验/pandas-ta 许可验后可用）。
- **反重复门基线（先查后采·三面·本窗实跑）**：①cph4/README.md 注册表 grep polars/vectorbt/pandas-ta/pandas-ta-classic=四零命中（开源采用 5 例在册无撞）；②仓内面：requirements.txt/PLAN.md/README.md 三件零命中·git grep 语料命中仅=O-20260928-1716 工具栈验证集（vectorbt/pandas-ta 为 verified real 成员非采用）+短线研究语料（research/shortline/requirements-research.txt·SHORTLINE_PLAYBOOK.md·BACKTEST_READINESS.md 提及面非依赖面）；③姊妹 OH 十四件 grep 本窗候选词=仅自窗上件 OH-20260929-bigmoney.md 指针行（无他司双建）。
- **实搜面（6 处 API 读取·5 成 1 死·采时 2026-10-05 00:3x-00:4x·零登录墙）**：①api.github.com/repos/pola-rs/polars=39,913★·3,152 forks·pushed 2026-10-04·非归档·open_issues 2,930·license=MIT（API 判定）；②api.github.com/repos/pola-rs/polars/license=LICENSE 原文 base64 逐字解码=标准 MIT（Copyright (c) 2025 Ritchie Vink+部分 (c) 2024 NVIDIA CORPORATION & AFFILIATES·许可门原文证据）；③api.github.com/repos/polakowo/vectorbt=9,275★·1,184 forks·pushed 2026-09-26·非归档·license spdx=NOASSERTION（非标=必须原文验）；④api.github.com/repos/polakowo/vectorbt/license=LICENSE.md 12,321B 原文解码=**Apache 2.0 + Commons Clause v1.0**（「License does not grant… the right to Sell the Software」·Sell=以收费向第三方提供价值全部/主要源自本软件功能的产品或服务·Copyright 2026 Oleg Polakow）；⑤api.github.com/repos/twopirllc/pandas-ta=**404 Not Found**（上窗指针正主仓上游死亡·诚实负发现·借力三律工程版实证=外源工具清单半真半假）；⑥api.github.com/search/repositories?q=pandas-ta=1,943 结果中继任正主=xgboosted/pandas-ta-classic（449★·104 forks·pushed 2026-10-02·非归档·license=MIT·250+ 指标+蜡烛图形态·2025-06-17 建=pandas-ta 社区续作）。
- **候选（3 件逐件五门：2 清偿 1 重定向·零新采用）**：polars（MIT·DataFrame 引擎=L1 因子普查批提速面）；vectorbt（Apache2+CommonsClause·回测框架=bm-b 已装 O-1716 verified real·许可原文验闭口）；pandas-ta→pandas-ta-classic（原仓 404 死·继任 MIT·短线研究语料消费面指针重定向）。
- **采用→落点**：**零新装（O-1750 needs-based 律·无消费线触发不装）**。本切片产出=三面许可门清偿+指针重定向：①polars 许可门 PASS=普查提速消费线（pandas 成瓶颈的真实普查烧批触发时）即可装（O-1716 隔离 venv 范式）；②vectorbt 许可原文闭口=内部研究用合法（Commons Clause 只禁售卖软件本身·我方自用回测零触线）·依赖面维持 parked（平台与自有 engine/science_gates 重叠·OH-20260929 parked 理由不变）；③pandas-ta 原仓死亡→**短线研究语料消费面（requirements-research.txt/SHORTLINE_PLAYBOOK）未来引用一律重定向 pandas-ta-classic**（MIT·活跃·250+ 指标超集）。
- **parked+理由**：polars=许可已清待消费线触发（needs-based 非囤积）；vectorbt=平台重叠 parked 维持+许可闭口；pandas-ta 原仓=上游死亡不可采（404）·继任 pandas-ta-classic 记档待触发。
- **下窗指针**：短线族若需 TA 指标实现参照→pandas-ta-classic（MIT）源码学实现（借力律正形=学实现不搬件）；N2 判决面统计工具链（多重比较校正族）候选苗=statsmodels Multipletests 方法学原文（许可验证待做）；风格轮动 drafting（10-06+）外源面=国内券商金工研报风格因子口径对照（经 sources 登记面）。
- **回执**：本件=D-20261005-05① 派工回执（P-51 送达=本司 commit 含 D-20261005-05① 行）；实搜面 ≥2 满足（6 处）；本司反馈面回执行=bigmoney HQ-FEEDBACK.md 2026-10-05 行。

## 结论应用表（research-protocol §结论应用律强制·无表=未交付）

| 候选 | 五门判定 | 落点（改了什么） | 消费面（谁吃产出） | 状态 |
|---|---|---|---|---|
| polars (pola-rs/polars) | 契合✓（L1 普查批提速面）/反重复✓（三面零撞）/许可✓（MIT 原文逐字验·含 NVIDIA 部分版权标注）/健康✓（39,913★·pushed 10-04·非归档）/成本✓（Rust 核+Python API·wheel 面·本地零 token） | 许可门清偿登记（零装·needs-based 待触发） | L1 因子普查批提速（pandas 瓶颈触发时·O-1716 venv 范式装） | **cleared-for-adoption** |
| vectorbt (polakowo/vectorbt) | 契合✓/反重复✓（O-1716 verified real 已在册）/许可✓（Apache2+CommonsClause 原文验=内部用合法·禁售条款不触）/健康✓（9,275★·pushed 09-26）/成本△（平台重叠） | 许可原文验闭口（OH-20260929 指针债清偿）·依赖维持 parked | bm-b 已装面·知识面（其组合回测实现学理） | **parked（许可闭口）** |
| pandas-ta → pandas-ta-classic (xgboosted) | 契合✓（TA 指标语料）/反重复✓/许可✓（继任 MIT·API spdx 验）/健康✓（449★·pushed 10-02·活跃）/成本✓（纯 Python） | **指针重定向**：原仓 twopirllc/pandas-ta=404 死亡实证·继任记档 | 短线研究语料（requirements-research.txt/SHORTLINE_PLAYBOOK 未来引用改 pandas-ta-classic） | **retargeted** |
