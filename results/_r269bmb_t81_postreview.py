"""r269 bm-b: register post_review rows for T-81 delivered chain (O-2115 / r246
law -- delivered slices' acceptance face must be machine-encoded; checks
anchor ONLY to pre-frozen preregs + deterministic product fields, per r256
reanchor law: no hot-file git checks, no event-dependent fields pinned).

Four slices delivered r254/r255/r257/r265 (chain complete, hook armed):
  T-81-PROFILE-CARDS         (slice-1, r254)
  T-81-L3-ACTIVATION-EVIDENCE(slice-2, r255)
  T-81-SAMPLE-SCIENCE        (slice-3, r257)
  T-81-LANDING-HOOKS         (slice-4, r265)

Byte-face mirror (R254/R255/R257 five-face law, probed from HEAD blob):
no BOM, LF-only, no trailing newline, ensure_ascii=False, indent=1,
top-level key order preserved on load-modify-dump.
"""
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "results", "post_review_criteria.json")

S1 = ("T-81 slice-1 profile cards delivered (O-20260926-1342 sec.3): prereg "
      "research/PROFILE_CARDS_P1.md v1.0.1 frozen pre-run + "
      "scripts/strategy_scorecard.py build_profile_cards extension + face "
      "results/strategy_scorecard.json profile_cards (17 cards, self-consistency "
      "gate PASS 17/17, conventions with_day1 x10 / without_day1 x7 disclosed, "
      "empty activation sets fail-closed x3); read-derived from T-79 retro "
      "ledgers, ledger +0 (read-only marks lane)")
S2 = ("T-81 slice-2 L3 activation-table evidence-drive delivered: prereg "
      "research/L3_ACTIVATION_EVIDENCE.md frozen pre-run (sleeve->member mapping, "
      "evidence never adds routing) + market_clock_call.py L3 evidence faces "
      "wired to results/market_clock/call_latest.json l3_evidence (evidence_face "
      "= strategy_scorecard profile_cards); evidence upgrade of MARKET_CLOCK_COMBO "
      "s0 SLEEVE_TABLE per O-1342 sec.3")
S3 = ("T-81 slice-3 sample science delivered: prereg research/SAMPLE_SCIENCE_P1.md "
      "v1.0 frozen pre-run (four-must per state+heat cell = oos_trades / "
      "covered_years / independent_regime_windows / ci95 via science_gates "
      "bootstrap_ci_sharpe verbatim seed; ZERO verdict-line change, CI = pure "
      "disclosure face) + scripts/strategy_scorecard.py _four_must_cell/"
      "_sample_science_block + card-level sample_science blocks in "
      "results/strategy_scorecard.json (selftest 10/10)")
S4 = ("T-81 slice-4 landing hooks delivered: prereg research/LANDING_HOOKS_P1.md "
      "v1.0 frozen pre-run commit 668cbd5e (freeze precedes run commit 8b392771, "
      "R99 order law; three-family landing watch CN/GRID/WILD, landing criteria = "
      "each family's own frozen-batch verdict faces verbatim, landing != "
      "activation) + landing_hooks() readout face in strategy_scorecard (hook "
      "armed, n_landings 0, re-derived every S6 refresh; L3 no-member sleeve "
      "structural labels cite this face)")

