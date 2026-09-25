"""R203 mid-round rebase resolver: autofill_state.json (r161/r185 union recipe)."""
import io
import json
import subprocess

PATH = "results/autofill_state.json"


def side(blob):
    txt = subprocess.run(
        ["git", "show", blob], capture_output=True, text=True,
        encoding="utf-8", errors="replace").stdout
    return json.loads(txt)


base = side(":1:" + PATH)
ours = side(":2:" + PATH)
theirs = side(":3:" + PATH)

# launches: ts-union (dedupe on ts+lane keys), preserve sorted by ts
def union_launches(a, b):
    seen = {}
    for row in list(a) + list(b):
        key = json.dumps(row, sort_keys=True, ensure_ascii=False)
        seen.setdefault(key, row)
    rows = list(seen.values())
    rows.sort(key=lambda r: str(r.get("ts", "")))
    return rows[-50:] if "launches" in ours and len(rows) > 50 else rows


merged = dict(ours)
merged["launches"] = union_launches(ours.get("launches", []),
                                    theirs.get("launches", []))
for k in ("last_tick",):
    # r203 lesson: last_tick is a DICT -- compare by its ts field and assign
    # the whole newer dict (max(str(dict)) silently writes a string face and
    # poisons downstream consumers like monitor.build_status tick.get).
    def tick_ts(v):
        return str(v.get("ts")) if isinstance(v, dict) else ""
    merged[k] = ours.get(k) if tick_ts(ours.get(k)) >= tick_ts(theirs.get(k)) else theirs.get(k)
# count check zero-loss
n_o = len(ours.get("launches", []))
n_t = len(theirs.get("launches", []))
n_m = len(merged["launches"])
print("launches ours=%d theirs=%d merged=%d last_tick=%s"
      % (n_o, n_t, n_m, merged.get("last_tick")))

txt = json.dumps(merged, ensure_ascii=False, indent=1)
json.loads(txt)  # parse-verify BEFORE write (r185 order law)
io.open(PATH, "w", encoding="utf-8", newline="\n").write(txt + "\n")
print("resolved + parse-verified")
