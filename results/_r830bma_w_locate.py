import io, re
t = io.open("CODELY.md", encoding="utf-8").read()
lines = t.split("\n")
for i, l in enumerate(lines):
    if l.startswith("- [") and len(l) > 150:
        print(i, len(l), "B |", re.sub(r"[^\x20-\x7e]", ".", l[:60]))
