tmp = open("results/_r433bma_mem.txt", encoding="utf-8").read()
with open("CODELY.md", "a", encoding="utf-8", newline="") as f:
    f.write(tmp)
chk = open("CODELY.md", encoding="utf-8").read()
assert "r433 bm-a] 同门换用法反向证伪律" in chk, "append verify failed"
assert "鎴" not in chk[-1000:], "mojibake marker found in tail"
print("CODELY.md appended ok, new size:", len(chk.encode("utf-8")), "bytes")
