# T-136 LOWAMP-P1 Verdict Integrity Audit — Adjudication Memo

- Ticket: T-2026-10-01-136-P0 (verdict-integrity-audit, bm-b r492 E1 finding)
- Auditor: bm-c r301 (lane-free, zero-network, deterministic; runner machinery imported as-is, zero reimplementation drift)
- Evidence artifact: `results/t136_verdict_audit/t136_leg123.json` (legs A/B/C, sort_keys deterministic)
- Fixture (runnable): `results/_r301bmc_t136_fixture.py`
- Frozen prereg: `research/LOWAMP-P1.md` (s1 5074b5102 + ADMIT 32c529f49); verdict under audit = `judged-negative` (finalize 2026-10-01 03:18 bm-a; headline LA-REP legacy base ret_full −17.99%, sharpe −1.4475, nav_last 820,129.43)

## Executive summary (plain language)

判决机器没有坏——坏的是批的「执行面规格」漏了一句话。引擎的缺省止损/止盈/时间退出规则是给股票类交易员调的（12 天涨不到 2% 就退、亏损 8 天就退、最多拿 25 天必退）。国债 ETF 一年才涨 2-3%，永远过不了这些门 → 被机器每 8-13 天强制来回买卖，6.5 年付了约 250 次往返成本，把本来 +16% 的策略硬生生磨成 −18%。全批 254 笔退出里 246 笔（97%）是引擎规则踢的，只有 7 笔是策略自己的信号。**「−39pp 不可调和缺口」已全额对账：−33.9pp=引擎缺省退出栈换手损耗 + −5.3pp=资格面闪烁/再入场间隙。** x2 面 −32.9pp 缺口同样全额对账（509 笔×13.04bp×0.5 权重）。测量仪无罪；烧的是预注册里自相矛盾的执行面。VOID 与否=治理决定（本备忘录只呈证据与建议，不自决）。

## Leg A — as-burned replay reconciles to the bp (instrument consistent)

Exact replay of the burned continuous face through the runner's own machinery (`load_axis('legacy')` + `build_signal` + `run_cell_portfolio` internals, per-symbol engine runs kept):

| field | replay | artifact | match |
|---|---|---|---|
| ret_full | −0.179871 | −0.179871 | ✓ (6 dp) |
| sharpe_full | −1.447533 | −1.447533 | ✓ |
| nav_last | 820129.43 | 820129.43 | ✓ |
| n_trades / n_entries | 254 / 255 | 254 / 255 | ✓ |
| full returns series (1630 rows) | max abs diff < 5e-7 | — | ✓ bp-level |

Panel anchors match the burn (members 48, panel 2020-01-02→2026-09-22, anchor_rows 1631, starts 1254 = amended G-CENSUS). Active members ever = {159934, 511010, 511260, 518880} = audit.liquidity.active_members_ever=4 ✓. **The engine, the sub-account decomposition, and the entry_size_scale weight mapping are all exact — no hidden instrument defect.**

## Leg A2 — exit-reason census: the churn mechanism

Per-symbol engine trade reasons on the as-burned face:

| symbol | loss_time_stop | time_decay | signal_reversal | total exits |
|---|---|---|---|---|
| 511010 (5Y treasury) | 55 | 67 | 1 | 123 |
| 511260 (10Y treasury) | 55 | 69 | 0 | 124 |
| 159934 / 518880 (occasional picks) | 0 | 1 | 3+3 | 7 |
| **total** | **110** | **137** | **7** | **254** |

**246/254 = 97% of exits were fired by the engine's DEFAULT exit stack** (P4 time_decay: hold≥12d & pnl<2% → close; P5 loss_time_stop: pnl<0 & hold≥8d → close; P6 global_hard_limit: hold≥25d → always close), not by the family's selection signal. A bond pair drifting +2~3%/yr can never pass the 12-day/2% decay gate → mechanical 8-13 day churn cycles for 6.5 years. The runner passed `params = {"position_size_pct": 1.0, "max_positions": 1, "sizing_mode": "fixed_initial", "report_num_entries": True}` — **zero exit keys** — so `engine/exit_rules.py` defaults (frozen, tuned for equity traders) fired on top of the signal exit.

## Leg B / Leg C — the intended ALWAYS-ON face is +15.9%

Leg B: identical window/signal/weights/costs, exit stack neutralized (P1 signal exit only; `take_profit_levels=()`, decay period 10^6/threshold −1, initial_stop −1, trailing 10.0, `ExitPatch({"loss_time_days": 10^6, "global_hard_limit": 10^6})`):

- ret_full **+15.88%**, sharpe **+1.158**, n_trades **7** (only real signal exits)

Leg C: fully independent P1-only arithmetic simulator (no engine on the path; T+1 open fills, 13.041bp/side both ways, 1-day re-entry gap):

