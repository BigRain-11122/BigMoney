# read-only probe: per-round row presence in root vs canonical (loose line matcher)
import re, json, os
BM = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
ROOT_FILE = os.path.join(BM, "round_reports-bm-c.md")
CANON_FILE = os.path.join(BM, "logs", "iteration-loop", "round_reports-bm-c.md")

line_re = re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}[:\uff1a]\d{2}")
lab_re = re.compile(r"\|\s*r(\d{3,4})\s*\|")

def scan(path):
    out = {}
    for ln in open(path, encoding="utf-8"):
        if line_re.match(ln):
            m = lab_re.search(ln)
            if m:
                n = int(m.group(1))
                out.setdefault(n, 0)
                out[n] += 1
    return out

root = scan(ROOT_FILE)
canon = scan(CANON_FILE)
missing_everywhere = []
root_only = []
for n in range(955, 985):
    in_root, in_canon = root.get(n, 0), canon.get(n, 0)
    tag = f"r{n}: root={in_root} canon={in_canon}"
    if n >= 958:
        if in_root and not in_canon:
            root_only.append(n)
        if not in_root and not in_canon:
            missing_everywhere.append(n)
    print(tag)
print("ROOT_ONLY:", root_only)
print("MISSING_EVERYWHERE:", missing_everywhere)
print("canonical tail labels:", sorted(k for k in canon if k >= 950))
