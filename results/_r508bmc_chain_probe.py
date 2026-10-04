"""r508 bm-c chain-block census probe (read-only).

Purpose: W3-JUDGE custody reported ADOPT_FAIL because EXPECT.prev_total
(646799, head at spawn) != product.prev_total (647953). Determine whether
a foreign batch landed +154 trials DURING the 17:44->02:16 W3 finalize
burn (legal race -> stale-expect false negative) or a real double-count.
Faces:
  1. census: every results/**/*.json (skip _quarantine) carrying
     trials_ledger.batch -> {file, mtime, batch, prev_total,
     batch_trials, total, ts fields if any}.
  2. chain: sort by total, assert prev_total[i] == total[i-1] link
     continuity (monotone chain, zero gap/double-count) and report the
     block(s) landing between 646799 and 647953.
  3. live head via science_gates.ledger_head().
Zero mutation; receipt -> results/_r508bmc_chain_probe.json.
"""
import glob
import json
import os
import sys

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, "..", "scripts"))
sys.path.insert(0, os.path.join(_here, ".."))
import science_gates as sg  # noqa: E402

REPO = os.path.dirname(_here)
OUT = os.path.join(REPO, "results", "_r508bmc_chain_probe.json")


def main():
    blocks = []
    for path in sorted(glob.glob(os.path.join(
            REPO, "results", "**", "*.json"), recursive=True)):
        if os.sep + "_quarantine" + os.sep in path:
            continue
        try:
            st = os.stat(path)
            with open(path, encoding="utf-8") as fh:
                d = json.load(fh)
        except (OSError, ValueError):
            continue
        if not isinstance(d, dict):
            continue
        tl = d.get("trials_ledger")
        if isinstance(tl, dict) and tl.get("batch"):
            blocks.append({
                "file": os.path.relpath(path, REPO),
                "mtime": __import__("time").strftime(
                    "%Y-%m-%d %H:%M:%S",
                    __import__("time").localtime(st.st_mtime)),
                "batch": tl.get("batch"),
                "prev_total": tl.get("prev_total"),
                "batch_trials": tl.get("batch_trials"),
                "total": tl.get("total"),
                "ts_in_file": tl.get("ts") or d.get("ts")
                or d.get("evidence_cutoff") or "",
            })
    blocks.sort(key=lambda b: (b["total"] if isinstance(
        b["total"], int) else 0))
    chain_ok = True
    links = []
    for i in range(1, len(blocks)):
        gap_ok = (blocks[i]["prev_total"] == blocks[i - 1]["total"])
        links.append({
            "from": blocks[i - 1]["total"],
            "to": blocks[i]["total"],
            "batch": blocks[i]["batch"],
            "link_ok": gap_ok,
        })
        if not gap_ok:
            chain_ok = False
    foreign = [b for b in blocks
               if isinstance(b["prev_total"], int)
               and 646799 <= b["prev_total"] and b["total"] <= 647953
               and b["batch"] != "MASS_TRIAL_W3_JUDGE"]
    w3 = [b for b in blocks if b["batch"] == "MASS_TRIAL_W3_JUDGE"]
    head = sg.ledger_head()["total"]
    rec = {
        "ts": __import__("time").strftime("%Y-%m-%dT%H:%M:%S"),
        "round": "r508 bm-c",
        "n_blocks": len(blocks),
        "tail_blocks": blocks[-8:],
        "links_tail": links[-8:],
        "chain_link_all_ok": chain_ok,
        "foreign_between_646799_647953": foreign,
        "w3_blocks": w3,
        "ledger_head_live": head,
        "w3_total_matches_head":
            bool(w3) and w3[-1]["total"] == head,
    }
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(rec, f, ensure_ascii=False, indent=1)
    print("N_BLOCKS", len(blocks), "CHAIN_OK", chain_ok,
          "HEAD", head)
    for b in foreign:
        print("FOREIGN", json.dumps(b, ensure_ascii=False))
    for b in w3:
        print("W3", json.dumps(b, ensure_ascii=False))
    print("receipt ->", os.path.relpath(OUT, REPO))


if __name__ == "__main__":
    main()
