import subprocess, io

out = io.open(r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\results\_r1029bma_d19_tail.txt", "w", encoding="utf-8")
for p, n in [("docs/decisions.md", 40), ("docs/orders.md", 30)]:
    r = subprocess.run(["git", "-C", "C:/Users/sjs20/Desktop/FluxGroup", "show", "origin/main:" + p],
                       capture_output=True)
    t = r.stdout.decode("utf-8", errors="replace")
    lines = t.splitlines()
    out.write("=" * 20 + " " + p + " tail " + str(n) + " " + "=" * 20 + "\n")
    out.write("\n".join(lines[-n:]) + "\n")
out.close()
print("OK")
