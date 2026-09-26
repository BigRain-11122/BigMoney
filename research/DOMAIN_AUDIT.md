# DOMAIN_AUDIT（T-2026-09-26-88 s1 首切·O-20260926-2325 全域解锁令）

- v0.1 首切=**数据面在库实况盘点**（T-86/T-87 勘探面+仓内正典交叉）；每域「可回测性」判据=数据审计→prereg→回测五步制（PRODUCT_MATRIX 新维度五步律），本表不构成任何 prereg。
- 纪律：判负族不重开（期货 CTA×3/P-A1/T-48 同数据同方法重跑=违令；新 prereg+更大 N=合法重试通道·RANDOM_LARGE_SAMPLE_LAW §5）；北向数据面已撤（O-1120）；T0/庄股跟风=红线外。

| # | 域 | 数据面实况 | 复权/幸存者诚实 | 成本模型 | T+1/T+0 | 判定 |
|---|---|---|---|---|---|---|
| 1 | A 股股票 | P1C 缓存全史 T=8792 N=5222（1990-12-19→2026-09-22，qfq；北交所零在场；ST=点时快照近似披露）＋fundamental eligibility/b_layer_mask | qfq 已证事件日精确（r105）；**osh=当前截面 ffilled 非逐行历史**（R258 律，×osh 派生面历史段=代理） | x1=13.041bp/side（V2 平价）；x2 压测恒开 | T+1 涨跌停 | **在库可判**（T-57 WILD-S1 已全史烧过；新族走新 prereg） |
| 2 | ETF core48 | data/daily ~700+ ETF CSV＋consolidation 19 调整视图＋core48 引擎面板（load_core，cutoff 2026-09-24） | 调整视图=分红再投基准（consolidation 冻结面） | 同上 | T+1 | **在库可判**（主线域：28 员工/融合锦标赛载体） |
| 3 | 转债 | 集思录面验通（09-24 GM 实测可达）；**采集器未建**（T-60 线=票在册收敛批，collector+audit 先行） | 待建（双低/下修/强赎事件面=数据审计第一腿） | 待建（转债佣金/强赎规则） | T+0/T+1 混合 | **数据审计先行**（s2 首战按新法 K≥1000 起点） |
| 4 | 国债逆回购（GC001/R-001 期限梯） | **仓内零数据面**（data/ 无 repo 目录）——采集器待建（s3：sina/EM 日线面，现金腿真实收益率曲线=SPM 现金腿价值，轻算力周末合法） | n/a（利率面） | 无摩擦（成交价=利率） | T+0 资金 T+1 可用 | **collector 先建**（s3 载体） |
| 5 | REITs | data/daily 有 REITs ETF？**PENDING 实探**（场内 REITs 2021 起，样本短=~5 年） | 待探 | 待建 | T+1 | PENDING（样本短=insufficient-sample 风险如实） |
| 6 | LOF | 集思录面同转债（ETF/LOF/转债/AH/套利公开面）；场内 LOF 日线在 data/daily？**PENDING 实探** | 待探 | 同 ETF | T+1 | PENDING |
| 7 | 场内 QDII | data/daily 恒生/纳指/标普类 QDII ETF 在库（如 513130/513500 族）——**PENDING 逐只实探** | QDII 溢价面（折溢价套利=ARB 面） | 同 ETF＋申赎摩擦 | T+1（QDII 溢价=事件面） | PENDING |
| 8 | 商品期货 | data/futures_daily 10 品种主力连续（AU/IC/IF/IH/IM/RB/SC/T/TF/TS）sina 同源增量 | 主力连续拼接（换月跳空如实披露） | 保证金/手续费（CTA 判负×3 已冻结同数据同方法） | T+0 | **数据在库**（新族=新 prereg+更大 N 通道；旧判负禁翻案） |
| 9 | 股指期货 | IC/IF/IH/IM 在库（同上拼接面） | 同上 | 保证金+基差 | T+0 | 在库（对冲腿用途=中性家族候选，T-87 s2 #5） |
| 10 | 期权（ETF 期权） | data/options 前向面板（T-69 wave-2b 采集门在链，sina 同源四面；**前向史<12 个月→新 prereg 冻结律 T-67 §2 未达**） | 前向采集=幸存者零（逐合约到期面） | 权利金/行权摩擦（tick=0.002 已核） | T+0/行权 T+1 | **采集先行**（保守族=备兑 proxy 等 s4 候选；判据门未开） |
| 11 | 国债期货 | T/TF/TS 在库（同 8） | 同上 | 保证金 | T+0 | 在库（配置部久期工具面候选） |
| 12 | 北交所 | P1C 缓存**零在场**（天然剔除披露）；单独采集=新数据工程 | 待建 | 待建 | T+1 30% 涨跌停 | **数据面缺**（不建模照登） |

## 缺口清单（PRODUCT_MATRIX 对账）

- 转债/REITs/LOF/QDII 逐只=**首批数据审计批**（s2/s4 供给面）；repo=collector 新建（s3）；期权=前向史积累期（≥12 个月才准 prereg）。
- 每域判定面走 RANDOM_LARGE_SAMPLE_LAW v1.0（K≥1000 虚拟起点/N≥500 随机参数/双 nulls≥2000；样本不足=insufficient-sample 诚实拒判）。

—— bm-a R277 首切；s3 repo 采集器=下一批工程载体（O-2320 满载线池批）。
