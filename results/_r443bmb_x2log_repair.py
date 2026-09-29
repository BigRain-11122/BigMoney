import json

path = "results/x2_watch_log.jsonl"
raw = open(path, encoding="utf-8").read()
lines = raw.split("\n")
print("raw lines:", len(lines))

out = []
bad_lines = 0
for ln in lines:
    s = ln.strip()
    if not s:
        continue
    # try parse as-is
    try:
        json.loads(s)
        out.append(s)
        continue
    except Exception:
        pass
    # split concatenated objects with a decoder loop
    decoder = json.JSONDecoder()
    pos = 0
    parts = []
    ok = True
    while pos < len(s):
        while pos < len(s) and s[pos] in " \t\r":
            pos += 1
        if pos >= len(s):
            break
        try:
            obj, end = decoder.raw_decode(s, pos)
        except Exception:
            ok = False
            break
        parts.append(json.dumps(obj, ensure_ascii=False, separators=(", ", ": ")))
        pos = end
    if ok and parts:
        bad_lines += 1
        out.extend(parts)
    else:
        print("UNREPAIRABLE:", s[:120])
        out.append(s)

n_obj = sum(1 for l in out if json.loads(l))
print("repaired-lines:", bad_lines, "| objects:", n_obj)
with open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(out) + "\n")
# verify
c = 0
for l in open(path, encoding="utf-8"):
    if l.strip():
        json.loads(l)
        c += 1
print("post-write verify objects:", c, "ALL-PARSE-OK")
