import json
import hashlib
import os
import shutil

m = json.load(open("fleet/transfers/T-20260927-93-sender.json".replace("T-20260927", "T-2026-09-27"),
                   encoding="utf-8-sig"))
norm = lambda s: s.replace("\\", "/")
byfile = {norm(e["file"]): e for e in m["files"]}
print("manifest file_count", m["file_count"], "total_bytes", m["total_bytes"])
print("sample key:", repr(m["files"][0]["file"]))
for probe in ("results/decision_chain/curves_x2_legacy_LA.jsonl",
              "results/pros_segs/cells_deep_DE.jsonl",
              "results/pros_segs/done_legacy_LB.json"):
    h = hashlib.sha256(open(probe, "rb").read()).hexdigest()
    e = byfile[probe]
    print(probe, "bytes", os.path.getsize(probe) == e["bytes"],
          "sha256", h == e["sha256"])
shutil.rmtree(os.path.join(os.environ["TEMP"], "t93_stage_r314bma"))
print("stage cleaned")
