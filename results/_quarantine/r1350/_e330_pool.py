"""Close E330 on the board (done + result_ref) and seed E331. Owner-written, append-only semantics."""
import io
import json
import os

POOL = os.path.join("results", "runnable_pool.json")
doc = json.load(io.open(POOL, encoding="utf-8"))
entries = doc["entries"]

face = "results/state_tilt/UNPINNEDCHOICE-2026-11-01.json"
closed = 0
for row in entries:
    if row.get("id") == "E330-WHICH-FALLBACK-IS-UNCOVERED":
        row["status"] = "done"
        row["owner"] = "bm-b"
        row["owner_since"] = "2026-11-01T04:48:00+08:00"
        row["done_at"] = "2026-11-01T05:35:00+08:00"
        row["result_ref"] = face
        row["result"] = ("1 two-reference decision in 2284 sources, 0 pinned; the only one is "
                         "e242's pointer-first chain, and for 2 of its 4 call-site stems a swap "
                         "returns 2026-10-29 instead of 2026-10-30 today; 34 one-sided `or` lines "
                         "rejected and published; 0 argparse defaults name a face; 0 mutable "
                         "defaults in 646k code lines")
        closed += 1

if not any(r.get("id", "").startswith("E331") for r in entries):
    entries.append({
        "id": "E331-POINTER-ONLY-READERS",
        "lane": "cpu-only",
        "priority": 3,
        "status": "ready",
        "owner": None,
        "owner_since": None,
        "entered_at": "2026-11-01T05:35:00+08:00",
        "question": ("E330 found the tree's single two-reference decision and it is a pointer-first "
                     "chain with a dated fallback. E327 found 143 pairs whose readers never see a "
                     "date in a file name, i.e. they resolve through a `_latest` pointer alone. A "
                     "pointer with no fallback is a reader that gets nothing in a tree where the "
                     "pointer is absent or points at a cut that is not on disk. Count pointer-only "
                     "readers and, for each, whether the None is handled: an explicit branch, a "
                     "raise, or a silent attribute access that would fail far from its cause."),
        "target": ("every reader that resolves a family through a `_latest` pointer and nothing "
                   "else, paired with how it handles the missing-file case"),
        "deliverable": ("results/state_tilt/<face> + scripts/e331_*.py + chain leg + smoke leg + "
                        "methodology card"),
        "source": ("E330 UNPINNEDCHOICE-2026-11-01 (decisions=1, unpinned=1, chains_whose_"
                   "fallback_lags=1) + E327 pointer pairs"),
        "notes": "seeded by r1350 bm-b at E330 close; supply floor stays breached honestly (ready 1 of 3)",
    })

with io.open(POOL, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(doc, fh, indent=1, ensure_ascii=False)
    fh.write("\n")

done = sum(1 for r in entries if r.get("status") == "done")
ready = [r["id"] for r in entries if r.get("status") == "ready"]
print("closed", closed, "entries", len(entries), "done", done, "ready", ready)