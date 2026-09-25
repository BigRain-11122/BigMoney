# DIGEST-20260926-r216-t71-sina-mf-freshness — T-71 新鲜度证伪分片（R215 掩膜陷阱正解）

> 认领线：bm-a 数据部·T-2026-09-26-71（R215 开票、GM 署名 O-1620 下放）本切片。
> 前件：DIGEST-20260926-r215-t71-sina-mf-probe.md（三面探针：活性 ALIVE／量纲=个股四档分解
> VERIFIED／深度≥2018-10-30／**新鲜度 UNDETERMINED**——netamount 降序 top-100 掩膜下不可证）。
> 本件=新鲜度证伪探针（新预算窗 ≤2 请求，R109 节制律；日期序读数，掩膜陷阱正解）。

## §一 探针设计（决策矩阵预注册于脚本头注）

- **正解**：R215 陷阱=按净额降序 top-N 掩膜读数（近窗静默日不进 top-N ⇒ date_max 只可作下界）。
  本片改用 `sort=opendate&asc=0`（日期降序）⇒ row0.opendate 即端点该股最新日期——直接证伪子。
  **防再掩膜**：逐行单调性校验（date_desc_monotone 必须为 true 才算干净读数；排序键被静默忽略
  ⇒ 退回掩膜读数 ⇒ 视为探针失败不采信）。
- **r1**：600519 日期序 → 干净 ⇒ 按结果分流 r2：fresh=第二股加固（601398）／stale=第二股分离
  「端点冻结 vs 个股特异」／parse-fail=备选参面重试（去 fenlei）。
- **新鲜度门**：最近完整 bar 日=2026-09-24（2026-09-25 中秋休市；面板 cutoff 09-24，R213/R214 实证；
  下一 bar 09-28 周一）。

## §二 实弹读数（预算 2/2 耗尽，R109 节制守住）

| # | 面 | 读数 |
|---|---|---|
| r1 | sh600519 `sort=opendate&asc=0&num=5` | HTTP 200 640ms；5 行**严格日期降序**；row0.opendate=**2026-09-24**=最新 bar 日 |
| r2 | sh601398 同配方（fresh 加固腿） | HTTP 200 83ms；row0.opendate=**2026-09-24**；r3 档=30,144,629 非零 |

- **verdict=FRESH**：双股日期序非掩膜读数均穿透至 2026-09-24 ⇒ **新鲜度门 PASSED**。
  R215「UNDETERMINED」翻案为 TRUE——掩膜下界 09-04 与端点真实新鲜度无关（陷阱实证二连）。
- **自洽律再验证**（今日两行手算）：600519 Σnets=-672,895,782.09=netamount 精确；
  601398 Σnets=323,002,267.88=netamount 精确（R215 百行 worst 4.77e-07 同律）。
- **r3 档结构零披露**：600519 r3≈0 非「档位废弃」——高价股单笔结构性越界（601398 r3 非零反证）。
  采集面禁把 r3 当死列丢弃。

## §三 判定与后续

- **候选 QUALIFIED+fresh 仍未准入**（prereg-first R99 恒在）：新鲜度门通过后，下一交付=
  **采集器 prereg 草案**（MF_COLLECTOR §8 族跨源双面候选）＝本日随本片落
  `research/shortline/SINA_MF_PREREG.md`（DRAFT）；采集器实现=另开新票（T-43 THS 先例：
  spec/prereg 冻结→GM 署名票→实现），P1 数据源扩容须署名单开工。
- **量纲纪律重申**：sina 四档（r0..r3 gross + r*_net）档位阈值未见于 API 面（folklore 称与 EM
  阈值不同源）——R118 量纲诚实律下**禁映射到 EM 超大/大/中/小语义**，独立量纲独立库
  （THS 分件分库先例）。§8「跨 provider 冗余对该量纲结构性不存在」裁定面收窄为
  「EM 族内+THS 聚合面」——sina 分解面为其后新证据，裁定律本身（聚合冒充分解禁行）不变。

## §四 证据件

- `results/_r216_sina_mf_freshness.json`（探针产物：双面读数+决策矩阵+判定）
- `results/_r216_sina_mf_freshness.py`（探针脚本：矩阵预注册于头注）
- `results/_r215_sina_mf_probe.json`（前件三面）
- `research/shortline/SINA_MF_PREREG.md`（TRUE 分支交付：prereg 草案 DRAFT）
