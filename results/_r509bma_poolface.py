import subprocess

R = "C:/Users/sjs20/Desktop/FluxGroup/quant/bmoney".replace("bmoney", "bigmoney")
raw = subprocess.check_output(["git", "-C", R, "show",
                               ":2:results/runnable_pool.json"])
print("origin side: len", len(raw), "| lf:", raw.count(b"\n"),
      "| crlf:", raw.count(b"\r\n"))
print("head:", raw[:90])
b = open(R + "/results/runnable_pool.json", "rb").read()
print("resolved: len", len(b), "| crlf:", b.count(b"\r\n"),
      "| lf:", b.count(b"\n"), "| ends-nl:", b.endswith(b"\n"))
print("head:", b[:90])
