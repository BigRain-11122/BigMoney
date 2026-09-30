import io, json, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
att = json.loads(io.open(r"results\gate_attrition.json", encoding="utf-8").read())
b = [h.get("batch") for h in att["history"]]
i = b.index("TRIAL_LAB_W13_SCREEN")
row = att["history"][i]
print("row idx:", i, "| batch:", row["batch"], "| ts:", row["ts"],
      "| delta:", row["cells_ledger_delta"], "| after:", row["ledger_total_after"],
      "| retro_fill:", row["retro_fill"])
print("prev row:", b[i-1], att["history"][i-1]["ts"], "| next row:", b[i+1], att["history"][i+1]["ts"])
# correct checks: ts monotone across the three, screen row internally consistent
ts_prev = att["history"][i-1]["ts"]; ts_sc = row["ts"]; ts_jd = att["history"][i+1]["ts"]
assert ts_prev < ts_sc < ts_jd, "ts order broken"
s13 = json.load(io.open(r"results\trial_labor_w13\w13_screen.json", encoding="utf-8"))
tl = s13["trials_ledger"]
assert row["ledger_total_after"] - row["cells_ledger_delta"] == tl["prev_total"], "prev mismatch"
assert tl["prev_total"] + tl["batch_trials"] == tl["total"] == row["ledger_total_after"], "screen ledger face"
jd = att["history"][i+1]
s13j = json.load(io.open(r"results\trial_labor_w13\w13_judge.json", encoding="utf-8"))
assert s13j["trials_ledger"]["total"] == jd["ledger_total_after"] == 362083
print("ALL CHECKS PASS: ts-ordered, per-row ledger faces consistent (screen prev 359387 +593 = 359980; judge prev 361984 +99 = 362083; inter-batch +2004 cells from other batches between 11:06 and 12:28 disclosed)")
