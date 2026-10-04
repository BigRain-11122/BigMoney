import re
src = open("results/_r699bma_merge_resolve.py", encoding="utf-8").read()
m = re.search(r"JSON_FACES\s*=\s*\[(.*?)\]", src, re.S)
print("--- JSON_FACES ---")
for x in re.findall(r'"([^"]+)"', m.group(1)):
    print(x)
m2 = re.search(r"JSONL_UNION_FACES\s*=\s*\[(.*?)\]", src, re.S)
print("--- JSONL_UNION_FACES ---")
for x in re.findall(r'"([^"]+)"', m2.group(1)):
    print(x)
