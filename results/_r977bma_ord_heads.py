import os

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
orders = ["O-20261010-2325-bm-b.md","O-20261011-1105-bm-c.md","O-20261011-1254-bm-c.md","O-20261011-1436-bm-c.md","O-20261011-1811-bm-c.md","O-20261011-1917-bm-c.md","O-20261011-2126-bm-c.md","O-20261011-2147-bm-c.md","O-20261011-2215-bm-c.md","O-20261011-2333-bm-c.md","O-20261012-0739-bm-c.md","O-20261012-0940-bm-a.md","O-20261013-0930-bm-b.md"]
for o in orders:
    p = os.path.join(ROOT, "fleet", "orders", o)
    txt = open(p, encoding="utf-8").read()
    head = "\n".join(txt.splitlines()[:6])
    print("=" * 20, o, f"({len(txt)}B)")
    print(head)
    print()
