tmp = open("results/_r433bma_rr.txt", encoding="utf-8").read()
if not tmp.endswith("\n"):
    tmp += "\n"
with open("logs/iteration-loop/round_reports-bm-a.md", "a", encoding="utf-8", newline="") as f:
    f.write(tmp)
chk = open("logs/iteration-loop/round_reports-bm-a.md", encoding="utf-8").read()
assert "r433 | 供给动作执行" in chk[-1500:], "rr append verify failed"
assert "鎴" not in chk[-1500:], "mojibake marker in rr tail"
print("round report appended ok")
