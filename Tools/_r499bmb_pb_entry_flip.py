"""r499 bm-b: PORTFOLIO-BOOK-P1-BURN entry-layer dual-done flip (r489 phantom-face
heal, bm-c r306 precedent adapted to exact-id scope).

Observing closure: entry has shard-layer done (bm-a r506 burn + judged-negative
same-round close, products committed) but entry-layer still ready -- the r489
two-layer phantom face (daemon never lands the entry half by design). This ghost
is the sole remaining live=1 that blocks the PERPETUAL_FACES sec.1 supply trigger
(N1-W4 wave). Guards: flip entry->done ONLY if every shard is done (no-phantom),
never revert done->ready, zero touches outside the exact id. Pool format law
(r289): indent2 + CRLF probe, write then surgical diff assert (shell side).
"""
import json
import sys

SRC = "results/runnable_pool.json"
TARGET = "PORTFOLIO-BOOK-P1-BURN"

with open(SRC, "rb") as f:
    raw = f.read()
crlf = raw.count(b"\r\n")
lf_only = raw.count(b"\n") - crlf
assert crlf > 0 and lf_only == 0, f"pool line-ending probe: CRLF={crlf} LF-only={lf_only}"

pool = json.loads(raw.decode("utf-8"))
flipped, skipped = [], []
for e in pool["entries"]:
    if str(e.get("id", "")) != TARGET:
        continue
    shards = e.get("shards", [])
    all_done = bool(shards) and all(s.get("status") == "done" for s in shards)
    if e.get("status") == "done":
        skipped.append((e["id"], "already-done"))
    elif all_done:
        e["status"] = "done"
        flipped.append(e["id"])
    else:
        skipped.append((e["id"], f"shards-not-all-done {[s.get('status') for s in shards]}"))

if flipped:
    # r289 format law (r499 live-fire lesson): NEVER hardcode indent -- the
    # pool file's producer format alternates across lane writers (bm-b
    # generator indent2 vs bm-a autofill indent1 observed 10-01); probe and
    # mirror, else whole-file diff (7054-line incident caught by diff --stat
    # and healed in-window).
    with open(SRC, "rb") as f:
        raw2 = f.read()
    lines2 = raw2.decode("utf-8").splitlines()
    probe_indent = 2
    for line in lines2:
        if line.strip():
            probe_indent = len(line) - len(line.lstrip(" "))
            break
    probe_crlf = raw2.count(b"\r\n") > 0
    probe_trailing = raw2.endswith(b"\n")
    s = json.dumps(pool, ensure_ascii=False, indent=probe_indent)
    if probe_crlf:
        s = s.replace("\n", "\r\n")
    if probe_trailing and not s.endswith("\r\n"):
        s += "\r\n" if probe_crlf else "\n"
    with open(SRC, "w", newline="", encoding="utf-8") as f:
        f.write(s)

print("flipped:", flipped)
print("skipped:", skipped)
results = {"flipped": flipped, "skipped": skipped,
           "guards": "all-shards-done + no-revert + exact-id-scoped",
           "evidence": "bm-a r506 6fd125422 burn+judged-negative close; shard layer done; "
                       "products results/portfolio_book/ committed"}
with open("results/_r499bmb_pb_entry_flip.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
sys.exit(0)
