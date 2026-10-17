# r1031 bm-a: fix inverted pct faces (free_pct must be free/total*100)
import io, json, os, sys

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
free_gb = float(sys.argv[1])
total_gb = 93.6
free_pct = round(free_gb / total_gb * 100.0, 1)
load_pct = round(100.0 - free_pct, 1)

for rel in (os.path.join("state-bm-a.json"), os.path.join("fleet", "machines", "bm-a.json")):
    p = os.path.join(ROOT, rel)
    d = json.loads(io.open(p, encoding="utf-8").read())
    d["free_ram_gb"] = free_gb
    d["ram_free_gb"] = free_gb
    d["idle_ram_gb"] = free_gb
    d["ram_free_pct"] = free_pct
    d["free_ram_pct"] = free_pct
    d["ram_load_pct"] = load_pct
    tmp = p + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    os.replace(tmp, p)
    back = json.loads(io.open(p, encoding="utf-8").read())
    assert back["ram_free_pct"] == free_pct and back["ram_load_pct"] == load_pct
print(json.dumps({"free_gb": free_gb, "free_pct": free_pct, "load_pct": load_pct}))
