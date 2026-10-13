# -*- coding: utf-8 -*-
import io
t = io.open(r"results\_w233bmc_20261013_probe.py", encoding="utf-8").read()
faces = ["r966", "r967", "r968", "8d3a1b78a", "a3a7aa632", "e58dbcda3",
         "5c90051e0", "776b15270", "931_989", "508_320", "934_189",
         "_r968bmc_w232_fivekey_receipt", "W233p_A", "fc223_a", "h222a",
         "inside223", '"ordinal": 223', "62nd owned", "63rd owned",
         "222nd wave", "range(16, 233)", "N1_BANDS[232]", "NINETY-THIRD",
         "NINETY-FOURTH", "934,189", "508,320", "mu=-0.0927",
         "owner_total == 222", "bmc_rows) == 62", "222/62", "231"]
for f in faces:
    print(repr(f), t.count(f))
