"""r673 bm-a crash_fuse 逐条目深层差异探针"""
import json, subprocess

def load_shared():
    raw = subprocess.run(["git", "show", "origin/main:results/crash_fuse.json"],
                         capture_output=True).stdout
    return json.loads(raw.decode("utf-8"))

origin = load_shared()
local = json.load(open("results/crash_fuse.json", encoding="utf-8"))
out = []
for key in sorted(set(local) | set(origin)):
    lv, ov = local.get(key), origin.get(key)
    if lv == ov:
        continue
    out.append(f"== key {key} ==")
    if isinstance(lv, dict) and isinstance(ov, dict):
        for k in sorted(set(lv) | set(ov)):
            if lv.get(k) != ov.get(k):
                out.append(f"  entry {k}")
                out.append(f"    local : {json.dumps(lv.get(k), ensure_ascii=False)[:600]}")
                out.append(f"    origin: {json.dumps(ov.get(k), ensure_ascii=False)[:600]}")
    else:
        out.append(f"  local : {json.dumps(lv, ensure_ascii=False)[:600]}")
        out.append(f"  origin: {json.dumps(ov, ensure_ascii=False)[:600]}")

lane = json.load(open("results/crash_fuse.bm-a.json", encoding="utf-8"))
out.append("== lane bm-a keys ==")
out.append(json.dumps(sorted(lane) if isinstance(lane, dict) else "list", ensure_ascii=False))

open("results/_r673bma_cf_deep.txt", "w", encoding="utf-8").write("\n".join(out))
print("\n".join(out))
