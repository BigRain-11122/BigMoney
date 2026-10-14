import json, os, urllib.request

BASE = r"K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\kf-demo-20261012"
PROG = os.path.join(BASE, "bmc", "v3gap7_r1011_progress.json")
I2V = os.path.join(BASE, "bmc", "i2v")

prog = json.load(open(PROG, encoding="utf-8"))
out = {"ts": "2026-10-15T02:40:00+08:00", "results": []}
all_ok = True
for name, face in prog["shots"].items():
    if face.get("status") != "DELIVERED":
        out["results"].append({"slot": name, "status": face.get("status"), "check": "skip-not-delivered"})
        continue
    local = os.path.join(I2V, name + ".mp4")
    if not os.path.exists(local):
        all_ok = False
        out["results"].append({"slot": name, "check": "LOCAL-MISSING"})
        continue
    local_bytes = os.path.getsize(local)
    url = face["url"]
    req = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            remote = int(r.headers.get("Content-Length", -1))
    except Exception as e:
        all_ok = False
        out["results"].append({"slot": name, "check": "HEAD-FAIL", "err": str(e)[:120]})
        continue
    ok = remote == local_bytes == face.get("mp4_bytes")
    if not ok:
        all_ok = False
    out["results"].append({"slot": name, "local": local_bytes, "remote": remote, "declared": face.get("mp4_bytes"), "match": ok})

out["verdict"] = "ALL-MATCH" if all_ok else "MISMATCH"
out["delivered_count"] = sum(1 for f in prog["shots"].values() if f.get("status") == "DELIVERED")
out["pending"] = [k for k, v in prog["shots"].items() if v.get("status") == "PENDING"]
dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_r1012bmc_gap7_byteverify.json")
json.dump(out, open(dst, "w", encoding="utf-8"), indent=1)
print(json.dumps({k: out[k] for k in ("verdict", "delivered_count", "pending")}, ensure_ascii=False))
for r in out["results"]:
    print(r)
