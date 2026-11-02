# DIGEST 2026-11-02 · r1242 bm-a · 快照闸把「重发」判成「改数」

**一句话**：`etf_book_phase_atlas_arms.py --live-widths-check` 把可执行单自己的 2×2 快照按逐位
相等判，而那张单每个交易日都会在新 bar 上重写——2026-11-02 首次跳出 8 个字段（12.21 vs 12.17 等），
闸读成「有人手改」（rc1）；正法是让快照记下它拍的是哪张单（`as_issued.ticket_asof`），
**更晚的单 = stale（rc2，链付 refresh）**，同日 = 真改数（rc1）。

## 现场

- 链记录 `results/_r1241bma_s6_chain.json`：127 legs，唯一非零 = `etf_book_live_widths` rc1。
- 断链根因：上一窗把它判为「inconsistent」，链按契约**不付 refresh**（refresh 只在 stale 时花），
  于是每轮固定红一次，修法只剩「放松断言」这条歪路。
- 证伪用时 30 秒：把当天票 `results/etf_book_order/TICKET-2026-11-02.json` 的四格与面里存的四格
  并排，差值与「多一个 bar 的 inception 模拟」量级一致（3-4bp），且面里四个格子逐字等于
  `TICKET-2026-10-30.json` 的四格——即快照忠实于旧票，不是被人改过。

## 改法（判据层，不动链路）

1. `_as_issued_block(..., ticket)` 增写 `ticket_asof`（`evidence_cutoff`，缺则文件名日期）。
2. 新 `_ticket_repriced(pub, rebuilt)`：仅当**全部**漂移落在 `as_issued` 内、且重建面的
   `ticket_asof` **严格更晚**时返回原因；`ticket_asof` 缺失（旧面）也走此分支（无法证明 ≠ 没变）。
3. `live_width_check()` 在该分支打印 `live-width face is stale: ...` 并 rc2 —— 链的
   `run_leg(refresh=...)` 本来就只在文本含 "stale" 时付刷新，于是自愈闭环现成。
4. `smoke_test.py` 该面腿加断言：`as_issued` 必须带 `ticket_asof`。

## 验收

- selftest 117 → **120 legs，0 failed**（L29b 旧单→2 / L29c 同日→1 / L29d 外部漂移→1）。
- 实弹：`--live-widths-check` → rc2（stale，指向 ticket 2026-11-02）→ `--live-widths` → rc0 →
  再 check → **rc0**，面内 `ticket_asof` 2026-11-02、`evidence_cutoff` 2026-10-30、
  verdict COIN_FLIP_INSIDE_ENGINE_DISAGREEMENT（配对 0.12pp / 引擎分歧 2.035pp）。
- 顺带确认确定性：本轮误用无横线参数把 `run` 跑了一遍，产物与链产出**逐字节相同**
  （`git diff` 空），故未污染族面。

## 教训

- 「研究面（定格）」与「票面（每日重写）」放在同一份 JSON 里时，闸必须分别对待：前者逐位相等，
  后者只判它是不是同一张单。
- 三态要由内容判，不由时间戳判（E275 同族）；本轮两个信号都取自内容：快照里的单日期 vs 现票日期。
- 卡 = `knowledge/METHODOLOGY_ASSETS.md` E359。