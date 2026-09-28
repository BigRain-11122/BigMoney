"""r402 bm-b S7 push-retry resolver: 3-UU vs bm-a r406-cont (01:30-31 push-storm closeout).

Recipes: CODELY.md memory-union (line-level union both machines' new entries);
compute_audit.json rolling-ledger (history union by (ts,host), latest take-new by deep-ts);
update_status.json snapshot take-new deep-ts probe. Side by BLOB ts, never identity (batch-72 law).
"""
import json
import re
import subprocess

TS_RE = re.compile(r"^20\d{2}-")
CLOCK_RE = re.compile(r"[T ]\d{2}:\d{2}")


def blob(stage, path):
    return subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True).stdout


def deep_wallclock(obj):
    best = None

    def walk(o):
        nonlocal best
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str):
                    nk = k.replace("_", "").replace("-", "").lower()
                    if any(nk.startswith(p) for p in ("asof", "updated", "generated", "ts", "last")):
                        if TS_RE.match(v) and CLOCK_RE.search(v):
                            if best is None or v > best:
                                best = v
                walk(v)
        elif isinstance(o, list):
            for it in o:
                walk(it)

    walk(obj)
    return best


def dump_conv(raw):
    obj = json.loads(raw)
    text = raw.decode("utf-8")
    for indent in (1, 2, 3, 4):
        for ea in (False, True):
            for trail in ("", "\n"):
                cand = json.dumps(obj, ensure_ascii=ea, indent=indent) + trail
                if cand == text:
                    return obj, dict(indent=indent, ensure_ascii=ea, trail=trail)
    return obj, dict(indent=2, ensure_ascii=False, trail="\n")


# 1) update_status.json snapshot take-new
p = "results/update_status.json"
o2, o3 = blob(2, p), blob(3, p)
t2 = deep_wallclock(json.loads(o2)) if o2.strip() else None
t3 = deep_wallclock(json.loads(o3)) if o3.strip() else None
side = "theirs" if (t2 or "") > (t3 or "") else "ours"
raw = o3 if side == "theirs" else o2
obj, conv = dump_conv(raw)
text = json.dumps(obj, ensure_ascii=conv["ensure_ascii"], indent=conv["indent"]) + conv["trail"]
open(p, "w", encoding="utf-8", newline="").write(text)
json.loads(open(p, encoding="utf-8").read())
print(f"{p}: side={side} ts2={t2} ts3={t3}")

# 2) compute_audit.json ledger union + latest take-new (newer of the two 'latest' faces)
p = "results/compute_audit.json"
o2, o3 = blob(2, p), blob(3, p)
a, b = json.loads(o2), json.loads(o3)
conv = dump_conv(o2)[1]


def ident(e):
    return (e.get("ts"), e.get("host"))


h2 = {ident(e): e for e in a.get("history", [])}
h3 = {ident(e): e for e in b.get("history", [])}
union = list(h2.values()) + [e for k, e in h3.items() if k not in h2]
union.sort(key=lambda e: e.get("ts", ""))
assert len(union) == len(h2) + len(h3) - len(set(h2) & set(h3))
la, lb = a.get("latest", {}), b.get("latest", {})
ta = deep_wallclock(la) or ""
tb = deep_wallclock(lb) or ""
merged = dict(b if tb > ta else a)  # newer latest wins; tie -> ours(=base, r140)
merged["history"] = union
text = json.dumps(merged, ensure_ascii=conv["ensure_ascii"], indent=conv["indent"]) + conv["trail"]
open(p, "w", encoding="utf-8", newline="").write(text)
json.loads(open(p, encoding="utf-8").read())
print(f"{p}: union={len(union)} latest_side={'base' if tb > ta else 'ours'} ta={ta} tb={tb}")

# 3) CODELY.md memory-union: line-level union, both machines' new entries kept
p = "CODELY.md"
t2 = blob(2, p).decode("utf-8").splitlines(keepends=True)
t3 = blob(3, p).decode("utf-8").splitlines(keepends=True)
# base = common prefix+suffix; union = base + each side's unique lines in order
s2, s3 = set(t2), set(t3)
merged = [l for l in t2 if True]  # start from base(ours) in order
# insert theirs-unique lines after their common anchor (append at tail keeps each machine's block)
tail3 = [l for l in t3 if l not in s2]
# find where t3 diverges from t2: common prefix
i = 0
while i < len(t2) and i < len(t3) and t2[i] == t3[i]:
    i += 1
# merged = t2 with t3-unique lines inserted at divergence point (bm-a new entries) then remaining t2
head = t2[:i]
rest2 = t2[i:]
merged = head + tail3 + rest2 if tail3 else t2
open(p, "w", encoding="utf-8", newline="").write("".join(merged))
print(f"{p}: union lines={len(merged)} (base {len(t2)} + theirs-unique {len(tail3)})")
