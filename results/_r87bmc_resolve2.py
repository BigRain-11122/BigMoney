# -*- coding: utf-8 -*-
"""r87 bm-c resolve2: regime_state history re-union fix.
resolve1 reused autofill composite key (ts,...) on regime rows keyed by 'asof' ->
all-rows-same-key collapse 1|2->1 = zero-loss violation (mine 09-24 row dropped).
r319 law: dedup key must be probed per-face before union. Fix: probe face key
(ts/asof/date), full-row dedup zero-loss, same-key-different-content = keep both + flag.
"""
import io, json, subprocess, os

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
os.chdir(ROOT)

def git(*a):
    return subprocess.run(["git", *a], capture_output=True).stdout

p = "results/regime_state.json"
b = git("show", f":1:{p}")
o = git("show", f":2:{p}")
t = git("show", f":3:{p}")
jo, jt = json.loads(o), json.loads(t)

def deep_ts(obj):
    best = [""]
    KEYS = ("ts", "generated", "generated_at", "updated", "updated_at", "asof", "last_run", "written_at")
    def scan(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if k in KEYS and isinstance(v, str) and len(v) >= 16:
                    nv = v.replace(" ", "T")[:19]
                    if nv > best[0]:
                        best[0] = nv
                scan(v)
        elif isinstance(x, list):
            for v in x:
                scan(v)
    scan(obj)
    return best[0]

out = dict(jo)
for lk in ("history", "transitions"):
    lo, lt = jo.get(lk, []), jt.get(lk, [])
    if not isinstance(lo, list) or not isinstance(lt, list):
        continue
    keyf = next((k for k in ("ts", "asof", "date", "day") if lo and k in lo[0]), None)
    seen, un = set(), []
    for r in lo + lt:
        rk = json.dumps(r, ensure_ascii=False, sort_keys=True)
        if rk not in seen:
            seen.add(rk)
            un.append(r)
    flags = []
    if keyf:
        byk = {}
        for r in un:
            byk.setdefault(r.get(keyf), []).append(r)
        for k, rs in byk.items():
            if len(rs) > 1:
                flags.append((keyf, k, len(rs)))
        un.sort(key=lambda r: r.get(keyf, ""))
    out[lk] = un
    print(f"  {p}[{lk}]: face-key={keyf} |ours|={len(lo)} |mine|={len(lt)} -> full-row-union={len(un)} collisions={flags if flags else 'none'}")

so, st = deep_ts(jo), deep_ts(jt)
pick = jo if (so, "") >= (st, "") else jt
for kk in set(jo) | set(jt):
    if kk not in ("history", "transitions"):
        out[kk] = pick.get(kk, jo.get(kk, jt.get(kk)))
print(f"  {p}: snapshot side={'HEAD' if pick is jo else 'mine'} ({so} vs {st})")

nb = b"\r\n" if b"\r\n" in b else b"\n"
with io.open(p, "w", encoding="utf-8", newline="") as f:
    f.write(json.dumps(out, ensure_ascii=False, indent=1) + ("\r\n" if nb == b"\r\n" else "\n"))
back = json.loads(io.open(p, encoding="utf-8").read())
asof_list = [r.get("asof") for r in back.get("history", [])]
assert asof_list == ["2026-09-23", "2026-09-24"], f"history asof mismatch: {asof_list}"
assert not flags, f"same-key different-content collision needs review: {flags}"
print(f"  {p}: VERIFY history asof={asof_list} len={len(back['history'])}")
print("RESOLVE2-OK")
