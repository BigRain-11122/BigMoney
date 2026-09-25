"""r206 rebase conflict resolver: compute_audit.json (multi-block, latest+history).

Generic two-side reconstruction (common lines + side blocks interleave), then:
  history = union by ts (both machines' runs kept, sorted by ts)
  latest  = take-newer ts
Parse-verify BEFORE git add (r185 ordering law).
"""
import json

PATH = "results/compute_audit.json"
raw = open(PATH, encoding="utf-8").read()
lines = raw.splitlines()

state = "common"
sides = {"ours": [], "theirs": []}
common = []
for ln in lines:
    if ln.startswith("<<<<<<<"):
        state = "ours"
        continue
    if ln.startswith("======="):
        state = "theirs"
        continue
    if ln.startswith(">>>>>>>"):
        state = "common"
        continue
    if state == "common":
        common.append(ln)
    else:
        sides[state].append(ln)

# reconstruct: full file per side = common skeleton with side blocks spliced in.
# Walk again tracking positions to interleave correctly.
out = {"ours": [], "theirs": []}
state = "common"
for ln in lines:
    if ln.startswith(("<<<<<<<", "=======", ">>>>>>>")):
        if ln.startswith("<<<<<<<"):
            state = "ours"
        elif ln.startswith("======="):
            state = "theirs"
        else:
            state = "common"
        continue
    if state == "common":
        out["ours"].append(ln)
        out["theirs"].append(ln)
    else:
        out[state].append(ln)

parsed = {}
for k in ("ours", "theirs"):
    txt = "\n".join(out[k])
    try:
        parsed[k] = json.loads(txt)
        print(k, "parse OK keys:", sorted(parsed[k].keys()))
    except json.JSONDecodeError as ex:
        print(k, "parse FAIL:", ex)
        raise SystemExit(2)

a, b = parsed["ours"], parsed["theirs"]
hist = {e["ts"]: e for e in a.get("history", [])}
for e in b.get("history", []):
    hist[e["ts"]] = e
merged_hist = [hist[t] for t in sorted(hist)]
merged = dict(b)                      # theirs as base (newer run)
merged["history"] = merged_hist
la, lb = a.get("latest", {}), b.get("latest", {})
merged["latest"] = lb if str(lb.get("ts", "")) >= str(la.get("ts", "")) else la
print("history union:", len(a.get("history", [])), "+", len(b.get("history", [])),
      "->", len(merged_hist), "| latest ts:", merged["latest"]["ts"])

with open(PATH, "w", encoding="utf-8", newline="\n") as f:
    json.dump(merged, f, ensure_ascii=False, indent=1)
chk = json.load(open(PATH, encoding="utf-8"))
assert chk["latest"]["ts"] and len(chk["history"]) >= len(merged_hist)
print("reparse OK. Now: git add results/compute_audit.json")
