# DIGEST — 供给面第三层：池子空着，是没题，还是题都过不了自己的日历（r1421 bm-c）

## 问题

`compute_audit` 的 supply_floor 已经红了约 11,760 分钟（ready 0 / floor 3）。r1199 把这个红拆成
两层：有活没入池（机制故障）vs 根本没活（选题债）——`AGENDA_DEBT`。但 r1415/r1418/r1420 建了
年度日历闸与相位层之后，第三层原因出现了，而它在任何供给面里都看不见：

- 池内 ready = 0
- 任务板 open 未认领 = 0
- 队列活草稿 = 0
- backlog 只能跨公司认领（不是本司供给）

于是供给面印 `AGENDA_DEBT`，读法是「该开题」。可本司**有**题：采用书 `nobond_vt08_adopted`、
它的兄弟 `nobond_base`、floor 0.5 臂、已发布的 `all_classes_published`。它们都被判过，判决是拒：
r1415 因 2026 部分年 CONDITIONAL；r1418 top-2 占比 71.08% 对 70% 线（差 1.08pp）；r1420 兄弟书
跨相位**根本不可判**。**「没人写题」与「题都过不了自己的日历」需要相反的动作**（开题 vs 等证据/
重切书），却在同一个词下面。

## 做法

`scripts/supply_calendar_face.py`（纯只读，零重算零引擎）：

- **只读已发布收据**：`results/etf_book_phase_gate.json`（相位读法，优先）与
  `results/etf_book_year_gate/YEAR-GATE.json`（单相位读法）。
- 每本书一行：判决词、未过的检查名（逐字搬运）、相位 spread/margin、收据指针。
- **只有字面 `ADMIT` 算过**。CONDITIONAL / REFUSE / UNADJUDICABLE_PHASE 一律算拒——日历闸不肯放行
  的候选，不能当作「今天就能点火」的供给。
- 判词四态（冻结先于读任何收据）：`ADMITTED_CANDIDATE_EXISTS` /
  `NO_CANDIDATE_PASSES_CALENDAR` / `NO_CANDIDATES` / `UNKNOWN`（收据读不到 ≠ 没人写题，r98）。
- 同一本书在两份收据里出现时，**列在前面的读法赢**，输家记在 `superseded_receipts`（不静默丢）。

`scripts/supply_candidate_face.py` 接入为单一读取器（import，不重写），新增 `agenda_cause`：
`mechanism` / `calendar` / `no_topics` / `unknown`，并把日历面的句子直接作为 `AGENDA_DEBT` 的读法。
`compute_audit.supply_candidates_face()` 的键集同步扩两个键（`agenda_cause` / `calendar`），
审计面因此也带上归因，而不是只有供给面自己知道。

## 读数（2026-11-08 10:31，实跑）

```
supply_calendar_face: NO_CANDIDATE_PASSES_CALENDAR  4 拒 / 0 过
  nobond_vt08_adopted     CONDITIONAL        via Y4_top2_share                (相位读法)
  nobond_base             UNADJUDICABLE_PHASE via Y3_worst_year, Y4_top2_share (spread 20.82pp vs margin 12.07pp)
  nobond_vt08_floor_050   UNADJUDICABLE_PHASE via Y4_top2_share              (spread 13.96pp vs margin 8.92pp)
  all_classes_published   CONDITIONAL        via Y4_top2_share                (单相位读法)
```

`supply_candidate_face` 增量后：`AGENDA_DEBT`（不变）+ `agenda_cause=calendar`，读法由
「该开题」变为逐名列出「谁被哪条检查判掉」。地板没有搬，红没有消——只是红现在指得出人。

## 可复用三条

1. **一个红只量一层，就会把两种相反动作印成同一个词**（r1199 拆了池 vs 选题债，本窗再拆开题 vs
   过不了日历）——每次看到「差 N 个批次」先问：这 N 个是被谁拿掉的。
2. **拒绝要有名字**：`CONDITIONAL` 这个词本身不可行动，`Y4_top2_share` 才可行动；收据里已有的检查名
   必须逐字搬到供给面上，否则读者还得回去读产物。
3. **多收据同一对象：读法优先级要写进文件、且必须记输家**。本窗的 merge 测试第一版两边候选名不同
   （根本没重叠），腿自己抓出「合并测试没测合并」——夹具必须让两侧撞在同一个名字上。

## 正身

- `scripts/supply_calendar_face.py`（selftest 22/22，`--check` 从发布行重算判词）
- `results/supply_calendar.json` + `results/supply_calendar.md`
- `scripts/supply_candidate_face.py`（selftest 22→34，`agenda_cause`）+ `results/supply_candidates.json`/`.md`
- `scripts/compute_audit.py` 供给块键集 +2
- 方法论卡 `knowledge/METHODOLOGY_ASSETS.md` E426