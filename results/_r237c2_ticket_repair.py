# r237 (bm-a): repair T-39 r116 tail truncated by _r237c insert bug (anchor text
# must be preserved as prefix of the replacement, not dropped)
import json

PATH = "fleet/tasks/T-2026-09-25-39-P1.json"
raw = open(PATH, "rb").read()
bad = b'cadence, ",\r\n'
good = b'cadence, next window ~03:41.",\r\n'
assert raw.count(bad) == 1, "repair anchor not unique: %d" % raw.count(bad)
raw2 = raw.replace(bad, good)
open(PATH, "wb").write(raw2)

obj = json.loads(raw2.decode("utf-8"))
assert obj["progress_r116"].endswith("next window ~03:41."), "r116 tail restored"
assert obj["progress_r237"].startswith("R237 bm-a"), "r237 intact"
print("repair OK: r116 tail restored, r237 intact, keys=%d" % len(obj))
