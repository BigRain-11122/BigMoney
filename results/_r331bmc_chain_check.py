import json

w18 = json.load(open(r"results/perpetual_faces/n1_w18_results.json", encoding="utf-8"))
w19 = json.load(open(r"results/perpetual_faces/n1_w19_results.json", encoding="utf-8"))
tl18 = w18.get("trials_ledger", {})
tl19 = w19.get("trials_ledger", {})
print("W18 K=", w18.get("K"), "total=", tl18.get("total"), "prev=", tl18.get("prev_total"), "batch=", tl18.get("batch_name"), "cut=", w18.get("evidence_cutoff"))
print("W19 K=", w19.get("K"), "total=", tl19.get("total"), "prev=", tl19.get("prev_total"), "batch=", tl19.get("batch_name"), "cut=", w19.get("evidence_cutoff"))
print("W19 mu=", w19.get("merged_mu"), "sigma=", w19.get("merged_sigma"))
