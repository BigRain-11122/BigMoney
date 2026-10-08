# -*- coding: utf-8 -*-
"""r767 bm-c S6 driver post-close edit receipt: the clone-gate-created
_r767bmc_s6.py was functionally edited AFTER the clone receipt (per-round
driver evolution, cta_p1 leg-addition precedent) to carry the REGIME_GUARD
v3 first-new-bar enforce face (r766 next_pointer milestone): live_paper leg
gains per-leg env BIGMONEY_REGIME_GUARD=enforce. This receipt re-compiles
the edited driver and records the edit -> results/
_r767bmc_s6_edit_receipt.json."""
import json
import os
import py_compile

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
DRV = os.path.join(ROOT, "Tools", "_r767bmc_s6.py")
txt = open(DRV, encoding="utf-8").read()
receipt = {
    "round": 767,
    "file": "Tools/_r767bmc_s6.py",
    "edit": ("live_paper leg per-leg env BIGMONEY_REGIME_GUARD=enforce "
             "(REGIME_GUARD v3 first-new-bar enforce, 10-08 reopen T-0 "
             "window, r766 next_pointer milestone; anchor gate "
             "self-protects)"),
    "bytes": len(txt.encode("utf-8")),
    "enforce_token_present": "BIGMONEY_REGIME_GUARD\": \"enforce" in txt
    or "BIGMONEY_REGIME_GUARD': 'enforce" in txt,
}
py_compile.compile(DRV, doraise=True)
receipt["compile"] = "OK"
out = os.path.join(ROOT, "results", "_r767bmc_s6_edit_receipt.json")
with open(out, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(receipt, fh, indent=1, ensure_ascii=False)
print(json.dumps(receipt, indent=1, ensure_ascii=False))
