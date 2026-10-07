# -*- coding: utf-8 -*-
"""r680 bm-c: compact grep of S6 log for round report facts (audit flags,
watermark verdict, dualrun streak). Throwaway helper, ascii only."""
import json
import re

log = open(r"results/_r680bmc_s6_log.txt", encoding="utf-8").read()

m = re.search(r"=== compute_audit rc=\d+ [^\n]*\n(.*?)\n===", log, re.S)
seg = m.group(1)
jm = re.search(r"\{.*\}", seg, re.S)
if jm:
    d, _ = json.JSONDecoder().raw_decode(jm.group(0))
    print("CA_FLAGS=", d.get("flags"))
    print("CA_root_cause=", d.get("root_cause") or d.get("root_causes"))
    print("CA_keys_sample=", [k for k in d.keys() if "supply" in k or "pool" in k][:6])

m2 = re.search(r"=== py_watermark rc=\d+ [^\n]*\n(.*?)\n===", log, re.S)
seg2 = m2.group(1)
jm2 = re.search(r"\{.*\}", seg2, re.S)
if jm2:
    d2, _ = json.JSONDecoder().raw_decode(jm2.group(0))
    print("WM_VERDICT=", d2.get("verdict"))
    print("WM_low_window=", d2.get("low_window_sustained") or d2.get("low_minutes"))
    for k in ("top_proc_cores", "runnable_burn_cands", "board_open", "bandit_open",
              "open_tickets", "burns_active", "bars_fresh"):
        if k in d2:
            print("WM_%s=%s" % (k, d2[k]))

m3 = re.search(r"=== pool_dualrun_reconcile rc=\d+ [^\n]*\n(.*?)\n===", log, re.S)
seg3 = m3.group(1).strip().splitlines()
print("DUALRUN_TAIL:")
for line in seg3[-8:]:
    print("  ", line)
