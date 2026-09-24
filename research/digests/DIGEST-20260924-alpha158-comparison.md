# DIGEST-20260924-alpha158-comparison — Alpha158 对照导出（外调专项纪要）

> 队列位：O-20260923-1636 外调队下一名（styles-sweep 定队：资金流源专项[R58 已闭环] → **本件** → RD-Agent 深读）。
> 类型：专项纪要（RESEARCH_MECHANISM §三）。执行=bm-a R59（dept:研究·零引擎·账本 N=3041 不动）。
> 交付链：vendored 源件 + `scripts/alpha158_compare.py`（L1 解析器·selftest）+ `results/shortline/alpha158_compare.json` + 本纪要。

## 一、来源与台账

- **Microsoft qlib**（MIT）：Alpha158 特征集定义=`qlib/contrib/data/loader.py::Alpha158DL`（+`contrib/data/handler.py::Alpha158` 包装层）。
- vendored：`research/shortline/external/qlib_alpha158_loader.py`（sha256 814b7f7a…，16,080B）+ `qlib_alpha158_handler.py`（b621481c…，5,092B），**逐字节原样**（非净室重写，与 GTJA/WQ vendored 同范式）；文件末次 commit `a7d5a9b500de`（2024-07-05，取于 2026-09-24 main）。
- 许可=MIT，可入库参照。**不装 qlib**（playbook §2.2 缺则降级禁装律）；vendored 定义件≠采纳 qlib 为计算依赖（O-1545 期 SOURCES 注记「后续拉取=P1」指的是拉取 qlib 计算框架——本件按 O-1636 外调队明定队列只做定义层对照导出，采纳/实现任何缺口族仍须各自预注册）。

## 二、Alpha158 构成（机械解析门 158/158）

handler 默认配置生成：**9 KBAR + 4 PRICE0 + 29 滚动算子族 × 窗 [5,10,20,30,60]（145）= 158 特征**（解析自 vendored 源件，names 全唯一，门=总数恰 158）。注意两点设计语义：
1. handler 默认**排除** volume 原始价特征（config 无 volume 键）——「Alpha158」实际不含 VOLUME0；量信息只经 8 个滚动算子族（VMA/VSTD/WVMA/VSUMP/VSUMN/VSUMD+CORR/CORD）进入。
2. qlib label=Ref($close,-2)/Ref($close,-1)-1=T+2 口径，与本项目 T+1 引擎语义不同——迁移任何结论须重锚。

## 三、四库覆盖图（核心交付）

| 信息族 | 特征数 | 覆盖判定 | 证据（实测批注） |
|---|---|---|---|
| ROC/MA/STD/BETA/RSQR/MAX/MIN/RANK/CORR/SUMP 族 | 50 | **covered** | mom 族/trend_r2/price_position/量价族等=内部+双外库已实测素材；多数已判死（432 MA 网格全灭、trend_r2≈0、低点接近度单边负） |
| RSV/SUMP/SUMN/SUMD | 20 | **covered_tested_dead** | 振荡超卖四族全灭律（kdj+cci+williams+rsi）、RSI 族=批负；SUMP≈RSI 同构 |
| KBAR/PRICE0/RESI/QTLU/QTLD/CORD/CNTP/CNTN/CNTD/VMA/VSTD | 63 | **partial** | 邻接但形态不同：影线连续因子只测过事件形态（engulf/needle/hammer）；resid_mom 在册未直测；streak 邻件 −0.976 深负给 CNTP 低先验；VSTD 在 GTJA 有邻件 std(amount,6) |
| **IMAX/IMIN/IMXD（Aroon）+ WVMA + VSUMP/VSUMN/VSUMD** | **35** | **gap（真缺口 7 族）** | 机械化扫描实锤：aroon/idxmax 在 vendored GTJA191+WQ101 全缺失；WVMA（量加权波动率 Std(|ret|×vol)/Mean）GTJA 的 std 行全是 close/high std 非该复合；量 RSI（上涨量占比）只有事件形态测过（量堆/放量） |

覆盖总账（按特征数）：covered 40 + covered_tested_dead 20 + partial 63 + gap 35 = 158。

## 四、发现与评级（A/B/C/D）

- **F1（律证实）**：Alpha158 六成特征（60/158）所在信息族已被本项目四库覆盖且大半实测判死——第三次印证「外部库单因子过墙无望」（GTJA 0/183 core48、WQ 0/82 严口径）。对照导出的价值在**缺口侧**非覆盖侧。
- **F2（真缺口 7 族·B 类候选）**：Aroon 三族（时间距极值——「几天前创新高/新低」，趋势新鲜度维度，四库全无同构）+ WVMA（量加权波动率）+ 量 RSI 三族（上涨量占比）。**评级 B**：需改造/过关后才可用——全部可在既有日线 OHLCV 上计算（零新数据源），但任何 IC 批须另开预注册（PREREG_TEMPLATE D6 机制段）+认领 MSG；主口径建议股票池 P-1c harness（量特征在股票语义强于 ETF）+ 季度/日频各自 null 校正线（r66 律）；先验须打折——streak −0.976/oscillator 全灭给 CNTP/量 RSI 族低位预期。
- **F3（C 类）**：KBAR 连续影线比、RESI、QTLU/QTLD、CORD、VMA/VSTD=邻接已测素材，只在「合成素材货架」意义上有增量，排队位低于 B 类。
- **F4（D 类·不入因子域）**：PRICE0 水平特征组（ML 导向）、Alpha360（滞后价格大网格，ML 导向）、22 模型 zoo/DDG-DA/RD-Agent（RD-Agent 已在队列下一名单独深读）。
- **F5（域适性）**：Alpha158 设计靶=CSI500 股票 ML；本项目 ETF core48=量特征弱语义域，B 层股票池长多倾斜两批判负（摩擦墙律）——若开批，成本口径按 V1 26bp 域基线+null 校正，禁跨域套用 0.4004/0.3521。

## 五、集成管线（不启动，仅登记）

1. B 类 7 族登记入 `research/STRATEGY_LIBRARY.md` §四 因子库「Alpha158 参照库」行——**参照身份非可算资产**；
2. 未来开批路径：认领 MSG → PREREG_TEMPLATE（α 机制段四选一：Aroon=行为偏差·新鲜度锚定；WVMA/量 RSI=微观结构）→ 小 K IC 参照批（非全 35 特征扫描——35 特征全扫=大 K 陷阱，P-2 弱尾稀释前车之鉴）→ 判据 v2 共享库；
3. 本批零引擎零账本，STRATEGY_LIBRARY/动物园均只加登记行。

## 六、坑与纪律

- vendored 件=外部不可信内容：仅作解析对象与证据，**永不 import 执行**（loader.py 顶部 `from qlib...` 一行 import 即崩=天然防误执行，好事）；解析器用 eval 只取字面量列表段。
- GBK 控制台读 UTF-8 文件坑（R58 同族）：核验一律 PYTHONIOENCODING=utf-8 或 JSON 真值。
