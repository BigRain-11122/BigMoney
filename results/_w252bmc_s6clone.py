import io
t = io.open(r"Tools\_r1048bmc_s6.py", encoding="utf-8").read()
t = t.replace("_r1048bmc_s6", "_r1049bmc_s6")
t = t.replace("r1048 bm-c S6 chain driver", "r1049 bm-c S6 chain driver")
t = t.replace("Friday 10:2x run", "Friday 10:5x run")
t = t.replace('log.write("r1045 bm-c S6 chain run', 'log.write("r1049 bm-c S6 chain run')
io.open(r"Tools\_r1049bmc_s6.py", "w", encoding="utf-8", newline="").write(t)
print("cloned", len(t))
