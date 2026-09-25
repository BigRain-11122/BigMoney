# DIGEST-20260925 · wave-8 slice-3（O-1721 常态链 · bm-a R154）

> 执行人：bm-a（OS iteration loop R154 · T-2026-09-25-51 wave-8 slice-3 · RESEARCH_MECHANISM v1.1 常态双频）
> 性质：内部研究用途，不构成采纳建议；一切外部内容未经我方门禁复验不得作为采纳依据；无登录、无绕墙、串行步速（R109 律）。
> 票据：T-2026-09-25-51 slice-3（face (c) jisilu feed run-6 + face (d) pending-list 首扫·GitHub 镜像面）；claim lock=18d074cd（r170 claim-lock-first 律，faces (c)/(d) 本片锁）。face (b)=bm-b slice-2 已交付（progress_r171），face (a)=bm-a slice-1 已交付（progress_r153）。

## 〇、通道实况（fetch 记账：jisilu 1 + GitHub API 3 搜索 + 2 树 + 2 README raw=8 外呼，全串行）

- **GitHub search API（api.github.com/search/repositories）=开放零登录新通道实证**：3 查询（`joinquant` total 150 / `聚宽 策略` total 54 / `聚宽 轮动` total 3）全部 200 零墙——聚宽社区登录墙的镜像替代路径（source-matrix 行-2 波-3 承诺腿）本轮闭项；queryface 修正=中文 OR 混合查询（`聚宽 OR joinquant 策略`）返回 10705 泛化噪音（书单/无关库），收窄为纯词面查询后命中精准。
- 探针证据：results/gh_mirror_probe_wave8slice3.json（3 搜索面）+ results/gh_deep_capture_wave8slice3.json（2 仓树+README 全文）。
- jisilu `/feed/category-5.rss` verbatim 一发 200（8,290 bytes·20 items）。
- 坑再证（r168 族）：PS 控制台 GBK 遇 emoji desc 直接 UnicodeEncodeError 崩脚本——探针脚本必须 `sys.stdout.reconfigure(encoding='utf-8', errors='replace')` 前置。

## 一、face (c)：jisilu 套利类目 feed run-6（机读差分）

- 源 URL：https://jisilu.cn/feed/category-5.rss（R138 律 verbatim 形态）
- 结果：**20 items / 0 新 / 0 淌** vs run-5 基线（ts 2026-09-25T10:34+08:00）——同日窗**四连稳**（run-3/4/5/6 同集合），日内稳定代谢再实证；基线已更新至 run-6（ts 2026-09-25T11:01+08:00）。
- 判读：常态道零新=诚实 no-op（防凑数律），feed 通道健康（fetch 新鲜 200）；深捕获候选池本窗零增量。

## 二、face (d)：pending-list 首扫——聚宽策略 GitHub 镜像面（2 仓深捕获）

### 候选 1：robertquant/python_jointquant（13★·聚宽策略集合镜像）

- 来源 URL：https://github.com/robertquant/python_jointquant（main 分支 16 文件全树在 results/gh_deep_capture_wave8slice3.json）
- **在册族变体候选（folklore 参数化，全部「社区声称·未实证」标签）**：
  - **ETF 动量轮动（ETF_rotation_v1.py/ETF_simple_rotation.py）**：趋势得分=**年化收益率×R²**（加权线性回归斜率，权重 1→2 线性递增=近期更重）；每周三 14:50 尾盘调仓持 top-3；安全区间过滤 `0<score≤5`；m_days=25；滑点 0.3%+佣金 0.02% 双边=成本假设与我们 core48 载体同量级。**该评分族=中文社区 ETF 轮动最大公约数 folklore**（与 wzetf 收集站 2026-08-23「聚宽 600 策略」帖同源生态），属既有在册 ETF 轮动族的**变体参数化**非新族。
  - **三宽基轮动（three_index_rotation.py）**：510300/510500/512100 纯动量无止损——与我方 core48 池面直接重叠的最小池变体。
  - **RSRS 择时+价值选股（rsrs_value_strategy.py）**：RSRS 阻力支撑相对强度（N=18/M=1100 样本窗，光大金工系公开方法论）+空仓防御机制——择时面变体候选（REGIME_GUARD 前置快线面参考，非采纳）。
  - **A/H 溢价套利（ah_premium_strategy.py）**：折价买入/溢价过高平仓（聚宽 `finance.STK_AH_PRICE_COMP` 表）——**与 ARB-1（T-16 fund_premium）+ jisilu AH 比价面交叉**：同一经济先验的跨市场兄弟面，社区实现=佐证面非新族。
  - 小市值轮动（5d 调仓·流通市值最小 5 只+ST/停牌/PE/负债率/ROE/现金流过滤）、低估值选股（PB<2 季调）、红利增强（30 只等权月调）、银行股轮动、ETF 乖离率动量——族名逐一登记（详情 README 已存证）。

