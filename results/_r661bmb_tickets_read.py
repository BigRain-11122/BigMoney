# -*- coding: utf-8 -*-
import json, io
for n in ("T-2026-10-03-153-P1.json", "T-2026-10-03-155-P1.json",
          "T-2026-10-02-148-P1.json", "T-2026-10-02-150-P1.json"):
    t = json.load(io.open("fleet/tasks/" + n, encoding="utf-8"))
    print("---", n, "| status:", t.get("status"), "---")
    for k in ("title", "subject", "summary", "next_pointer"):
        if k in t:
            print(" ", k, ":", str(t[k])[:280])
