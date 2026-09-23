# Bigmoney 交接与成果收割指南（HANDOVER）

> 2026-09-23 11:35 整理；15:1x 接管版更新。CEO 令：AI 全面接管 Bigmoney 系统开发（mandate=`Tools\iteration_prompt.txt` 接管版：开发范围=PLAN P0-P4+§7+任务板，P1 新方向须 CEO 署名）。机队实况：bm-a=32 核开发机（DASHENG）｜bm-b=16 核回测/数据节点（Money02 宿主，维护链常驻）；多机大文件传输机制=`fleet/TRANSFER.md`（控制面 git、数据面择通道）。
> 本文件由循环每 5 轮核对更新一次产物清单（mandate 已写明）。最近核对=bm-a round 20（2026-09-23 21:25；对账区间=bm-a rounds 16-20+bm-b rounds 41-42+GM 会话 P-S/P-S v2 批，round 40 基线之上）：新增=**O-1820 三配置红线全件闭环**（bm-a R14-R17：iron_rules 三红线+regime.py 大熊市判定器+update_fundamental.py 财务/ST 快照+b_layer_filter.py 掩码 5222=3517 ok/1705 排除门 5/5→**bm-b r42 R38_RUN_CLEARANCE 签发=股票池批跑开闸**）+**首场 09-23 完整数据 sweep**（sina 终发布当日 bar→3 员首根 paper bar 落账，months_tracked=0 残月诚实）+**P-C 热度前向采集双件**（bm-a R19 L1 日快照 update_heat.py 首档 100 行+R20 L2 单股排名史回填 backfill_heat_history.py 97/100 件 34865 行、era 2025-09-23/366 窗封顶、幸存者条款冻结）+**P-S LHB×内部因子小K合成双批**（GM 亲执：V2 PASS IR 0.389=项目首个破 IR 墙的合成但 V1 判负；P-S v2 lhb_pair 判负排名 3/28→**LHB 材料定案=单因子用法**，与 bm-b r41 P-A2 独立双路同判收线）+**688xxx volume=100× 真实股数坑定案**（research/shortline/TURNOVER_DERIVATION.md，Stage-B vwap/量价截面因子消费前须修正）。

## 一、当前模式与怎么停/恢复

