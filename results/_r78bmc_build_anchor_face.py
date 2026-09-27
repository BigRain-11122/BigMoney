"""r78 bm-c: build the T-14 anchor-face snapshot (pinned registration blobs).

Root cause (r78): T-19 stage-2c runner read CURRENT registrations via
_load_traders(); r242 (T-78 s4 EXIT-OVERLAY-P1 winner wiring, 2026-09-26)
legitimately evolved live registrations for C01/C02/ENGULF AFTER the T-14
freeze (4a5754a3, 2026-09-24 12:35) -- so rails ran with tp_ladder/ov_full
overlays and G-REPRO (bit-exact vs frozen T-14 A faces) correctly refused.
The prereg's frozen intent (s2: "与 stage-1 审计逐位同镜" + s4 hard gate
"基线复现逐位==T-14 冻结 A 面") requires the T-14-FREEZE registration face.
This script snapshots those blobs as a committed consumer file; the runner
then pins to the snapshot instead of the live directory (implementation fix,
zero judgment touch, J18 law).

Usage: python results/_r78bmc_build_anchor_face.py
Writes: data/consolidation/t14_anchor_face.json
"""
import hashlib
import json
import subprocess

SRC_COMMIT = "4a5754a3"   # T-14 DONE (bm-c r47), frozen A faces of record
SRC_FILES_DIR = "firm/traders"
OUT = "data/consolidation/t14_anchor_face.json"
FROZEN_BATCH = "results/rules_fidelity_t14.json"


def main() -> int:
    batch = json.load(open(FROZEN_BATCH, encoding="utf-8-sig"))
    ids = sorted(r["trader"] for r in batch["traders"])
    assert len(ids) == 6, f"expected 6 frozen T-14 traders, got {len(ids)}"
    subj = subprocess.run(
        ["git", "show", "-s", "--format=%ci %s", SRC_COMMIT],
        capture_output=True, text=True, check=True).stdout.strip()
    traders, sha_map = [], {}
    for tid in ids:
        blob = subprocess.run(
            ["git", "show", f"{SRC_COMMIT}:{SRC_FILES_DIR}/{tid}.json"],
            capture_output=True, check=True).stdout
        sha_map[tid] = hashlib.sha256(blob).hexdigest()
        t = json.loads(blob.decode("utf-8-sig"))
        assert t.get("id") == tid, f"id mismatch {tid}"
        assert t.get("level") == "INTERN", f"{tid} not INTERN at freeze"
        traders.append(t)
    out = {
        "provenance": {
            "source_commit": SRC_COMMIT,
            "source_commit_line": subj,
            "pinned_face": "T-14 freeze registration blobs (INTERN 6)",
            "pin_reason": (
                "r242 T-78 s4 EXIT-OVERLAY-P1 winner wiring (2026-09-26 "
                "10:58) evolved live registrations for COMPOSITE-CE-01 "
                "(tp_ladder) / COMPOSITE-CE-02+ENGULF-CE-01 (ov_full) "
                "after the T-14 freeze; T-19 stage-2c mirrors the "
                "stage-1/T-14 audited face (prereg s2 same-mirror law), so "
                "rails pin to the frozen-commit blobs, not the live dir "
                "(r78 implementation fix, zero judgment touch)"),
            "files_sha256": sha_map,
        },
        "traders": traders,
    }
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    loaded = json.load(open(OUT, encoding="utf-8-sig"))
    assert [t["id"] for t in loaded["traders"]] == ids
    print(f"anchor face written: {OUT} ({len(ids)} traders, "
          f"src={SRC_COMMIT})")
    for tid in ids:
        eo = {t["id"]: t for t in traders}[tid].get("exit_overrides")
        has_tp = any("take_profit" in str(eo)
                     for t in traders if t["id"] == tid)
        print(f"  {tid}: exit_overrides={eo} take_profit_present={has_tp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
