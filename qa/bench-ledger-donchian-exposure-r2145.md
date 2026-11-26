# QA — bench-ledger-donchian-exposure (bm-c r2145)

Charter 清单逐项，证据可复跑。

| # | 项 | 结果 | 证据 |
|---|---|---|---|
| 1 | 可运行 | PASS | `python scripts\bench_ledger_donchian_exposure.py run` rc0，落 `results/bench_ledger_donchian_exposure.json` |
| 2 | 确定性 | PASS | 任意两次 `run` 除 `generated` 外逐键相同；`check` 重 derive 后与发布面 4 个判据键全等（`OK verdict=LEDGER_NOT_EXPOSED faces=77`，rc0） |
| 3 | 自检 | PASS | `selftest` **15/15 PASS**（见 §1） |
| 4 | 判据可机械核 | PASS | 血统判据=面自己的 schema 键集；受影响判据=代码面 AST 探针（`trial_labor_w4.py:1071` 面板门、`cta_p1_screen.py:69` 滚动基座）；关闭族判据=`science_gates.CLOSED_FAMILIES` 的 evidence 字面对撞 |
| 5 | 不静默丢面 | PASS | 6 张自审面进 `self_audit_excluded` 并各带理由；12 张未分类面原样列在 `face_table`（`lineage=unknown`），24 行不并入结论 |
| 6 | 不越权改共享面 | PASS | 本件只新增 4 件（脚本/JSON/页面/本 QA）；未改 `bench_generic`、未改判词、未跑 S6 链（竞争窗 rc=3） |
| 7 | 不过度声称 | PASS | 页面 §4 明列 4 条不主张项（臂已修/行数=臂数/mass 全干净/未分类已定性） |

## §1 自检 15 腿

```
[PASS] mentions donchian            [PASS] ignores other families
[PASS] bench lineage                [PASS] mass lineage
[PASS] mixed lineage                [PASS] unknown lineage
[PASS] gate found                   [PASS] gate has file:line
[PASS] cta screen located           [PASS] cta screen judged consistent
[PASS] screen names its rolling base
[PASS] closed families readable
[PASS] face counts non-negative     [PASS] verdict is a known token
[PASS] bucket records agree with table
```

## §2 两枚自捕（开发中当场抓出并修）

1. **分类器把候选面当成未分类**：首版 mass 血统标记只有 `cells/trials_ledger/n_cells`，而盘上多数 mass 面是**候选波**（`candidates`/`grammar_sha256`/`prereg`），于是 739 行掉进 `unknown`，差点让"账本未受影响"这个结论只剩一半证据。修=补候选面标记，mass 血统从 27 面 411 行涨到 60 面 1,089 行。
2. **自审面自我膨胀**：首版把 r2143/r2144 自己的审计面当试验记录计数（`bench_donchian_repair_rerun.json` 一次灌进 72 行，比真卡片还多）。修=按 schema/载荷词（audit/dedupe/invariance、`n_faces_audited`/`cards_examined`/`arms_examined`、`defect`+`cards`）排除并逐条印理由。
   同窗第三枚（更小）：`families` 键曾被当成审计标记，把 15 张 `*_grammar.json` 整体误排除——已撤。

## §3 未验证（如实）

- 未逐张读 57 张 mass 面的数据路径；"不受影响"由面板门一条代码腿 + CTA 屏 AST 一条代码腿支撑，不是逐面证明。
- `CLOSED_FAMILIES` 的 `cta_futures_p1` 证据指向 `research/STRATEGY_LIBRARY.md`（文档），未直接点名三张 `shortline_cta_*` 面——"三屏免疫"是本件另起路径证明的，注册簿字面链未闭死（需改共享面写面路径，竞争窗不做）。
- S6 链连续第 14 轮未跑（竞争窗 rc=3）。
