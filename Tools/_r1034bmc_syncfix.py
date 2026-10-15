"""r1034 bm-c sync-face honesty patch: push raced twice in the bm-a/bm-b hot
window -> branch fallback landed (machine/bm-c-r1034 = 9fdf36ba5, ls-remote
verified). Updates state/heartbeat sync faces + report addendum row. No
history edits, append/patch only."""
import datetime
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HEART = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
REPORT = os.path.join(ROOT, "round_reports-bm-c.md")

iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

sync = {
    "origin_tip": ("c1f67faba (r1034 push raced x2 in hot window: first "
                   "rejection -> pull --rebase retry lawfully consumed "
                   "[daily_report conflict resolved newer-mine, rebase "
                   "clean] -> second rejection mid-rebase by c1f67faba -> "
                   "branch fallback per law)"),
    "ts": iso,
    "ahead_behind": ("local-ahead-1: r1034 = 9fdf36ba5 (base 5e71102e2) not "
                     "yet on origin/main; durable backup branch "
                     "machine/bm-c-r1034 = 9fdf36ba5 pushed + ls-remote "
                     "verified; r1035 S0 = fetch + rebase onto origin/main "
                     "+ closeout push (r1009 precedent self-heal)"),
}
push_note = ("r1034 push saga: first push rejected (origin advanced "
             "5e71102e2/024388e2f) -> pull --rebase hit r784 multi-branch "
             "pit -> direct rebase origin/main (r1000 path) -> stash-bridge "
             "-> rebase clean 9fdf36ba5 (one conflict docs/daily_report/"
             "REPORT-2026-10-15.json resolved newer-mine = my 19:03 S6 "
             "regeneration vs bm-a 18:40 re-derive, idempotent same-day "
             "regenerable) -> push rejected AGAIN (c1f67faba landed "
             "mid-flight) -> branch fallback origin machine/bm-c-r1034 = "
             "9fdf36ba5 PUSHED + ls-remote VERIFIED; stash bridges x2 "
             "dropped identity-verified live-wins (runnable_pool daemon "
             "face + watermark_red probe face, both regenerable, committed "
             "snapshots ride in 9fdf36ba5); r1008 legacy stash protected "
             "intact; tail dual-scan ORD/DEC FALSE vs self-advanced "
             "watermark f48fdb82 = zero double-count risk for r1035")

for path in (STATE, HEART):
    with open(path, "r", encoding="utf-8") as fh:
        d = json.load(fh)
    d["sync"] = sync
    d["head_sha"] = ("9fdf36ba5 (r1034 local; origin/main c1f67faba; "
                     "branch machine/bm-c-r1034 = same, verified)")
    d["r1034_push_note"] = push_note
    if "verify" in d and isinstance(d["verify"], str):
        d["verify"] = (d["verify"] + " ; PUSH-HONESTY: raced x2 hot window, "
                       "branch fallback landed + verified, r1035 S0 "
                       "rebases+pushes main")
    d["last_pulled_at"] = iso
    tmp = path + ".tmp_r1034b"
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        fh.write(json.dumps(d, ensure_ascii=False, indent=1))
    os.replace(tmp, path)

row = (iso + " | r1034 addendum | bm-c | PUSH SAGA honesty: origin raced "
       "twice during closeout (bm-a/bm-b hot window: 5e71102e2/024388e2f "
       "then c1f67faba mid-rebase); one lawful pull --rebase retry executed "
       "(r784 pit -> direct rebase origin/main path; daily_report conflict "
       "resolved newer-mine; rebase clean 9fdf36ba5); second rejection -> "
       "BRANCH FALLBACK per law: origin machine/bm-c-r1034 = 9fdf36ba5 "
       "pushed + ls-remote VERIFIED; stash bridges x2 dropped "
       "identity-verified live-wins (regenerable faces; r1008 legacy "
       "protected) | tail dual-scan ORD/DEC FALSE vs self-advanced "
       "watermark f48fdb82 (zero double-count) | r1035 S0 = fetch + "
       "rebase onto origin/main + push main (r1009 precedent, "
       "local-ahead-1 self-heals same window)\n")
with open(REPORT, "a", encoding="utf-8", newline="\n") as fh:
    fh.write(row)
print("sync faces patched; report addendum appended", iso)
