"""R317 bm-a rebase-conflict resolver: autofill_state.json (mixed-dict+ledger canon).

Sides during rebase: :2 = ours = origin/HEAD (bm-c r199 autofill tick claim 8e68f689),
:3 = theirs = replayed round-317 commit (bm-a eb29d212).
Recipe (classify_conflicts.py GREEN, r203/R208/r215/r220/r245 laws):
  launches   = union both sides, dedup by (ts,machine,entry,shard,pid),
               re-sort ts ASCENDING (write-back format face, r245), cap 50 keep-newest
  last_tick  = compare inner ts -> assign WHOLE dict; same-second tie -> HEAD (:2 ours)
  other keys = side with newer last_tick ts wins (single state face), fall back union-safe
  write-back = mirror base blob line endings (CRLF producer format, r223/r234)
  r185 law   = parse-verify before git add; isinstance(last_tick, dict) assert
"""
import json
import subprocess
import io

ROOT = "."
PATH = "results/autofill_state.json"


def side(n):
    out = subprocess.run(["git", "show", f":{n}:{PATH}"], capture_output=True, cwd=ROOT)
    if out.returncode != 0:
        raise RuntimeError(f"git show :{n}:{PATH} rc={out.returncode}")
    return out.stdout


b2, b3 = side(2), side(3)
a, b = json.loads(b2.decode("utf-8-sig")), json.loads(b3.decode("utf-8-sig"))

# base-blob line-ending mirror (r223/r234)
crlf = b"\r\n" in b2

# --- launches union (dedup by full identity tuple per r317 bm-b law) ---
la, lb = a.get("launches", []), b.get("launches", [])


def lkey(x):
    return (x.get("ts"), x.get("machine"), x.get("entry"), x.get("shard"), x.get("pid"))


seen, union = set(), []
for item in list(la) + list(lb):
    k = lkey(item)
    if k not in seen:
        seen.add(k)
        union.append(item)
union.sort(key=lambda x: x.get("ts") or "")
launches = union[-50:]  # cap 50 = keep newest after asc sort (r215 rolling window)

# --- last_tick whole-dict ts compare (tie -> HEAD :2) ---
ta, tb_ = (a.get("last_tick") or {}).get("ts"), (b.get("last_tick") or {}).get("ts")
if ta is None and tb_ is None:
    last_tick = a.get("last_tick")
elif ta is None:
    last_tick = b.get("last_tick")
elif tb_ is None:
    last_tick = a.get("last_tick")
elif ta > tb_:
    last_tick = a.get("last_tick")
elif tb_ > ta:
    last_tick = b.get("last_tick")
else:
    last_tick = a.get("last_tick")  # same-second tie -> HEAD/ours (r140)

# --- merged state: base = newer-ts side, overlay canonical faces ---
base, other = (a, b) if (ta or "") >= (tb_ or "") else (b, a)
merged = dict(base)
merged["launches"] = launches
merged["last_tick"] = last_tick
for k, v in other.items():
    if k not in merged:
        merged[k] = v

# r185 law: parse-verify before write-back
txt = json.dumps(merged, ensure_ascii=False, indent=1)
json.loads(txt)  # raises on malformed
assert isinstance(merged.get("last_tick"), dict), "last_tick must stay a dict"

data = txt + ("\r\n" if crlf else "\n")
with io.open(PATH, "wb") as f:
    f.write(data.encode("utf-8"))

# post-write verification: reload from disk as producer would
chk = json.loads(io.open(PATH, "r", encoding="utf-8-sig").read())
assert chk["launches"] == launches and chk["last_tick"] == last_tick
print(json.dumps({
    "path": PATH,
    "side2_last_tick_ts": ta, "side3_last_tick_ts": tb_,
    "kept_last_tick_ts": (last_tick or {}).get("ts"),
    "launches": f"{len(la)}+{len(lb)} -> {len(union)} unique -> cap50 {len(launches)}",
    "launches_sorted": [x.get("ts") for x in launches[:2]] + ["..."] + [x.get("ts") for x in launches[-2:]],
    "crlf_mirror": crlf,
    "parse_verify": "PASS",
}, ensure_ascii=False))
