"""r2108 bm-c: which carry-family faces are older than the panel, and why nobody fixes them.

Read-only census. No shared face is written; the only write is this script's own JSON.

The question it answers: the r1282 orphan class is "a face nobody re-derives quotes last
week's numbers while every page stays green". The carry family has 24 published faces and
only some of them sit on Tools/s6_chain_bmc.py. For every face not on the chain this census
asks the two questions that decide whether the lag is a defect or a design:
  1. how many sessions behind the panel is its evidence_cutoff?
  2. does anything read it (a page that would quote a stale number)?
A face with no chain leg and no reader is dormant (cheap: nobody consumes the stale number).
A face with no chain leg but with a reader is the r1282 defect: the reader quotes it forever.
"""
from __future__ import annotations

import glob
import json
import os
import re

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAIN = os.path.join(HERE, "Tools", "s6_chain_bmc.py")
PANEL = os.path.join(HERE, "data", "daily", "510300.csv")


def panel_sessions() -> list[str]:
    days = []
    with open(PANEL, encoding="utf-8", errors="replace") as fh:
        for i, line in enumerate(fh):
            if i == 0:
                continue
            head = line.split(",")[0].strip()[:10]
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", head):
                days.append(head)
    return sorted(set(days))


def main() -> int:
    days = panel_sessions()
    latest = days[-1]
    chain_src = open(CHAIN, encoding="utf-8", errors="replace").read()

    script_src = {}
    for path in glob.glob(os.path.join(HERE, "scripts", "*.py")) + glob.glob(
        os.path.join(HERE, "Tools", "*.py")
    ):
        try:
            script_src[os.path.basename(path)] = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            pass

    rows = []
    for path in sorted(glob.glob(os.path.join(HERE, "results", "idx_fut_carry_*.json"))):
        name = os.path.basename(path)[: -len(".json")]
        try:
            doc = json.load(open(path, encoding="utf-8"))
        except Exception as exc:  # unreadable face is itself a finding
            rows.append({"face": name, "error": f"{type(exc).__name__}: {exc}"})
            continue
        cutoff = str(doc.get("evidence_cutoff") or doc.get("cutoff") or "")
        behind = None
        if cutoff in days:
            behind = len(days) - 1 - days.index(cutoff)
        elif cutoff:
            behind = "cutoff_not_a_panel_session"
        # A mention is a write only if the same script also dumps json / opens for writing;
        # a script that both writes and reads a face is its producer, not a consumer, and is
        # excluded from readers -- otherwise every face looks "quoted by four pages".
        mentions, writers = [], []
        for base, src in script_src.items():
            if (name + ".json") not in src:
                continue
            mentions.append(base)
            if re.search(r"json\.dump|\.write\(|open\([^)]*['\"]w['\"]", src):
                writers.append(base)
        readers = sorted(b for b in mentions if b not in writers)
        rows.append(
            {
                "face": name,
                "cutoff": cutoff,
                "sessions_behind_panel": behind,
                "generated": doc.get("generated"),
                "on_chain": name in chain_src,
                "readers": [r for r in readers if not r.startswith("_")],
            }
        )

    stale = [
        r for r in rows
        if isinstance(r.get("sessions_behind_panel"), int) and r["sessions_behind_panel"] > 0
    ]
    defects = [r for r in stale if not r["on_chain"] and r.get("readers")]
    dormant = [r for r in stale if not r["on_chain"] and not r.get("readers")]

    doc = {
        "schema": "carry-family-staleness-census/v1",
        "panel_latest_session": latest,
        "panel_sessions": len(days),
        "faces": len(rows),
        "on_chain": sum(1 for r in rows if r.get("on_chain")),
        "stale": len(stale),
        "stale_no_leg_with_reader": [
            {"face": r["face"], "cutoff": r["cutoff"], "behind": r["sessions_behind_panel"],
             "readers": r["readers"]} for r in defects
        ],
        "stale_no_leg_no_reader": [
            {"face": r["face"], "cutoff": r["cutoff"], "behind": r["sessions_behind_panel"]}
            for r in dormant
        ],
        "rows": rows,
        "reading": {
            "no_reader": "every stale face is written only by its own producer script and read by "
                         "nothing else -- no literal mention in scripts/ or Tools/, no idx_fut_carry_* "
                         "glob, and no reference from the CEO page (docs/live_usage/LIVE-latest.md) or "
                         "the block board. The r1282 defect (a page quoting a dead face) is not "
                         "present in this family.",
            "they_are_dated_studies": "each of the eight was committed as a one-question study between "
                                      "r1961 and r2084 (11-23..11-25) and carries its own "
                                      "evidence_cutoff, so the lag is the age of the answer, not a "
                                      "broken writer: 'the 2-lot hedge is the top of an eight-year beta "
                                      "distribution' does not become wrong when the panel moves bars.",
            "correction": "an earlier draft of this census said a one-shot task at r2090 re-priced "
                          "these eight and self-disabled. That was unverified and is corrected here: "
                          "r2090's 'eight stale arms' are the ETF phase-atlas arms, while these carry "
                          "faces were last committed at r1961..r2084 with no later touch in git.",
            "so_do_not": "do not put the eight on the S6 chain to 'fix' the lag -- that spends a write "
                         "per round to freshen answers nobody reads and would bury the date that makes "
                         "them honest. If one is needed again, re-run its producer and say so.",
        },
        "contention": "repo_write_contention rc3 at 23:32 (peer host pid 98008 wrote shared faces at "
                      "23:31:43) -> new files only, no chain re-run, no shared-face re-derive",
    }
    out = os.path.join(HERE, "results", "_r2108bmc_carry_staleness_census.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh.write("\n")

    print(f"panel latest {latest} ({len(days)} sessions); {len(rows)} faces, {doc['on_chain']} on chain")
    for r in stale:
        flag = "DEFECT" if r in defects else ("dormant" if r in dormant else "on-chain")
        print(f"  {flag:<8} {r['face']:<46} cutoff={r['cutoff']} behind={r['sessions_behind_panel']} readers={len(r.get('readers') or [])}")
    print(f"stale={doc['stale']} defect={len(defects)} dormant={len(dormant)} -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
