import subprocess, json

# original registration shape at r598 landing
out = subprocess.run(["git", "show", "4e916d599:results/runnable_pool.json"],
                    capture_output=True, text=True, encoding="utf-8",
                    errors="replace").stdout
i = out.find('"FUND-VALUE-P1-NULLS"')
j = out.rfind('{', 0, i)
depth = 0; k = j
while k < len(out):
    if out[k] == '{': depth += 1
    elif out[k] == '}':
        depth -= 1
        if depth == 0: break
    k += 1
print("=== V entry at r598 landing (original registration) ===")
print(out[j:k+1])

# full current Q block tail (fields after the 1400-char truncation)
raw = open('results/runnable_pool.json', encoding='utf-8', newline='').read()
i = raw.find('"FUND-QUALITY-P1-NULLS"')
j = raw.rfind('{', 0, i)
depth = 0; k = j
while k < len(raw):
    if raw[k] == '{': depth += 1
    elif raw[k] == '}':
        depth -= 1
        if depth == 0: break
    k += 1
qb = raw[j:k+1]
print("=== current Q entry TAIL (last 900 bytes) ===")
print(qb[-900:])
