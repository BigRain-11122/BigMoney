"""r376 bm-a: field-level diff -- same composite-key rows, union of
field faces per key vs shared row (r375 fix contract check)."""
import json

sh = json.load(open(r"results\autofill_state.json", encoding="utf-8"))
lanes = {}
for m in ("bm-a", "bm-b", "bm-c"):
    try:
        lanes[m] = json.load(
            open(rf"results\autofill_state.{m}.json", encoding="utf-8"))
    except FileNotFoundError:
        pass


def key(r):
    return (r.get("ts"), r.get("machine"), r.get("pid"), r.get("sha256"),
            r.get("entry"), r.get("shard"))


sh_rows = {key(r): r for r in sh.get("launches", [])}
# union per key (r375 fix: field-union keep-one)
union = {}
for m, ln in lanes.items():
    for r in ln.get("launches", []):
        k = key(r)
        if k not in union:
            union[k] = dict(r)
        else:
            for f, v in r.items():
                if f not in union[k]:
                    union[k][f] = v
                elif union[k][f] != v and f != "lane_machine":
                    print(f"TRUE-DIVERGENCE key={k} field={f}: "
                          f"merged={union[k][f]!r} vs {m}={v!r}")
ndiff = 0
for k, u in union.items():
    s = sh_rows.get(k)
    if s is None:
        print("lane-only row:", k)
        continue
    extra = set(u) - set(s)
    # ignore lane_runtime extras vs shared? report all non-shared fields
    if extra and extra != {"lane_machine"}:
        ndiff += 1
        print(f"key={k} extra-fields-in-union: {sorted(extra)}")
        for f in sorted(extra):
            if f != "lane_machine":
                print(f"   {f} = {u[f]!r}  (shared row lacks field)")
print("rows with field diff:", ndiff)
# top-level face diff
sh_top = {k: v for k, v in sh.items() if k != "launches"}
un_top = {}
for m, ln in lanes.items():
    for k, v in ln.items():
        if k == "launches":
            continue
        if k not in un_top:
            un_top[k] = v
        elif un_top[k] != v:
            print(f"top-level divergence {k}: {un_top[k]!r} vs {m}={v!r}")
print("shared top-level keys:", sorted(sh_top))
print("union top-level keys:", sorted(un_top))
