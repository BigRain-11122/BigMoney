# r670 bm-a: grammar-ledger row verification (append already landed; idempotent check only)
P = "research/TRIAL_GRAMMAR_LEDGER.md"
chk = open(P, "rb").read().decode("utf-8")
n = chk.count("THEME_JUDGE_P1")
assert n == 2, f"expect 2 (batch name + prereg file path), got {n}"
tail_row = [l for l in chk.splitlines() if "THEME_JUDGE_P1" in l][-1]
assert "judged_negative" in tail_row and "FORBIDDEN" in tail_row
assert "20585000" in tail_row and "12/20" in tail_row
print("grammar-ledger row verified in place (2 occurrences = name+path), tail row len:", len(tail_row))
