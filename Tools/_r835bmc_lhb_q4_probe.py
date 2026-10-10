"""r835 bm-c probe: LHB quarter-boundary deadlock evidence (zero-write).
The update_lhb.py fetch window is pinned to the cutoff's quarter
[20260701, 20260930] while the fetch gate expects disclosures up to
2026-10-09 -- Q4 rows are unreachable by construction. This probe
fetches the Q4 window directly to confirm the source holds rows the
refresh can never see. Read-only: writes results/_r835bmc_lhb_q4_probe.json
only, touches no store."""

import datetime
import json
import time

import requests as _rq
_rq_request_orig = _rq.Session.request


def _jacket(self, *a, **k):
    k.setdefault("timeout", 45)
    return _rq_request_orig(self, *a, **k)


_rq.Session.request = _jacket

import akshare as ak  # noqa: E402

out = {"ts": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
       "machine": "bm-c", "purpose": "Q4 LHB rows reachable via direct fetch?",
       "q3_refetch": None, "q4_fetch": None}
try:
    t0 = time.time()
    q3 = ak.stock_lhb_detail_em(start_date="20260701", end_date="20260930")
    out["q3_refetch"] = {"rows": int(len(q3)),
                         "max_date": str(q3["上榜日"].max()) if len(q3) else None,
                         "sec": round(time.time() - t0, 1)}
except Exception as ex:
    out["q3_refetch"] = {"error": f"{type(ex).__name__}: {str(ex)[:120]}"}
try:
    t1 = time.time()
    q4 = ak.stock_lhb_detail_em(start_date="20261001", end_date="20261010")
    if len(q4):
        dates = sorted(q4["上榜日"].astype(str).unique())
        out["q4_fetch"] = {"rows": int(len(q4)), "dates": dates,
                           "max_date": str(q4["上榜日"].max()),
                           "sec": round(time.time() - t1, 1)}
    else:
        out["q4_fetch"] = {"rows": 0, "note": "empty (not yet disclosed)",
                           "sec": round(time.time() - t1, 1)}
except Exception as ex:
    out["q4_fetch"] = {"error": f"{type(ex).__name__}: {str(ex)[:120]}"}

path = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r835bmc_lhb_q4_probe.json"
json.dump(out, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False))
