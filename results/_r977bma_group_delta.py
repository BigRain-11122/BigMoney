import subprocess, re

GIT = r"C:\Program Files\Git\cmd\git.exe"
GRP = r"C:\Users\sjs20\Desktop\FluxGroup"

def show(path):
    r = subprocess.run([GIT, "-C", GRP, "show", f"origin/main:{path}"], capture_output=True)
    return r.stdout.decode("utf-8", "replace")

dec = show("docs/decisions.md")
orders = show("docs/orders.md")

# decisions: extract rows from the recent window (2026-10-11..13) mentioning BigMoney/quant/bm-a
print("### decisions.md rows 10-11..10-13 mentioning BigMoney/quant/bm-a:")
for line in dec.splitlines():
    if re.search(r"2026-10-1[123]", line) and re.search(r"BigMoney|量化|bm-a|bigmoney", line, re.I):
        print(" D:", line[:400])

print("\n### decisions.md 派工通告板 section:")
m = re.search(r"派工通告板(.*?)(\n## |\Z)", dec, re.S)
if m:
    print(m.group(1)[:3000])

print("\n### orders.md rows 10-11..10-13 mentioning BigMoney/quant:")
for line in orders.splitlines():
    if re.search(r"2026-10-1[123]", line) and re.search(r"BigMoney|量化|bigmoney", line, re.I):
        print(" O:", line[:400])
