"""r246 bm-b: register T-78 family post_review claims (O-2115 chain closure).

Gap being closed: progress_r241/r242/r244/r245 all annotated
"review=post_review pending (O-2115 chain)" but the claims were never
encoded into results/post_review_criteria.json -- the registry the
deterministic reviewer (Tools/post_review.py) sweeps. Dangling "pending"
= the chain can never sweep them. This script appends the 4 T-78 rows
(overlay batch / winner wiring / grid sleeve batch / grid paper wiring)
with machine-verifiable checks drawn from the pre-frozen faces
(ticket spec discipline + prereg sec.4/10/8, frozen pre-run per canon)
plus product-field existence/consistency re-derivation (T-72 row pattern).

Idempotent: skips ids already present. Zero network, zero engine.
"""
import json

CRITERIA = r"results\post_review_criteria.json"

ROWS = [
    {
        "id": "T-78-EXIT-OVERLAY-P1",
        "claim": "T-78 s2+s3: engine dd_control additive flag (None=legacy byte-equal, entry-size face, hysteresis, selftest 5/5) + EXIT-OVERLAY-P1 paired-judgment bench run: 6 WIN / 18 REJECT honest negatives reported (anchor repro 6/6 OK, ledger 184826->184856 N_eff=30, evidence_cutoff 2026-09-24, prereg sec.7/8 backfilled same round)",
        "claim_source": "T-2026-09-26-78 spec discipline (b) controlled comparison + research/EXIT_OVERLAY_P1.md prereg frozen pre-run (r240 commit 224caafb; sec.4 dual-face non-hurt gate) -- delivered r241 commit afee27e5",
        "status": "closed",
        "checks": [
            {"kind": "file_exists", "args": ["research/EXIT_OVERLAY_P1.md"]},
            {"kind": "file_exists", "args": ["results/exit_overlay_p1.json"]},
            {"kind": "json_field", "args": ["results/exit_overlay_p1.json", "verdict.n_win", "6"]},
            {"kind": "json_field", "args": ["results/exit_overlay_p1.json", "verdict.n_reject", "18"]},
            {"kind": "json_field", "args": ["results/exit_overlay_p1.json", "anchor_ok", "True"]},
            {"kind": "json_field", "args": ["results/exit_overlay_p1.json", "evidence_cutoff", "2026-09-24"]},
            {"kind": "json_field", "args": ["results/exit_overlay_p1.json", "trials_ledger.total", "184856"]},
            {"kind": "git_log_file", "args": ["engine/backtester.py", "dd_control"]},
        ],
        "evidence_pointer": "results/exit_overlay_p1.json",
        "due": "delivered 2026-09-26 r241",
    },
    {
        "id": "T-78-WINNER-WIRING",
        "claim": "T-78 s4 winner wiring: 3 members registered with maximal WIN cells (COMPOSITE-CE-01 ov_tp_ladder; COMPOSITE-CE-02 + ENGULF-CE-01 ov_full), registered evidence re-derived same round at evidence_cutoff 09-22 per prereg sec.10, smoke anchor gates reflect wired configs (25/25 incl anchor COMPOSITE-CE-01 IS 0.4696/OOS 1.7479), x2 margins honest (C01 0.1238 ok; C02 0.0491 + ENGULF 0.0143 probation disclosed)",
        "claim_source": "research/EXIT_OVERLAY_P1.md sec.10 wiring rule (frozen pre-run) + T-78 progress_r242 (commit f95adf89, rebase re-anchor d65f2d4a) -- smoke 25/25 anchor-gate face re-derives wired configs every round",
        "status": "closed",
        "checks": [
            {"kind": "json_field", "args": ["firm/traders/COMPOSITE-CE-01.json", "params.take_profit_levels.0", "0.05"]},
            {"kind": "json_field", "args": ["firm/traders/COMPOSITE-CE-01.json", "backtest.out_sample.sharpe", "1.7479"]},
            {"kind": "json_field", "args": ["firm/traders/COMPOSITE-CE-02.json", "backtest.out_sample.sharpe", "1.6392"]},
            {"kind": "json_field", "args": ["firm/traders/COMPOSITE-CE-02.json", "params.trailing_stop_activate", "0.03"]},
            {"kind": "json_field", "args": ["firm/traders/ENGULF-CE-01.json", "backtest.out_sample.sharpe", "0.3835"]},
            {"kind": "json_field", "args": ["firm/traders/ENGULF-CE-01.json", "paper.x2_watch.margin", "0.0143"]},
            {"kind": "file_contains", "args": ["firm/traders/COMPOSITE-CE-02.json", "ov_full"]},
            {"kind": "file_contains", "args": ["firm/traders/ENGULF-CE-01.json", "ov_full"]},
        ],
        "evidence_pointer": "firm/traders/COMPOSITE-CE-01.json (+COMPOSITE-CE-02, ENGULF-CE-01)",
        "due": "delivered 2026-09-26 r242",
    },
    {
        "id": "T-78-GRID-SLEEVE-P1",
        "claim": "T-78 s5a+s5b (unlock-4, T-73 s3 slice consumed-by-T-78): GRID_SLEEVE_P1 prereg frozen pre-run + engine/grid_sleeve.py v1 additive machinery (selftest 8/8, excl-today band law) + batch run honest negative: 0/5 science survivors, 0 paper candidates (G1'v2 all-fail vs skill_line 1.1634; GATE-A 3/5 chop face; K=50 nulls cell_beats_null_max=false 5/5; x2 stress degrades all), ledger 185738+60=185798, SEED_REGISTRY 62_500 pre-registered",
        "claim_source": "research/GRID_SLEEVE_P1.md frozen pre-run (r243 commit bd42a609) + T-78 progress_r244 (commit eab79ed5) + CEO O-20260926-0958 unlock-4",
        "status": "closed",
        "checks": [
            {"kind": "file_exists", "args": ["research/GRID_SLEEVE_P1.md"]},
            {"kind": "file_exists", "args": ["results/grid_sleeve_p1.json"]},
            {"kind": "file_exists", "args": ["research/grid_sleeve_p1_results.csv"]},
            {"kind": "json_field", "args": ["results/grid_sleeve_p1.json", "survivors_science", "[]"]},
            {"kind": "json_field", "args": ["results/grid_sleeve_p1.json", "paper_candidates", "[]"]},
            {"kind": "json_field", "args": ["results/grid_sleeve_p1.json", "evidence_cutoff", "2026-09-24"]},
            {"kind": "json_field", "args": ["results/grid_sleeve_p1.json", "trials_ledger.total", "185798"]},
            {"kind": "git_log_file", "args": ["engine/grid_sleeve.py", "s5a"]},
        ],
        "evidence_pointer": "results/grid_sleeve_p1.json",
        "due": "delivered 2026-09-26 r243-r244",
    },
    {
        "id": "T-78-GRID-PAPER-WIRING",
        "claim": "T-78 s5c: GRID-* 5-cell paper observation-account family wired (scripts/grid_paper.py run/selftest hermetic 6/6 + E2E results/_r245bmb_grid_paper_e2e.py ALL PASS; honest labels loaded per account from frozen batch product results/grid_sleeve_p1.json single truth source zero hand-copy; panel-cutoff idempotency real-run honest no-op exit 0 with panel cutoff 09-24 == evidence_cutoff; S6 chain leg inserted after alloc_paper); marks start 2026-09-28 first bar strictly after evidence_cutoff",
        "claim_source": "research/GRID_SLEEVE_P1.md sec.8 GRID paper family contract (frozen pre-run) + CEO O-20260926-0958 'GRID accounts paper-wired' + T-78 progress_r245 (commit c06d9284)",
        "status": "closed",
        "checks": [
            {"kind": "file_exists", "args": ["scripts/grid_paper.py"]},
            {"kind": "file_exists", "args": ["results/_r245bmb_grid_paper_e2e.py"]},
            {"kind": "file_contains", "args": ["scripts/grid_paper.py", "grid_sleeve_p1.json"]},
            {"kind": "file_contains", "args": ["Tools/iteration_prompt.txt", "grid_paper.py run"]},
            {"kind": "file_contains", "args": ["Tools/iteration_prompt.txt", "T-78 s5c"]},
        ],
        "evidence_pointer": "scripts/grid_paper.py",
        "due": "delivered 2026-09-26 r245; marks window opens 2026-09-28 (forward observation, not a claimed result)",
    },
]


def main() -> int:
    d = json.load(open(CRITERIA, encoding="utf-8-sig"))
    items = d["items"]
    have = {it.get("id") for it in items}
    added = [r for r in ROWS if r["id"] not in have]
    if not added:
        print("register: all 4 T-78 rows already present -- no-op")
        return 0
    items.extend(added)
    with open(CRITERIA, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print(f"register: appended {len(added)} rows -> {[r['id'] for r in added]}")
    print(f"register: registry total {len(items)} items")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
