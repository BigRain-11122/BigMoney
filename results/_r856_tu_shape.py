import re

s = open("results/token_usage.json", encoding="utf-8", errors="replace").read()
ours = re.search(r'<<<<<<<.*?\n(.*?)\n=======', s, re.S)
theirs = re.search(r'=======\n(.*?)\n>>>>>>>', s, re.S)
for name, blk in [("OURS(bm-c)", ours), ("THEIRS(mine)", theirs)]:
    if not blk:
        print(name, "NO BLOCK")
        continue
    txt = blk.group(1)
    lines = txt.count("\n") + 1
    print(f"{name}: {lines} lines, {len(txt)} bytes")
    for key in ("history", "machines", "per_machine", "daily", "entries"):
        m = re.search(rf'"{key}"', txt)
        if m:
            print(f"  has key: {key}")
    # show first 3 lines
    print("  head:", " | ".join(txt.split("\n")[:3])[:200])
