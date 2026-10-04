# -*- coding: utf-8 -*-
"""r698 bm-a moneyflow panel status probe (read-only, next_pick advisory check)."""
import json, os, io

out = io.StringIO()
cands = [
    "results/moneyflow_panel.json",
    "results/moneyflow/panel.json",
    "results/moneyflow/panel_status.json",
    "results/moneyflow/status.json",
    "results/moneyflow_panel_status.json",
]
for c in cands:
    if os.path.exists(c):
        print("FOUND", c, file=out)
        with open(c, encoding="utf-8-sig") as fh:
            st = json.load(fh)
        for k, v in st.items():
            print("  %s: %s" % (k, str(v)[:160]), file=out)
        break
else:
    print("no status json in candidates; dir listing:", file=out)
    for d in ("results/moneyflow", "results/moneyflow_panel"):
        if os.path.isdir(d):
            for f in sorted(os.listdir(d))[:20]:
                p = os.path.join(d, f)
                print("  %s %d" % (f, os.path.getsize(p)), file=out)

# also run the gate's own status subcommand if present
with open("results/_r698bma_mf_status.txt", "w", encoding="utf-8", newline="") as fh:
    fh.write(out.getvalue())
print(out.getvalue())
