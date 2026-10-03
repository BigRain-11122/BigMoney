import json

for face in ("x1", "x2"):
    path = rf"results\fund_divlowvol_p1\cells_DIVLOWVOL-YIELDVOL_{face}.jsonl"
    rows = 0
    syms = set()
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        rows += 1
        r = json.loads(line)
        blob = json.dumps(r, ensure_ascii=False)
        for m in blob.replace('"', " ").replace(",", " ").split():
            if len(m) == 6 and m.isdigit():
                syms.add(m)
    n68 = sorted(s for s in syms if s.startswith("68"))
    print(face, "rows:", rows, "| 68x syms:", len(n68), n68[:8])
