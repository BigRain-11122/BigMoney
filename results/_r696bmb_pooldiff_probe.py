"""r696 bm-b: pool diff faces via subprocess, outputs to files (r489/r660 laws)."""
import subprocess

MB = "df18b49f59468f59b9391108f393f34234b9f361"
for tag, a, b in (("ours", MB, "HEAD"), ("theirs", MB, "MERGE_HEAD")):
    r = subprocess.run(["git", "diff", a, b, "--", "results/runnable_pool.json"],
                       capture_output=True)
    out = r.stdout.decode("utf-8", "replace")
    open(f"results/_r696bmb_pooldiff_{tag}.txt", "wb").write(r.stdout)
    print(tag, "diff bytes=", len(r.stdout), "lines=", len(out.splitlines()))

# also: git merge-tree style check of the SHARD-3 region at each rev
import json
for rev in (MB, "HEAD", "MERGE_HEAD"):
    r = subprocess.run(["git", "show", f"{rev}:results/runnable_pool.json"],
                       capture_output=True)
    txt = r.stdout.decode("utf-8", "replace")
    idx = txt.find('"id": "PERPETUAL-N2-W15-SHARD-3"')
    seg = txt[idx:idx + 700] if idx >= 0 else "NOT FOUND"
    print("=== " + rev + " SHARD-3 region ===")
    print(seg[:700])
