import re, json, sys

p = r"results\watermark_red.json"
raw = open(p, encoding="utf-8", errors="replace").read()
mm = re.search(r"<<<<<<<[^\n]*\n(.*?)\n?=======\n(.*?)\n?>>>>>>>[^\n]*", raw, re.S)
if not mm:
    print("NO_MARKERS")
    sys.exit(0)
mine, theirs = mm.group(1), mm.group(2)

def ts_of(block):
    m = re.search(r'"ts"\s*:\s*"([^"]+)"', block) or re.search(r'"(?:asof|timestamp)"\s*:\s*"([^"]+)"', block)
    return m.group(1) if m else "none"

def red_of(block):
    m = re.search(r'"red"\s*:\s*(true|false)', block)
    return m.group(1) if m else "?"

tm, tt = ts_of(mine), ts_of(theirs)
print("mine ts:", tm, "| theirs ts:", tt)
winner = "theirs" if (tt and tt >= tm) else "mine"
block = theirs if winner == "theirs" else mine
out = raw[:mm.start()] + block + raw[mm.end():]
# validate JSON after strip of wrapper keys
try:
    json.loads(out)
    print("JSON_VALID")
except Exception as e:
    print("JSON_INVALID", e)
    sys.exit(1)
open(p, "w", encoding="utf-8", newline="").write(out)
print("WINNER:", winner)
