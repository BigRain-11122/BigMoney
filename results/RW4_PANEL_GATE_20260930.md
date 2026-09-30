# RW-4 数据门禁落地（T-127 / D-20260930-05·2026-09-30）

门禁件 = `knowledge/panel_gate.py`（三腿·fail-closed：门禁不过=批不受理）
实弹证据 = `results/_r476bma_rw4_slice2_probe.json`
接线面 = `live/paper.py load_core`（在役面·行为恒等由 6/6 锚定门证明）

## 审计验收面对账

- 全目录 1724 个 CSV → 归一化去重后 1676 个唯一 symbol
  （孪生 48 对去重·`len(set)==len(list)` = True）
- 陈旧排除（N=5 日·面板锚 2026-09-29）：
  归一化码面排除 1628 只 / 文件面陈旧 1671 件
  （审计口径 1670+ 只陈旧件被排除 ✓·双口径如实并列）
- 在役面板锁：48 只冻结白名单（sha16 abf3d43b9ca13ea5）实弹过门 48/48
- 注入例 5/5 fail-closed 全过（孪生请求拒/越锁拒/在役陈旧拒/必需陈旧拒/在锁缺件拒）

## 「锁定 30 只」差异披露（诚实律）

audit RW-4 row says in-service panel 'locked to 30'; no in-repo count reproduces 30 (48 bare core48 / 53 fresh / 6 registered / 18 held / 22 PROSPECT). Lock = REAL 48-member universe, frozen sha16 abf3d43b9ca13ea5; divergence disclosed, no 30-member panel fabricated.

## 陈旧排除样例（前 5）

- 158000: stale last_bar=2026-09-22 (>5d behind 2026-09-29)
- 158001: stale last_bar=2026-09-22 (>5d behind 2026-09-29)
- 158003: stale last_bar=2026-09-22 (>5d behind 2026-09-29)
- 158005: stale last_bar=2026-09-22 (>5d behind 2026-09-29)
- 158006: stale last_bar=2026-09-22 (>5d behind 2026-09-29)

## 采行注记

- 直接前缀读者（div_lowvol 族 / trial_labor_w4 w5 / regime_calibration）
  = 判负或归档线，按档存重估律留在原冻结口径；新批禁复用其读法。
- 新批装配一律走 `panel_gate.gate(symbols, mode=...)`；G1 孪生/G2 陈旧
  /G3 越锁任一命中 = rc≠0 = 批不受理。
