"""r688 bm-a S3d-pre: dump SHARD-2 entry raw text to learn field layout."""
import re

text = open("results/runnable_pool.json", encoding="utf-8").read()
m = re.search(r'\{\s*"id":\s*"MASS-TRIAL-W3-JUDGE-SHARD-2"', text)
start = m.start()
depth = 0
i = start
while True:
    c = text[i]
    if c == "{":
        depth += 1
    elif c == "}":
        depth -= 1
        if depth == 0:
            break
    i += 1
end = i + 1
print(text[start:end][:3000])
