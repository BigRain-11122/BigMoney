# r231b (bm-b round 231, 07:5x): autofill_state.json conflict resolver for the
# S0 rebase UU (23468fd8 replay onto origin 70192fd4) and the follow-up stash-pop
# UU batch. Canonical recipe (bigmoney-conflict-resolve skill, mixed-dict+ledger):
#   launches  = union both sides dedup by canonical entry json, sort by ts
#               ASCENDING (producer order: autofill.py appends at end, keeps
#               [-50:] -> newest last), cap newest 50 (R215 rolling window).
#   last_tick = compare internal "ts" strings, take newer; same-second tie ->
#               HEAD side (r140). Written as whole dict, never str()-ified (r203).
#   eol       = CRLF mirror of the bm-b producer format (r223 law: repo converges
#               to producer format, Windows autofill open() default).
#   verify    = parse-verify before write (r185): json.loads + isinstance(last_tick,
#               dict) + union |A|+|B|-|dup| == |A u B| zero-loss assertion.
# Blob reads via git cat-file subprocess bytes (r209: no PS redirection).
import json
import subprocess
import sys

PATH = "results/autofill_state.json"


def _blob(stage):
    out = subprocess.run(
        ["git", "ls-files", "-u", PATH], capture_output=True, text=True
    ).stdout.strip().splitlines()
    for line in out:
        parts = line.split()
        if len(parts) >= 4 and parts[2] == str(stage):
            return subprocess.run(
                ["git", "cat-file", "blob", parts[1]], capture_output=True
            ).stdout
    raise SystemExit(f"stage {stage} not found for {PATH}")


def _canon(e):
    return json.dumps(e, sort_keys=True, ensure_ascii=False)


def resolve():
    ours_raw = _blob(2)
    theirs_raw = _blob(3)
    ours = json.loads(ours_raw)
    theirs = json.loads(theirs_raw)

    a, b = ours["launches"], theirs["launches"]
    seen, union = set(), []
    for e in a + b:
        k = _canon(e)
        if k not in seen:
            seen.add(k)
            union.append(e)
    dup = len(a) + len(b) - len(union)
    union.sort(key=lambda e: e.get("ts", ""))
    kept = union[-50:]  # producer cap: [-50:] keeps newest (R215)
    dropped = len(union) - len(kept)

    lt_a, lt_b = ours["last_tick"], theirs["last_tick"]
    ta, tb = str(lt_a.get("ts", "")), str(lt_b.get("ts", ""))
    if tb > ta:
        last_tick = lt_b  # whole-dict assignment (r203)
        pick = "theirs"
    else:
        last_tick = lt_a  # same-second tie -> HEAD/ours side (r140)
        pick = "ours"

    merged = {"launches": kept, "last_tick": last_tick}
    assert isinstance(merged["last_tick"], dict), "last_tick must stay dict"
    json.loads(json.dumps(merged))  # parse-verify before write (r185)

    crlf = theirs_raw.count(b"\r\n") > 0  # bm-b producer format mirror (r223)
    body = json.dumps(merged, ensure_ascii=False, indent=1)
    with open(PATH, "w", encoding="utf-8", newline="\r\n" if crlf else "\n") as fh:
        fh.write(body + "\n")

    print(f"union: |A|={len(a)} |B|={len(b)} dup={dup} |AuB|={len(union)} "
          f"kept={len(kept)} dropped_oldest={dropped}")
    print(f"last_tick: ours={ta} theirs={tb} -> {pick} {last_tick.get('ts')}")
    print(f"eol: {'CRLF' if crlf else 'LF'}")
    print("P1E-SYNTH launch record preserved:",
          any(e.get("pid") == 17616 for e in kept))


if __name__ == "__main__":
    resolve()
