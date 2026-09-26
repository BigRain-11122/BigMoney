# -*- coding: utf-8 -*-
"""_r250bma_t22_canon_assemble.py -- assemble pinned-path canon CE deep files (T80 battery lane unblock).

bm-b MSG-20260926-1400 checklist item 1 self-serve step: the runner's pinned
default paths expect results/t22/cells_deep_base.jsonl / cells_deep_x2.jsonl;
bm-a holds the same canon content shard-split as cells_deep_{base,x2}_{d-a1,d-c1}.jsonl
(106 + 1400 = 1506 starts x 6 CE = 9,036 rows per face). This assembles the
pinned-path files by byte-preserving concatenation with fail-closed census
assertions (dprobe 12-row partial is EXCLUDED -- forbidden partial face).

Zero modification of existing files; two NEW pinned-path files + provenance
report. Deterministic, zero network.
"""
import hashlib
import json
import os
import sys

T22 = os.path.join("results", "t22")
FACES = {
    "base": ("cells_deep_base_d-a1.jsonl", "cells_deep_base_d-c1.jsonl", "cells_deep_base.jsonl"),
    "x2": ("cells_deep_x2_d-a1.jsonl", "cells_deep_x2_d-c1.jsonl", "cells_deep_x2.jsonl"),
}
EXPECT_ROWS = 9036  # 6 CE x 1506 starts (per face)
EXPECT_TRADERS = {
    "COMPOSITE-CE-01", "COMPOSITE-CE-02", "VOLATILITY-CE-01",
    "DROUGHT-CE-01", "NEEDLE-DE-01", "ENGULF-CE-01",
}


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    report = {"assembled": {}, "sources": {}, "assertions": []}
    try:
        for face, (fa, fb, fout) in FACES.items():
            pa, pb = (os.path.join(T22, x) for x in (fa, fb))
            for p in (pa, pb):
                if not os.path.exists(p):
                    raise SystemExit(f"assemble: source absent: {p}")
            rows_a = [json.loads(l) for l in open(pa, encoding="utf-8")]
            rows_b = [json.loads(l) for l in open(pb, encoding="utf-8")]
            rows = rows_a + rows_b
            traders = {r["trader"] for r in rows}
            starts = {r["start"] for r in rows}
            pairs = {(r["trader"], r["start"]) for r in rows}
            if len(rows) != EXPECT_ROWS:
                raise SystemExit(f"assemble[{face}]: rows {len(rows)} != {EXPECT_ROWS}")
            if traders != EXPECT_TRADERS:
                raise SystemExit(f"assemble[{face}]: trader set mismatch: {sorted(traders)}")
            if len(starts) != 1506:
                raise SystemExit(f"assemble[{face}]: starts {len(starts)} != 1506")
            if len(pairs) != EXPECT_ROWS:
                raise SystemExit(f"assemble[{face}]: (trader,start) overlap across shards: {len(pairs)} != {len(rows)}")
            # byte-preserving concat: original line bytes, d-a1 block then d-c1 block
            out_path = os.path.join(T22, fout)
            with open(out_path, "wb") as w:
                for p in (pa, pb):
                    with open(p, "rb") as r:
                        while True:
                            chunk = r.read(1 << 20)
                            if not chunk:
                                break
                            w.write(chunk)
            report["assembled"][face] = {
                "path": out_path, "rows": len(rows),
                "sha256": sha256(out_path),
                "source_sha256": {fa: sha256(pa), fb: sha256(pb)},
            }
            report["assertions"].append(f"{face}: rows=={EXPECT_ROWS} traders==6 starts==1506 pairs-unique==OK")
        report["note"] = ("pinned-path assembly for T80-AGGR-FULLPOOL-BATTERY lane burn; dprobe partial "
                           "EXCLUDED (forbidden face); byte-preserving concat d-a1 then d-c1; zero source modification")
        with open(os.path.join(T22, "canon_assemble_report.json"), "w", encoding="utf-8") as fh:
            json.dump(report, fh, ensure_ascii=False, indent=1)
        print(json.dumps(report["assertions"], ensure_ascii=False))
        print("CANON ASSEMBLE: PASS")
        return 0
    except SystemExit as e:
        print(f"CANON ASSEMBLE: FAIL-CLOSED -> {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
