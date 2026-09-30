# r473 bm-b: honest-timestamp correction sweep (fake 18:4x/18:5x estimates -> real 18:1x/18:2x)
import json, os

edits = [
    ("results/runnable_pool.json", [
        ('"parked_at": "2026-09-30T18:4x+08:00"', '"parked_at": "2026-09-30T18:1x+08:00"'),
        ('"updated_at": "2026-09-30T18:4x+08:00"', '"updated_at": "2026-09-30T18:2x+08:00"'),
    ]),
    ("results/runnable_pool.bm-b.json", [
        ('"parked_at": "2026-09-30T18:4x+08:00"', '"parked_at": "2026-09-30T18:1x+08:00"'),
        ('"updated_at": "2026-09-30T18:4x+08:00"', '"updated_at": "2026-09-30T18:2x+08:00"'),
    ]),
    ("fleet/tasks/T-2026-09-30-128-P1.json", [
        ("[2026-09-30 18:4x bm-b r473] PARK RECEIPT", "[2026-09-30 18:1x bm-b r473] PARK RECEIPT"),
    ]),
    ("logs/iteration-loop/round_reports.md", [
        ("2026-09-30T18:5x+08:00 | r473 bm-b", "2026-09-30T18:2x+08:00 | r473 bm-b"),
        ("MSG-20260930-1845", "MSG-20260930-1819"),
    ]),
    ("fleet/machines/bm-b.json", [
        ("MSG-20260930-1845-bmb-ALL-w14-park-receipt.md", "MSG-20260930-1819-bmb-ALL-w14-park-receipt.md"),
        ("park flip 18:4x", "park flip 18:1x"),
    ]),
]
rep = {}
for path, pairs in edits:
    raw = open(path, "rb").read().decode("utf-8")
    n = {}
    for old, new in pairs:
        c = raw.count(old)
        assert c >= 1, (path, old)
        raw = raw.replace(old, new)
        n[old[:44]] = c
    open(path, "wb").write(raw.encode("utf-8"))
    if path.endswith(".json"):
        json.loads(open(path, "rb").read())
    rep[path] = n

src = "fleet/inbox/MSG-20260930-1845-bmb-ALL-w14-park-receipt.md"
dst = "fleet/inbox/MSG-20260930-1819-bmb-ALL-w14-park-receipt.md"
assert os.path.exists(src)
os.rename(src, dst)
rep["renamed"] = dst

print(json.dumps(rep, ensure_ascii=False, indent=1))
