import json

w = json.load(open(r"results/perpetual_faces/n1_w20_results.json", encoding="utf-8"))
famA = w["families"]["A_random_engine_exit"]
famB = w["families"].get("B_random_entry_engine_exit", {})
sg = w.get("science_gates", {})
led = sg.get("ledger", {})
print("W20 A n=", famA.get("n"), "p95=", famA.get("full_sharpe_p95"), "p99=", famA.get("full_sharpe_p99"), "mu=", famA.get("full_sharpe_mu"))
print("W20 B n=", famB.get("n"), "p95=", famB.get("full_sharpe_p95"), "mu=", famB.get("full_sharpe_mu"))
print("ledger prev=", led.get("prev_total"), "batch=", led.get("batch_trials"), "total=", led.get("total"))
print("keys:", sorted(w.keys()))
print("cut=", w.get("evidence_cutoff"), "batch=", w.get("batch"))
