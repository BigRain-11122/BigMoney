"""r243 resolver: results/autofill_state.json UU (mixed-dict+ledger).

Recipe per bigmoney-conflict-resolve skill + classifier output:
  launches = union both blobs -> sort by ts -> cap 50 (R215 rolling window)
  last_tick = compare inner ts then assign WHOLE dict (no str());
              same-second tie -> HEAD/ours (:2 in rebase) per r140
  assert isinstance(last_tick, dict); mirror base-blob line endings
  parse-verify before write-back + git add (r185 law)

Rebase stages: :2 ours = origin/main (bm-b latest), :3 theirs = r243 replay.
"""
import json
import subprocess
import sys


def blob(stage):
    raw = subprocess.run(
        ["git", "show", f":{stage}:results/autofill_state.json"],
        capture_output=True).stdout
    return raw


def main():
    b2, b3 = blob(2), blob(3)
    crlf2 = b2.count(b"\r\n")
    crlf3 = b3.count(b"\r\n")
    d2 = json.loads(b2.decode("utf-8"))
    d3 = json.loads(b3.decode("utf-8"))

    # launches union by (ts, entry-key fields), sort by ts, cap 50
    l2 = d2.get("launches", [])
    l3 = d3.get("launches", [])
    seen, merged = set(), []
    for e in l2 + l3:
        k = (e.get("ts"), e.get("entry"), e.get("shard"), e.get("machine"))
        if k in seen:
            continue
        seen.add(k)
        merged.append(e)
    merged.sort(key=lambda e: e.get("ts", ""))
    n_union = len(merged)
    merged = merged[-50:]                     # cap 50 rolling window (R215)

    # last_tick: compare inner ts; whole-dict assign; tie -> ours (:2)
    t2 = (d2.get("last_tick") or {}).get("ts", "")
    t3 = (d3.get("last_tick") or {}).get("ts", "")
    if t3 > t2:
        last_tick = d3.get("last_tick")
    else:
        last_tick = d2.get("last_tick")       # tie or newer -> HEAD/ours
    assert isinstance(last_tick, dict), "last_tick must stay a dict (r203)"

    out = {"launches": merged, "last_tick": last_tick}
    txt = json.dumps(out, ensure_ascii=False, indent=1)
    # mirror base-blob line-ending style (r223/r234: CRLF producer format)
    use_crlf = crlf2 >= crlf3
    with open("results/autofill_state.json", "wb") as fh:
        if use_crlf:
            fh.write(txt.replace("\n", "\r\n").encode("utf-8"))
        else:
            fh.write(txt.encode("utf-8"))

    # parse-verify (r185) + zero-loss anchor report
    back = json.loads(open("results/autofill_state.json", encoding="utf-8").read())
    assert back["last_tick"] == last_tick
    assert len(back["launches"]) == len(merged)
    print(f"union launches: |ours|={len(l2)} |theirs|={len(l3)} "
          f"-> union {n_union} -> cap50 {len(merged)}")
    print(f"last_tick: ours_ts={t2!r} theirs_ts={t3!r} -> "
          f"{'theirs' if t3 > t2 else 'ours/HEAD'} "
          f"(ts={last_tick.get('ts')!r})")
    print(f"line-ending mirror: crlf base2={crlf2} base3={crlf3} "
          f"-> {'CRLF' if use_crlf else 'LF'} write-back")
    print("PARSE-VERIFY OK")


if __name__ == "__main__":
    sys.exit(main())
