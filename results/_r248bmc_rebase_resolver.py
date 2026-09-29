# r248 bm-c rebase conflict resolver (r444 union law / r449 dedupe law):
# - regenerable single-value artifacts (29 files): take REBASE-"theirs" =
#   my replayed close-out version (later wall-clock 02:52-55 vs dead-tick
#   02:41-42) -> git checkout --theirs
# - compute_audit.json: history is append-only per (ts,machine) -> union
#   both sides, dedupe by (ts,machine), sort by ts
# - token_usage.json: per-machine rows -> union machines dict, per-key
#   later-yields by generated ts
# After resolve: verify append-only jsonl faces (r443 law: lines==objects)
import json, subprocess, sys, io

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def blob(ref, p):
    r = subprocess.run(["git", "show", ref + ":" + p],
                        capture_output=True, text=True, encoding="utf-8")
    return r.stdout

MINE = "c399816b6"   # my replayed close-out commit (rebase "theirs")
ORIG = "7f3f867db"   # origin bm-a dead-tick adoption (rebase "ours")

uu = subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"],
                    capture_output=True, text=True, encoding="utf-8").stdout.split()
uu = [f for f in uu if f.strip()]
print("conflicted:", len(uu))

UNION_FILES = {"results/compute_audit.json", "results/token_usage.json"}

n_theirs = 0
for f in uu:
    if f in UNION_FILES:
        continue
    subprocess.run(["git", "checkout", "--theirs", f], check=True)
    subprocess.run(["git", "add", f], check=True)
    n_theirs += 1
print("later-yields (mine) resolved:", n_theirs)

# --- compute_audit.json: union history by (ts, machine)
p = "results/compute_audit.json"
m = json.loads(blob(MINE, p)); o = json.loads(blob(ORIG, p))
hm, ho = m.get("history", []), o.get("history", [])
def key(e): return (e.get("ts", ""), e.get("machine", e.get("host", "")))
seen, merged = set(), []
for e in sorted(hm + ho, key=lambda e: e.get("ts", "")):
    k = key(e)
    if k in seen:
        continue
    seen.add(k)
    merged.append(e)
m["history"] = merged
# top-level scalars from the LATER run (mine)
m_out = m
io.open(p, "w", encoding="utf-8", newline="\n").write(
    json.dumps(m_out, ensure_ascii=False, indent=1))
subprocess.run(["git", "add", p], check=True)
print("compute_audit union: mine", len(hm), "+ origin", len(ho),
      "-> merged", len(merged), "| last ts", merged[-1].get("ts"))

# --- token_usage.json: union machines by key (later generated per key)
p = "results/token_usage.json"
m = json.loads(blob(MINE, p)); o = json.loads(blob(ORIG, p))
mm, om = m.get("machines", {}), o.get("machines", {})
def gts(d):
    try: return d.get("generated", "") or ""
    except Exception: return ""
merged_machines = {}
for k in sorted(set(mm) | set(om)):
    a, b = mm.get(k), om.get(k)
    if a is None: merged_machines[k] = b
    elif b is None: merged_machines[k] = a
    else: merged_machines[k] = a if gts(a) >= gts(b) else b
# shared top-level scalars: later generated wins (mine)
m["machines"] = merged_machines
io.open(p, "w", encoding="utf-8", newline="\n").write(
    json.dumps(m, ensure_ascii=False, indent=1))
subprocess.run(["git", "add", p], check=True)
print("token_usage union machines keys:", len(merged_machines))

# --- r443 law: append-only jsonl faces line==object verification
import os
for p in ["results/x2_watch_log.jsonl", "results/pool_dualrun.bm-c.jsonl"]:
    if not os.path.exists(p):
        continue
    lines = [l for l in io.open(p, encoding="utf-8", errors="replace")
             .read().splitlines() if l.strip()]
    ok = 0
    dec = json.JSONDecoder()
    bad = 0
    for l in lines:
        s = l.strip()
        i = 0
        try:
            while i < len(s):
                obj, j = dec.raw_decode(s, i)
                ok += 1
                s2 = s[j:].lstrip()
                i = len(l.strip()) - len(s2)
                s = s2
        except Exception:
            bad += 1
    print(f"{p}: lines={len(lines)} objects={ok} badlines={bad}",
          "PASS" if bad == 0 else "FAIL-NEEDS-SPLIT")
print("RESOLVER DONE")
