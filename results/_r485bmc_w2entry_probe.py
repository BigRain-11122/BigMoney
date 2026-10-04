"""r485 bm-c: dump full W2-JUDGE-SHARD-0 entry + pool meta for the
W3-JUDGE enrollment mirror. Read-only probe -> txt file (r446 law)."""
import json

data = json.load(open("results/runnable_pool.json", encoding="utf-8"))
e = next(x for x in data["entries"] if x.get("id") == "MASS-TRIAL-W2-JUDGE-SHARD-0")
with open("results/_r485bmc_w2entry_probe.txt", "w", encoding="utf-8") as f:
    f.write(json.dumps(e, ensure_ascii=False, indent=1))
    f.write("\n--- top-level keys ---\n")
    f.write(json.dumps({k: v for k, v in data.items() if k != "entries"},
                       ensure_ascii=False, indent=1)[:2000])
    f.write("\n--- entry key order (W2-JUDGE-0) ---\n")
    f.write(", ".join(e.keys()))
    f.write("\n--- entry key order (W3-SCREEN-0) ---\n")
    s = next(x for x in data["entries"] if x.get("id") == "MASS-TRIAL-W3-SCREEN-SHARD-0")
    f.write(", ".join(s.keys()))
    f.write("\n--- statuses of all judge-family entries ---\n")
    for x in data["entries"]:
        if "JUDGE" in str(x.get("id", "")):
            f.write("%s -> %s\n" % (x["id"], x.get("status")))
print("PROBE OK")
