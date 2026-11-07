# DIGEST 2026-11-07 r1266 (bm-a) -- 一条车道不写自己是没人管的

## 症状
`docs/data_lanes/FRESHNESS.md` 的「Lanes nobody can pick up while the host is away」节里，`marks` 这个唯一的前向盘中证据面印着：

> the row reads another face rather than a collector of its own, so there is nothing to reassign

而 `scripts/update_intraday_marks.py` 从 r1101 起就带着 `--takeover` 与标记句 `TAKEOVER: declared stale takeover of`。板子用一句话把「两台机都能动」的车道说成「放弃吧」。

## 根因（表，不是代码）
`data_lane_freshness.LANES` 里 marks 行写的是 `"writer": None`。能力判据 `takeover_capable(writer)` 读自写者源码，`None` 直接短路成 False，于是：
- 该行进 `frozen_without_takeover`；
- 渲染器走「没有自己采集器」的分支，印出那句 give-up 的话。

「表没填写者」与「写者没有开关」是两种不同的人事状态（前者是板子的缺陷，后者是需要建开关的设计缺口），此前共用一个判词。

## 修法
1. 声明写者：`"writer": "update_intraday_marks"`（同轮 `fatal_loss` 也补上：盘中 tick 不可重建）。
2. 成因分解上人面：外部车道若被审计面发布了 `holes_by_cause`，原样搬到行上；人类页新增「Who was awake on the days that are missing」节，逐因打印。
3. 两个数不同源不许混印（自踩后改）：收集器账是全史 9 孔，本行 `missing` 只是尾后 6 天 → 句子同时点名两者，相等时不出从句。

## 验证
- `python scripts\data_lane_freshness.py selftest` → **25/25 PASS**（L26 未申报写者三态 / L27 成因分解与两数一致性）
- `run` → `frozen_without_takeover` 由 `['marks']` 变 `[]`；marks 行 `takeover_capable=true`、`holes_by_cause` 与 `results/marks_coverage.json` 全等
- `docs/data_lanes/FRESHNESS.md` 实读：`- marks: 6 missing day(s) after the lane's last captured day, out of 9 hole(s) recorded since the lane started (host_down 2, host_offhours 4, lane_missed 1, takeover_possible 2)`
- 新 smoke 腿 `fleet: a lane that names its collector is not told nothing can be done`（从已发布面独立复算，离线绿灯）

## 可复用的一句话
「没人能动它」是一个结论，它至少要两个前提——表里有写者、写者的源码里有开关；缺第一个时印出来的不是结论，是板子自己的空白。