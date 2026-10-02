"""r565 bm-b: deep-diff one W61 shard (mine vs origin bm-c) — locate exact differing keys."""
import subprocess, json

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"

def git(*args):
    r = subprocess.run(["git", "-C", REPO] + list(args), capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {args} rc={r.returncode}: {r.stderr.decode('utf-8','replace')[:300]}")
    return r.stdout

p = "results/p2cal_ext/n1_w61/shard-0-of-12.json"
mine = json.loads(git("show", f":3:{p}").decode())
ours = json.loads(git("show", f":2:{p}").decode())

print("mine keys:", sorted(mine.keys()))
print("origin keys:", sorted(ours.keys()))
print("audit mine:", json.dumps(mine.get("audit", {}))[:400])
print("audit origin:", json.dumps(ours.get("audit", {}))[:400])

common = [k for k in mine if k in ours]
for k in sorted(common):
    if k == "audit":
        continue
    mv, ov = mine[k], ours[k]
    ms, os_ = json.dumps(mv, sort_keys=True), json.dumps(ov, sort_keys=True)
    if ms != os_:
        print(f"DIFF key={k}: mine={ms[:200]}")
        print(f"          origin={os_[:200]}")
only_mine = [k for k in mine if k not in ours]
only_ours = [k for k in ours if k not in mine]
print("only-mine keys:", only_mine)
print("only-origin keys:", only_ours)

# if there is an embedded rows/cells structure, compare a couple of numeric rows
for k in common:
    if k == "audit":
        continue
    if isinstance(mine[k], list) and mine[k] and isinstance(mine[k][0], dict):
        r0m = json.dumps(mine[k][0], sort_keys=True)
        r0o = json.dumps(ours[k][0], sort_keys=True) if isinstance(ours.get(k), list) and ours[k] else ""
        print(f"list key={k} len(mine)={len(mine[k])} len(origin)={len(ours.get(k, []))} first_row_equal={r0m == r0o}")
        if r0m != r0o:
            print("  mine row0:", r0m[:300])
            print("  orig row0:", r0o[:300])
