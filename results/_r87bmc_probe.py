# -*- coding: utf-8 -*-
"""r87 bm-c probe: inherited rebase (onto c3ca1fe9, replaying d1271fbf r86) 30-UU facts.
Roles: :1=base, :2=ours=origin landed face (bm-b r330 addendum), :3=theirs=my r86 commit.
Read-only. Facts only, no writes. Law: list derive programmatic (r327), probe-before-resolve.
"""
import io, json, re, subprocess, sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
import os
os.chdir(ROOT)

def git(*a):
    r = subprocess.run(["git", *a], capture_output=True)
    return r.stdout

def blobs(path):
    return git("show", f":1:{path}"), git("show", f":2:{path}"), git("show", f":3:{path}")

def deep_ts(obj):
    best = [""]
    KEYS = ("ts", "generated", "generated_at", "updated", "updated_at", "asof", "last_run", "written_at")
    def scan(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in KEYS and isinstance(v, str) and len(v) >= 16:
                    nv = v.replace(" ", "T")[:19]
                    if nv > best[0]:
                        best[0] = nv
                scan(v)
        elif isinstance(o, list):
            for v in o:
                scan(v)
    scan(obj)
    return best[0]

out = {}

uu = [l.decode().strip() for l in subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"],
     capture_output=True).stdout.splitlines() if l.strip()]
out["uu_count"] = len(uu)
out["uu"] = uu

# ---- CODELY.md structure facts
b, o, t = blobs("CODELY.md")
bl, ol, tl = b.decode("utf-8").splitlines(), o.decode("utf-8").splitlines(), t.decode("utf-8").splitlines()
bs, os_, ms = set(bl), set(ol), set(tl)
o_new = [l for l in ol if l not in bs]
m_new = [l for l in tl if l not in bs]
shared_new = [l for l in o_new if l in ms]
out["codely"] = {
    "bytes": {"base": len(b), "ours2": len(o), "theirs3": len(t)},
    "lines": {"base": len(bl), "ours2": len(ol), "theirs3": len(tl)},
    "origin_new_count": len(o_new), "mine_new_count": len(m_new),
    "shared_new_count": len(shared_new),
    "origin_new": o_new,
    "mine_new": m_new,
    "base_pitlaw_live_ours": [l for l in bl if l.startswith("- [2026-09-27") and "坑律" in l and l in os_],
    "base_pitlaw_gone_ours": [l[:60] for l in bl if l.startswith("- [2026-09-27") and "坑律" in l and l not in os_],
    "base_pitlaw_gone_mine": [l[:60] for l in bl if l.startswith("- [2026-09-27") and "坑律" in l and l not in ms],
}

# ---- archive prefix facts
p = "research/memory-archive/202609.md"
b, o, t = blobs(p)
bd, od, td = b.decode("utf-8"), o.decode("utf-8"), t.decode("utf-8")
out["archive"] = {
    "ours_prefix_ok": od.startswith(bd), "mine_prefix_ok": td.startswith(bd),
    "bytes": {"base": len(b), "ours2": len(o), "theirs3": len(t)},
    "ours_suffix": od[len(bd):] if od.startswith(bd) else None,
    "mine_suffix": td[len(bd):] if td.startswith(bd) else None,
    "16batch_sections_ours": od.count("十六批"), "16batch_sections_mine": td.count("十六批"),
}

# ---- autofill composite keys
p = "results/autofill_state.json"
b, o, t = blobs(p)
jo, jt = json.loads(o), json.loads(t)
KEYF = ("ts", "machine", "pid", "runner_sha256", "entry", "shard")
def key(r):
    return tuple(r.get(k) for k in KEYF)
lo, lt = jo.get("launches", []), jt.get("launches", [])
ko, kt = set(map(key, lo)), set(map(key, lt))
out["autofill"] = {
    "ours_n": len(lo), "mine_n": len(lt),
    "keyset_identical": ko == kt, "common": len(ko & kt), "ours_only": len(ko - kt), "mine_only": len(kt - ko),
    "last_tick_ts": {"ours": (jo.get("last_tick") or {}).get("ts"), "mine": (jt.get("last_tick") or {}).get("ts")},
}

# ---- rolling ledgers
for p, keys in (("results/compute_audit.json", ("history",)), ("results/regime_state.json", ("history", "transitions"))):
    b, o, t = blobs(p)
    jo, jt = json.loads(o), json.loads(t)
    out[p] = {f"ours_{k}": len(jo.get(k, [])) if isinstance(jo.get(k, []), list) else "nonlist" for k in keys}
    out[p].update({f"mine_{k}": len(jt.get(k, [])) if isinstance(jt.get(k, []), list) else "nonlist" for k in keys})
    out[p]["ts_ours"] = deep_ts(jo); out[p]["ts_mine"] = deep_ts(jt)

# ---- jsonl
p = "results/x2_watch_log.jsonl"
b, o, t = blobs(p)
out["x2"] = {"base": len(b.decode().splitlines()), "ours": len(o.decode().splitlines()), "mine": len(t.decode().splitlines())}

# ---- side-ts for coupled/take-new faces
side_ts = {}
for p in uu:
    if p in ("CODELY.md", "research/memory-archive/202609.md", "results/autofill_state.json",
             "results/compute_audit.json", "results/regime_state.json", "results/x2_watch_log.jsonl"):
        continue
    b, o, t = blobs(p)
    try:
        if p.endswith(".js"):
            mo = re.search(r"window\.DASH_DATA\s*=\s*(\{.*\})\s*;?\s*$", o.decode("utf-8"), re.S)
            mt = re.search(r"window\.DASH_DATA\s*=\s*(\{.*\})\s*;?\s*$", t.decode("utf-8"), re.S)
            so, st = deep_ts(json.loads(mo.group(1))), deep_ts(json.loads(mt.group(1)))
        elif p.endswith(".md"):
            side_ts[p] = "md-twin"; continue
        else:
            so, st = deep_ts(json.loads(o)), deep_ts(json.loads(t))
        side_ts[p] = {"ours": so, "mine": st}
    except Exception as e:
        side_ts[p] = f"ERR {type(e).__name__}: {e}"
out["side_ts"] = side_ts

print(json.dumps(out, ensure_ascii=False, indent=1))
