# -*- coding: utf-8 -*-
"""R259 bm-a: archive run1 (descriptive-defective) per r240 preserve law +
r253 single-count law: strip the trials_ledger block from the archived copy
(superseded by run2's row, same frozen hypothesis set -- deterministic
re-execution != new trials), keep every other face byte-preserved."""
import io
import json
import shutil

SRC = "results/t73_s2/style_rotation.json"
DST = "results/t73_s2/style_rotation_run1_descriptive_defective.json"

d = json.load(io.open(SRC, encoding="utf-8-sig"))
row = d.pop("trials_ledger", None)
assert row is not None, "run1 must carry a ledger row"
d["superseded_by_run2"] = {
    "reason": "descriptive tables quoted RAW closes; fund artifacts "
              "(510500 2015-04-15 +248.6%, 512100 2022-09-05 +176.3%, "
              "512890 2021-10-25 -51.1%) poisoned yearly/era CAGR cells "
              "(csi500 2015 +454.5%, csi1000 2022 +123.7%, div_lowvol 2021 "
              "-41.0% = artifacts not market facts); law faces were "
              "strict-window clean (valid); r239 rotation-guard law applied "
              "to descriptive via clean_value bridge face in run2",
    "ledger_row": row,
    "ledger_disposition": "stripped from this archive; run2 re-links "
                          "prev 187585 -> total 187687 single-count "
                          "(same frozen hypothesis set, r253 "
                          "legal-re-execution law); chain contiguous",
}
io.open(DST, "w", encoding="utf-8", newline="\n").write(
    json.dumps(d, ensure_ascii=False, indent=1) + "\n")
print("archived", DST, "ledger row stripped+documented, prev_total was",
      row["prev_total"], "total was", row["total"])
