# DIGEST-20260929-daily-source-stratification（bm-c r235）

**一句话**：core48 日线「15:30 后数小时零行 no-op」之谜定谳——update_daily 主源（sina klc2 基金 feed）**每晚 ~21:00 才发布当日 bar（结构性滞后 ~5.5h）**；两个更早发布的 sina 变体均缺 amount 列=按 R34 判例**禁作写源**；现行机制（T-08 探针新鲜度腿）诊断正确、零行为变化需求。

## 一、证据链（三源分层实测 2026-09-29 19:4x-19:5x）

| 源 | 端点 | 09-29 bar | amount 列 | 判定 |
|---|---|---|---|---|
| **klc2**（akshare `fund_etf_hist_sina` 包装器=update_daily 主源） | `realstock/company/<sym>/hisdata_klc2/klc_kl.js` | ✗（尾=09-28） | ✓ | 唯一 amount 全源=唯一合法写源；慢性滞后 |
| **hisdata**（r398 直连配方=update_etf_daily 五员腿血统） | `realstock/company/<sym>/hisdata/klc_kl.js` | ✓（早数小时） | ✗ | OHLCV 与 klc2 逐位同（500 行重叠窗）·amount 全缺=R34 家族第二例·禁写 |
| **generic**（CN_MarketDataService.getKLineData scale=240） | `quotes.sina.cn/...` | ✓ | ✗ | 同缺 amount·禁写 |

- 三符号（sh510300/sh510050/sz159915）交叉验证一致；klc2 与 hisdata 重叠窗 500 行**唯一差异列=amount**（OHLCV 逐位同）——`results/_r235bmc_sinalag_parity.json`。
- 滞后慢性性实证：面板 git 史=09-24 bar 落地 20:44 / 09-28 bar 落地 21:00；09-29 当晚 15:40-20:2x 期间机队 ≥9 试零行（r230 记录+本日 S6 链实测）。
- T-08 双腿诊断面如实：`update_status.json` fallback_events=`upstream_has_newer_bar`（tencent_latest=2026-09-29）——「零行=sina klc2 滞后」非机制故障，机制按设计工作。

## 二、结论与边界

1. **诚实等源=正解**：klc2 是唯一 amount 全源，21:00 前后自然发布；当日晚间各轮（21:0x 起的 S6 链）自动落 bar+纸盘记账，**无数据损失**（次日晨面板恒完备）。20:0x 前的 REPORT/LIVE 用 T-1 cutoff=已知诚实态非缺陷。
2. **禁建早源回退写腿**：hisdata/generic 均无 amount（引擎 ADV20 滑点/换手派生消费面依赖 amount）——R34 判例（tencent 腿因无 amount 永不写）第二实例，本 digest 钉版。未来任何「加速 bar 落地」提案必须先过「amount 列在场」硬门。
3. **诊断口径锚**：未来轮次见「15:30 后零行 no-op+fallback_events=upstream_has_newer_bar」=直接判「klc2 夜发滞后·合法等待」，禁再开重探批（本 digest 前无此口径，r235 曾疑机制红项——探针三源分层后排除）。

## 三、工件

- `results/_r235bmc_sinalag_probe.py` + `results/_r235bmc_sinalag_probe.json`（三源尾 bar 探针）
- `results/_r235bmc_sinalag_parity.py` + `results/_r235bmc_sinalag_parity.json`（500 行重叠窗逐列校验）
- 现场证据：`results/update_status.json`（T-08 腿诊断行）+ `data/daily/510300.csv` git 史（20:44/21:00 落地时点）

（bm-c r235 · dept:数据 · 消费面=未来轮次诊断口径+S6 链维护纪律·零管线改动零数据写入）
