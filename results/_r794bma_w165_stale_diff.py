import io
import re

s163 = io.open(r"results/_r789bma_w163_freeze_edits.py", encoding="utf-8", newline="").read()
s164 = io.open(r"results/_r792bma_w164_freeze_edits.py", encoding="utf-8", newline="").read()

def stale_list(s):
    lines = s.splitlines()
    out, inside = [], False
    for ln in lines:
        if "for stale in (" in ln:
            inside = True
        elif inside and ln.strip().endswith("):"):
            out += re.findall(r'"([^"]+)"', ln)
            break
        if inside:
            out += re.findall(r'"([^"]+)"', ln)
    return out

a = stale_list(s163)
b = stale_list(s164)
print("W163 tool stale count:", len(a), "| W164 tool stale count:", len(b))
print("--- added in 164:")
print([x for x in b if x not in a])
print("--- removed in 164:")
print([x for x in a if x not in b])
