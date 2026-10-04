# r670 bm-a: T-167 ticket progress_r670 append (programmatic write + parse self-check)
import json

P = "fleet/tasks/T-2026-10-04-167-P1.json"
d = json.load(open(P, encoding="utf-8"))
d["progress_r670"] = (
    "r670 bm-a: s3 CRASH-HEAL + RELIGHT (claim continuation, same ticket): first daemon "
    "burn 10:00:31 died at null-family assembly assert (10:01:30; fuse confirm 10:05:36, "
    "refusals 4). Root cause = ci semantics double-track in runner: task-gen emits ci as "
    "k-start offsets range(0,K,CHUNK)={0,100..1900} but _null_chunk computed "
    "ks=range(ci*CHUNK,(ci+1)*CHUNK) treating ci as chunk index -> 38/40 chunks EMPTY "
    "(ks=[]), assembly assert len==2000 false. Second latent bug: checkpoint scanner "
    "startswith('chunk_') never matches real frag names TJ-*_chunk_*.json (resume never "
    "skipped) AND would have skipped poisoned empty frags if it had matched. Fix (minimal, "
    "zero frozen-quantity touch: same K=2000, same rng([20585000,k]) per-k substreams, same "
    "ks coverage 0..1999 exactly once per stratum): ks=range(ci,min(ci+CHUNK,K)); scanner "
    "f.endswith('.json') + non-empty-ks guard. Selftest +1 leg: mini-pipeline ks-tiling "
    "== 0..K-1 (would have caught this exact bug) -> 16/16. Verify legs: AST gate, "
    "per-stratum 2000-ks tiling arithmetic, on-disk 2 healthy chunk_00 reusable + 38 "
    "poisoned recompute list (results/_r670bma_fix_verify.py ALL PASS). Commit sha change "
    "-> fuse auto-cleared 10:16:04 (code_changed tombstone) -> daemon claim OK 10:19:01 "
    "-> C8 LAUNCH pid=12372 10:19:01 (relight verified alive; ~9-10min ETA; finalize = "
    "owner-side next step once burn_state.json lands: gates + verdict + ledger 8004 + "
    "attrition r248 + THEME_JUDGE_P1.md sec.7/8 backfill)."
)
tmp = P + ".tmp"
with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(d, fh, ensure_ascii=False, indent=2)
import os
os.replace(tmp, P)
chk = json.load(open(P, encoding="utf-8"))
assert "progress_r670" in chk and chk["status"] == "claimed"
print("T-167 progress_r670 landed, parse self-check PASS")
