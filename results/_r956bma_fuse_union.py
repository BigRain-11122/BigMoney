"""r956 bm-a: resolve crash_fuse.json rebase conflict (UU) via per-sig union.

Law: fuse = shared per-sig counters face (machine-attributed union);
conflict = two daemon writers' counters. Resolution = per-sig max(count)
+ max(last_refusal_ts / last_crash_ts); zero-loss on both sides' keys.
"""
import io, json, re

P = r"results\crash_fuse.json"
src = io.open(P, encoding="utf-8", newline="").read()

# conflict-block parser: <<< ours(HEAD=origin newer) ... === mine ... >>>
pat = re.compile(
    r"<<<<<<< HEAD\r\n(.*?)\r\n=======\r\n(.*?)\r\n>>>>>>> [^\r\n]*\r\n",
    re.S,
)

def maxfield(a, b, name, mode="max"):
    ma = re.search(r'"%s": "?([^",\r\n]*)"?' % name, a)
    mb = re.search(r'"%s": "?([^",\r\n]*)"?' % name, b)
    va = ma.group(1) if ma else None
    vb = mb.group(1) if mb else None
    if va is None:
        return vb
    if vb is None:
        return va
    if name in ("refusals", "count"):
        return str(max(int(va), int(vb)))
    return max(va, vb)  # ISO-ish ts strings compare lexically

n = 0
def fix(m):
    global n
    a, b = m.group(1), m.group(2)
    fields = sorted(set(re.findall(r'"([a-z_0-9]+)":', a + b)))
    out = []
    for f in fields:
        va = re.search(r'"%s": "?([^",\r\n]*)"?' % f, a)
        vb = re.search(r'"%s": "?([^",\r\n]*)"?' % f, b)
        if va and vb:
            out.append(f'   "{f}": "{maxfield(a, b, f)}"')
        elif va:
            out.append(f'   "{f}": "{va.group(1)}"')
        elif vb:
            out.append(f'   "{f}": "{vb.group(1)}"')
    n += 1
    return "\r\n".join(out) + "\r\n"

res = pat.sub(fix, src)
assert "<<<<<<<" not in res and ">>>>>>>" not in res, "markers remain"
data = json.loads(res)
sigs = data.get("sigs", {})
w17 = {k: v for k, v in sigs.items() if "w17" in k}
for k, v in sorted(w17.items()):
    print(k, "->", {kk: v.get(kk) for kk in ("count", "refusals", "last_crash_ts", "last_refusal_ts", "machine")})
print("total sigs:", len(sigs), "resolved hunks:", n)
with io.open(P, "w", encoding="utf-8", newline="") as fh:
    fh.write(res)
print("WROTE", P)
