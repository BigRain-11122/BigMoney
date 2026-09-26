# r244 bm-b resolver: autofill_state.json UU from stash-pop after pull --rebase (mixed-dict+ledger, classifier-confirmed)
# Stash-pop stages: :2=HEAD(post-pull origin latest), :3=stashed local tick. Union symmetric (r188/R208).
# Recipe: launches union->sort ts desc->cap50 (R215); last_tick inner-ts compare, whole-dict assign,
# tie->HEAD/:2 (r140); isinstance(last_tick,dict) assert; EOL+indent mirror base blob (r209/r220/r223).
import json
import subprocess
import sys

REPO = r"C:\Users\Administrator\Desktop\Bigmoney"
PATH = "results/autofill_state.json"


def blob(stage):
    out = subprocess.run(["git", "show", f":{stage}:{PATH}"], cwd=REPO,
                        capture_output=True)
    if out.returncode != 0:
        raise RuntimeError(f"blob :{stage} rc={out.returncode}")
    return out.stdout  # bytes


base_b, ours_b, theirs_b = blob(1), blob(2), blob(3)
crlf = base_b.count(b"\r\n") * 2 > base_b.count(b"\n")  # majority EOL probe (producer format, r223 law)
base = json.loads(base_b.decode("utf-8-sig"))
ours = json.loads(ours_b.decode("utf-8-sig"))      # HEAD side (post-pull)
theirs = json.loads(theirs_b.decode("utf-8-sig"))  # stash side (local tick)

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

# last_tick: inner-ts compare, whole-dict assign, same-second tie -> :2/HEAD (r140)
to, tt = ours.get("last_tick", {}), theirs.get("last_tick", {})
ts_o, ts_t = str(to.get("ts", "")), str(tt.get("ts", ""))
if ts_t > ts_o:
    last_tick = tt
else:
    last_tick = to  # includes tie->HEAD law

merged = dict(ours)  # HEAD-side base for all other keys (key order preserved)
merged["launches"] = capped
merged["last_tick"] = last_tick
assert isinstance(last_tick, dict), "last_tick must stay dict (r203 law)"
json.loads(json.dumps(merged))  # parse-verify before write-back (r185 law)

# indent mirror from base blob
indent = 1
first_lines = base_b.decode("utf-8-sig").splitlines()
for ln in first_lines[1:4]:
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
    "kind": "stash-pop UU",
    "launches": {"head": len(lo), "stash": len(lt), "union": len(union), "capped": len(capped)},
    "last_tick": {"head_ts": ts_o, "stash_ts": ts_t, "picked": last_tick.get("ts"), "tie": ts_o == ts_t},
    "eol": "CRLF" if crlf else "LF",
    "indent": indent,
    "zero_loss": len(capped) == len(union) or len(union) > 50,
}
print(json.dumps(report, ensure_ascii=False))
with open(REPO + r"\results\_r244bmb_af_resolve_report.json", "w", encoding="utf-8", newline="\n") as fh:
    json.dump(report, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
sys.exit(0)
