# -*- coding: utf-8 -*-
# r888 bm-c closeout: state + heartbeat update (JSON-int epoch law R170/R178)
import json, time, datetime

STATE = "state-bm-c.json"
HB = "fleet/machines/bm-c.json"

now_dt = datetime.datetime.now().astimezone()
clock_read = now_dt.strftime("%Y-%m-%dT%H:%M:%S") + ("+08:00" if now_dt.utcoffset().total_seconds() >= 0 else "-08:00")
# exact offset form:
off = now_dt.utcoffset()
sign = "+" if off.total_seconds() >= 0 else "-"
abs_s = int(abs(off.total_seconds()))
clock_read = now_dt.strftime("%Y-%m-%dT%H:%M:%S") + f"{sign}{abs_s//3600:02d}:{(abs_s%3600)//60:02d}"
epoch = int(time.time())

# ---- state ----
st = json.load(open(STATE, encoding="utf-8"))
st["round_no"] = 888
st["activity_now"] = (
    "current activity: r888 W211 freeze-prep bundle LANDED (origin e8a2f4638: prereg PERPETUAL_N1_W211_PREREG.md anchored W209 actuals "
    "883,589/K=457,720 + splice editor _w211bmc_freeze_edits.py derived from W209 template, estate face=own W209 block structural choice, "
    "banned ADMIT + seed_admit FREE x2 + fail-closed dry-run proven at r609 gate) + M11 row stays armed (upstream=W210 bm-b five-face+finalize "
    "pending, bm-b busy O-1917 CEO lanes honest) + W209 watch cron 9defca39 retired (M10 done) + W211 backup watch cron 847675d7 armed "
    "(17min, escalation leg 5h/12h) + M9 row flipped done (W207 bm-b r856/857 evidence-cited queue hygiene) + MV-lane observation MSG-2100 "
    "(batch client gone, ComfyUI idle orphan, CEO-priority lane fact receipt) | round proof: smoke 49/49 + S6 chain rc0 all legs "
    "(dualrun streak 3 / audit supply_floor flag structural W210 bottleneck honest / wm insufficient_history fresh window / daily-regime-clock-"
    "lhb-scorecard rc0 / collectors lane-guard honest no-ops / thermo-dualarm-revosc lane no-ops / fund_premium weekend no-op / b_layer rc0 / "
    "daily_report+live_usage written / token delta 0) + attrition guard CLEAN + claws OK + loop pin 5 no-op | next milestone: W210 lands on "
    "bm-b -> M11/cron auto-executes W211 freeze same window -> n1_w211 12/12 burn -> W211 finalize -> W212 chain continues (M12 row next)"
)
json.dump(st, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---- heartbeat ----
hb = json.load(open(HB, encoding="utf-8"))
hb["round_no"] = 888
hb["last_seen"] = clock_read
hb["ts"] = clock_read
hb["now_active"] = "r888: W211 freeze-prep landed (prereg+splice editor, e8a2f4638) + M11 armed + cron watch refreshed"
hb["current_task"] = (
    "r888: W211 freeze-prep bundle landed + M11 watch armed (upstream W210 bm-b) + S6 chain + closeout; "
    "next: W210 landing -> W211 freeze auto-exec -> burn -> finalize -> W212"
)
hb["verdict"] = (
    "py_low structural honest (insufficient_history fresh window; supply_floor flag=W210 bm-b five-face pending=structural bottleneck, "
    "bm-b busy O-1917 CEO lanes; M11+freeze-prep+cron=armed response, burn resumes on W210 landing)"
)
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["heartbeat_epoch_utc"] = epoch  # python int, JSON int type law R170/R178
hb["clock_read"] = clock_read
json.dump(hb, open(HB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---- self-verify (law: write then read back) ----
chk = json.load(open(HB, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178)"
assert "T" in chk["clock_read"], "clock_read must be T-separated ISO (R262)"
chk2 = json.load(open(STATE, encoding="utf-8"))
assert chk2["round_no"] == 888
print("closeout state OK: round_no=888 epoch=", chk["heartbeat_epoch_utc"], "clock=", chk["clock_read"])
