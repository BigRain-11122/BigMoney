# -*- coding: utf-8 -*-
# r665 bm-b merge resolver ROUND 2 (2 UU after bm-a r671 mid-closeout push-race):
#   results/compute_audit.json -> (ts, canonical) union + zero-loss containment
#     (r660 law), latest = theirs 10:46:49 (fresher)
#   results/token_usage.json -> take-THEIRS under mirrored 4 premises (theirs
#     10:51:01 successor chained on bm-c 10:42:06 row; fuse append faces
#     identical; keyset identical; theirs machine reads fresher-or-equal)
import json, subprocess, io, os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run(cmd):
    p = subprocess.run(cmd, capture_output=True)
    return p.returncode, p.stdout, p.stderr

def blob(ref, path):
    rc, out, err = run(["git", "show", ref + ":" + path])
    if rc != 0:
        raise RuntimeError(f"blob read fail {ref}:{path}: {err.decode('utf-8','replace')[-120:]}")
    return out

rc, st, _ = run(["git", "status", "--porcelain"])
uu = [l[3:].strip() for l in st.decode("utf-8", "replace").splitlines()
      if l[:2] in ("UU", "AA")]
print("UU faces:", uu)
assert sorted(uu) == ["results/compute_audit.json", "results/token_usage.json"], uu

# --- 1) compute_audit.json union (r660) ---
AUDIT = "results/compute_audit.json"
o = json.loads(blob("HEAD", AUDIT))
t = json.loads(blob("MERGE_HEAD", AUDIT))

def canon(row):
    return json.dumps(row, sort_keys=True, ensure_ascii=False)

seen = set()
union = []
for row in sorted(o["history"] + t["history"], key=lambda r: str(r.get("ts", ""))):
    k = (str(row.get("ts", "")), canon(row))
    if k in seen:
        continue
    seen.add(k)
    union.append(row)
o_set = {(str(r.get("ts", "")), canon(r)) for r in o["history"]}
t_set = {(str(r.get("ts", "")), canon(r)) for r in t["history"]}
u_set = {(str(r.get("ts", "")), canon(r)) for r in union}
assert len(o_set - u_set) == 0 and len(t_set - u_set) == 0, "audit union LOSS"
lo, lt = str(o["latest"].get("ts", "")), str(t["latest"].get("ts", ""))
latest = o["latest"] if lo >= lt else t["latest"]
merged = {"latest": latest, "history": union}
with io.open(AUDIT, "wb") as f:
    f.write(json.dumps(merged, ensure_ascii=False, indent=1).encode("utf-8"))
rc, out, err = run(["git", "add", "--", AUDIT])
assert rc == 0, "audit add fail"
print(f"audit union: ours={len(o['history'])} theirs={len(t['history'])} -> {len(union)} "
      f"latest={'ours' if lo >= lt else 'theirs'} {latest.get('ts')}")

# --- 2) token_usage.json take-THEIRS (mirrored premises) ---
TOKEN = "results/token_usage.json"
O = json.loads(blob("HEAD", TOKEN))
T = json.loads(blob("MERGE_HEAD", TOKEN))
p1 = str(T["generated"]) > str(O["generated"])
of = O.get("l2_local_llm", {}).get("crash_fuse", {})
tf = T.get("l2_local_llm", {}).get("crash_fuse", {})
p2 = of.get("sigs") == tf.get("sigs") and of.get("refusals") == tf.get("refusals")
p3 = sorted(O.get("machines", {}).keys()) == sorted(T.get("machines", {}).keys())
ok_machines = all(
    T.get("machines", {}).get(k, {}).get("report_bytes", 0) >=
    O.get("machines", {}).get(k, {}).get("report_bytes", 0)
    for k in O.get("machines", {}).keys())
assert p1 and p2 and p3 and ok_machines, \
    f"token take-theirs premises broken: p1={p1} p2={p2} p3={p3} machines={ok_machines}"
with io.open(TOKEN, "wb") as f:
    f.write(json.dumps(T, ensure_ascii=False, indent=1).encode("utf-8"))
rc, out, err = run(["git", "add", "--", TOKEN])
assert rc == 0, "token add fail"
print(f"token take-theirs ok: gen {T['generated']} > ours {O['generated']}, "
      f"fuse {tf.get('sigs')}/{tf.get('refusals')}")

# --- 3) verification: markers + reparse ---
for f in uu:
    data = io.open(f, "rb").read()
    for ln in data.split(b"\n"):
        assert not (ln.startswith(b"<<<<<<<") or ln.startswith(b">>>>>>>")), f"marker in {f}"
    if f.endswith(".json"):
        json.load(io.open(f, encoding="utf-8"))
print("marker+reparse verification: clean")
print("RESOLVE2 OK -- commit merge as separate step")
