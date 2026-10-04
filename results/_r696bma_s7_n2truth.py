"""r696 bm-a S7: origin N2/CONTEST shard truth + new-commits check."""
import json, os, subprocess

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
out = {}
subprocess.run(["git", "-C", ROOT, "fetch", "origin"], capture_output=True)
r = subprocess.run(["git", "-C", ROOT, "log", "--oneline", "HEAD..origin/main"],
                   capture_output=True)
out["behind_commits"] = r.stdout.decode("utf-8", "replace").strip().splitlines()

r = subprocess.run(["git", "-C", ROOT, "show", "origin/main:results/runnable_pool.json"],
                   capture_output=True)
if r.returncode == 0:
    d = json.loads(r.stdout.decode("utf-8"))
    for e in d["entries"]:
        if e.get("id") in ("PERPETUAL-N2-W15-GENERATE", "CONTEST-YTD-P1-RC-0OF1"):
            out[e["id"]] = {"status": e.get("status"),
                            "shards": [{"k": s.get("key"), "st": s.get("status"),
                                        "own": s.get("owner"),
                                        "ts": s.get("owner_since"),
                                        "ka": s.get("keepalive_at")}
                                       for s in e.get("shards", [])]}
# N2 product on origin?
r = subprocess.run(["git", "-C", ROOT, "log", "origin/main", "--oneline", "-5",
                    "--", "results/n2_w15"], capture_output=True)
out["n2_product_commits"] = r.stdout.decode("utf-8", "replace").strip().splitlines()[:5]

with open(os.path.join(ROOT, "results", "_r696bma_s7_n2truth.json"), "w",
          encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1)[:1200])
