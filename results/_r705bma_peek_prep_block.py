"""r705 bm-a: dump raw-text JUDGE-PREP pool block (surgery anchor pre-read)."""
raw = open("results/runnable_pool.json", encoding="utf-8", newline="").read()
i = raw.find('"PERPETUAL-N2-W15-JUDGE-PREP"')
assert i >= 0, "entry id not found"
# block ends at the next entry id or pool tail
j = raw.find('"PERPETUAL-', i + 10)
j2 = raw.find('"id"', i + 10)
end = min(x for x in (j, j2, len(raw)) if x > 0)
print("entry id at char", i, "| next id at", end)
print(raw[i - 60:end][:3200])
