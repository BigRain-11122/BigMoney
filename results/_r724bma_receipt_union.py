"""r724 bm-a: union merge receipts from both windows (r516-3 law: multi-window
receipt must union, not overwrite) into the canonical receipt file."""
import json

r1 = json.load(open("results/_r724bma_merge_resolve_w1.json", encoding="utf-8"))
r2 = json.load(open("results/_r724bma_merge_resolve.json", encoding="utf-8"))

combined = {
    "round": "r724 bm-a S7 push-race merge (two-window treadmill)",
    "windows": [
        {"merge_head": r1["merge_head"], "faces": r1["faces"], "decisions": r1["decisions"]},
        {"merge_head": r2["merge_head"], "faces": r2["faces"], "decisions": r2["decisions"]},
    ],
    "note": ("window1=bm-c r538 wave (10 take-ours our-regen-newer); window2=bm-c r539 wave "
             "(10 take-theirs their-regen-newer 12:39-40); unions ran twice zero-loss; "
             "receipt union per r516-3 law (pick-window overwrite pit)"),
}
with open("results/_r724bma_merge_resolve.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(combined, ensure_ascii=False, indent=1) + "\n")
print("receipt union written: w1=%s w2=%s" % (r1["merge_head"][:9], r2["merge_head"][:9]))
