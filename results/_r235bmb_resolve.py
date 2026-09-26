"""r235 replay resolver (bm-b) -- 12-UU push-collision, TEMP-external per r231.

Classifier 12/12 zero-UNKNOWN. Recipes:
  8 snapshots + dashboard_status.js (js-wrapper): whole-side take-theirs
    (stage 3 = my r235 run 08:50-08:51 > bm-a R236 08:44-08:45 on every
    ts key: meta.generated_at / updated / ts / generated) -- done via
    `git checkout --theirs` (producer bytes verbatim, wrapper intact).
  autofill_state.json: launches union -> sort ts -> cap 50 (R215);
    last_tick theirs 08:50:02 > ours 08:40:01 -> whole dict (r203);
    CRLF working-tree mirror (r223); isinstance(last_tick, dict) assert.
  compute_audit.json: history union zero-loss (r188), latest take-new.
  regime_state.json: history union, face take-new (asof equal).
  CODELY.md: line-level memory-union (R208/r212) -- both machines' new
    entries kept verbatim, dedupe identical lines.
Parse-verify everything before exit (r185). Anchors printed for the
round report.
"""
import json
import subprocess
import sys
from collections import OrderedDict

REPO = r"C:\Users\Administrator\Desktop\Bigmoney"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def blob(ref: str) -> bytes:
    r = subprocess.run(["git", "show", ref], capture_output=True, cwd=REPO)
    if r.returncode != 0:
        raise RuntimeError(f"git show {ref} rc={r.returncode}: {r.stderr[:200]}")
    return r.stdout


def write_crlf(path: str, obj) -> None:
    text = json.dumps(obj, ensure_ascii=False, indent=1)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text.replace("\n", "\r\n"))


def dedupe_rows(rows, ts_key):
    """Union preserving newest-first ordering stability: sort by ts then
    dedupe on the ts key + machine/verdict identity via full serialization."""
    seen, out = set(), []
    for r in sorted(rows, key=lambda x: str(x.get(ts_key, "")), reverse=True):
        key = json.dumps(r, ensure_ascii=False, sort_keys=True)
        if key not in seen:
            seen.add(key)
            out.append(r)
    return list(reversed(out))  # oldest-first like the producers append


def main() -> int:
    report = []

    # ---- 1) autofill_state.json (mixed-dict+ledger) ----
    p = "results/autofill_state.json"
    o = json.loads(blob(":2:" + p).decode("utf-8"))
    t = json.loads(blob(":3:" + p).decode("utf-8"))
    lo, lt = o.get("launches", []), t.get("launches", [])
    union = dedupe_rows(lo + lt, "ts")
    union = sorted(union, key=lambda x: str(x.get("ts", "")))[-50:]  # cap50 R215
    ltick_o = (o.get("last_tick") or {}).get("ts", "")
    ltick_t = (t.get("last_tick") or {}).get("ts", "")
    last_tick = t["last_tick"] if ltick_t > ltick_o else o["last_tick"]  # tie->ours(HEAD r140)
    merged = {"launches": union, "last_tick": last_tick}
    assert isinstance(merged["last_tick"], dict), "last_tick must stay dict (r203)"
    write_crlf(p, merged)
    json.loads(open(p, encoding="utf-8").read().replace("\r\n", "\n"))
    report.append(f"autofill_state: launches {len(lo)}+{len(t)} -> union {len(union)} cap50; "
                  f"last_tick {'theirs' if ltick_t > ltick_o else 'ours'} "
                  f"({ltick_o} vs {ltick_t}); dict-assert OK")

    # ---- 2) compute_audit.json (rolling-ledger) ----
    p = "results/compute_audit.json"
    o = json.loads(blob(":2:" + p).decode("utf-8"))
    t = json.loads(blob(":3:" + p).decode("utf-8"))
    ho, ht_ = o.get("history", []), t.get("history", [])
    hu = dedupe_rows(ho + ht_, "ts")
    lo_latest = (o.get("latest") or {}).get("ts", "")
    lt_latest = (t.get("latest") or {}).get("ts", "")
    latest = t["latest"] if lt_latest > lo_latest else o["latest"]
    merged = {"history": hu, "latest": latest}
    write_crlf(p, merged)
    json.loads(open(p, encoding="utf-8").read().replace("\r\n", "\n"))
    report.append(f"compute_audit: history {len(ho)}+{len(ht_)} -> union {len(hu)} zero-loss "
                  f"(deduped {len(ho)+len(ht_)-len(hu)} identical); latest "
                  f"{'theirs' if lt_latest > lo_latest else 'ours'} ({lo_latest} vs {lt_latest})")

    # ---- 3) regime_state.json (rolling-ledger + face) ----
    p = "results/regime_state.json"
    o = json.loads(blob(":2:" + p).decode("utf-8"))
    t = json.loads(blob(":3:" + p).decode("utf-8"))
    ho, ht_ = o.get("history", []), t.get("history", [])
    hu = dedupe_rows(ho + ht_, "asof")
    merged = dict(t)  # face take-new (theirs; asof equal both sides)
    merged["history"] = hu
    merged["transitions"] = dedupe_rows(list(o.get("transitions", []))
                                        + list(t.get("transitions", [])), "ts")
    write_crlf(p, merged)
    json.loads(open(p, encoding="utf-8").read().replace("\r\n", "\n"))
    report.append(f"regime_state: history {len(ho)}+{len(ht_)} -> union {len(hu)}; "
                  f"transitions -> {len(merged['transitions'])}; face take-theirs asof={t.get('asof')}")

    # ---- 4) CODELY.md (memory-union, line-level) ----
    p = "CODELY.md"
    txt = open(p, encoding="utf-8", errors="replace").read()
    lines = txt.split("\n")
    out, ours_new, theirs_new, mode = [], [], [], "base"
    for ln in lines:
        s = ln.rstrip("\r")
        if s.startswith("<<<<<<<"):
            mode = "ours"; continue
        if s.startswith("======="):
            mode = "theirs"; continue
        if s.startswith(">>>>>>>"):
            mode = "base"; continue
        if mode == "ours":
            ours_new.append(s)
        elif mode == "theirs":
            theirs_new.append(s)
        else:
            out.append(s)
    seen = set()
    for ln in ours_new + theirs_new:  # both machines' entries, dedupe identical
        if ln not in seen:
            seen.add(ln)
            out.append(ln)
    # drop trailing empties produced by marker surgery, keep single final newline
    while out and out[-1].strip() == "":
        out.pop()
    with open(p, "w", encoding="utf-8", newline="") as fh:
        fh.write("\n".join(out) + "\n")
    report.append(f"CODELY.md: memory-union ours-block {len(ours_new)} + "
                  f"theirs-block {len(theirs_new)} -> dedup {len(seen)} unique kept")

    for r in report:
        print("  [OK]", r)
    print("resolver done: 4 constructed + (8 snapshots + js via git checkout --theirs, done by caller)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
