# Are the block board's red rows real?

The board is the one page that tells the line what to fix next, and its line state is
`STARVING` whenever a red row sits next to an empty queue. So a red row is an
instruction. Two of the three reds this round turn out to be defects in the board's own
readers or producer, and the third is red for a reason that cannot be trusted in either
direction -- which is why the line has been told to refill a bank that already holds
eighteen pre-registered questions.

## What it says

<!-- TRIAGE-BEGIN -->
_generated 2026-11-28T17:06:10+08:00 · evidence cutoff 2026-11-27_

| red row | class | what the reader prints | what is true |
|---|---|---|---|
| C4_drawdown_guard | **UNCLASSIFIED** | 136.9h old > 120h | — |
| W1_supply | **REAL** | no open question left; blocked on data: options_vol_premium, minute_intraday_reversal | — |
| G6_ingest | **FALSE_GREEN_PRODUCER** | self-diff (FLUXGROUP vs FLUXGROUP) -- not a handover | no handover has ever been measured (the file says **COMPLETE**) |
| P1_cpu_fill | **UNCLASSIFIED** | duty 0.0% < floor 60.0% (units=0, waiting=0) | — |

- board: **26 rows / 4 red** · class counts {"UNCLASSIFIED": 2, "REAL": 1, "FALSE_GREEN_PRODUCER": 1}
- real gap(s): **W1_supply** · false red(s): **none** · untrusted verdict(s): **G6_ingest**
- line state printed **STARVING** -> honest **STARVING** (bench pending 0, bank claimable 0)
- the cash panel's last bar is **2026-11-27**; the board's reference is today's weekday while a bar dated today only exists after 15:30, so the printed lag overstates the honest one by **0 day(s)** and the 4-day allowance would pass a **0-session** gap

- vocabulary evidence (WORK-BANK.json revisions, newest first): bfb43120 {"queued": 18, "blocked": 2} · 61f1bc85 {"queued": 17} · a0c6e52f {"queued": 13, "open": 4}

Patches are **proven, not applied** (contention window: the shared faces `scripts/block_board.py` / `research/QUANT-BLOCKS.json` are not edited here).
<!-- TRIAGE-END -->
## What this is not

- not a re-run of the board: every red is re-derived by a second implementation, and the
  two readings are printed side by side so a disagreement is visible
- not a fix: the patches are proven against the real files but the shared faces are left
  untouched until the contention window closes
- not a claim that the cash panel is fine: it is two sessions behind, and the honest
  number is the one this face prints, not the board's

Reproduce: `python scripts/block_red_triage.py` (writes this block), `--check`
(re-derive and compare), `--selftest` (offline legs).
