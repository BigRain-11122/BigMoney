"""r376 bm-a: autofill_state shared-face field restoration -- V2-P1
02:30:01 launch row lost its crash_counted=True enriched face in the
r375 push-storm union resolve (tie->HEAD took bm-a's stale side);
launching machine bm-b's lane holds the authoritative truth (only the
launcher can confirm its own crash). Restore the field on the shared
face + mirror bm-a's own lane (R31: foreign lanes untouched)."""
import json
import os

SHARED = r"results\autofill_state.json"
LANE_A = r"results\autofill_state.bm-a.json"
KEY = ("2026-09-28 02:30:01", "bm-b", 24976, "880297a0fb0854bf",
       "DECISION-CHAIN-V2-P1", "v2-0of1")


def key(r):
    return (r.get("ts"), r.get("machine"), r.get("pid"),
            r.get("runner_sha256"), r.get("entry"), r.get("shard"))


def patch(path, want_machines):
    with open(path, encoding="utf-8") as fh:
        st = json.load(fh)
    hit = 0
    for r in st.get("launches", []):
        if key(r) == KEY and r.get("machine") in want_machines:
            before = r.get("crash_counted")
            r["crash_counted"] = True
            if before is not True:
                hit += 1
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(st, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, path)
    return hit


h1 = patch(SHARED, {"bm-b"})
h2 = patch(LANE_A, {"bm-b"})
print(f"shared patched rows={h1}; bm-a lane patched rows={h2}")

# verify: relaunch guard reads back True on both faces
for path in (SHARED, LANE_A):
    with open(path, encoding="utf-8") as fh:
        st = json.load(fh)
    rows = [r for r in st.get("launches", []) if key(r) == KEY]
    print(path, "->", [r.get("crash_counted") for r in rows],
          "launches:", len(st.get("launches", [])))
