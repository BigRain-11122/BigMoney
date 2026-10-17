import hashlib

p = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\_ord_fresh.txt"
b = open(p, "rb").read()
print("sha1=" + hashlib.sha1(b).hexdigest())
t = b.decode("utf-8", "replace")
lines = t.splitlines()
print("total_lines=" + str(len(lines)))
for ln in lines[-14:]:
    print(ln.encode("unicode_escape").decode("ascii"))