- ret_full **+15.95%**, nav_last 1,159,457.50; B-vs-C daily-returns max abs diff 5.05e-4 (boundary fill-semantics residue)

Cross-validation: the family as designed is positive, consistent with the raw-path expectation (511010 +17.87%, 511260 +24.43% in-window; invvol pair ≈ +21% gross).

## Decomposition — the E1 "irreconcilable 39pp" fully reconciles

| face | ret_full |
|---|---|
| raw B&H expectation (bond pair, equal weight) | ≈ +21.2% |
| intended ALWAYS-ON face (Leg B; Leg C agrees) | **+15.88%** (−5.3pp vs B&H = eligibility flicker onto 159934/518880, 7 signal-exit 1-day gaps, rebalance costs) |
| as burned (Leg A) | **−17.99%** |
| **exit-stack churn cost (A − B)** | **−33.86pp** |

x2 secondary evidence also reconciles: LA-REP legacy x2 −50.85% vs base −17.99% → Δ=−32.86pp = 509 fills × 13.041bp × ~0.495 avg weight (66.4% × 0.495) — the ticket's "implied ~347bp/trade = 13× declared" inference assumed the wrong trade count (39 vs the true ~509 churned fills); there is **no per-trade cost anomaly**. All four input-face proofs (a)-(d) of the ticket stand unchanged.

## Blast radius — LOWAMP-P1 is the sole member

- **t22 lineage (29 in-registry traders)**: 17 explicitly tune exits in registered params (decay 25d/5%, loss_time_days 16, TP ladders…); 12 bare (PROS-*, TREND-001, NEEDLE-DE-01) are equity/shortline-class where the default stack is the house style their verdicts were judged under from day one (positive Sharpes on that face prove no structural kill for equity-class). Not contaminated.
- **Trial-labor W1..W14 (incl. the queued W14 万人波)**: exit face = explicit 8-choice `AXIS_EXITS` axis (`template_default` is one legitimate drawn choice = measured-by-design). Not contaminated. **W14 holiday burn is safe to fire.**
- **LOWAMP-P1**: the only judged batch that combined (i) zero exit keys, (ii) bond-class low-amplitude instruments, (iii) ALWAYS-ON family semantics. Sole blast-radius member. The 2000 nulls and 500 sensitivity draws share the same hybrid face (same `run_cell_portfolio` glue) — internally consistent family-vs-null comparison, but both measure the hybrid, not the family.
- Sibling engine consumers (exclusion_marginal_scan / cross_start_robustness / aggressive_lab) use different glue (own sim machinery / marks harness), out of radius.

## Adjudication analysis (governance decision — NOT self-service)

**The verdict measured the wrong face.** The frozen prereg contains an internal contradiction: §3 family definition says "ALWAYS-ON (no regime gate, no confirmation); daily rebalance, weights set at entry, never resized" — but under the engine's frozen default exit stack an always-on position cannot exist (25-day hard limit; 12-day/2% decay gate). The execution sentence ("engine-canonical T+1, frozen exit priority") made the defaults binding, and the burn faithfully measured that hybrid. Judged outputs are exact (Leg A), so this is a **specification-face defect, not an instrument defect**.

- **Option VOID (auditor recommendation)**: face-validity grounds — the prereg's α-mechanism sentence (ALWAYS-ON family) is the thing under test and it is contradicted by the burned execution face; prereg-intent discipline gives the family-definition sentence precedence when a frozen prereg self-contradicts. Consequences (GM/CEO action, not self-service): trials ledger 368,797 rollback (+2,008 n_eff absorbed by skill_line_v2), watchlist ①-exit and grammar-band consumption revert, verdict → void-with-face-note (not deleted — the hybrid measurement itself is valid science about the default stack's interaction with low-amp instruments). The family's intended face per Legs B/C = +15.9%/Sharpe +1.16 — **the low-amp family is NOT judged-negative as designed** and re-enters supply via a NEW prereg with an explicit exit axis (trial-labor AXIS_EXITS pattern), evidence_cutoff unchanged.
- **Option STANDS**: letter-of-law grounds — the prereg froze "frozen exit priority" verbatim; the house engine canon is part of every judged face; the family genuinely dies under the default stack (a real, reproducible finding: always-on bond sleeves are incompatible with the untuned house exit rules). Then the correct follow-up is the same new prereg with an explicit exit axis, and the E1 flag resolves as "reconciled, no defect, face retained".
- **Either way**: the E1 integrity flag resolves (gap fully reconciled, no measurement-instrument defect); the consumption warnings published at r492 were the correct protective action; no re-run of the frozen batch under either option (zero-burn amendment lineage: the NEW prereg is a new batch, not a rerun).

## What this audit did NOT do

No verdict flip, no ledger write, no watchlist edit, no registry write, no re-run of any frozen batch, no engine file touch (read-only audit per iron law). Verdict stays `judged-negative` + UNDER REVIEW until GM/CEO rule on VOID vs stands.
