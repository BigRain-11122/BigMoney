"""R314 bm-b S0 resolver: results/autofill_state.json UU (mixed-dict+ledger).

Trigger: S0 stash (background-writer residue) -> pull --rebase fast-forward ->
stash pop -> UU. stage2=ours=pulled HEAD face (bm-a autofill tick self-commit),
stage3=theirs=stashed bm-b local autofill tick residue.

Canonical recipe per bigmoney-conflict-resolve skill (r203/R208/r215/r220):
  launches = union both stage blobs -> sort ts desc -> cap 50 -> re-sort ts ASC
             before write-back (producer append order, bm-b r245 law);
  last_tick = compare inner ts, WHOLE-dict assignment (no str() compare),
             same-second tie -> HEAD/ours (r140);
  parse-verify before write-back (r185); isinstance(last_tick, dict) assert;
  line-ending/indent mirror the base blob (CRLF producer format r223/r234).
Zero-loss check: post-write launches length == |union| pre-cap.
"""
import json
import subprocess
import sys

PATH = "results/autofill_state.json"


def blob_bytes(rev):
    return subprocess.run(["git", "show", rev], capture_output=True,
                           check=True).stdout


def main():
    a = json.loads(blob_bytes(":2:" + PATH).decode("utf-8-sig"))
    b = json.loads(blob_bytes(":3:" + PATH).decode("utf-8-sig"))
    base_raw = blob_bytes(":1:" + PATH)          # indent/newline mirror face

    la, lb = a.get("launches", []), b.get("launches", [])
    key = lambda e: (e.get("ts", ""), json.dumps(e, sort_keys=True,
                                                 ensure_ascii=False))
    union, seen = [], set()
    for e in la + lb:
        k = key(e)
        if k not in seen:
            seen.add(k)
            union.append(e)
    union.sort(key=lambda e: e.get("ts", ""), reverse=True)
    union = union[:50]
    union.sort(key=lambda e: e.get("ts", ""))     # producer append order

    ta = (a.get("last_tick") or {}).get("ts", "")
    tb = (b.get("last_tick") or {}).get("ts", "")
    if ta >= tb:                                  # same-second tie -> ours
        last = a.get("last_tick")
    else:
        last = b.get("last_tick")

    out = dict(a)                                 # pulled-HEAD scalar face
    out["launches"] = union
    out["last_tick"] = last
    assert isinstance(out["last_tick"], dict), "last_tick not a dict"

    nl = "\r\n" if b"\r\n" in base_raw[:2000] else "\n"
    indent = 1 if base_raw[:200].find(b'\n "') >= 0 else 2
    text = json.dumps(out, ensure_ascii=False, indent=indent)
    with open(PATH, "w", encoding="utf-8", newline="") as fh:
        fh.write(text + nl)

    chk = json.load(open(PATH, encoding="utf-8-sig"))
    assert isinstance(chk["last_tick"], dict)
    pre_cap = len({key(e) for e in la + lb})
    assert len(chk["launches"]) == min(pre_cap, 50), \
        f"union loss: {len(chk['launches'])} != min({pre_cap}, 50)"
    print(f"r314 S0 resolver: launches |A|={len(la)} |B|={len(lb)} "
          f"union={pre_cap} -> kept {len(chk['launches'])} (cap 50); "
          f"last_tick ts={chk['last_tick'].get('ts')} "
          f"({'ours' if ta >= tb else 'theirs'}); "
          f"nl={'CRLF' if nl == chr(13) + chr(10) else 'LF'} indent={indent}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
