"""R278 bm-a rebase conflict resolver: results/autofill_state.json (mixed-dict+ledger).

Recipe (bigmoney-conflict-resolve skill / r203/R208/r215/r220/r245):
  launches = union both stages -> sort ts ASCENDING (producer append order;
             desc write = whole-column flip pseudo-diff, bm-b r245 law)
             -> cap 50 newest (rolling window R215)
  last_tick = compare inner ts -> assign WHOLE dict (no str()); tie -> ours(stage2)
  write-back mirrors base blob line-ending + indent + trailing-newline face.

Stages during rebase: :2 = ours (origin/main side), :3 = theirs (replayed commit).
"""
import json
import subprocess
import sys

PATH = "results/autofill_state.json"


def blob(stage: str) -> bytes:
    r = subprocess.run(["git", "show", f":{stage}:{PATH}"], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"stage {stage} read fail: {r.stderr[:200]}")
    return r.stdout


def main() -> int:
    raw2, raw3 = blob("2"), blob("3")
    a, b = json.loads(raw2), json.loads(raw3)

    # -- launches union (dedup by exact record equality), sort ts asc, cap 50
    seen, merged = [], []
    for rec in list(a.get("launches", [])) + list(b.get("launches", [])):
        if rec not in seen:
            seen.append(rec)
            merged.append(rec)
    merged.sort(key=lambda r: r.get("ts", ""))
    if len(merged) > 50:
        merged = merged[-50:]

    # -- last_tick: inner ts compare, whole-dict assign; tie -> ours
    lt2, lt3 = a.get("last_tick"), b.get("last_tick")
    t2 = lt2.get("ts") if isinstance(lt2, dict) else None
    t3 = lt3.get("ts") if isinstance(lt3, dict) else None
    if t3 is not None and (t2 is None or str(t3) > str(t2)):
        last_tick = lt3
    else:
        last_tick = lt2
    assert isinstance(last_tick, dict), "last_tick must stay a dict (r220 law)"

    # -- other keys: prefer non-null/meaningful from either, ours first
    out = dict(a)
    for k, v in b.items():
        if k not in out or out[k] in (None, "", [], {}):
            out[k] = v
    out["launches"] = merged
    out["last_tick"] = last_tick

    # -- format mirror: CRLF if base blob carries CRLF; indent/trailing newline
    crlf = b"\r\n" in raw2
    text = json.dumps(out, ensure_ascii=False, indent=1)
    if raw2.endswith(b"\n") and not text.endswith("\n"):
        text += "\n"
    data = text.encode("utf-8")
    if crlf:
        data = text.replace("\n", "\r\n").encode("utf-8")
    with open(PATH, "wb") as fh:
        fh.write(data)

    # parse-verify before add (r185 law)
    chk = json.loads(open(PATH, encoding="utf-8").read())
    assert chk["launches"] == merged and isinstance(chk["last_tick"], dict)
    print(f"resolved: launches union={len(merged)} (cap50 asc), "
          f"last_tick ts={last_tick.get('ts')}, crlf={crlf}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
