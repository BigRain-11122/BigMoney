# r245 bm-b replay resolver: autofill_state.json UU during rebase replay of round-244 commit
# (mixed-dict+ledger, classifier-confirmed face). Stages during rebase: :2=origin/main side
# (bm-a latest ticks), :3=my replayed round-244 commit (bm-b 11:50:01 tick).
# Recipe: launches union -> sort ts desc -> cap50 (R215 cap semantics) -> RE-SORT ASCENDING
# before write-back (r245 correction to r244 resolver: producer canon = append order =
# ts-ascending; r244 wrote desc face = 275-line pseudo-diff + producer inherited inversion;
# R209 mirror-producer law covers ORDER, not just EOL/indent); last_tick inner-ts compare,
# whole-dict assign, tie->:2 (r140); isinstance dict assert (r203); CRLF+indent mirror base (r223).
import json
import subprocess
import sys

REPO = r"C:\Users\Administrator\Desktop\Bigmoney"
PATH = "results/autofill_state.json"


def blob(stage):
    out = subprocess.run(["git", "show", f":{stage}:{PATH}"], cwd=REPO, capture_output=True)
    if out.returncode != 0:
        raise RuntimeError(f"blob :{stage} rc={out.returncode}")
    return out.stdout


base_b, ours_b, theirs_b = blob(1), blob(2), blob(3)
crlf = base_b.count(b"\r\n") * 2 > base_b.count(b"\n")
base = json.loads(base_b.decode("utf-8-sig"))
ours = json.loads(ours_b.decode("utf-8-sig"))      # :2 = origin/main (bm-a side)
theirs = json.loads(theirs_b.decode("utf-8-sig"))  # :3 = replayed commit (bm-b side)

lo, lt = ours.get("launches", []), theirs.get("launches", [])
ident = lambda e: json.dumps(e, ensure_ascii=False, sort_keys=True)
seen, union = set(), []
for e in lo + lt:
    k = ident(e)
    if k not in seen:
        seen.add(k)
        union.append(e)
union.sort(key=lambda e: str(e.get("ts", "")), reverse=True)
capped = union[:50]
lost = [e for e in union[50:] if ident(e) not in {ident(x) for x in capped}]
capped_asc = sorted(capped, key=lambda e: str(e.get("ts", "")))  # producer canon order

to, tt = ours.get("last_tick", {}), theirs.get("last_tick", {})
ts_o, ts_t = str(to.get("ts", "")), str(tt.get("ts", ""))
last_tick = tt if ts_t > ts_o else to  # includes same-second tie -> :2/origin (r140)

merged = dict(ours)
merged["launches"] = capped_asc
merged["last_tick"] = last_tick
assert isinstance(last_tick, dict), "last_tick must stay dict (r203 law)"
json.loads(json.dumps(merged))

indent = 1
for ln in base_b.decode("utf-8-sig").splitlines()[1:4]:
    stripped = ln.lstrip(" ")
    if stripped and len(ln) - len(stripped) in (1, 2, 4):
        indent = len(ln) - len(stripped)
        break

nl = "\r\n" if crlf else "\n"
text = json.dumps(merged, ensure_ascii=False, indent=indent)
with open(REPO + "\\" + PATH.replace("/", "\\"), "w", encoding="utf-8", newline="") as fh:
    fh.write(text)
    if not text.endswith(nl):
        fh.write(nl)

report = {
    "path": PATH,
    "kind": "rebase-replay UU (round-244 commit onto origin/main)",
    "launches": {"origin_side": len(lo), "replay_side": len(lt), "union": len(union),
                 "capped": len(capped), "capped_over50_dropped": len(lost),
                 "writeback_order": "ts-ascending (producer canon, r245 correction)"},
    "last_tick": {"origin_ts": ts_o, "replay_ts": ts_t, "picked": last_tick.get("ts"),
                  "tie": ts_o == ts_t},
    "eol": "CRLF" if crlf else "LF",
    "indent": indent,
    "zero_loss": len(lost) == 0 or len(union) > 50,
}
print(json.dumps(report, ensure_ascii=False))
sys.exit(0)
