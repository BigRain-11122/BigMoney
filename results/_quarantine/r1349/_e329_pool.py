"""Close E329 in the runnable pool and seed E330 (the next honest gap E329 exposed)."""
import io
import json

PATH = "results/runnable_pool.json"
with io.open(PATH, encoding="utf-8") as fh:
    pool = json.load(fh)

closed = 0
for card in pool["entries"]:
    if card.get("id") == "E329-WHICH-SOURCE-READS-TWO-VINTAGES":
        card["status"] = "done"
        card["owner"] = "bm-b"
        card["closed_at"] = "2026-11-01T05:0x+08:00"
        card["result_ref"] = "results/state_tilt/TWOVINTAGE-2026-11-01.json"
        card["result_note"] = (
            "9 of 597 source-family pairs name two vintages of one stem; 1 is a real fallback chain "
            "(e242: pointer first, pinned 2026-10-29 second) with no leg covering its order, and for "
            "2 of its 4 call-site stems the pinned branch is already stale against a 2026-10-30 cut "
            "that is on disk. 0 stems serve stale today. The other real pair names its roles "
            "(asof/fresh) and cannot race.")
        closed += 1

card = {
    "id": "E330-WHICH-FALLBACK-IS-UNCOVERED",
    "lane": "cpu-only",
    "priority": 3,
    "status": "ready",
    "owner": None,
    "owner_since": None,
    "entered_at": "2026-11-01T05:0x+08:00",
    "question": (
        "E329 found one resolver whose order decides which cut a reader gets and no selftest leg "
        "naming it: e242's _face_file tries the pointer first and falls back to a pinned date. A "
        "pinned fallback is only safe while it is younger than every cut the family will ever "
        "publish, which it cannot be by construction. The wider question is mechanical: across the "
        "tree, which resolvers take a stale-vs-fresh decision that no assertion pins -- order of an "
        "existence chain, a mutable default argument, a module constant used as an argparse default, "
        "or a `dict.get(...) or OTHER` fallback -- and for each, what would a two-line change to the "
        "order silently alter?"),
    "target": (
        "every source-level construct that picks between two references to one family (order in an "
        "existence chain, `or` fallback, argparse/module default, mutable default argument), paired "
        "with whether any selftest leg, chain leg or published assertion pins the choice"),
    "deliverable": (
        "results/state_tilt/<face> + scripts/e330_*.py + chain leg + smoke leg + methodology card"),
    "source": (
        "E329 TWOVINTAGE-2026-11-01 (pairs_order_decided=1, chains_whose_order_a_leg_covers=0, "
        "stems_where_the_pinned_fallback_is_already_stale=2)"),
    "notes": (
        "seeded by r1349 bm-b at E329 close; supply floor stays breached honestly (ready 1 of floor 3)"),
}
if not any(c.get("id") == card["id"] for c in pool["entries"]):
    pool["entries"].append(card)

pool["updated_at"] = "2026-11-01T05:0x+08:00"
with io.open(PATH, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(pool, fh, indent=1, ensure_ascii=False)
    fh.write("\n")
print("closed", closed, "entries", len(pool["entries"]),
      "ready", sum(1 for c in pool["entries"] if c.get("status") == "ready"))