"""R318 bm-b: T-89/T-90 ticket progress entries (harvest finalize receipts)."""
import json

P89 = ("fleet/tasks/T-2026-09-26-89-P1.json")
P90 = ("fleet/tasks/T-2026-09-27-90-P1.json")

d = json.load(open(P89, encoding="utf-8-sig"))
d["progress_r318_bmb"] = (
    "R318 bm-b: slice-1 HARVEST COMPLETE -- T-93 receiver face landed 30/30 "
    "dual-manifest verified (80,984,350B), 18/18 shards in place, finalize "
    "PASS: G-ANCHOR 22/22 byte-reconciled, G-PANEL/G-CENSUS legacy n=1256 "
    "27,632 cells + deep n=1506 33,132 cells, trials 60,764+2,762=63,526 "
    "(ledger total 269,975); outputs results/prospect_regime_segments.json + "
    "shortline CSV 528 rows; pooled 6m base legacy 0.5134/deep 0.4122 (both "
    "< 0.70 line), attack candidates 0/22 both axes (top legacy bull "
    "DUCK-CE 0.4809), roles bear/chop only; MARKET_STAGE_TABLE.md "
    "auto-refresh fired (22x2 segment rows + change log). REMAINING: "
    "slice-3 attack-corps supply acceleration review memo (proposal to GM, "
    "O-0752 sec.2; now evidence-hardened: PROSPECT pool 0/22 candidates, "
    "T-90 ring4 seat vacancy face) -- exact continuation point.")
json.dump(d, open(P89, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

d = json.load(open(P90, encoding="utf-8-sig"))
d["progress_r318_bmb"] = (
    "R318 bm-b: HARVEST VERDICT LANDED (x2 9/9 done + T-93 shards received) "
    "-- finalize PASS all gates (G-V3 leg1/leg2, 6 anchors, G-REPRO 12/12 "
    "bit-equal, overlay both axes 99.1s): chain_win=False, j_target_pass=False "
    "(all 12 J-TARGET cells fail beat_gt_b; worst: legacy x2 24m A1 0.0228 vs "
    "B 0.5758, min_dd -0.3194); J-L half-ladder PASS both faces (base uplift "
    "0.0363/0.0362, x2 0.0656/0.0312, dd ok); disposition = J-C1 pass + "
    "J-C2 fail = no routing value (member-book effect) read separately. "
    "Four-ring localization: ring1 temperature day_disagreement 0.7304 "
    "(1032 days, disagreement starts -0.0203 vs agreement -0.0164 = version "
    "choice no rescue); ring2 routing NEGATIVE in ALL regimes (A1-D base "
    "bear -0.0613/bull -0.0528/chop -0.0795; x2 all ~-0.12); ring3 friction "
    "45.57 switches mean, -0.0665pp base/-0.1266pp x2, share of gross "
    "-1.30/-3.12 (A1' zero-fee counterfactual still loses); ring4 seat "
    "attack corps 0 live, green starts -0.0847 vs other -0.0987. Verdict "
    "face results/decision_chain_e2e.json + shortline CSV 48 rows. "
    "REMAINING: deliverable-4 monthly four-piece chain-health section "
    "wiring (verdict face now exists; broken-ring scan consumable) -- "
    "exact continuation point.")
json.dump(d, open(P90, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("T-89 + T-90 progress_r318_bmb written")
