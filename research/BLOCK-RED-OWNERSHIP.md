# Block red ownership

Whose red is it, and can this machine clear it?  Generated block below is re-derived by `scripts/block_red_ownership.py`; edit the script, not the numbers.

<!-- BEGIN BLOCK-RED-OWNERSHIP (generated) -->
### Block red ownership -- 2026-11-29T02:34:46+08:00

machine **bm-c** | board 2026-11-29T02:21:08+08:00 (STARVING) | verdict **PARTLY_CLEARABLE_HERE**

1 of 4 red row(s) clearable from bm-c; 1 because an upstream reader printed before the ledger moved; the rest: HUMAN_GAP=2, PRODUCER_DEFECT=1; designated writers silent >= 20 min (bm-a 14802 min), so the stale-takeover window is open on all 12 registered face(s); 8 of the registry's files on disk have not been refreshed in over an hour

| row | group | seat | class | what decides it | clear |
|---|---|---|---|---|---|
| C5_paper_recon | 风控 | 对账席 | **STALE_UPSTREAM_COPY** | 1 reader face holds a pre-restatement printing (34,238.82 CNY of gaps, 34,238.82 CNY of it closes to the cent against the restatement arithmetic -- all gaps closed); refreshing the reader clears the row | python scripts/strategy_scorecard.py -> python scripts/paper_equity_recheck.py |
| W1_supply | 治理 | 研究席 | **HUMAN_GAP** | write new pre-registered questions into WORK-BANK (bank=cards that already carry verdicts; 0 unconsumed) | -- |
| G6_ingest | 治理 | 数据管道席 | **PRODUCER_DEFECT** | the probe compares the producer's output with itself, so its verdict cannot be trusted -- a re-derive cannot clear it | -- |
| P1_cpu_fill | 治理 | 算力调度席 | **HUMAN_GAP** | enqueue CPU work -- a re-derive cannot raise duty | -- |

**C5_paper_recon** -- results/paper_equity_recheck.json would read **PASS** once the reader is refreshed.
- reader `strategy_scorecard` printed 2026-11-28T22:18:07, ledger stamp 2026-11-28T22:20:14 (127 s older), 5 of 6 traders behind, 34,238.82 CNY of gap, 34,238.82 CNY closes to the cent.

Sequence in a non-contention window: `python scripts/strategy_scorecard.py` then `python scripts/paper_equity_recheck.py`


**Single-writer registry** (12 faces name another machine; a re-derive from anywhere else exits 0 without writing):

| face | owner | owner heartbeat (local / origin, min) | on disk | verdict from this machine |
|---|---|---|---|---|
| `results/daily_scorecard.html` | bm-a | 14802 / 14802 | yes (2026-11-28T22:23:09) | WINDOW_OPEN |
| `results/daily_scorecard.json` | bm-a | 14802 / 14802 | yes (2026-11-28T22:23:09) | WINDOW_OPEN |
| `results/dashboard_status.js` | bm-a | 14802 / 14802 | yes (2026-11-28T22:24:37) | WINDOW_OPEN |
| `results/dashboard_status.json` | bm-a | 14802 / 14802 | yes (2026-11-28T22:24:37) | WINDOW_OPEN |
| `results/market_clock/l3_activation_table.json` | bm-a | 14802 / 14802 | yes (2026-11-28T22:18:30) | WINDOW_OPEN |
| `results/paper/*` | bm-a | 14802 / 14802 | 6 file(s) | -- |
| `results/paper_export/*` | bm-a | 14802 / 14802 | 42 file(s) | -- |
| `results/prospect_paper/*` | bm-a | 14802 / 14802 | 23 file(s) | -- |
| `results/prospect_promotion/*` | bm-a | 14802 / 14802 | 23 file(s) | -- |
| `results/scorecard_v1.json` | bm-a | 14802 / 14802 | yes (2026-11-28T22:17:53) | WINDOW_OPEN |
| `results/strategy_scorecard.json` | bm-a | 14802 / 14802 | yes (2026-11-28T22:18:07) | WINDOW_OPEN |
| `results/t35_open_fill_verify.json` | bm-a | 14802 / 14802 | yes (2026-11-28T22:20:15) | WINDOW_OPEN |

Classes: FIXABLE_HERE | STALE_UPSTREAM_COPY | FOREIGN_WRITER_FRESH | HUMAN_GAP | PRODUCER_DEFECT | UNMEASURED. Read-only over every other face.
<!-- END BLOCK-RED-OWNERSHIP (generated) -->
