"""r495 bm-c N2-W15 pool entry origin-truth probe (MSG-2005 single-shard
claim vs observed 2-ready-shards face). Laws: r660 raw-blob bytes via
subprocess (no PS pipeline) / r474+r648 fetch-then-verify origin truth /
r446 probe-to-file. Read-only."""
import json
import subprocess
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "results", "_r495bmc_n2_entry.txt")
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def run(args, cwd=REPO):
    return subprocess.run(args, capture_output=True, cwd=cwd, creationflags=CNW)


def main():
    lines = []
    r = run(["git", "fetch", "origin"])
    lines.append(f"fetch_rc={r.returncode}")
    r = run(["git", "show", "origin/main:results/runnable_pool.json"])
    if r.returncode != 0:
        lines.append("ORIGIN_POOL_READ_FAIL " + r.stderr.decode("utf-8", "replace")[:200])
        pool = None
    else:
        pool = json.loads(r.stdout.decode("utf-8"))
    if pool is not None:
        for e in pool.get("entries", []):
            if e.get("id") == "PERPETUAL-N2-W15-GENERATE" or "N2-W15" in str(e.get("id", "")):
                lines.append("=== entry id=" + str(e.get("id")))
                lines.append(json.dumps(e, ensure_ascii=False, indent=1))
    with open(os.path.join(REPO, "results", "runnable_pool.json"), encoding="utf-8") as f:
        lp = json.load(f)
    for e in lp.get("entries", []):
        if e.get("id") == "PERPETUAL-N2-W15-GENERATE":
            lo = json.dumps(e, ensure_ascii=False, sort_keys=True)
            oo = ""
            if pool is not None:
                for e2 in pool.get("entries", []):
                    if e2.get("id") == "PERPETUAL-N2-W15-GENERATE":
                        oo = json.dumps(e2, ensure_ascii=False, sort_keys=True)
            lines.append("LOCAL==ORIGIN: " + str(lo == oo))
    r = run(["git", "log", "-4", "--format=%h %ad %an %s", "--date=iso",
             "origin/main", "--", "results/runnable_pool.json"])
    lines.append("--- recent pool-file commits on origin/main ---")
    lines.extend(r.stdout.decode("utf-8", "replace").strip().splitlines())
    n2dir = os.path.join(REPO, "results", "n2_w15")
    if os.path.isdir(n2dir):
        for fn in sorted(os.listdir(n2dir)):
            p = os.path.join(n2dir, fn)
            lines.append(f"N2DIR {fn} size={os.path.getsize(p)} mtime={os.path.getmtime(p)}")
    else:
        lines.append("N2DIR missing")
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print("WROTE", OUT)


if __name__ == "__main__":
    main()
