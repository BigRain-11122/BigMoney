import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

n1 = open("scripts/perpetual_faces_n1.py", "rb").read().decode("utf-8")
j = n1.find('39: {"batch"')
k = n1.find("W39 materializer face")
k2 = n1.find("# --- T-141 s2 lane face", k)
print("=== WAVE_CONFIGS W39 FULL ROW ===")
print(n1[j:j + 1000])
print("=== materializer face block (end boundary) ===")
print(n1[k2 - 1500:k2])

law = open("research/PERPETUAL_N1_W39_PREREG.md", "rb").read().decode("utf-8")
print("=== W39 prereg lines 49-68 ===")
for i, l in enumerate(law.splitlines()[48:68], start=48):
    print(i, "|", l[:170])
