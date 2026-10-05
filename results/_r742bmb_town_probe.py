# r742 bm-b probe v2: town.html building registry vs org_chart v2
import io, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
t = open("town.html", encoding="utf-8").read()

# 1) JS name fields
for m in re.finditer(r"name\s*:\s*'([^']{2,24})'", t):
    print("NAME:", m.group(1))

# 2) draw functions and their info-title mapping
for m in re.finditer(r"function (draw\w+)\(([^)]*)\)\s*\{\s*//?\s*([^\n]*)", t):
    print("FN:", m.group(1), "|", m.group(3).strip()[:60])

# 3) BLD / building list config
i = t.find("const BLD")
if i < 0:
    i = t.find("BLD =")
print("--- BLD config region ---")
print(t[i:i+1500] if i >= 0 else "BLD not found")
