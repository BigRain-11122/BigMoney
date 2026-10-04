"""r673 bm-a S0 crash_fuse.json 本地 vs origin 原字节比对探针（r446 落文件律+r660 subprocess 原字节律）"""
import json, subprocess

raw = subprocess.run(["git", "show", "origin/main:results/crash_fuse.json"],
                     capture_output=True).stdout
origin = json.loads(raw.decode("utf-8"))
local = json.load(open("results/crash_fuse.json", encoding="utf-8"))

ka, kb = set(local), set(origin)
out = []
out.append(f"local_only: {sorted(ka - kb)}")
out.append(f"origin_only: {sorted(kb - ka)}")
for k in sorted(ka & kb):
    if local[k] != origin[k]:
        lv, ov = local[k], origin[k]
        out.append(f"DIFF {k}\n  local = {json.dumps(lv, ensure_ascii=False)[:400]}\n  origin= {json.dumps(ov, ensure_ascii=False)[:400]}")

open("results/_r673bma_cf_diff.txt", "w", encoding="utf-8").write("\n".join(out))
print("WROTE results/_r673bma_cf_diff.txt; keys local=%d origin=%d" % (len(ka), len(kb)))
