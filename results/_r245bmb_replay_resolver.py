"""r245 bm-b rebase replay resolver: results/autofill_state.json
mixed-dict+ledger (classifier GREEN, recipe per SKILL.md r203/R208/r215/
r220 + r245 ORDER amendment).

Replay context: bm-b S7 push rejected (bm-a landed bc50b6b2 mid-round);
git pull --rebase replaying af4cad2b (autofill tick 12:10) onto bm-a side.
Stage semantics during rebase: :2 ours = bm-a/main face, :3 theirs = bm-b
replayed commit face.

Recipe (frozen):
  launches = union both blobs -> sort ts DESC -> cap 50 (cap-semantics
             face, R215) -> RE-SORT ts ASC before write-back (producer
             append order = format face, bm-b r245 law);
  last_tick = compare INNER ts, assign WHOLE dict (no str()), same-second
             tie -> HEAD/ours (r140); assert isinstance(last_tick, dict);
  EOL+indent = mirror base blob probe (:1), write in newline-translation
             mode (CRLF producer format, r223/r234: probe != write-back);
  parse-verify before add (r185).
"""
import json
import subprocess
import sys

PATH = "results/autofill_state.json"


def blob(spec: str) -> bytes:
    r = subprocess.run(["git", "show", spec], capture_output=True)
    if r.returncode != 0:
        sys.exit(f"git show {spec} failed: {r.stderr.decode()[:200]}")
    return r.stdout


base_raw = blob(f":1:{PATH}")
ours_raw = blob(f":2:{PATH}")     # bm-a / main face (HEAD side)
theirs_raw = blob(f":3:{PATH}")   # bm-b replayed commit face

base = json.loads(base_raw.decode("utf-8-sig"))
ours = json.loads(ours_raw.decode("utf-8-sig"))
theirs = json.loads(theirs_raw.decode("utf-8-sig"))

# ---- launches: union -> ts DESC -> cap 50 -> re-sort ts ASC (r245 ORDER)
lo, lt = ours.get("launches", []), theirs.get("launches", [])
seen, union = set(), []
for rec in lo + lt:
    key = json.dumps(rec, sort_keys=True, default=str)
    if key not in seen:
        seen.add(key)
        union.append(rec)
desc = sorted(union, key=lambda r: str(r.get("ts", "")), reverse=True)
capped = desc[:50]
launches = sorted(capped, key=lambda r: str(r.get("ts", "")))  # ASC write-back

# ---- last_tick: inner-ts compare, whole-dict assign, tie -> HEAD/ours
ot, tt = ours.get("last_tick"), theirs.get("last_tick")


def _ts(x):
    return str(x.get("ts", "")) if isinstance(x, dict) else ""


if not isinstance(ot, dict) and isinstance(tt, dict):
    last_tick = tt
elif isinstance(ot, dict) and not isinstance(tt, dict):
    last_tick = ot
elif _ts(tt) > _ts(ot):
    last_tick = tt
else:
    last_tick = ot                      # includes same-second tie -> HEAD
assert isinstance(last_tick, dict), "last_tick must be a dict (r203 law)"

# ---- other keys: take ours (bm-a main face) as the carrying dict, then
#      overlay the resolved ledger faces (single-writer semantics)
out = dict(ours)
out["launches"] = launches
out["last_tick"] = last_tick

# ---- EOL probe from base blob (r223/r234: probe != write-back)
crlf = b"\r\n" in base_raw
eol = "\r\n" if crlf else "\n"

text = json.dumps(out, ensure_ascii=False, indent=1,
                  default=str) + eol
with open(PATH, "w", encoding="utf-8", newline="") as fh:
    fh.write(text)

# ---- parse-verify (r185) + evidence
chk = json.load(open(PATH, encoding="utf-8-sig"))
assert isinstance(chk["last_tick"], dict)
ts_list = [str(r.get("ts", "")) for r in chk["launches"]]
assert ts_list == sorted(ts_list), "launches write-back order must be ASC"
print(json.dumps({
    "resolver": "r245 replay autofill_state mixed-dict+ledger",
    "last_tick_taken": last_tick.get("ts"),
    "last_tick_machine": last_tick.get("machine"),
    "launches_ours": len(lo), "launches_theirs": len(lt),
    "launches_union": len(union), "launches_written": len(launches),
    "cap_applied": len(union) > 50,
    "write_back_order": "ts-ascending (r245 ORDER law)",
    "eol": "CRLF" if crlf else "LF",
    "parse_verify": "OK",
}, ensure_ascii=False))
