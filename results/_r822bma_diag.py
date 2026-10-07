import io, re
pfblk = io.open(r"results\_r822bma_w173_probe_pf_block.txt", encoding="utf-8", newline="").read()
entry = io.open(r"results\_r822bma_w173_probe_n1_entry.txt", encoding="utf-8", newline="").read()
mat = io.open(r"results\_r822bma_w173_probe_n1_mat.txt", encoding="utf-8", newline="").read()

print("== pf dump 'r818' occurrences ==")
for m in re.finditer(r".{30}r818.{20}", pfblk):
    print(repr(m.group(0)))
print("== mat dump 'w171_' count:", mat.count("w171_"))
for m in re.finditer(r".{25}w171_.{15}", mat):
    print(repr(m.group(0)))
print("== mat '395_204..395_403' count:", mat.count("395_204..395_403"))
for m in re.finditer(r".{35}395_204\.\.395_403.{10}", mat):
    print(repr(m.group(0)))
print("== mat 'MSG-1012' count:", mat.count("MSG-1012"))
print("== mat h10 area bytes ==")
i = mat.find("--no-verify; self-ack")
print(repr(mat[i:i + 320]))
print("== entry B-face split check ==")
j = entry.find("cross-window")
print(repr(entry[j:j + 260]))
