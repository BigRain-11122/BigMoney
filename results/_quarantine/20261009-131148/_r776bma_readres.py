# -*- coding: utf-8 -*-
"""Read THEME_DEEPEN_P1 results summary for report + prereg backfill."""
import json

d = json.load(open("results/theme_deepen_p1/theme_deepen_p1.json", encoding="utf-8"))
print("== verdicts ==")
print(json.dumps(d["verdicts"], ensure_ascii=False, indent=1))
print("== face2 position summary ==")
print(json.dumps(d["face2"]["position_summary"], ensure_ascii=False, indent=1))
print("== face2 tests ==")
print(json.dumps(d["face2"]["tests"], ensure_ascii=False, indent=1))
print("== sign test ==", d["face2"]["sign_test"])
print("== sensitivity ==")
print(json.dumps(d["face2"]["sensitivity_summary"], ensure_ascii=False, indent=1))
print("== composite ==", json.dumps(d["composite"], ensure_ascii=False))
print("== d6 max|corr| ==", d["d6"]["max_abs_corr"], "| any_reject:", d["d6"]["any_reject"])
print("== face1 dropped ==")
print(json.dumps(d["face1"]["dropped"], ensure_ascii=False, indent=1))
print("== expansion events (id/ignition/pclass/dur/ret/dd) ==")
for m in d["face1"]["expansion_events"]:
    print(m["id"], m["ignition"], m["persistence_class"], m["dur_to_peak_td"],
          round(m["ret_ign_to_peak"], 3), round(m["dd_after_peak"], 3))
print("== crosstab dedup ==")
print(json.dumps(d["face1"]["crosstab_dedup"], ensure_ascii=False, indent=1))
print("== n rows ==", d["audit"]["n_rows_ledger"], "| elapsed:", d["audit"]["elapsed_sec"])
