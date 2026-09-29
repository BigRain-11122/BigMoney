# C6(c) 响应一致性判据修订预注册（SCIENCE_AUDIT_PREREG §9(c) 修订 · GM 署名 · §8 协议）

> 登记：2026-09-30 01:4x（bm-a r452）·署名：GM（P1 自决权·O-1620；非特别重大——本件只改**审计器读哪个字段**与**补齐预声明腿**，零行为门变更、零阈值放松）·变更协议：SCIENCE_AUDIT_PREREG §8（修订=本件+新预注册+7 天否决窗·BACKTEST_SCIENCE §7 末行原文）·权威链：firm/risk/REGIME_GUARD.md §2 响应矩阵+§3.4 enforce 启用链+§3.5（C6 须检「enforce 后响应与状态一致」）+ SCIENCE_AUDIT_PREREG §9 末行预声明（「该腿在 enforce 接线落地前不实现，届时=新预注册追加判据」）。
> **否决窗：至 2026-10-07 00:00（登记+7 天）**。窗内：审计代码零改动、旧判据照跑、六项 VIOLATION 旗按轮如实复现+轮报告裁定注记指向本件。任何 CEO/GM 否决=冻结本件重新预注册。窗后无否决=实现腿（§4）落地生效。

## §1 动机与证据（跑后如实·判据文本先于实现写死）

1. **触发实况**：月度审计第二场（2026-09-30 01:35 bm-a r452）C6 报 6 项 VIOLATION——六员 paper 件 regime_guard 块 `mode='enforce' != 'shadow'`（旧判据 §9(c) 字面：state 件 mode=='shadow' 时任一 paper 块 mode≠'shadow' → VIOLATION 越权干预）。
2. **裁定（本窗）**：**零实际干预**——六员块 effective 面全为 `active:false · enforced.days_enforced:0 · entries_blocked:0 · entries_halved:0`，`gate_note` 明写日期门未开诚实降级 shadow 语义。`mode` 字段=**请求信道**记录（S6 链明文动作「有新bar则先设 `$env:BIGMONEY_REGIME_GUARD='enforce'` 再 live.paper」·iteration_prompt），非生效模式。判据冻结于 2026-09-24，**先于 T-21 v3 接线**（三重门=批准件+2026-10-01 日期门+环境请求；live/paper.py L789-807：`days_enforced=窗内≥active_from 交易日数`、`active=bool(days_enforced>0)`）。
3. **不改判据则必然误报风暴**：`regime_state.json` 的 `mode` 由 market_regime.py（纯 shadow 探测件）写入=**恒 'shadow'**；日期门 2026-10-01 开后 paper 块 mode 继续 'enforce'（请求信道不变）→ 旧判据**每月审计 6 误报**，真干预反被狼来了噪声淹没。
4. **缺口定性**：§9 末行预声明的 enforce 接线配套预注册（「届时=新预注册追加判据」）在 T-21 落地窗**从未追加**——本件即补齐该预声明路径，非看结果放松（见 §5 零削弱声明）。

## §2 修订后判据 C6(c) v2（窗后生效·冻结文本）

裁定词汇表不变（OK / DRIFT / GAP / STALE / INCONSISTENT / VIOLATION / MISSING，只报不阻断）。**era 锚点改为 paper 块自身 `active_from` 日期门**（state 件 mode 字符串恒 shadow，不承载纪元切换；生效纪元由 T-21 日期门承载）。

- **(c1) 请求信道合法域**：`blk.mode ∉ {shadow, enforce}` → `INCONSISTENT`（未知请求信道）。mode 字串不再作 era/违例判据。
- **(c2) 前门窗口（窗内交易日全 < active_from）——实际干预面全零检查（替代旧字串检查·更严）**：
  - `blk.active != false` → `VIOLATION`（日期门未开而激活=enforce 越权）；
  - `blk.enforced.days_enforced / entries_blocked / entries_halved` 任一非零 → `VIOLATION`（门前实际执行=enforce 越权干预）。
- **(c3) 后门窗口（窗内存在 ≥active_from 交易日）——激活一致性**：`blk.active != true` → `VIOLATION`（门开而守卫未激活=防线失效）。`days_enforced` 应 ≥1 且随窗内门后天数单调递增（对 510300 日历可复核；不符 → `INCONSISTENT`）。
- **(c4) enforce 响应一致性腿（§9 末行预声明·REGIME_GUARD §2 矩阵）**：对每员 open_positions 逐仓，以 510300 交易日历自 cutoff 按 `hold_days` 回走推 entry_date；entry_date ≥ active_from 且该日 state ∈ {ORANGE, RED} → `VIOLATION`（停新仓日新开仓=响应矩阵失效直证）；state ∈ {YELLOW} → ×0.5 名义腿快照不可机读 → 诚实注记（`scaled_entries` 计数交叉引用为软面，非硬判据）。
- **(c5) 不变面**：blk.state 与 history 该 asof 读数一致性 VIOLATION 判据照旧；块缺席=诚实注记；n_paper/n_with_block 计数照旧；state 件 mode=='enforce' 且接线缺失时的 `not_wired` 诚实注记照旧（该腿保留——防未来 state 件纪元切换场景）。
- (a) 阈值指纹、(b) 状态序列连续性、C1-C5 五检：**零改动**（§8 白名单纪律）。

## §3 数据面（零新增采集）

results/regime_state.json（history 按 asof→state）+ results/paper/*_paper.json（regime_guard 块+open_positions+hold_days+cutoff）+ data/daily/510300.csv（交易日历）+ live/paper.py 块 schema（L789-807 语义冻结引用）。

## §4 实现腿（否决窗后 2026-10-07 起方可动代码）

`scripts/science_audit.py` `check_regime_guard()` (c) 段照 §2 改写；selftest 追加四腿：①前门窗口 nonzero counter fixture → VIOLATION；②前门窗口 active=true fixture → VIOLATION；③后门 ORANGE 日新开仓 fixture → VIOLATION；④后门 YELLOW 注记 fixture → 诚实注记非 VIOLATION。实现时本节判据文本一字不改（跑前写死纪律）。

## §5 零削弱声明

旧检查实质=「防未经批准的 enforce 干预」。v2 不弱反强：旧面读 mode 字串（T-21 后必误报·真干预淹没），新面读**实际执行面**（active+三计数器+门后响应矩阵直证），检测灵敏度对真越权事件严格提升；且补齐 §9 末行+REGIME_GUARD §3.5 声明的 enforce-era 响应腿（旧判据该腿 not_wired 空缺）。六员现 VIOLATION 旗在窗内各轮如实复现+裁定注记（本件 §1.2），不以本件翻绿。
