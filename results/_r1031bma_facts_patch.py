# r1031 bm-a: patch honest live machine facts (ctypes RAM + wmic CPU read failures disclosed)
import io, json, os, sys

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
free_gb = float(sys.argv[1])
cpu_pct = float(sys.argv[2])
vram_free = int(sys.argv[3])
ram_free_pct = round(100.0 - (free_gb / 93.6 * 100.0), 1)

sp = os.path.join(ROOT, "state-bm-a.json")
st = json.loads(io.open(sp, encoding="utf-8").read())
st["free_ram_gb"] = free_gb
st["ram_free_gb"] = free_gb
st["idle_ram_gb"] = free_gb
st["ram_free_pct"] = ram_free_pct
st["free_ram_pct"] = ram_free_pct
st["ram_load_pct"] = round(100.0 - ram_free_pct, 1)
st["cpu_pct"] = cpu_pct
st["cpu_load_pct"] = cpu_pct
st["cpu_total_pct"] = cpu_pct
st["gpu_free_vram_mb"] = vram_free
tmp = sp + ".tmp"
with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
os.replace(tmp, sp)

hp = os.path.join(ROOT, "fleet", "machines", "bm-a.json")
hb = json.loads(io.open(hp, encoding="utf-8").read())
hb["free_ram_gb"] = free_gb
hb["ram_free_gb"] = free_gb
hb["cpu_pct"] = cpu_pct
hb["cpu_total_pct"] = cpu_pct
hb["gpu_free_vram_mb"] = vram_free
tmp = hp + ".tmp"
with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
os.replace(tmp, hp)

back = json.loads(io.open(sp, encoding="utf-8").read())
assert back["ram_free_gb"] == free_gb
print(json.dumps({"ram_free_gb": free_gb, "ram_free_pct": ram_free_pct, "cpu_pct": cpu_pct, "vram_free": vram_free}))
