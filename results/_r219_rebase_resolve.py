# r161/r203 union resolver v2: conflict block sits mid-file -> prefix + winning-side + tail rebuild
import io, json, re

PATH = r"C:\Users\Administrator\Desktop\Bigmoney\results\autofill_state.json"
raw = io.open(PATH, "r", encoding="utf-8").read()

blocks = re.findall(r"^<<<<<<<", raw, flags=re.M)
print("conflict_blocks:", len(blocks))
assert len(blocks) == 1

start = re.search(r"^<<<<<<< HEAD\r?\n", raw, flags=re.M)
mid = re.search(r"^=======$\r?\n", raw[start.end():], flags=re.M)
end = re.search(r"^>>>>>>> [^\r\n]*\r?\n", raw, flags=re.M)
prefix = raw[:start.end()]            # includes everything before <<<<<<< line
side_head = raw[start.end():start.end() + mid.start()]
side_mine = raw[start.end() + mid.end():end.start()]
tail = raw[end.end():]
print("side_head:", repr(side_head))
print("side_mine:", repr(side_mine))

# pick winning side by last_tick ts (r203: compare inside, assign whole side)
ts_re = re.compile(r'"ts":\s*"([^"]+)"')
ts_h, ts_m = ts_re.search(side_head).group(1), ts_re.search(side_mine).group(1)
winning, win_ts = (side_mine, ts_m) if ts_m >= ts_h else (side_head, ts_h)
resolved_txt = raw[:start.start()] + winning + tail
print("winning ts:", win_ts)

d = json.loads(resolved_txt)
assert isinstance(d.get("last_tick"), dict), "last_tick must stay dict"
assert isinstance(d.get("launches"), list), "launches must stay list"
# duplicate-launch scan (dedupe check: git automerge should have unioned cleanly)
keys = set()
dups = 0
for row in d["launches"]:
    k = json.dumps(row, sort_keys=True)
    if k in keys:
        dups += 1
    keys.add(k)
print("launches:", len(d["launches"]), "dups:", dups)
assert d["last_tick"]["ts"] == win_ts
io.open(PATH, "w", encoding="utf-8").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
chk = json.loads(io.open(PATH, "r", encoding="utf-8").read())
assert isinstance(chk["last_tick"], dict) and chk["last_tick"]["ts"] == win_ts
print("RESOLVE_OK last_tick=%s launches=%d dups=%d" % (chk["last_tick"], len(chk["launches"]), dups))
