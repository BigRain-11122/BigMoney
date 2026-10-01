import subprocess

R = "C:/Users/sjs20/Desktop/FluxGroup/quant/bmoney".replace("bmoney", "bigmoney")
for rev in ("43f69b5cf", "fbb0c49a0", "979e483a2"):
    raw = subprocess.check_output(
        ["git", "-C", R, "show", f"{rev}:results/runnable_pool.json"])
    head = raw[:60]
    print(rev, "len", len(raw), "crlf", raw.count(b"\r\n"),
          "nl", raw.count(b"\n"), "head:", head[:50])
