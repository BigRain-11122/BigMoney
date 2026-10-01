import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
n1 = open("scripts/perpetual_faces_n1.py", "rb").read().decode("utf-8")
k = n1.find("    # --- W39 materializer face")
k2 = n1.find("    # --- T-141 s2 lane face", k)
block = n1[k:k2]
print(block)
print("=== BLOCK LEN:", len(block))
