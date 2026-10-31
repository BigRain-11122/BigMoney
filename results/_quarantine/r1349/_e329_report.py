import io

row = ("| 2026-11-01T05:1x+08:00 | r1349 | bm-b | **watermark: insufficient_history at open "
       "(1 ready card = E329, py idle); the round burned the ready head E329 in-round** | E329 "
       "two-vintage binding: 228 sources naming a face form 597 source-family pairs, 9 of which "
       "name two vintages of one stem (8 two dated cuts, 1 pointer pair); 1 is a real fallback "
       "chain -- e242's _face_file tries `*_latest` first and a pinned 2026-10-29 second, and no "
       "leg covers that order -- and for 2 of its 4 call-site stems (owncross, sharediff) the "
       "pinned branch is already stale against a 2026-10-30 cut on disk; 0 stems serve stale "
       "today, 2 pairs name their roles (ASOF/FRESH) and cannot race. **CURRENT:** E329 done. "
       "**LATEST PHYSICAL:** results/state_tilt/TWOVINTAGE-2026-11-01.json. **NEXT MILESTONE:** "
       "E330 uncovered fallbacks (ready, due next round, <=48h). **PRODUCT:** a pinned fallback is "
       "not a safety net -- it is the branch that fires in exactly the tree where the pointer is "
       "missing |\n")

with io.open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8", newline="\n") as fh:
    fh.write(row)
print("row written", len(row))