"""Read-only probe: why does the day-word census call the page PRINTED_BUT_UNANCHORED
while the page's own head line says the counts are settled?"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import live_book_day_words as L  # noqa: E402

c = L.census() if hasattr(L, "census") else None
out = {"module": L.__file__}
if c is None:
    for name in ("build", "derive", "census_page", "run"):
        fn = getattr(L, name, None)
        if callable(fn):
            try:
                c = fn()
                out["used"] = name
                break
            except TypeError:
                continue
if isinstance(c, dict):
    out["verdict"] = c.get("verdict")
    out["offenders"] = c.get("offenders")
    out["printed"] = c.get("printed")
    out["date_claims"] = c.get("date_claims") or c.get("_dc_public")
    out["keys"] = sorted(c.keys())
print(json.dumps(out, ensure_ascii=False, indent=1, default=str)[:4000])
