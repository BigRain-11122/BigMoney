import subprocess, os

GRP = r"K:\Fluxgroup\FluxGroup"
BM = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

def tail_lines(path, n):
    txt = subprocess.run(["git", "-C", GRP, "show", "origin/main:" + path], capture_output=True).stdout.decode("utf-8", "replace")
    lines = txt.splitlines()
    return lines[-n:], len(lines)

dec_tail, dec_n = tail_lines("docs/decisions.md", 40)
ord_tail, ord_n = tail_lines("docs/orders.md", 50)

out = []
out.append(f"=== decisions.md total {dec_n} lines, tail 40 ===")
out.extend(dec_tail)
out.append(f"=== orders.md total {ord_n} lines, tail 50 ===")
out.extend(ord_tail)

txt = "\n".join(out)
open(os.path.join(BM, "results", "_r984bmc_s05_tails.txt"), "w", encoding="utf-8").write(txt)
print(f"decisions {dec_n} lines / orders {ord_n} lines -> written to _r984bmc_s05_tails.txt")
