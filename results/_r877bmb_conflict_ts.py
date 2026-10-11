import re
t = open("results/update_status.json", encoding="utf-8", errors="replace").read()
# conflict file: show the ts lines on both sides of conflict markers
chunks = t.split("<<<<<<<")
for c in chunks[1:]:
    side = c.split("=======")
    ours = re.findall(r'"[^"]*(?:ts|time|at|date)[^"]*":\s*"[^"]*"', side[0])
    theirs = re.findall(r'"[^"]*(?:ts|time|at|date)[^"]*":\s*"[^"]*"', side[1]) if len(side) > 1 else []
    print("OURS(origin-side):", ours[:2])
    print("THEIRS(my-side):  ", theirs[:2])
    print("---")
