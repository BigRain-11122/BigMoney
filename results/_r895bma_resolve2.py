# r895 bm-a S0 dead-tail rebase adoption, leg 2: restore lines lost from append-only
# engine ledgers when the rebase checkout materialized the older tree (01:27:20 state)
# over the worktree, discarding the 01:27->01:30 appends captured only in dead-chain
# commit ea0a6eaed. Union(workdisk, ea0a6eaed) with ts-order restoration + parse-verify (r185).
import json, subprocess, sys

GIT = r"C:\Program Files\Git\cmd\git.exe"
EA0A = "ea0a6eaedfa0152043733b2eb84951b6e6499abe"
FACES = [
    "results/saturation_engine/history_bm-a.jsonl",
    "results/saturation_engine/ledger_bm-a.jsonl",
]

def blob(rev):
    return subprocess.run([GIT, "show", rev], capture_output=True).stdout

def split_lines(b):
    return [l + b"\n" for l in b.split(b"\n") if l]

for path in FACES:
    disk = split_lines(open(path, "rb").read())
    dead = split_lines(blob(EA0A + ":" + path))
    seen, union = set(), []
    for l in disk + dead:
        if l not in seen:
            seen.add(l); union.append(l)
    # ts-order restoration: sort by parsed ts when available, stable fallback keeps tail order
    def ts_key(item):
        try:
            return (0, json.loads(item.decode("utf-8").strip()).get("ts", ""))
        except Exception:
            return (1, "")
    union_sorted = sorted(union, key=ts_key)
    for i, l in enumerate(union_sorted):
        try:
            json.loads(l.decode("utf-8").strip())
        except Exception as e:
            print(json.dumps({"verdict": "PARSE_FAIL", "path": path, "line": i, "err": str(e)[:200]}))
            sys.exit(2)
    out = b"".join(union_sorted)
    with open(path, "wb") as f:
        f.write(out)
    print(json.dumps({
        "verdict": "LEDGER_UNION_OK", "path": path,
        "disk_lines": len(disk), "dead_lines": len(dead),
        "union_lines": len(union_sorted),
        "union_eq_union_set": len(union_sorted) == len(set(disk) | set(dead)),
        "bytes_out": len(out),
    }))
