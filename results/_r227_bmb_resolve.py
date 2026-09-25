# -*- coding: utf-8 -*-
"""r227 (bm-b) stash-pop conflict resolver -- skill bigmoney-conflict-resolve
dogfood #5. Single UU: results/autofill_state.json = mixed-dict+ledger
(classifier GREEN, recipe r203/R208/r215/r220):
  launches = union stage2+stage3 -> sort by ts -> cap 50 (rolling window, R215)
  last_tick = compare inner ts then assign WHOLE dict (no str()-compare,
  r140 same-second tie -> HEAD/ours); isinstance(last_tick, dict) assert
  CRLF producer-format mirror (bm-b r223 law); parse-verify before add (r185).
Context: ours(stage2)=HEAD post-rebase incl. bm-a OS-loop watchdog tick
06:00:01 (b3b54cbc); theirs(stage3)=bm-b local watchdog tick 06:00:02 stashed
at S0 pre-pull."""
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PATH = "results/autofill_state.json"


def raw(stage):
    out = subprocess.run(["git", "show", f":{stage}:{PATH}"],
                         capture_output=True)
    assert out.returncode == 0, out.stderr[:200]
    return out.stdout


s2, s3 = raw(2), raw(3)
a, b = json.loads(s2.decode("utf-8")), json.loads(s3.decode("utf-8"))

# launches union (dedupe by canonical json) -> sort by ts -> cap 50
key = lambda r: json.dumps(r, ensure_ascii=False, sort_keys=True)
seen, rows = set(), []
for r in a.get("launches", []) + b.get("launches", []):
    k = key(r)
    if k not in seen:
        seen.add(k)
        rows.append(r)
rows.sort(key=lambda r: str(r.get("ts", "")))
n_union = len(rows)
rows = rows[-50:]          # rolling window cap 50, keep newest

# last_tick: whole-dict by inner ts, tie -> HEAD (ours)
lta, ltb = a.get("last_tick", {}), b.get("last_tick", {})
tsa, tsb = str(lta.get("ts", "")), str(ltb.get("ts", ""))
newer = ltb if tsb > tsa else lta

# other top-level keys: take-new side (note field), preserve both provenance
note = b.get("rebase_union_note", a.get("rebase_union_note", ""))

out = {"last_tick": newer, "launches": rows, "rebase_union_note": note}
eol = "\r\n" if b"\r\n" in s2 else "\n"
body = json.dumps(out, ensure_ascii=False, indent=1)
with open(PATH, "wb") as f:
    f.write(body.replace("\n", eol).encode("utf-8"))

chk = json.load(open(PATH, encoding="utf-8"))
assert isinstance(chk["last_tick"], dict), "last_tick must stay dict (r203)"
assert isinstance(chk["last_tick"].get("ts"), str)
assert len(chk["launches"]) == min(n_union, 50)
print(f"autofill_state resolve OK: union {n_union} (dedup of "
      f"{len(a['launches'])}+{len(b['launches'])}), kept newest {len(chk['launches'])}; "
      f"last_tick={'theirs(bm-b ' + tsb + ')' if tsb > tsa else 'ours(HEAD ' + tsa + ')'}; "
      f"EOL={'CRLF' if eol == chr(13) + chr(10) else 'LF'}")
print("parse-verify passed; next: git add + drop stash")
