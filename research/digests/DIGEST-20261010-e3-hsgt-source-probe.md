# DIGEST-20261010-e3-hsgt-source-probe — 北向资金数据源可达性扫描（E3 P3 队头·判负关闭件）

> 车道：数据部·外源扫描（state/queue/explore.md E3 队头·Self-Drive v2.0·48h 节律）。
> 执行：bm-a r947（2026-10-10 08:3x-08:5x）。
> 纪律：R109 诊断节制（每候选 ≤3 请求）；直连铁律（proxy 剥除）；零网络源码内省先行（8 接口 introspection 先落 results/_e3_hsgt_introspect.json）；宣称≠验证。
> 探针请求账：hist_em ×2（首探+持股面复验）+summary_em ×2（首探+控制实验复验）+min_em ×1+hold_stock ×1+stock_statistics ×1+individual_detail ×1=8 请求（6 接口·均 ≤3/接口）。
> 实证载体：scripts/hsgt_source_probe.py（selftest 7/7）+results/shortline/hsgt_source_probe.json + R58 先例 scripts/moneyflow_source_probe.py（D/E/F 腿不重复建设）。
> 零引擎零账本零判据宣称（reachability scan 面·新 prereg 需另过预注册正门）。

## 一、结论速览（候选评级表）

| 候选面 | 接口 | 判定 | 证据 | 情绪面因子候选评级 |
|---|---|---|---|---|
| 北向日度流量（净买额/买入卖出/资金流入/余额） | stock_hsgt_hist_em | **死亡面（政策终止）** | post-2024-08-16 共 501 行流量列 alive=0/501（全 NaN 零填）；近 3 行（09-30/10-08/10-09）六流量列全 NaN | **判负关闭** |
| 北向分钟流量 | stock_hsgt_fund_min_em | **僵尸端点（0.0 零填）** | 2026-10-09 全天 241 行时间栅格·沪股通/深股通/北向资金三列全 0.0（14:59/15:00 实锚） | **判负关闭**（并入上行） |
| 北向当日汇总 | stock_hsgt_fund_flow_summary_em | **死亡面+天然控制实验** | 2026-10-09 北向两行（沪股通/深股通）成交净买额=0.000000/资金净流入=0.0；**同端点同日同列南向两行=-23.31/+26.22 亿真实值**——零填=政策面非源损坏的单端点控制实验实证 | **判负关闭**（证据面归档） |
| 北向持股季度快照 | stock_hsgt_hist_em 持股市值列 | **季度快照存活** | post-policy alive=8/501 且 8 行恰为 2024-09-30..2026-06-30 全部季度末（2.41→3.10 万亿）——披露降频为季度 | **候选但不可开 prereg**（8 数据点+T-67 前向冻结律 12 个月远不够·wrapper 另破） |
| 持股排行/个股持股明细/每日个股统计 | hold_stock_em / individual_detail_em / stock_statistics_em | **akshare 1.18.96 wrapper 全破** | hold_stock=TypeError（R58 同症复现）·individual_detail=TypeError（R58 时活·今破=上游端点变更）·stock_statistics 近 20 日窗 empty | **数据债登记**（复活需直连端点工程·超出 reachability 扫描面） |
| 南向日度流量（旁系存活面） | stock_hsgt_fund_flow_summary_em 南向行 | **存活** | 2026-10-09 港股通(沪/深) 成交净买额 -23.31/+26.22 亿·真实日度值（南向披露归沪深交易所域·不受 HKEX 北向终止令约束） | **旁系候选登记**（港股市场情绪·A 股情绪相关性弱·非 E3 主范围） |

## 二、政策锚与交叉验证

- **政策锚**：HKEX 2024-08-16 起终止北向实时/日度净买入披露（公开公告事实·结构断点恰落在该日=自洽）。
- **两源交叉（E3 行内范围=akshare/东财源）**：三个独立 EM report 端点（hist 报表/min 报表/summary 报表）同向零填+summary 端点内南北向同列对照（北向 0 vs 南向真值）——**单 vendor（EM 系）局限如实披露**；政策日为公开公告事实非本探针首创宣称。
- **R58 承接修正**：R58（2026-09-24 moneyflow_source_probe）D 腿判 "hist ok 2759 行至 2026-09-23" 为传输面可达——本探针补上**量纲死亡面**判读（可达≠可用：流量列全 NaN 零填）；E 腿 individual_detail 2026-09-24 时活、今 TypeError=上游端点又变（akshare wrapper 跟进债）；F 腿 TypeError 复现确认非参数误用（"北向/持股市值" 正参同症）。

## 三、族级关闭判词（消费面纪律）

1. **北向资金流量情绪因子族=数据源级判负关闭**：流量披露已死——任何基于「北向净买额→A 股情绪/前向信息」的新 prereg 主张**禁开面**（复活条件=HKEX 政策反转或官方替代披露出台，数据面先决）。
2. 情绪/温度类新主张按既有族级闭合纪律（LHB_THERMO_IC_P1 §8+THERMO-OVERLAY-P1 §8 双判负档）对照——本判负=**数据源层**关闭（比族判决更上游），两层叠加后北向流量面彻底闭合。
3. 持股季度面与南向旁系=**登记不开发**：季度面 8 点样本+wrapper 债；南向面属港股情绪域（如未来开题须独立 prereg+与 A 股情绪面的相关性假设显式声明）。
4. 零判据宣称：本件不携带任何 IC/胜率数字（reachability scan 无前向信息测量义务）。

## 四、E3 队列出列回执

- 探针：scripts/hsgt_source_probe.py（selftest 7/7·6 接口·8 请求·3s 节流·直连）。
- 证据：results/shortline/hsgt_source_probe.json + results/_e3_hsgt_introspect.json。
- 判词：见上表——主候选（北向日度情绪因子）判负关闭；两枚登记候选（季度持股/南向旁系）零开发。
- 队列：state/queue/explore.md E3 行翻 closed+消耗行 append。

—— bm-a r947·2026-10-10
