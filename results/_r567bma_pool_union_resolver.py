import subprocess
# union-resolve the append-only jsonl conflict (r294 domain law: dedupe CONFLICT REGION only)
ours = subprocess.check_output(["git", "show", ":2:results/pool_core_samples.jsonl"],
                               encoding="utf-8").splitlines()
theirs = subprocess.run(["git", "show", ":3:results/pool_core_samples.jsonl"],
                         capture_output=True).stdout.decode("utf-8").splitlines()
base = subprocess.check_output(["git", "show", ":1:results/pool_core_samples.jsonl"],
                               encoding="utf-8").splitlines()
base_set = set(base)
seen = set(base)
out = []
for line in ours + theirs:
    if line in base_set:
        continue
    if line in seen:
        continue
    seen.add(line)
    out.append(line)
merged = base + out
with open("results/pool_core_samples.jsonl", "w", encoding="utf-8", newline="") as f:
    f.write("\n".join(merged) + ("\n" if merged else ""))
print(f"base {len(base)} + ours-new {len([l for l in ours if l not in base_set])} "
      f"+ theirs-new {len([l for l in theirs if l not in base_set])} "
      f"-> merged {len(merged)} (dedupe within conflict region only, base preserved verbatim)")
