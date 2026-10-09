# r928 bm-a rebase UU resolver (r924 bloodline; r648 sha-channel; r790 content-driven)
# Policy: runnable_pool -> stage2(origin, bm-c newer claims) + post-rebase sync_face;
#          token_usage -> per-machine values-union (newer-wins per machine key);
#          all other UU -> stage3 (replayed estate side = fresher post-10-09-bar derivation).
# Rebase window stage semantics (r782): stage2=onto(origin) side, stage3=replayed commit (ours/estate).
import subprocess, sys, json, io

GIT = r"C:\Program Files\Git\cmd\git.exe"

def run(args, **kw):
    return subprocess.run([GIT] + args, capture_output=True, **kw)

def ls_arity():
    out = run(["ls-files", "-u"]).stdout.decode("utf-8", "replace")
    files = {}
    for line in out.splitlines():
        if not line.strip():
            continue
        meta, _, path = line.partition("\t")
        m = meta.split()  # [mode, sha, stage]
        if len(m) < 3 or not path:
            continue
        files.setdefault(path, {})[int(m[2])] = m[1]
    return files

def blob(sha):
    return run(["cat-file", "-p", sha]).stdout

def resolve():
    uu = ls_arity()
    if not uu:
        print("NO-UU (clean replay or already resolved)")
        return 0
    receipt = {"round": 928, "uu_count": len(uu), "faces": {}}
    for path, stages in sorted(uu.items()):
        s2 = stages.get(2)
        s3 = stages.get(3)
        # stage1 (base) may exist; we only need 2/3
        if path == "results/runnable_pool.json":
            pick, side = s2, "stage2-origin(sync_face post)"
        elif path == "results/token_usage.json":
            # per-machine union: base=stage3 (estate, fresher generated), overlay machine keys newer-wins
            a = json.loads(blob(s3).decode("utf-8"))
            b = json.loads(blob(s2).decode("utf-8"))
            ma, mb = a.get("machines", {}), b.get("machines", {})
            for k, v in mb.items():
                cur = ma.get(k)
                if cur is None or str(v.get("ts", "")) > str((cur or {}).get("ts", "")):
                    ma[k] = v
            a["machines"] = ma
            data = json.dumps(a, ensure_ascii=False, indent=1).encode("utf-8")
            with open(path, "wb") as f:
                f.write(data)
            # verify parse
            json.loads(open(path, "rb").read().decode("utf-8"))
            receipt["faces"][path] = "union-per-machine"
            print(f"RESOLVED-union: {path}")
            continue
        else:
            pick, side = s3, "stage3-estate"
        if pick is None:
            print(f"SKIP (no stage for {path}): {sorted(stages)}")
            continue
        data = blob(pick)
        if path.endswith(".json"):
            json.loads(data.decode("utf-8"))  # parse gate: poison/marker face would explode here
        with open(path, "wb") as f:
            f.write(data)
        receipt["faces"][path] = side
        print(f"RESOLVED-{side}: {path}")
    with open(r"results\_r928bma_resolve_rebase_receipt.json", "w", encoding="utf-8") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=1)
    print(f"receipt: {len(receipt['faces'])} faces, uu={len(uu)}")
    return 0

if __name__ == "__main__":
    sys.exit(resolve())