ROWS = [
    {"id": "T-81-PROFILE-CARDS",
     "claim": S1,
     "claim_source": ("fleet/tasks/T-2026-09-26-81-P1.json spec slice-1 "
                      "(frozen at claim r252) + research/PROFILE_CARDS_P1.md "
                      "v1.0.1 prereg frozen pre-run (r254)"),
     "status": "claimed",
     "checks": [
         {"kind": "file_exists", "args": ["research/PROFILE_CARDS_P1.md"]},
         {"kind": "file_contains",
          "args": ["research/PROFILE_CARDS_P1.md",
                   "append_ledger('PROFILE-CARDS-P1', 0"]},
         {"kind": "file_contains",
          "args": ["scripts/strategy_scorecard.py", "def build_profile_cards("]},
         {"kind": "json_field",
          "args": ["results/strategy_scorecard.json", "profile_cards.batch",
                   "PROFILE-CARDS-P1"]},
         {"kind": "json_field",
          "args": ["results/strategy_scorecard.json", "profile_cards.ticket",
                   "T-2026-09-26-81"]},
         {"kind": "json_field",
          "args": ["results/strategy_scorecard.json", "profile_cards.prereg",
                   "research/PROFILE_CARDS_P1.md"]},
         {"kind": "json_field",
          "args": ["results/strategy_scorecard.json",
                   "profile_cards.prereg_sha256_16", "1d72d4b67ea07e34"]},
         {"kind": "json_field",
          "args": ["results/strategy_scorecard.json",
                   "profile_cards.summary.n_cards", "17"]},
     ]},
    {"id": "T-81-L3-ACTIVATION-EVIDENCE",
     "claim": S2,
     "claim_source": ("fleet/tasks/T-2026-09-26-81-P1.json spec slice-2 "
                      "(frozen at claim r252) + research/L3_ACTIVATION_EVIDENCE.md "
                      "prereg frozen pre-run (r255)"),
     "status": "claimed",
     "checks": [
         {"kind": "file_exists", "args": ["research/L3_ACTIVATION_EVIDENCE.md"]},
         {"kind": "file_contains",
          "args": ["research/L3_ACTIVATION_EVIDENCE.md",
                   "append_ledger('L3-ACTIVATION-EVIDENCE', 0"]},
         {"kind": "json_field",
          "args": ["results/market_clock/call_latest.json",
                   "l3_evidence.prereg", "research/L3_ACTIVATION_EVIDENCE.md"]},
         {"kind": "json_field",
          "args": ["results/market_clock/call_latest.json",
                   "l3_evidence.prereg_sha256_16", "3304f84f60826cd6"]},
         {"kind": "json_field",
          "args": ["results/market_clock/call_latest.json",
                   "l3_evidence.evidence_face",
                   "results/strategy_scorecard.json profile_cards"]},
     ]},
    {"id": "T-81-SAMPLE-SCIENCE",
     "claim": S3,
     "claim_source": ("fleet/tasks/T-2026-09-26-81-P1.json spec slice-3 "
                      "(frozen at claim r252) + research/SAMPLE_SCIENCE_P1.md "
                      "v1.0 prereg frozen pre-run (r257)"),
     "status": "claimed",
     "checks": [
         {"kind": "file_exists", "args": ["research/SAMPLE_SCIENCE_P1.md"]},
         {"kind": "file_contains",
          "args": ["research/SAMPLE_SCIENCE_P1.md",
                   "append_ledger('SAMPLE-SCIENCE-P1', 0"]},
         {"kind": "file_contains",
          "args": ["scripts/strategy_scorecard.py", "def _four_must_cell("]},
         {"kind": "json_field",
          "args": ["results/strategy_scorecard.json",
                   "profile_cards.sample_science_prereg",
                   "research/SAMPLE_SCIENCE_P1.md"]},
         {"kind": "json_field",
          "args": ["results/strategy_scorecard.json",
                   "profile_cards.sample_science_prereg_sha256_16",
                   "d7ec6432cf40917d"]},
     ]},
    {"id": "T-81-LANDING-HOOKS",
     "claim": S4,
     "claim_source": ("fleet/tasks/T-2026-09-26-81-P1.json spec slice-4 "
                      "(frozen at claim r252) + research/LANDING_HOOKS_P1.md "
                      "v1.0 prereg frozen pre-run commit 668cbd5e (r265)"),
     "status": "claimed",
     "checks": [
         {"kind": "file_exists", "args": ["research/LANDING_HOOKS_P1.md"]},
         {"kind": "file_contains",
          "args": ["research/LANDING_HOOKS_P1.md",
                   "append_ledger('LANDING-HOOKS-P1', 0"]},
         {"kind": "file_contains",
          "args": ["scripts/strategy_scorecard.py", "def landing_hooks("]},
         {"kind": "json_field",
          "args": ["results/strategy_scorecard.json", "landing_hooks.batch",
                   "LANDING-HOOKS-P1"]},
         {"kind": "json_field",
          "args": ["results/strategy_scorecard.json", "landing_hooks.ticket",
                   "T-2026-09-26-81"]},
         {"kind": "json_field",
          "args": ["results/strategy_scorecard.json", "landing_hooks.prereg",
                   "research/LANDING_HOOKS_P1.md"]},
         {"kind": "json_field",
          "args": ["results/strategy_scorecard.json",
                   "landing_hooks.prereg_sha256_16", "a68933c6f2d1c0e2"]},
     ]},
]


def main():
    with io.open(PATH, encoding="utf-8") as fh:
        d = json.load(fh)
    ids = [r["id"] for r in d["items"]]
    for row in ROWS:
        assert row["id"] not in ids, "row already registered: " + row["id"]
        d["items"].append(row)
        print("registered", row["id"])
    # byte-face mirror: no BOM, LF, ensure_ascii=False, indent=1, no trailing \n
    with io.open(PATH, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)
    print("items=%d" % len(d["items"]))


if __name__ == "__main__":
    main()
