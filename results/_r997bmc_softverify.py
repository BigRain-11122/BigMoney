# -*- coding: utf-8 -*-
# _r997bmc_softverify.py -- soft-copyright 18-model rerun verification (r997 leg)
import io, os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
D = r"K:\Fluxgroup\FluxGroup\软著申请材料"
out = io.open(os.path.join(D, "_gen_r996.out.log"), encoding="utf-8", errors="replace").read()
err_size = os.path.getsize(os.path.join(D, "_gen_r996.err.log"))
lines = out.strip().splitlines()
print("out.log lines:", len(lines), "| err size:", err_size)
print("TAIL 14:")
for ln in lines[-14:]:
    print("  ", ln)
# census: which of the 18 models produced src txt today
B = ["G04_ScrewOut", "G05_ReelRiot", "G07_MobTide", "G08_CrazyCampus", "G13_我要有个农场",
     "G14_人从众", "G20_MonsterInn", "G23", "G26_归园田居", "G28_ArrowOut"]
C = ["G02_TimeRepairShop", "G03_MergeMania", "G06_ArrowRush", "G09Y", "G10_涨停板", "G12_LineRescue", "G17", "G18_PalacePlunder"]
import glob, datetime
today = datetime.date(2026, 10, 14)
def fresh(p):
    try:
        return datetime.date.fromtimestamp(os.path.getmtime(p)) == today
    except Exception:
        return False
fresh_files, stale_expected = [], []
for sub in os.listdir(D):
    p = os.path.join(D, sub)
    if not os.path.isdir(p):
        continue
    for f in os.listdir(p):
        fp = os.path.join(p, f)
        if fresh(fp) and (f.endswith(".txt") or f.endswith(".pdf")):
            fresh_files.append(os.path.join(sub, f))
print("FRESH today txt/pdf count:", len(fresh_files))
for f in sorted(fresh_files)[:60]:
    print("  ", f)
