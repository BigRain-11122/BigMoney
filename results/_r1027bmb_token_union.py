import json, subprocess

def get(stage):
    b = subprocess.run(["git", "show", f":{stage}:results/token_usage.json"], capture_output=True)
    return json.loads(b.stdout.decode("utf-8", "replace"))

head = get(2)   # origin/HEAD side (bm-c r1120 snapshot 15:30:52)
mine = get(3)   # my stash side (r1026 snapshot 15:45:56)

u = dict(mine)  # base = mine (bm-b own run: generated/per_round_context/delta_vs_prev)
machines = {}
for k in sorted(set(head["machines"]) | set(mine["machines"])):
    if k == "default":
        machines[k] = mine["machines"][k]      # bm-b own face -> mine (r1026 row included)
    else:
        machines[k] = head["machines"].get(k) or mine["machines"].get(k)  # other machines -> origin side (r1008 law)
u["machines"] = machines
u["total_state_tokens_est"] = sum(v.get("state_tokens_est", 0) for v in machines.values())
u["total_report_tokens_est"] = sum(v.get("report_tokens_est", 0) for v in machines.values())

out = json.dumps(u, ensure_ascii=False, indent=1)
with open("results/token_usage.json", "w", encoding="utf-8", newline="\n") as f:
    f.write(out + "\n")
json.load(open("results/token_usage.json", encoding="utf-8"))  # round-trip verify
print("union written; machines:", sorted(machines), "| totals:", u["total_state_tokens_est"], u["total_report_tokens_est"])
