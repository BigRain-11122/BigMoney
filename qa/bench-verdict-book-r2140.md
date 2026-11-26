# QA — 答卷册（bench verdict book）· r2140 · bm-c

**实物**
- `scripts/bench_verdict_book.py`
- `results/bench_verdict_book.json`
- `research/BENCH-VERDICT-BOOK.md`

**为什么做这一件**
`work_bank_supply_truth` 已经把「银行里还有没有活」回答成「没有」（18/20 已答、2 数据阻塞、没人写下第 21 张卡）。但它只修了**供给**读法，没修**消费**读法：33 张已答卡（银行 20 + 赚钱线 13）的判词散在 `results/bench_*.json` 里，每个后来的轮次都得逐张打开才知道「问过什么、回了什么、把案子的哪一块关掉了」。本件把这些散件编成一册，并把「同一问别付两次钱」写成机器可查的问句指纹。

**读数（2026-11-26 16:4x）**
- 33 张门票面 → **96 行判词**（多臂面按臂展开）
- 处置分布：**EXHAUSTED 75 · CANDIDATE 6 · DATA_GAP 2 · OTHER 12 · REVALIDATED 1**
- 缺证据 0 行；册内重复问句 0 对（相似度 ≥0.80）
- 6 行 CANDIDATE：`basis_timing_perm`(SIGNIFICANT) · `basis_timing_size`(GO) · `census_bond_futures`(CENSUS_LEANS_POSITIVE, 年化 3.20%/夏普 0.523/回撤 -11.64%) + `pair_index_60d`/`census_index_futures` 各一条 GO 臂 —— 都在赚钱线（基差/容量/时点）一侧，银行侧一条都没有

**验证**
- `--check`（selftest）**17/17 PASS**
- `run` rc0；`--verify` rc0（重派生与发布件逐字节相同，仅 `generated` 变）
- 页面字节级检查：20,859 B、`%` 无重复残迹（0 处 `%%`）、无 CRLF（CRLF=0）、中文 42 处「缺」字完好

**自检钉住的行为腿（不是描述）**
1. 多臂面必须按臂出行，且每条臂引用**自己的**数字（首版把 6 条债券臂印成同一组 1.77%/0.443 —— 由这条腿当场抓出）
2. dict 判词若只含读数字段，不得展开成「每个小数一行」
3. 缺证据面 → 标 `result_present=False` + 进 `missing_evidence`，禁印 0
4. 失败关卡必须点名（`4/5 缺 H5_excess_ge_2pct_t_ge_1.5`），不许只剩一个计数
5. 同一张卡的多臂不得被判成重复问句（首版 300 条假重复，由「按卡不按行」修正）
6. `--verify` 归一 `generated` 后逐字节相等

**未验证（如实）**
- 判词处置表（NO_EDGE/UNSTABLE_/CENSUS_* → EXHAUSTED 等）是本件定的读法，不是上游定义；上游若改判词词面，本册只会在 OTHER 列增长，不会自己报警
- 只看已经写在 `BENCH-QUEUE.json` / `WORK-BANK.json` 的卡；未入册的实验（如 r2137–r2139 的 carry/资金面）不在册内
- 银行 13 张 off_bank 卡没有 `question` 字段，指纹为空 → 跨册查重对此类无效
- 本面不重算任何收益，全部继承各自结果面（字节摘要可核对）

**竞争窗**
`repo_write_contention` rc=3（对端 interactive pid=107624 自 11:49 存活）：本件全部为新增文件面，未改任何共享面，未跑 S6 链。
