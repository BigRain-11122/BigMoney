import io
mat = io.open(r"results\_r822bma_w173_probe_n1_mat.txt", encoding="utf-8", newline="").read()
i = mat.find("395_204..395_403")
print("occurrence at", i)
print("CONTEXT:", repr(mat[i - 120:i + 80]))
old = "# 395_204 and lands 395_204..395_403, hops=1, non-rotational"
print("b42 old count:", mat.count(old))
old2 = "# 395_204 and lands 395_204..395_403, hops=1, non-rotational\r\n"
print("with CRLF count:", mat.count(old2))
# check the line break form after the match
j = mat.find(old)
print("AFTER:", repr(mat[j + len(old):j + len(old) + 30]))
