"""r383 bm-c W113 results re-fix: strip the double-appended ledger block +
skill faces from the UNPUBLISHED n1_w113_results.json (draft-not-committed =
refreshable per r576 law), so the one-pass finalize re-derives against the
true chain head (W112 total 610,948) instead of the phantom 613,148.
Root cause: a mid-window wave-complete materialization wrote the file with a
ledger block (prev 610,948 total 613,148) between our FF (20:19) and our
manual finalize (20:23:24); the n1 finalize lacks the pit-95
finalize_already_landed guard, so it appended ON TOP of that head ->
prev 613,148 / total 615,348 = W113 counted twice. Fix = re-finalize."""
import json

P = (r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\perpetual_faces"
     r"\n1_w113_results.json")
with open(P, encoding="utf-8") as f:
    d = json.load(f)
sg = d["science_gates"]
led = sg["ledger"]
assert led["batch"] == "PERPETUAL-N1-W113", led.get("batch")
assert led["prev_total"] == 613148 and led["total"] == 615348, led
del sg["ledger"]
assert "skill_line_v2_k_lift" in d
n_eff_wrong = d["skill_line_v2_k_lift"]["n_eff_held_equal"]
assert n_eff_wrong == 613148, n_eff_wrong
del d["skill_line_v2_k_lift"]
with open(P, "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, default=str)
print("stripped ledger+skill faces from unpublished draft; "
      "finalize will re-derive against true head 610,948")
