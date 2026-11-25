import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import etf_book_ceo_page as P  # noqa: E402

r = P.cost_tape_face()
out = {"status": r.get("status"), "artifact": r.get("artifact")}
for k, v in r.items():
    if isinstance(v, (dict, list)):
        out[k] = "<%s>" % type(v).__name__
    else:
        out[k] = v
print(json.dumps(out, ensure_ascii=False, indent=1)[:1200])

surv, noisy, raised = P.reader_probe()
print("survivors=%d noisy=%d raised=%s" % (len(surv), len(noisy), raised))
