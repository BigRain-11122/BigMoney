raw = open(r"results\runnable_pool.bm-b.json", "rb").read()
print("crlf", raw.count(b"\r\n"), "lf_total", raw.count(b"\n"))
i = raw.find(b"N2U3-ALPHAGEN-RL-P1-LEG3-TRAIN")
seg = raw[i:i + 2500]
for line in seg.split(b"\n"):
    if b'status' in line or b"note" in line:
        print(repr(line))
