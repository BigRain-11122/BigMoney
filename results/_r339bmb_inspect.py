# r291 bm-b: inspect both sides vs base (fixed) + format detection for write-back
import json

def load(p):
    with open(p, "rb") as f:
        raw = f.read()
    return raw, json.loads(raw.decode("utf-8"))

base_raw, base = load("results/_r291bmb_blobs/base.r291bmb.json")
ours_raw, ours = load("results/_r291bmb_blobs/ours.r291bmb.json")
theirs_raw, theirs = load("results/_r291bmb_blobs/theirs.r291bmb.json")

print("first 160 bytes base:", repr(base_raw[:160]))
print("first 160 bytes ours:", repr(ours_raw[:160]))
print("first 160 bytes theirs:", repr(theirs_raw[:160]))

def sig(e):
    return json.dumps(e, sort_keys=True)

base_set = {sig(e) for e in base["launches"]}
for side, name in ((ours, "ours"), (theirs, "theirs")):
    sl = [sig(e) for e in side["launches"]]
    ss = set(sl)
    new = ss - base_set
    print(f"--- {name}: launches={len(sl)} unique={len(ss)} new_vs_base={len(new)} dup_in_side={len(sl)-len(ss)}")
    for e in sorted(new):
        d = json.loads(e)
        print("   ", d.get("ts"), d.get("machine"), d.get("entry"), d.get("shard"), d.get("verdict"), "pid", d.get("pid"))

print("last_tick ts base/ours/theirs:", base["last_tick"].get("ts"), "|", ours["last_tick"].get("ts"), "|", theirs["last_tick"].get("ts"))
print("last_tick machine ours/theirs:", ours["last_tick"].get("machine"), "|", theirs["last_tick"].get("machine"))
print("ours==base launches set:", {sig(e) for e in ours["launches"]} == base_set or None)
print("theirs launches subset of base:", {sig(e) for e in theirs["launches"]} - base_set == set())
print("union size:", len(base_set | {sig(e) for e in ours["launches"]} | {sig(e) for e in theirs["launches"]}))
# indent detection: count leading spaces of the "launches" key line
for name, raw in (("base", base_raw), ("ours", ours_raw), ("theirs", theirs_raw)):
    for line in raw.split(b"\n"):
        if b'"launches"' in line:
            print(name, "launches-key line:", repr(line[:20]))
            break
