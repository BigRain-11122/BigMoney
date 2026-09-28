"""r367 fix: rejoin round-report line split by raw CRCRLF (JSON-decode control chars leaked into script source);
tidy state.json note to single-line ASCII wording."""
import io, json

# 1. round_reports.md rejoin
p = "logs/iteration-loop/round_reports.md"
raw = open(p, "rb").read()
lines = raw.split(b"\n")
# identify the broken triple: my r367 line starts at the line containing b"round 367 bm-b"
idx = next(i for i, l in enumerate(lines) if b"round 367 bm-b" in l)
seg = lines[idx:idx+2]
assert seg[0].endswith(b"x2 \r\r"), "unexpected split shape: %r" % seg[0][-30:]
assert b"round 367" not in seg[1], "second piece is not the continuation"
first = seg[0].rstrip(b"\r")
third = seg[1].lstrip(b" ")
joined = first + b"\\r\\r\\n " + third
lines[idx:idx+2] = [joined]
out = b"\n".join(lines)
open(p, "wb").write(out)
check = open(p, "rb").read()
assert check.count(b"\r\r") == 0, "raw CRCR remains"
n = len(check.split(b"\n"))
print("round_reports rejoined: lines=%d" % n)

# 2. state.json note tidy
sp = "state.json"
d = json.load(open(sp, encoding="utf-8"))
d["note"] = d["note"].replace("x2 \r\r\n heal landed", "x2 CRCR-double-terminator heal landed")
assert "\r" not in d["note"] and "\n" not in d["note"], "note still has control chars"
with io.open(sp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
    f.write("\n")
json.load(open(sp, encoding="utf-8"))
print("state.json note tidied:", d["note"][-50:])