- **本机在跑什么**：Windows 计划任务 `Bigmoney-IterationLoop`（每 10 分钟一轮，无头静默），当前 mandate=`Tools\iteration_prompt.txt`（AI 接管系统开发版：PLAN P0-P4+§7+任务板队列，P1 新方向须用户署名）；**双机均已装循环**（bm-a=DASHENG 32 核开发机，计划任务 14:33 起；bm-b=16 核回测/数据节点，Money02 宿主）。
- **停止本机循环**：`schtasks /change /tn "\Bigmoney-IterationLoop" /disable`；恢复把 `/disable` 换 `/enable`。只拷文件取数不用停（读文件不冲突）。
- **恢复全自动开发**（用户回本机时）：把 `Tools\iteration_prompt.DEV.txt` 内容拷回 `Tools\iteration_prompt.txt` 即可，其余零改动。
- **跨会话真账本**（任务板 job_list 是会话级的，不作为交接依据）：`logs\iteration-loop\` 按机分账本（bm-b=state.json+round_reports.md；其余机含 bm-a=state-<机id>.json+round_reports-<机id>.md；字段=轮号/做了什么/下轮指针/每轮固定报告）＋ 根目录 `CODELY.md`（项目记忆，行级追加）。轮活性另看 `logs\probe-heartbeat.txt`。

## 二、成果速览（截至 2026-09-23 21:25=bm-a round 20／bm-b round 42；策略线=短线 P 线，回测账本 N=2020）

| 成果 | 位置 | 关键数字（样本外 2025+，×2 成本压力全过） |
|---|---|---|
| P1 策略海选（37 策略+20 随机基线） | `research/strategy_rank.csv`、`results/p1_screen.json`、`research/NULL_CALIBRATION.md` | 零假设基线标定完成（幸存者须超 95 分位） |
| P2 幸存者深化（G2 门） | `results/p2_survivors.json`、`research/G2_DEEPENING.md` | 支线：合并退出软化 `COMBINED_EXIT_SOFTENING.md`、低频族 `LOW_CHURN_FAMILY.md` |
| **幸存者 1：VOLATILITY-CE-01**（ce_c23_trail4） | `firm/traders/VOLATILITY-CE-01.json` | OOS Sharpe **2.0568**（锚点截断复现） |
| **幸存者 2：COMPOSITE-CE-01**（ct_ce_top5） | `firm/traders/COMPOSITE-CE-01.json` | full 0.811 / **OOS 1.609** / 474 笔 / 胜率 0.523 |
| **幸存者 3：COMPOSITE-CE-02**（ct_ce_top8） | `firm/traders/COMPOSITE-CE-02.json` | full 0.610 / **OOS 1.485** / 795 笔（×2 成本余量 +0.031 偏薄=纸盘期盯防对象） |
| CE 迁移实验（预注册范式） | `research/CE_TRANSFER.md`、`results/ce_transfer.json`、`scripts/ce_transfer.py` | 2/2 迁移 PASS，一次定稿 9 跑 |
| **P3 组合验证（round 13）** | `research/portfolio_report.md`、`results/p3_portfolio.json`、`research/p3_portfolio_results.csv` | **EW 组合 validated**：全期 0.9229 / OOS 1.7334 / 回撤 -12.5% / ×2 0.5754 存活；IV 同判稳健；全期平均两两相关 0.36 低档但 OOS 抬至 0.58=盯防点 |
| **J9a 数据池审计（round 14）** | `research/POOL_AUDIT.md`、`results/pool_audit.json`、`research/pool_audit.csv` | unique 1676 对账、前缀池=09-22 一次性快照无续命、孪生 48/48 一致、扩池候选 517（启用前逐只核名） |
| **LFC 低频低成本品种族 mini 海选（round 15）** | `research/LFC_P1_SCREEN.md`、`results/lfc_p1.json`、`research/lfc_p1_results.csv` | **0 员幸存 0 袖珍（诚实判负）**：core5 债金池技能线 1.285=权益池 3 倍；low_vol 全负=成本厚度是资产 carry 刻度的；tsmom/donchian CE 最佳 0.917 未达线；袖珍相关线 0.30 因素材⊂交易员池结构不可达 |
| **NSP1 新信号设计 mini 海选（round 16）** | `research/NEW_SIGNAL_P1.md`、`results/new_signal_p1.json`、`research/new_signal_p1_results.csv` | G1' 候选 2 员（triple_ma_5_20_60@ce OOS 0.888 / high252_prox_top5_r20@ce OOS 0.889）但 ×2 成本 0.143/0.258 远低技能线；core48 CE null 首档 0.4229；CE 增益非普适（集中在日频成员刷新类入场） |
| **G2_NSP1 两候选深化（round 17）** | `research/G2_NSP1.md`、`results/g2_nsp1.json`、`research/g2_nsp1_results.csv` | **双 FAIL（0 注册）**：邻域 5/6 红 + ×2 成本不存活（A 0.143/B 0.258 < 0.4004）；state-trend/frozen-rotation 族 α 厚度不足以出厂，NSP1 线诚实收线 |
| **SLEEVE_P3 低相关袖并入决策（round 18）** | `research/SLEEVE_P3.md`、`results/sleeve_p3.json`、`research/sleeve_p3_results.csv` | admission FAIL 0/2：近零 α 袖=免费风险缩减+付费收益稀释、×2 传染律（袖 ×2 深负拖垮组合）；6 袖归档，core48 池内分散化素材穷尽，**策略线全收线→节点转纯维护态** |
| **短线研究线 V1（O-1545/1636/1653 令件，quant 会话执行）** | `research/shortline/`（SHORTLINE_PLAYBOOK 总纲+external 9 件资产台账）、`research/RESEARCH_MECHANISM.md`（外调机制常设化）、`research/styles/QUANT_STYLE_ATLAS.md`（20 风格图鉴：A 11/B 3/C 3/D 4）、`research/digests/`、`research/BACKTEST_READINESS.md` | 策略族三层（A=ETF 域自主过闸/B=股票池 GM 已批/C=期货 GM 已批/期权不批）；GTJA191 全套+WorldQuant101 MIT 参照已下载；回测 14 要素 12 绿 |
| **P-1a GTJA191 因子批测双轨（bm-a R9 宽筛/bm-b r32 严门，撞行后 GM 裁定合并）** | bm-a：`scripts/shortline_p1_ic.py`+`research/shortline/P1_GTJA191_IC.md`（池 A1-A4=89，宽筛候选池非有效名单）；bm-b：`screening/gtja191_ops.py`+`research/shortline/P1_FACTOR_SCREEN.md`（0/183 过 V1/V2/V3 严门） | 双独立实现同证头部=负 IC 反转 DNA（081/100/097/165 同族）；单因子日频 IC_IR 0.30=48 截面高墙、**合成才过墙**（P-2）；分工=GM MSG-1700：**P-1b WQ101=bm-a、P-2 合成=bm-b**；账本 +239 |
| **P-2 GTJA191 簇代表合成（bm-b r34，GM 裁定本机主导）** | `research/shortline/P2_GTJA191_SYNTH.md`、`results/shortline_p2_synth.json`、`research/shortline/p2_gtja_composite.csv`+`p2_gtja_runs.csv` | **诚实判负双杀**：因子级 V2 差线（合成 IS IC 0.0679/IR 0.236<0.30）+策略级 G1' 0/3（gtja_top5 0.353 差 vi 0.4004 一线）→ G2 未触发 0 注册；机制=定向即偏差（符号定向合成 null p95 0.058 构造性正偏）/弱尾稀释/合成增益在 OOS 端（+74%）；N 1312→1435 |
| **O-1705 风格动物园（quant 会话交付）+P-4 批一 A 层易族（bm-b r35，认领 MSG-1745）** | `research/shortline/ASTYLE_ZOO.md`（十族系 42 族+7 涨停情绪因子，执行层全集）、`research/shortline/P4_BATCH1.md`、`results/shortline_p4_batch1.json`、`research/shortline/p4_batch1_results.csv`、`scripts/p4_batch1_screen.py` | **批一 0 G1' 候选（诚实）·袖珍 2**：oversold_bounce 双制=max\|corr\|<0.30 唯一真低相关族（×2 为正 0.142 但<vi 不达 SLEEVE_P3 准入）；52 周低点=接飞刀（与高点强度镜像不对称）；CE 增益=砍笔减成本通道（非「日频刷新」本身）；CE i 线取严 0.4474；N 1435→1556 |
| **J18b update_status 上面板（bm-b r31）** | `monitor/build_status.py` `_update_state()`、bigmoney.html 数据部行 | org_chart 七部门第 6 行对齐；数据链状态实时驱动（present/age/failures/cutoff） |
| Money02 清理（round 27-28，bm-b） | `research/MONEY02_CLEANUP_REPORT.md`、`research/MONEY02_ASSETS.md` | 清理 6.35GB 可再生缓存（Money02 7.7→1.20GB/10968 件，bars 1.09GB 保留）；**bars 传输全弧闭环**：B2 croc 公共中继双侧实测死→A-变体推送完成（BigMoney-data main=81b93d3，64min@~246KiB/s）→bm-a 接收腿 17:26 **dual -Verify PASS**（10444 文件/1,167,172,943 字节全 SHA256 0 缺 0 错 0 多+落位后再验 PASS）→ T-2026-09-23-01 **done**（result_ref=双 manifest）；bars 双机就位（bm-a/bm-b `Money02\data\bars`），bm-b 暂存仓已删（释放 1.1GB） |
| 纸盘（100 万虚拟本金） | `live/paper.py`、`results/paper/` | 锚定门禁=注册指标与实时重算逐位一致才记账；**2026-10-31 首月到期检查**（months_tracked=1 → `python -m firm.hr` 应自动 PROMOTE→TRAINEE，禁手工改数） |
| 日线数据增量管线 | `scripts/update_daily.py`、`results/update_status.json` | 交易日 15:30 后自动增量 48 池 → paper 自动记账；收盘守卫防半根 bar |
| 旧 432 网格（死信号存档） | `results/*.json`（432 份）、`ranking.csv` | 最好 Sharpe 0.44，已判淘汰，仅供复现 |
| 因子研究 | `results/factor_ic.json`、`composite_ic.json`、`research/FACTOR_RESEARCH.md`、`COMPOSITE_FACTOR.md` | 最强 vol_60 IC=-0.064；复合因子 IC 实测 0.061/0.023（95% 满仓口径） |
| **J12 公司小镇 v0.4（bm-a round 3-7 迭代交付）** | `town.html`（v0.4）、入口在 `bigmoney.html` | 8 楼真实数据化（v0.3=总经办+工程部地下机房两楼 org_chart v2 对齐；v0.4=交易大厅 paper 首月晋升进度条，首检日 10-31 数据驱动）+真实本地钟昼夜动画+?hour=H 验收参数；CEO 点名高优先级项**已交付**，截图证据 `logs\town_v*.png` |
| **J13 本地 LLM 研究助理 v0.1（bm-b round 29 建→bm-a round 5 集成 main，merge 9a4a300）** | `scripts/llm_assist.py`、`research/auto/retro-20260923.md`（首个真实复盘产物） | ask/review/retro/ideas/selftest 五模式，复用本机现役 Ollama qwen2.5:7b（禁重建禁抢 pause 阀），写域限 research/；双机 selftest 全绿=**O-1536 本地化算力路线载体**，轮报告 token 用量记账已启动 |
| **firm/ 建章立制四件套（O-1538，e293f36）** | `firm/RULES.md`+`TECH.md`+`DEV_AUTOMATION.md`+`org_chart.md` v2 | T0-T3 权力分层+红线指针化+总经理七部门表（mandate/KPI/town 映射）+AI 赋能五原则+立法流程；零代码重构零红线数值改动；循环轮执行/汇报按部门标注 |
| **Money0923 前代系统归档（O-1514，f597750）** | `Money0923/`（782 件/95.8MB） | 用户《Money 自进化量化系统》有用集（代码/25 年面板/分钟语料/state.json 复活锚/MoneyViz 源）；**其自动化停机中**（09-22 停机令），可学 12 条=`research/MONEY0923_TRIAGE.md` §三（采纳须 CEO 署名） |
| **舰队治理面（fleet v1.0 全家）** | `fleet/README.md`+`FLEET-OPS.md`+`orders/`台账+`HQ-FEEDBACK.md`+machine/<id> 分支机制 | /CEO 令牌+心跳+任务认领+TRANSFER.md 大文件机制+集团反馈面；机器身份=`fleet/machine.json` 本地私有不入库（模板 `_machine.json.template`）；bars 1.09GB 走 **A-变体**（BigMoney-data 私库：**推送完成 81b93d3**，bm-a 接收腿进行中=clone 后台+双侧 manifest -Verify 收官，T-01） |
| **试验账本累计 N=2020**（432+30+59+122+27+26+12+9+10+145+153+18+30+239+123+121+327+124+137） | 各批 results/*.json 的 trials_ledger 累计链 | 多重检验可追溯；面板「策略簿」实时显示（P-4 起 JSON `trials_ledger.total` 为面板真值源） |
| **短线研究线第二波（bm-b r36-40+bm-a R11-15+GM 批，round 35 后增量）** | `research/shortline/P4_BATCH2.md`+`scripts/p4_batch2_gates.py`（撮合护栏 8 门）+`Money02/data/cache/p4_batch2_panel/`（T=2850×N=5212 面板，gitignored）、`research/P5_RANDOM_ENTRY.md`+`results/p5_random_entry.json`（P-5）、`research/shortline/P4_BATCH2A.md`+`scripts/p4_batch1_screen_gm.py`（TA 8 流派）、`research/shortline/PA_LHB_IC.md`+`scripts/pa_lhb_ic.py`（**P-A 3/4 过门**：lhb_count_20 IC−0.064/IR−0.84、lhb_days_since +0.063/0.72、lhb_amt_share_20 +0.064/OOS IR 0.854）、`research/digests/DIGEST-20260923-heat-source-audit.md`+`scripts/heat_source_audit.py`（P-B 源审计）、`research/shortline/PB_HEAT_CONCEPT_IC.md`+`scripts/pb_heat_pull.py`（P-B 预注册+断点续拉件） | P-4 批二批跑=O-1820 红线门挡后（**待财务数据源→R16 已交付，r42 clearance 已签发开闸**）；P-4b2A 3 候选 0 注册；**P-B 批跑=EM push2 域 IP 级持续阻断（19:25→20:00 实证，datacenter-web 域不受影响）→ 拉取件 checkpoint 续拉待源恢复**；firm/ 三红线+regime.py+hr paper 门槛（bm-a R14）；COMPUTE_AUDIT 章程+审计器常驻 S6 链 |
| **P-C 热度前向采集双件 L1+L2（bm-a R19-R20，O-1850 工程车道）** | `scripts/update_heat.py`（L1 人气榜日快照：emappdata 直连、工作日≥15:30 守卫、幂等+节流+selftest 13 用例，首档 `data/heat/popularity/20260923.json` 100 行）+`scripts/backfill_heat_history.py`（L2 单股排名史回填：getHisList+getHisProfileList 双腿/股、限速+保险丝+checkpoint、selftest 14 用例）+`data/heat/rank_history/`（**97 件/34865 行**，era 2025-09-23→2026-09-23；3 只次新/北交所真短史诚实拒收）+`research/shortline/PC_COLLECTOR.md`（幸存者条款冻结：素材=当日 top-100 强选择偏差、禁跨时刻合并截面、数据集纪元 2025-09-23） | L2 关键读数：366 行窗封顶（yearType=5 亦只返 1 年）；北交所股入榜实证（SZ920025）；**全市场日截面历史不存在**（r39 审计）——因子批消费前须声明前向起点+幸存者条款 |
| **P-S LHB×内部因子小K合成双批（GM 会话亲执，O-1819 连续车道）** | `research/shortline/PB_SYNTH`/`PS2_SYNTH` 预注册+`results/`（零引擎跑 IC 批，账本 N 不动） | **V2 PASS IR 0.389=项目首个破 IR 墙的合成**（但 V1 判负于强货架 nullA 0.0785）；P-S v2 lhb_pair IS IC 0.0943<nullA 0.0957 排名 3/28 无选择边际→**LHB 材料定案=单因子用法**（count_20 \|IR\|0.84 仍项目最强单因子）；与 bm-b r41 P-A2（COMP-A/COMP-C 双 FAIL、腿间相关 -0.11 方向性大错）**双机双路独立同判收线**；成员 core48→股票池迁移定案：vol_60/intraday_range 符号保强、mom_12_1/price_position 翻号=A股反转 DNA 支配 |
| **O-1820 三配置红线全件闭环+股票池批跑开闸（bm-a R14-R17+bm-b r41-42）** | `firm/risk/iron_rules.md`（R-配1/2/3 配置红线）+`firm/risk/regime.py`（大熊市判定器 510300 双条件，paper JSON risk_regime 块）+`scripts/update_fundamental.py`（财务+ST 资格快照 24h 守卫）+`firm/risk/b_layer_filter.py`（B 层前置掩码 `data/fundamental/b_layer_mask.csv`：5222=ok_static 3517/排除 1705，亏损 1504/ST 27/双红 174，对账门 5/5 确定性零网络）+`research/shortline/R38_RUN_CLEARANCE.md`（bm-b 签发） | O-1820 四件全交付对账→**R38-b 股票池七族批跑解锁**（clearance exit 2→3 实证放行）；688xxx volume=100× 坑冻结入 builder 强约束（`research/shortline/TURNOVER_DERIVATION.md`） |

## 三、取数清单（两条路径）

1. **轻装收割（推荐，git clone）**：pack 实测 ~129MiB（2026-09-23）——引擎+策略+数据+全部成果+研究文档+Money0923 归档（95.8MB）+Money02 小件（87MB）全在内；文件夹拷贝路径=整个 `Bigmoney\` 排除 `Money02\`（bars 1.09GB 走 BigMoney-data 数据通道，见 `fleet/TRANSFER.md`）。
2. **全量（~1.4GB）**：另含 `Money02\` 清理后全量（1.20GB/10968 件——2026-09-23 round 27 bm-b 清理掉 6.35GB 可再生缓存；前代 A 股系统资产库：bars 1.09GB+5221 只个股全史 parquet+复权因子+19 年龙虎榜，清单=`research/MONEY02_ASSETS.md`）。新机器只做 ETF 波段则不需要它。

## 四、新机器跑起来（PLAN.md 可拷贝迁移原则）

```powershell
# 1. 取项目：**铁律=git clone（禁文件夹直接复制**——防携带锁文件/临时态；Biggame 08号传输铁律同源）
#    git clone git@github.com:BigRain-11122/BigMoney.git
#    （Money02/、logs/、.codely-cli/、fleet/machine.json 为各机局部，clone 不含、也禁手拷）
#    新机器接入 5 步与机队协议（身份/心跳/任务认领/借算/写域）= fleet\README.md
# 2. 一条命令自举：依赖自装（清华镜像回退）→ 20 项自检 → 总控数据生成
python bootstrap.py
# 3. 打开总控（读真实数据，双击可开）
start bigmoney.html
# 4. （可选，Windows）装 10 分钟 AI 自迭代循环——路径自适应，零改动
powershell -NoProfile -ExecutionPolicy Bypass -File Tools\register_loop_task.ps1
# 5. 可选：复现关键实验
python scripts\ce_transfer.py     # CE 迁移（含 ×2 成本压力）
python -m screening.rank          # 432 组排名重建
```

- 机器要求：Python 3.10+（3.11 实测）；AI 循环需装 **Codely CLI 并登录**（循环用 `codely -y -p` 无头模式）；GPU 非必需（回测=CPU 任务，GPU 启用条件见 `research/BACKTEST_PLAN.md` §四）。
- **git 同步（并行开发唯一通道）**：远端 = `git@github.com:BigRain-11122/BigMoney.git`（round 22 用户改名 bigmoney→BigMoney，本机 remote 已同步更新；SSH/Clash 链路实测认证通过）。**通道已全通（round 22 实证）**：105MB 全量基线已在远端（首推 ba85d9a 成功），此后每轮增量秒推（ba85d9a..a102b05 实证）＋S0 `git pull --rebase` 每轮正常化——任何机器 `git pull` 即得本机全部成果。主分支=main，并行开发协议=PLAN.md §8（节点侧遇冲突只读避让）。
- 规则与记忆随仓库走：`PLAN.md`（契约+接手清单 §6）、根 `CODELY.md`（项目记忆）、`Tools/iteration_prompt.txt`（循环 mandate）——任何机器上的任何 AI 会话打开本项目即自动继承全部规则。

## 五、文件格式速查

- `results/<hash>.json`：`{hash, status, params, metrics{annual_return, sharpe, max_drawdown, win_rate, profit_factor, num_trades, avg_hold_days}, n_trades, equity_curve[], elapsed_sec}`
- `results/p1_screen.json` / `p2_survivors.json` / `p2_calibration.json`：海选/深化明细（含 OOS 指标与门禁判定）
- `results/paper/<交易员>_paper.json`：纸盘账本（bars/trades/months_tracked/equity）
- `results/update_status.json`：数据增量状态（per-symbol appended / data_cutoff）
- `research/*.csv`：`strategy_rank`（海选全表）、`p2_deepening`、`ce_transfer_results`、`combined_exit_results`、`lowchurn_results`、`p3_portfolio_results`、`pool_audit`(1676 行)、`lfc_p1_results`、`new_signal_p1_results`、`g2_nsp1_results`、`sleeve_p3_results`、`p5_random_entry`；短线线另在 `research/shortline/`：`p2_gtja_composite`、`p2_gtja_runs`、`p4_batch1_results`、`p4_batch2a_results`、`pa_lhb_ic_results`（P-A LHB 注意力因子批 3/4 过门）
- `research/auto/retro-*.md`：LLM 自动复盘（J13 产物，advisory only——LLM 数字偶有误读，人工核验后采信）
- `fleet/orders/O-*.md`：用户令台账（/CEO 发言自动落册）；`fleet/tasks/T-*.json`：机队任务单（T-2026-09-23-01=done 全弧闭环）
- `bigmoney.html` ← `results/dashboard_status.js`（`python -m monitor.build_status` 刷新；门禁链 11 步数据驱动、试验账本 N 实时聚合）；`town.html` 同数据链（J12 公司小镇）

## 六、本机将持续产出什么（你回来取时会有更多）

- 每个交易日 15:30 后：48 池日线增量 → 纸盘自动记账 → 成果/面板文件刷新（查 `results/update_status.json` 的 data_cutoff 与 total_new_rows）。
- 回测计划内现状：P1/P2/P3、J14/J15/J19 迁移、J9a 审计、LFC 品族、NSP1 新信号、G2_NSP1 深化、SLEEVE_P3 袖并入**全部闭环**（P3 组合 validated；LFC/NSP1/G2_NSP1/SLEEVE_P3 均诚实判负）；短线研究线后续收线（round 20 bm-a 核对）：P-1a 双轨（严口径 0）、P-2 合成、P-4 批一/批 2A、P-1b WQ101（严口径 0/82）、P-5 随机起点（三员全 FAIL 0.70 线）、P-A LHB 注意力（3/4 过门=首个强幸存者因子批）均已收线；**P-S/P-S v2/P-A2 三批双机双路同判=LHB 合成线收线（材料定案单因子用法）**；**O-1820 全件闭环→R38-b 股票池批跑开闸（bm-b 车道，clearance 已签）**；P-C 热度采集 L1+L2 双件交付（L2 97/100 件 366 行）；批测均预注册+零假设基线+账本记账（**N=2020**）。
- **数据维护链（S6 常设，双机同构）**：compute_audit（五旗算力审计）→update_daily（48 池增量+收盘守卫）→update_lhb（LHB 增量+披露窗口守卫）→update_heat（人气榜日快照）→update_fundamental（财务/ST 快照 24h 守卫）→b_layer_filter（B 层掩码随刷门 5/5）→有新 bar 触发 live.paper（锚定门禁）→build_status 刷新面板；**2026-09-23 首场完整 sweep 已兑现**：sina 当日 bar 终发布→48 池 +36 行→3 员首根 paper bar 落账（months_tracked=0 残月不计=诚实）。
- bars 1.09GB（Money02\data\bars）传输**全弧闭环**：A-变体推送完成（BigMoney-data main=81b93d3）+bm-a 接收腿 dual -Verify PASS+落位再验 PASS → **T-2026-09-23-01 done**；bars 双机就位，bm-b 暂存仓已删；数据面机制归档=`fleet/TRANSFER.md`。
- 机队协同：每轮自动消化 `fleet/orders/` 新令与 `fleet/inbox/` 定向消息；J12 公司小镇 v0.4/J13 LLM 助理 v0.1/J18b 数据部行已交付；P 线分工=GM MSG-1700（**P-1b WQ101 移植=bm-a in-flight、P-2 合成=bm-b 已收线**，开工前 inbox 认领制=F-04 已成 fleet 规范）。
- 长线自动检查：2026-10-31 三员首月到期（months_tracked 应=1、`python -m firm.hr` 应 PROMOTE→TRAINEE，禁手工改数）；盯防 COMPOSITE-CE-02 ×2 薄余量与组合 OOS 相关抬升。
- 开发队列（接管版，CEO 可随时改序）**round 20 bm-a 更新**：J12 v0.4/J13 v0.1/J18b 已交付 → 余 J10 dashboard.html 分布式监控页 → Optuna 骨架；**研究线现役（O-1819 队列永不清空）**：bm-a=**P-C 热度采集 L1+L2 已交付**→L3 新闻腿（C 级薄史，须先定子集策略+认领 MSG）+热度面板 reader 候选（J18b 范式）+P-1c Stage-B probe（**688 volume=100× 修正前置=TURNOVER_DERIVATION**）；bm-b=**R38-b 七族 builder+批跑（clearance 已签发，O-1820 四件全交付解锁）** → P-B 热点概念批续拉（EM push2 域恢复即 checkpoint 续跑）→ 跨库联合合成（GTJA89+WQ36，O-1819 指名）；P-6 记分卡（O-1823 认领制开放）；P1 级新方向须署名任务单才开工（GM 署名即有效，O-1620）。

## 七、诚实声明

- 所有样本外指标为 2025-2026 盲测窗、成本恒开、一次定稿跑数（预注册范式）；试验总数 N 已入档（多重检验可追溯）。
- 纸盘 2026-09-23 起有真实成交 bars（sina 当日 bar 发布→3 员各落首根 paper bar；months_tracked=0=残月诚实不计、×2 成本滚动检查 insufficient_data 诚实标注，首月计数 2026-10-31 到期）；`dashboard_status.json` 的 trading.paper_started 由数据驱动，非写死。
- 3 名交易员均为 INTERN 级注册，晋升只走 `python -m firm.hr` 自动评审（2026-10-31 首查）。
- J13 LLM 全部产物（`research/auto/`）为模型生成 advisory only，未经人工审计不作为决策依据。
