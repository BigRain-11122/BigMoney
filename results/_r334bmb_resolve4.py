# -*- coding: utf-8 -*-
"""r334 bm-b: 4-file rebase-round-2 resolver (d9cea197 replay onto 6c0fd764).

CODELY.md = memory-union WITH anti-archival-regression filter (bm-c r89
"mine_new oa-filter anti-18th-batch-regression"): take ours (post-19th-batch
archival face) + ONLY my original commit's added lines (dcaa14ff^..dcaa14ff),
byte-deduped -- naive two-blob union would resurrect archived-away lines.
compute_audit = rolling-ledger union + snapshot take-new (r188/R208).
lhb_update_status = snapshot take-new deep-ts (R208/R216).
x2_watch_log = append-log base-first line union (r188/r217).
rebase side map: :1=base(31f87759) :2=ours(HEAD=origin face) :3=theirs(mine).
"""
import datetime
import io
import json
import subprocess

NOW = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def blob(stage, path):
    return subprocess.run(["git", "show", f"{stage}:{path}"],
                          capture_output=True).stdout


uu = [l.decode().strip() for l in subprocess.run(
    ["git", "diff", "--name-only", "--diff-filter=U"],
    capture_output=True).stdout.splitlines() if l.strip()]
print("UU files:", uu)
assert set(uu) == {"CODELY.md", "results/compute_audit.json",
                  "results/lhb_update_status.json",
                  "results/x2_watch_log.jsonl"}, f"unexpected UU set: {uu}"


def deep_ts(obj):
    best = [""]
    KEYS = ("ts", "generated", "generated_at", "updated", "updated_at", "asof",
            "last_run", "written_at", "last_attempt")

    def scan(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in KEYS and isinstance(v, str) and len(v) >= 16:
                    nv = v.replace(" ", "T")[:19]
                    if nv > NOW:
                        continue          # r334 future sentinel
                    if nv > best[0]:
                        best[0] = nv
                scan(v)
        elif isinstance(o, list):
            for v in o:
                scan(v)
    scan(obj)
    return best[0]


# ---------------------------------------------------- 1. CODELY.md memory-union
b, o, t = blob(":1", "CODELY.md"), blob(":2", "CODELY.md"), blob(":3", "CODELY.md")
mine_new = []
diff = subprocess.run(["git", "diff", "dcaa14ff^", "dcaa14ff", "--", "CODELY.md"],
                      capture_output=True).stdout.decode("utf-8")
for l in diff.splitlines():
    if l.startswith("+") and not l.startswith("+++"):
        mine_new.append(l[1:])
print(f"CODELY: ours={len(o)}B theirs={len(t)}B mine_new={len(mine_new)} lines")
ol = o.decode("utf-8").splitlines()
added = 0
for l in mine_new:
    if l.strip() and l not in ol:
        ol.append(l)
        added += 1
        print(f"  + appended: {l[:80]}...")
crlf = b"\r\n" in o
data = "\n".join(ol) + ("\r\n" if crlf else "\n")
with io.open("CODELY.md", "w", encoding="utf-8", newline="") as f:
    f.write(data)
newlen = len(io.open("CODELY.md", encoding="utf-8").read().encode("utf-8"))
print(f"CODELY resolved: {newlen}B (+{added} mine-new, archived face preserved)")

# ------------------------------------------- 2. compute_audit rolling union
b, o, t = (blob(s, "results/compute_audit.json") for s in (":1", ":2", ":3"))
jo, jt = json.loads(o), json.loads(t)
un, seen = [], set()
for r in jo.get("history", []) + jt.get("history", []):
    kk = tuple(r.get(f) for f in ("ts", "machine", "pid", "entry", "shard",
                                  "runner_sha256"))
    if kk not in seen:
        seen.add(kk)
        un.append(r)
un.sort(key=lambda r: (r.get("ts") or r.get("asof") or ""))
print(f"compute_audit history: |ours|={len(jo.get('history', []))} "
      f"|theirs|={len(jt.get('history', []))} -> union={len(un)}")
out = dict(jo)
out["history"] = un
so, st = deep_ts(jo), deep_ts(jt)
if not (so, "") >= (st, ""):
    for k in set(jo) | set(jt):
        if k != "history":
            out[k] = jt.get(k, jo.get(k))
print(f"compute_audit snapshot: ours={so or '-'} theirs={st or '-'} -> "
      f"{'ours' if (so, '') >= (st, '') else 'theirs'}")
nb = b"\r\n" if b"\r\n" in b else b"\n"
with io.open("results/compute_audit.json", "w", encoding="utf-8", newline="") as f:
    f.write(json.dumps(out, ensure_ascii=False, indent=1)
            + ("\r\n" if nb == b"\r\n" else "\n"))
json.loads(io.open("results/compute_audit.json", encoding="utf-8").read())

# ------------------------------------------- 3. lhb_update_status take-new
b, o, t = (blob(s, "results/lhb_update_status.json") for s in (":1", ":2", ":3"))
jo, jt = json.loads(o), json.loads(t)
so, st = deep_ts(jo), deep_ts(jt)
win = "ours" if (so, "") >= (st, "") else "theirs"
data = o if win == "ours" else t
nb = b"\r\n" if b"\r\n" in b else b"\n"
with io.open("results/lhb_update_status.json", "wb") as f:
    f.write(data)
json.loads(io.open("results/lhb_update_status.json", encoding="utf-8").read())
print(f"lhb_update_status: take_new {win} (ts {so or '-'} vs {st or '-'}) "
      f"identical={o == t}")

# ------------------------------------------- 4. x2_watch_log line union
b, o, t = (blob(s, "results/x2_watch_log.jsonl") for s in (":1", ":2", ":3"))
bl = b.decode("utf-8").splitlines()
ol = o.decode("utf-8").splitlines()
tl = t.decode("utf-8").splitlines()
seen = set(bl)
out = list(bl)
n_o = n_t = 0
for l in ol:
    if l and l not in seen:
        seen.add(l)
        out.append(l)
        n_o += 1
for l in tl:
    if l and l not in seen:
        seen.add(l)
        out.append(l)
        n_t += 1
with io.open("results/x2_watch_log.jsonl", "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(out) + ("\n" if out else ""))
print(f"x2_watch_log: base={len(bl)} +ours {n_o} +theirs {n_t} -> {len(out)}")

print("RESOLVE4-OK")
