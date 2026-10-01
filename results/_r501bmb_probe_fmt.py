import io, json

for p in ["state.json", "fleet/machines/bm-b.json"]:
    raw = io.open(p, encoding="utf-8", newline="").read()
    d = json.loads(raw)
    ind0 = raw.startswith('{\n"') or '\n"' in raw[:200]
    print(p, "| bytes:", len(raw), "| CRLF:", raw.count("\r\n") > 0,
          "| flat0:", ind0, "| keys:", list(d.keys())[:10])
