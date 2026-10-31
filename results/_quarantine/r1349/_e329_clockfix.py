import io, json

# 校时修正: the clock read at closeout is 2026-11-01T04:33+08:00, not the 05:1x I typed from memory.
fixes = [("logs/iteration-loop/round_reports.md", "2026-11-01T05:1x+08:00", "2026-11-01T04:33:00+08:00")]
for path, old, new in fixes:
    with io.open(path, encoding="utf-8", newline="") as fh:
        text = fh.read()
    if old in text:
        text = text.replace(old, new)
        with io.open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        print("fixed", path)
    else:
        print("nothing to fix in", path)

path = "results/runnable_pool.json"
with io.open(path, encoding="utf-8") as fh:
    pool = json.load(fh)
pool["updated_at"] = "2026-11-01T04:33:00+08:00"
for card in pool["entries"]:
    if card.get("id") == "E329-WHICH-SOURCE-READS-TWO-VINTAGES":
        card["closed_at"] = "2026-11-01T04:33:00+08:00"
    if card.get("id") == "E330-WHICH-FALLBACK-IS-UNCOVERED":
        card["entered_at"] = "2026-11-01T04:33:00+08:00"
with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(pool, fh, indent=1, ensure_ascii=False)
    fh.write("\n")
print("pool timestamps aligned to the clock read")