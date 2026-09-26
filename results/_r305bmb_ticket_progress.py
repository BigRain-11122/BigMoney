# -*- coding: utf-8 -*-
"""r305 bm-b: append progress_r305_bmb line to the T-87 ticket (lane-claim
progress key family, r279-r285_bmb precedent). Read-modify-write with
re-parse verify; only adds one key, never touches other machines' faces."""
import io
import json

P = r"C:\Users\Administrator\Desktop\Bigmoney\fleet\tasks\T-2026-09-26-87-P1.json"
KEY = "progress_r305_bmb"
LINE = (
    "T-87 r305 bm-b supply-lane FIRST-PULL SETTLED + settle-law design fix: "
    "main pass (spawned r280 23:47, pid 29440) ended 06:40:11, per_files "
    "5217/5228 zero shape defect across frozen probe lineage #2-#18 "
    "(r301-r305 health-watch arc); 11 stragglers (000019 suspended + "
    "001235/001246 + 301569/301660/301716/301718 + 688089/688143/688173/"
    "689009 new-listing faces) 3-strike quarantined honest; 12 suspended "
    "short-tail symbols settled via NEW settle law -- r305 design-gap fix: "
    "fetch-success symbols get attempts.pop so quarantine never catches "
    "them, complete was structurally unreachable (30-min gate spawn loop "
    "forever); fix = suspended-settle face (>=3 fetch-success-no-new-bar "
    "cycles at SAME expected cutoff leave todo, disclosed settled_n; new "
    "cutoff re-arms = resumed stocks fetched, self-heal law preserved) + "
    "load_progress whitelist carry fix (settle counter was reset to n=1 "
    "every cycle by the attempts-only load face) + panel cutoff bytes-derive "
    "priority (cycle-scope fetch max stamped a lagging cutoff on settle-only "
    "cycles); selftest extended, all guard cases PASS; manual refresh "
    "cycles 3-8 (deliberate operator cycles past the 30-min gate throttle, "
    "~60 extra requests at 2.5s, disclosed) reached the steady face 06:52: "
    "panel complete=true cutoff=2026-09-24 universe 5228 per_files 5217 "
    "quarantined 11 settled 12, GATE no-op panel-fresh zero-network. "
    "Evidence: results/_r305bmb_astock_completion_probe.json (pass_complete) "
    "+ _r305bmb_astock_pass_probe.json (#18 last in-flight face) + "
    "results/astock_daily_update_status.json. NEXT: Mon 09-28 first "
    "daily-continuation live fire = full-universe detached fetch ~3.5h "
    "family by-design cost (honest disclosure), settled symbols re-arm at "
    "the new expected cutoff; consumption face (REV_OSC_STOCK_P1 forward "
    "leg) opens per r280 next-pointer when a machine claims it."
)

with io.open(P, encoding="utf-8") as f:
    d = json.load(f)
assert KEY not in d, "progress_r305_bmb already present"
assert d.get("progress_r285_bmb"), "lineage anchor missing"
d[KEY] = LINE
with io.open(P, "w", encoding="utf-8", newline="") as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
    f.write("\n")
v = json.load(io.open(P, encoding="utf-8"))
assert v[KEY] == LINE and v.get("progress_r285_bmb")
print("ticket T-2026-09-26-87-P1 +progress_r305_bmb ok (keys=%d)" % len(v))
