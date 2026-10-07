# r806 bm-b LHB gate probe: why does fetch_gate allow fetch during golden week?
# (hung leg-08 root-cause probe, read-only, zero panel touch)
import io, json, sys
import pandas as pd

sys.path.insert(0, "scripts")
src = io.open("scripts/update_lhb.py", encoding="utf-8").read()
head = src.split("def save_status")[0]
ns = {"__file__": "scripts/update_lhb.py", "__name__": "lhb_probe"}
exec(compile(src, "update_lhb_probe", "exec"), ns)

d = ns["_load_local_dates"]()
import os as _os, traceback
dbg = {"core_calendar_file": ns["CORE_CALENDAR_FILE"],
        "exists": _os.path.exists(ns["CORE_CALENDAR_FILE"])}
try:
    import pandas as _pd
    _df = _pd.read_csv(ns["CORE_CALENDAR_FILE"], usecols=[0])
    dbg["read_ok"] = True; dbg["rows"] = len(_df)
except Exception:
    dbg["read_ok"] = False; dbg["exc"] = traceback.format_exc()[-500:]
print("DBG " + json.dumps(dbg, ensure_ascii=False))
now = pd.Timestamp.now()
expected = ns["expected_disclosure_date"](now)
gate_no_throttle = ns["fetch_gate"](pd.Timestamp("2026-09-30"), now, None)
gate_with_throttle = ns["fetch_gate"](pd.Timestamp("2026-09-30"), now,
                                      pd.Timestamp("2026-10-07 14:35:16"))
st = {
    "probe": "lhb_gate_probe", "machine": "bm-b",
    "calendar_is_none": d is None,
    "calendar_tail": [str(x.date()) for x in d[-3:]] if d else None,
    "expected_now": str(expected.date()),
    "gate_cutoff_0930_no_throttle": gate_no_throttle,
    "gate_cutoff_0930_throttle_1435": gate_with_throttle,
}
print(json.dumps(st, ensure_ascii=False, indent=1))
json.dump(st, open("results/_r806bmb_lhb_gate_probe.json", "w",
                   encoding="utf-8"), ensure_ascii=False, indent=1)
