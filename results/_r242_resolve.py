"""r242 resolver: stash-pop UU on results/autofill_state.json (bm-b).

Recipe = bigmoney-conflict-resolve mixed-dict+ledger (r203/R208/r215/r220/r223):
- last_tick: compare by internal ts, whole-dict assign (newer wins; same-sec tie -> HEAD)
- launches: union by identity key, sort by ts, cap 50 (R215)
- write back mirroring producer CRLF (r223/r234: newline='\r\n' translation)
- json.loads re-verify + isinstance(last_tick, dict) assert before add (r185/r203)
"""
import io
import json
import subprocess
import sys

PATH = "results/autofill_state.json"


def _blob(rev):
    out = subprocess.run(["git", "show", rev + ":" + PATH], capture_output=True)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.decode("utf-8", "replace"))
    return out.stdout


def _resolve():
    head = json.loads(_blob("HEAD"))
    stashed = json.loads(_blob("stash@{0}"))

    lt_h, lt_s = head.get("last_tick") or {}, stashed.get("last_tick") or {}
    ts_h, ts_s = lt_h.get("ts", ""), lt_s.get("ts", "")
    # r140: same-second tie -> HEAD; else newer ts wins; whole-dict assign (R203)
    last_tick = dict(lt_s) if ts_s > ts_h else dict(lt_h)
    assert isinstance(last_tick, dict), "last_tick must stay dict (R203)"

    seen, merged = set(), []
    for row in head.get("launches", []) + stashed.get("launches", []):
        key = (row.get("ts"), row.get("entry"), row.get("machine"), row.get("pid"))
        if key in seen:
            continue
        seen.add(key)
        merged.append(dict(row))
    merged.sort(key=lambda r: r.get("ts", ""))
    launches = merged[-50:]  # R215 rolling window cap 50

    resolved = {"last_tick": last_tick, "launches": launches}

    text = json.dumps(resolved, indent=1, ensure_ascii=False)
    raw = _blob("HEAD")
    crlf = raw.count(b"\r\n") > 0
    with io.open(PATH, "w", encoding="utf-8", newline="\r\n" if crlf else "\n") as fh:
        fh.write(text)

    # r185: parse-verify before add
    with io.open(PATH, "r", encoding="utf-8") as fh:
        back = json.load(fh)
    assert isinstance(back["last_tick"], dict)
    assert back["last_tick"]["ts"] == max(ts_h, ts_s)
    n_union = len({(r.get("ts"), r.get("entry"), r.get("machine"), r.get("pid"))
                   for r in head.get("launches", []) + stashed.get("launches", [])})
    print(f"resolved last_tick.ts={back['last_tick']['ts']} "
          f"(HEAD={ts_h} STASH={ts_s}) launches={len(back['launches'])} "
          f"(union_raw={n_union} cap50) crlf={crlf}")


if __name__ == "__main__":
    try:
        _resolve()
    except Exception as exc:
        print(f"RESOLVE-FAIL {exc}")
        sys.exit(2)
