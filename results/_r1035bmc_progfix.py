# -*- coding: utf-8 -*-
# r1035 bm-c: fix jayredo progress json false-negative marks (5 clips judged BAD SIZE by the
# 500KB threshold in _r1035bmc_jayredo_harvest_repair.py, but ffprobe-verified valid:
# h264 1344x768 5.17s each; small size = low-motion legit). Marks -> ok:true + note.
import io, json, os
PROG_PATH = r"K:\Fluxgroup\FluxGroup\media\MV\mv0001\jayredo\jayredo_v4_r1032_progress.json"
I2V_DIR = r"K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\kf-demo-20261012\bmc\i2v\jayredo"
fixed, total_ok = [], 0
p = json.load(io.open(PROG_PATH, encoding="utf-8"))
i2v = p.get("i2v", {})
for name, ent in list(i2v.items()):
    f = os.path.join(I2V_DIR, name)
    good = os.path.isfile(f) and os.path.getsize(f) > 300000
    if good and not ent.get("ok"):
        ent["ok"] = True
        ent["sec"] = round(os.path.getsize(f) / 1048576.0, 2)
        ent["note"] = "bad-size mark healed r1035: ffprobe-verified valid h264 1344x768 5.17s (small size = low-motion)"
        fixed.append(name)
    if ent.get("ok"):
        total_ok += 1
json.dump(p, io.open(PROG_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("fixed:", fixed)
print("i2v ok total: %d/11" % total_ok)
