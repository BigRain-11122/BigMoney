import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

b = open("scripts/perpetual_faces.py", "rb").read().decode("utf-8")
i = b.find("39: {")
print("=== N1_BANDS W39 row tail (perpetual_faces.py) ===")
print(b[i:i + 500])
print("...has '40:' row already:", b.find("40: {") >= 0)

n1 = open("scripts/perpetual_faces_n1.py", "rb").read().decode("utf-8")
j = n1.find('39: {"batch"')
print("=== WAVE_CONFIGS W39 (perpetual_faces_n1.py) ===")
print(n1[j:j + 850])
k = n1.find("W39 materializer face")
print("=== selftest W39 materializer face ===")
print(n1[k - 250:k + 1400])

law = open("research/PERPETUAL_FACES.md", "rb").read().decode("utf-8")
m = law.find("W40+")
print("=== canon W39 row W40+ projection prose ===")
print(law[m - 100:m + 500])
s5 = law.find("## ")
print("=== canon headings ===")
for h in [x for x in law.splitlines() if x.startswith("## ")][:12]:
    print(repr(h[:60]))
