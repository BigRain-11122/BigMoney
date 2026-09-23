# 换手率推导档案（TURNOVER_DERIVATION）· 纯数据工程 · 零统计推断

> 来源：MSG-20260923-1937 §3 附带数据考古发现 + 本档案=全宇宙实证落地件；**修正回执=MSG-20260923-1945**（§1 三股手检表述过宽的勘误）。
> 性质：数据审计（J9a/P-4-2a 先例）——零 IC、零引擎跑、**试验账本 N 不动**。

## §1 发现（考古事实 + 全宇宙修正）

- bars parquet 的 `turnover` 列**全史 NaN**（仅末 bar 有值）——P-1c Stage-A 缓存 nan_coverage 采样 1.0 的根因
- `outstanding_share`（osh）列**全史零缺失**（全宇宙 null_frac=0.0，252d 内变动>5% 者仅 8 股=逐股内部一致）
- 三股手检：**turnover = volume / outstanding_share**（000001: 0.0039✓、600519: 0.002✓、300750: 0.0111✓）——**但三股全为非 688 板=选择偏差，该公式仅对非 688 板成立**
- **全宇宙探针判定（§4）：公式非全宇宙成立**——根因不是 osh 语义，而是 **688xxx 文件的 volume 列=100×真实股数**（vwap 锚定实证）

## §2 推导公式与检查定义（跑前写死于 scripts/p1c_turnover_derive.py）

- 原始公式：`turnover_derived = volume / outstanding_share`（osh≤0 或 NaN→NaN）
- 检查 A（存储对账）：存储 turnover 有限处 |derived−stored|/|stored| ≤ 1e-6，逐行对账全宇宙
- 检查 B（osh 覆盖）：逐股 osh 缺失率；检查 C（推导覆盖）：derived 有限行/总行
- 检查 D（合理性）：derived > 1.05 异常行计数——记录不裁决
- 诊断探针（scripts/p1c_turnover_diag.py，检查 A 判负后追加）：末 bar 隐含分母 `implied=volume/stored` 对 `r1=implied/osh` 分布、`r2=osh_now/osh_252d` 时间稳定性、异常行时代分布、vwap 锚定（amount/volume vs close）

## §3 用法指引（谁消费、怎么消费）

- **P-1c Stage-B**：GTJA 033/062 涉换手因子的「缺字段跳过」可解除——**分板推导**：非 688 `turnover=volume/osh`；**688 `turnover=(volume/100)/osh`**；勿用 bars 原生 turnover 列（全史空）；是否入批由 Stage-B 预注册自裁
- **⚠ 688 数据质量警报（新发现，全车队生效）**：688xxx 文件 **volume 列=100×真实股数**（vwap=amount/volume=股价/100，688001/688008 实证）→ 一切消费 688 **volume/vwap** 的缓存列/面板/因子须先修正：P-1c 缓存 `vwap` 列 688 列=100×过小；**bm-b R38-a 面板 7 字段自查**；WQ101/GTJA 量价类截面因子同受影响。amount/osh/价格列不受影响
- **经查不受影响**（如实披露）：P-A 四因子（count/days_since/netbuy(用 amount)/amt_share(用 LHB 源)）、P-B 六成员（全价格类）均不涉 volume/vwap
- **范围红线**：P-1c 缓存是循环轮资产，本推导**不改缓存**；缓存修正（vwap 688 列）由 Stage-B 预注册自决

## §4 结果（2026-09-23 19:5x 实跑一次定稿；探针 2s/8 workers 全宇宙 5,222 件零读错）

- **检查 A 判定：MISMATCH（诚实判负）**——5,204/5,222 股末 bar 对账超差（max_rel_dev≈101.5×）；仅 18 股通过
- **检查 B/C**：osh 全宇宙零缺失 ✓；derived 覆盖=1.0 ✓
- **诊断（r1=implied/osh 末 bar 反推）**：
  - **r1≈1.0000：4,480 股**（p99 内 ±0.2%）=公式**精确成立**，覆盖 000/001/002/300/301/600/601/603/605 全部非科创板
  - **r1≈100.0：666 股，全部 688xxx**=隐含分母=100×osh → **volume 列 100×**（非 osh 语义差）
  - **vwap 锚定定性**（688001: close 73.36 元、amount/volume=0.73=股价/100 ✓；688008: 221.83/2.27 ✓；osh 列=真实总股本 ✓、stored turnover=真实换手 ✓）→ **单位差在 volume 列**：688 文件 volume=100×真实股数（源单位异常，科创板原始数据或以「百股/手×100」口径写入）
  - r2=osh 时间稳定性中位 1.0（p1/p99 0.9996/1.0005）✓
  - 检查 D 异常行 334,967 **全部 >2015** 且全部集中 688（科创板 2019 年开板）=纯单位问题非坏点；≤2015 异常 0 行
  - 边缘：14 股末 bar 无有限存储值（如实记，不裁决）
- **修正后定案公式**：非 688 `turnover = volume/osh`；688 `turnover = (volume/100)/osh`——**截面换手因子必须分板修正**（688 不修=虚高 100 倍=截面排名全歪）
- **教训（诚实记）**：三股手检的选择偏差（全流通大盘股）险些把「逐位实证」过宽表述发成全队口径——全宇宙探针在 Stage-B 消费前拦住；修正回执 MSG-1945 已发
- 账本：纯数据工程，N 不动；探针+诊断代码全入仓（本档案 §2+两脚本），可复现
