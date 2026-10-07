import subprocess, re, io
b = subprocess.run(["git", "show", "59fde9319:results/_r819bma_w172_freeze_edits.py"],
                  capture_output=True).stdout
t = b.decode("utf-8")
i = t.find("malformed")
io.open(r"results\_r822bma_r819_scan_ref.txt", "w", encoding="utf-8", newline="").write(
    t[max(0, i - 500):i + 900])
print(t[max(0, i - 500):i + 900])
