# QA · r2122 (bm-c) · 「8% 波动」这句话在这本书上有价钱，且一页纸的日期全部可核

窗口 2026-11-26 08:0x–09:0x（无人值守轮）｜machine=bm-c｜watermark=绿（red=false·lane=healthy）
｜孤儿面=0｜竞争窗 rc=0 CLEAN（单 codely 宿主）

## 本轮改什么

1. **把一个「接线进了 git、被接的脚本没进 git」的洞堵上**（r1783 族实证）：
   `scripts/carry_risk_dial_vs_book.py` 被 `Tools/s6_chain_bmc.py` 的一条链腿和
   `smoke_test.py` 的两条腿同时点名，而该脚本 + 面 + 页三件**从未进过 git**（只在写手本机磁盘上）。
   在本机全绿、任何新克隆都会跑三腿打空。
2. **把这条洞变成机械检查**（E 族：问题 → 可查检查项）：`smoke_test.py` 新增
   `unwired_script_problems()` + 两条腿（正判 + 负控）。
3. **产品面**：CEO 一页纸 §⑦ 新增「8% 波动」的价钱段——账本 1052 根 bar 实测年波动 14.05%、
   要在 100 万本金上把它压到 8% 需要 **1,756,600 元**（净值 1.76 倍）、代价是账面年化
   27.19% → 15.48%（夏普不变），并同时印两种读法（权重读法 / 同尺寸读法）各自判词。
4. **一页纸第一段（「先读这个」）20 处日期此前无规则可核**：补 3 条映射规则 + 3 个如实分类桶
   → 现在 **136 处日期逐句对上引用面，0 处判不了，0 处无规则可核**。
5. 顺带把一条面代差红关掉：`etf_book_promotion_provenance` STALE → run → **CHECK_OK**。

## 证据

| 检查 | 命令 | 结果 |
| --- | --- | --- |
| dial 面自检 | `python scripts/carry_risk_dial_vs_book.py --selftest` | **20 of 20 PASS** |
| dial 面 check | `python scripts/carry_risk_dial_vs_book.py check` | **CHECK_OK**（verdict DIAL_FITS_THE_BEST_SESSION_ONLY / SAME_SIZE_BREACHES_THE_WORST_SESSION） |
| 日词审计（重算） | `python scripts/live_usage_day_words.py run` | **PRINTED_DATES_AGREE**（136 处日期 / 101 条规则 / 0 判不了 / 0 无规则） |
| 日词审计（校验） | `python scripts/live_usage_day_words.py check` | rc **0** |
| 日词审计自检 | `python scripts/live_usage_day_words.py --selftest` | **30/30** |
| CEO 页自检 | `python scripts/ceo_live_usage.py selftest` | **selftest: ALL PASS** |
| 页面重复句守卫 | `python Tools/page_repeat_guard.py scan` | 4 face / **0 repeated** |
| 接线守卫（修前） | `python results/_r2122bmc_unwired_probe.py` | POSITIVE 报出 `scripts/carry_risk_dial_vs_book.py (on this disk but not in git)` |
| 接线守卫（暂存后） | 同上 | POSITIVE **none**；负控 `scripts/__r2122_not_in_git__.py` **仍被报出**（谓词会说话） |
| 面代差红 | `python scripts/etf_book_promotion_provenance.py check` | **CHECK_OK**（16 行 / 14 个东西 / 6 个机制） |

## 没做的（如实）

- **全量冒烟本轮未跑完**：`python -m smoke_test` 以分离进程跑到 675 行仍在飞（6 条 FAIL，
  全部属 r2121 已登记 carried 清单：paper book NAV 身份、lane appended nothing、
  k-gap 面代差、phase_atlas_arms 9 腿、toll-ladder、以及一条本轮已修）。**不宣称套件总数。**
- 剩余 carried 红未动：`k-gap 面 2026-11-20 vs 票面 2026-11-25`（无链腿重跑该面）、
  `etf_book_phase_atlas_arms`（三臂需重烧）、`paper book owns the book the card sells`
  （navdev=6.5e-09 被判 NAV_IDENTITY_BROKEN，容差来历需先查再改，不擅放）、
  `toll-ladder verdict is recomputable`、`a lane that appended nothing`。
- 未改任何判据线去「修绿」；两种读法只并列不合并。

## 工具的坑（本窗两枚）

1. `subprocess.run(..., text=True)` 在本机按 GBK 解码 git 的 UTF-8 路径输出 →
   `UnicodeDecodeError` 且 `stdout=None`（守卫当场崩）。正法：`encoding="utf-8",
   errors="replace"` 显式钉死。
2. 用「扫源码里的 `"scripts/xxx.py"` 字面量」当接线证据时，**docstring 与负控里的假名字会被当真**：
   首版把 `scripts/x.py`、`scripts/__r2122_not_in_git__.py` 都报成缺陷。正法：腿参数是权威（照报），
   纯字面量只在文件确实存在时才可信。
