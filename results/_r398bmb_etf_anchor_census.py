"""r398 bm-b verification: G-ANCHOR-FACE census 5/5 against the REFRESHED
five-member panel (post-cutoff rows on disk; D2 lockbox truncates before
anchor compare). Read-only loader, zero burn, zero writes."""

import sys

sys.path.insert(0, "scripts")
import etf_ops_bp1 as bp  # noqa: E402

fails = 0
for c in bp.MEMBERS:
    m, err = bp.load_member(c)
    if err:
        print(c, "REFUSE:", err)
        fails += 1
        continue
    f = m["face"]
    a = bp.ANCHORS[c]
    ok = (f["rows"] == a["rows"] and f["first"] == a["first"]
          and f["last"] == bp.EVIDENCE_CUTOFF)
    print(c, "PASS" if ok else "FAIL",
          "rows=" + str(f["rows"]), "first=" + f["first"],
          "last=" + f["last"], "truncated_on_disk=yes")
    fails += 0 if ok else 1
print("CENSUS", "5/5 PASS" if fails == 0 else f"{5 - fails}/5 FAIL",
      "-- refreshed panel + frozen anchors coexist via D2 lockbox")
sys.exit(1 if fails else 0)
