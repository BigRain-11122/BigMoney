# DIGEST 2026-11-08 r1427 (bm-c) — 拒的是书，还是尺子？

## 问题

r1426 证明了 Y4（`net_top2_share`，top-2 年占比）在三臂上判不了自己，而供给地板（`ready 0 < floor 3`）
连红 35 轮、四个候选全被「日历」拒，其中三个的失败项就是 Y4。于是那句「池子空=题都过不了日历」
在新尺子下还成立吗？

## 做法（不改生产判据，只复读）

`candidate_year_gate_phases.py` 已持有三本书 × 五个相位的年度表，本窗在**同一张表**上补四把尺子
（数值 `etf_book_year_caliber.calibers`、判决 `adjudicate_caliber`，全部 import、零重写），并按
`results/etf_book_year_caliber.json` 的 trusted 名单复判，得到 `refusal_survival` 五词：
`REFUSAL_SURVIVES_TRUSTED_RULER` / `REFUSAL_WAS_RULER_ARTIFACT` / `PARTIAL_TRUSTED_READ` /
`UNCERTIFIED` / 无相位集不判。`supply_calendar_face.py` 把这词搬进操作面（`ruler_split` + WARNING 行）。

## 读数

| 书 | 控制尺 net_top2_share | effective_years（线 3 年） | years_for_half（线 3 年） | 生存词 |
|---|---|---|---|---|
| nobond_vt08_adopted | FAIL（中位 0.796，散 0.087） | PASS（中位 4.98） | **FAIL（中位 2）** | SURVIVES |
| nobond_base | UNADJUDICABLE（散 0.208 > 距 0.121） | PASS（4.71） | **FAIL（2）** | SURVIVES |
| nobond_vt08_floor_050 | UNADJUDICABLE（散 0.140 > 距 0.089） | PASS（4.99） | **FAIL（2）** | SURVIVES |
| all_classes_published | 单相位（0.7719） | — | — | 无相位集，未复读 |

## 结论

1. **两本古典的拒绝句是坏尺子印的**（控制尺自己 UNADJUDICABLE），所以「被日历拒了」这句话在那两本上
   从来没被验证过。
2. **换成两把能自判的尺子，三本全部还是拒**，且拒的是同一件事：宽（4.7–5.0 年）但前置（一半收益来自
   2 年，线 3）。→ 供给地板的红是真因，动作是开新题/重切书，不是调闸。
3. **单相位候选诚实留空**：没有相位集就没法复读尺子，面里印 `no phase set, ruler not re-read`。

## 正身

- `scripts/candidate_year_gate_phases.py`（selftest 21/21：L10–L12 生存词三态 + L13 口径块恒等）
- `scripts/supply_calendar_face.py`（selftest 30/30：artifact WARNING + no_phase_set 不冒充 artifact）
- `results/etf_book_phase_gate.json`、`results/supply_calendar.json`、`results/supply_calendar.md`
- S6 腿 `supply_calendar`（每轮 regenerated，receipts only）；smoke 双腿沿用
- 方法卡 `knowledge/METHODOLOGY_ASSETS.md` E434

## 坑

phase 模块与 caliber 模块互相 import → 循环（caliber 在模块级 import phases 求 `PHASE_STARTS`）。
正法：caliber 侧保持模块级，phases 侧改函数内惰性 import（`_caliber_module()`）。