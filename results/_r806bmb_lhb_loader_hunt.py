# r806 bm-b LHB loader exception hunt: instrumented copy of _load_local_dates
# (read-only probe, zero panel touch)
import io, json, sys, traceback
import pandas as pd

src = io.open("scripts/update_lhb.py", encoding="utf-8").read()
ns = {"__file__": "scripts/update_lhb.py", "__name__": "lhb_probe"}
exec(compile(src, "update_lhb_probe", "exec"), ns)

import os
path = ns["CORE_CALENDAR_FILE"]
out = {"path": path, "exists": os.path.exists(path)}
try:
    df = pd.read_csv(path, usecols=[0])
    out["step1_read"] = True
    ds = pd.to_datetime(df[df.columns[0]], errors="coerce")
    out["step2_todatetime"] = True
    ds2 = sorted(ds.dropna().normalize().unique())
    out["step3_sortunique"] = len(ds2)
    dates = [pd.Timestamp(d) for d in ds2]
    out["step4_list"] = len(dates)
    out["tail"] = [str(d.date()) for d in dates[-3:]]
except Exception:
    out["EXC"] = traceback.format_exc()[-900:]
print(json.dumps(out, ensure_ascii=False, indent=1))
