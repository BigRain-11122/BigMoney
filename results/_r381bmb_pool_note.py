# r381 bm-b: append diagnosis+claim note to TRIAL-LABOR-W4-GENERATE shard
# (r121 pool-entry-note precedent; single-writer claim MSG-20260928-1215).
import json

P = "results/runnable_pool.json"
d = json.load(open(P, encoding="utf-8"))
e = [x for x in d["entries"] if x.get("id") == "TRIAL-LABOR-W4-GENERATE"][0]
sh = e["shards"][0]
note = (" || r381 bm-b 12:15: 11:46 G-VOL live refusal DIAGNOSED = face "
         "divergence -- probe ran on the W1-floored load_core face "
         "(n=1631, calm 594/wild 518) but frozen anchors {519,1523,1441} "
         "reproduce ONLY on the raw full-history face "
         "data/daily/sh510300.csv (n=3483, r396 probe basis; reproduced "
         "byte-exact live this round); fix claimed bm-b per "
         "MSG-20260928-1215 (raw-face loader + anchors moved to the raw "
         "face across generate/screen-prep/screen/judge-prep/judge, "
         "structural-only checks stay on leg faces; engineering face "
         "zero science change, zero products burned, single-shot marker "
         "intact); relaunch = autofill next tick on changed runner sha "
         "(r379 fuse auto-clear law)")
if "r381 bm-b 12:15" not in sh["note"]:
    sh["note"] += note
with open(P, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(d, fh, ensure_ascii=False, indent=2)
    fh.write("\n")
print("pool note appended; shard note len", len(sh["note"]))