### 候选 2：stepven8/wufu-etf-rotation-strategy（5★·五福策略族 ETF 轮动独立提取）

- 来源 URL：https://github.com/stepven8/wufu-etf-rotation-strategy（「五福.txt」多策略文件单策略提取：原文含小市值/ETF反弹/ETF轮动/白马攻防四模块——**五福族=社区流传多策略合集**，本仓仅轮动模块）
- **结构要点（README 逐字存证，全部「社区声称·未实证」）**：
  - **动态候选池构造**（本片最有信息量的结构面）：固定全球池（商品/纳指标普日欧/港股红利低波/A股宽基风格/债券）∪ 昨日成交额 top-5 ∪「5 日均额高流动候选中的 5 日涨幅 top-5」——**流动性门+动量门双层动态池**=宇宙构造面变体候选（我方 core48 为静态池，此为动态池先例）。
  - 得分：25 日加权趋势得分，**持 top-1**（集中度与我方组合律对照面）；防御腿=511880 货币基金（无合格进攻标的时切换）。
  - **风险过滤叠加（攻防 overlay 变体）**：近 3 日任一单日价格比<0.97 即过滤（短回撤熔断）；放量过热过滤（当日量>5 日均量 2 倍且年化收益>100% 剔除）；短期动量过滤开关。
  - 诚实边界（仓库自述）：聚宽 API 依赖（jqdata/jqfactor），本地不可独立回测；语法检查≠可运行。

## 三、与我方线对接（消费面路由·零采纳零跑批零 engine 触碰）

- **①进攻军 T-33 补给面**：`年化收益率×R²` 趋势得分+权重 1→2 递增+安全区间 `0<score≤5` = ETF 轮动族 folklore 正典参数化——T-33 进攻军动量面 prereg 素材卡（外源先验，采纳唯一路径=门禁链实战复验；CEO 最高判据：实战出真知）。
- **②宇宙构造变体**：五福双层动态池（流动性门∪动量门）vs 我方静态 core48——变体批候选（预注册对照面：动态池是否在成本约束下胜静态池，须 prereg 后跑）。
- **③风控 overlay**：0.97 三日短熔断+放量过热剔除=ENGINE 层外的过滤面变体，可作 G2 门禁族变体登记（不碰 engine/exit_rules.py 红线）。
- **④ARB-1 交叉验面**：A/H 溢价套利社区实现+jisilu AH 比价公开表+T-16 fund_premium 面板=三面同族经济先验（折溢价均值回归），社区实现仅佐证。
- **⑤反重复律核对**：ETF 轮动/小市值/红利/RSRS 均为既有在册族（STRATEGY_LIBRARY/ASTYLE_ZOO 已载），本片零 SEED_REGISTRY 新族登记、零 engine 触碰、零新数据馈入（GitHub README/代码=公开研究阅读面，P1 数据扩容律不触发）。

## 四、funnel 双列（O-1721 报告律·本片）

| 面 | 收割数 | 过闸数（入册/变体批） |
|---|---|---|
| jisilu feed run-6（20 items 机读差分） | 1 | 0（0 新 0 淌=诚实 no-op） |
| GitHub 镜像首扫（2 仓深捕获：16 文件树+2 README 全文存证） | 2 | 0（folklore 变体登记 5 族面·全部门禁链前置·0 采纳） |
| **合计** | **3 收割面 / 8 fetch** | **0 过闸 / 0 新族 / 0 采纳 / 0 跑批** |

采集≠入册；本片=既有族变体素材卡（T-33 prereg 素材+变体批候选池），非新族收割。

## 五、相关性评级与种子留痕

- **评级：B**（在途域——T-33 进攻军动量面 prereg 素材+G2 变体批候选池+ARB-1 佐证面对齐）。
- hibor 晶宫 run-3 title 雷达：**盘后窗依赖诚实顺延**（票面 spec=post-market window；本片 11:0x 盘中，物理窗依赖+票内留痕=合法暂缓事由，非「排未来轮」违令）。
- 建议动作：T-33 prereg 素材卡引用本片 §二①③；五福动态池变体=变体批候选池登记（GM 署名批才启动）；`robertquant` 仓其余 6 策略文件已树存证可后续按需深读。
- 种子留痕：GitHub search API 通道=常态可复用面（query 收窄纪律：纯词面查询）；`joinquant` 150 库面=后续波次种子库（JizhiXiang/Quant-Strategy 291★/easyQuant/real_trader 148★ 待扫）。
