# r234 bm-b TEMP resolver #2: compute_audit.json + regime_state.json UU (rolling-ledger, classifier-confirmed)
# Recipes: history/transitions union by identity (zero row loss, r188/R208); snapshot faces take-new
# (CA latest.ts / RS updated); ties -> ours/HEAD (r140); triggers = state face (r231 E1 law, NEVER union);
# EOL+indent mirror base blob (r209/r220/r223); parse-verify before write-back (r185).
import json
import subprocess
import sys

REPO = r"C:\Users\Administrator\Desktop\Bigmoney"
ident = lambda e: json.dumps(e, ensure_ascii=False, sort_keys=True)


def blobs(path):
    def get(stage):
        out = subprocess.run(["git", "show", f":{stage}:{path}"], cwd=REPO, capture_output=True)
        if out.returncode != 0:
            raise RuntimeError(f"{path} :{stage} rc={out.returncode}")
        return out.stdout
    return get(1), get(2), get(3)


def eol_indent(base_b):
    crlf = base_b.count(b"\r\n") * 2 > base_b.count(b"\n")
    indent = 1
    for ln in base_b.decode("utf-8-sig").splitlines()[1:4]:
        st = ln.lstrip(" ")
        if st and (len(ln) - len(st)) in (1, 2, 4):
            indent = len(ln) - len(st)
            break
    return ("\r\n" if crlf else "\n"), indent


def union_rows(a, b, ts_key="ts"):
    seen, out = set(), []
    for e in a + b:
        k = ident(e)
        if k not in seen:
            seen.add(k)
            out.append(e)
    out.sort(key=lambda e: str(e.get(ts_key, "")))
    return out


def pick_newer(o, t, ts_key):
    vo, vt = str(o.get(ts_key, "")), str(t.get(ts_key, ""))
    return (t, vt) if vt > vo else (o, vo)  # tie -> ours (r140)


report = {}

# ---- compute_audit.json ----
P = "results/compute_audit.json"
base_b, ours_b, theirs_b = blobs(P)
ours, theirs = json.loads(ours_b.decode("utf-8-sig")), json.loads(theirs_b.decode("utf-8-sig"))
hist = union_rows(ours.get("history", []), theirs.get("history", []))
latest, picked = pick_newer(ours.get("latest", {}), theirs.get("latest", {}), "ts")
merged = {"history": hist, "latest": latest}
assert isinstance(latest, dict) and latest.get("ts")
json.loads(json.dumps(merged))
nl, ind = eol_indent(base_b)
with open(REPO + "\\" + P.replace("/", "\\"), "w", encoding="utf-8", newline="") as fh:
    fh.write(json.dumps(merged, ensure_ascii=False, indent=ind))
report["compute_audit"] = {
    "hist_ours": len(ours.get("history", [])), "hist_theirs": len(theirs.get("history", [])),
    "union": len(hist), "latest_picked": picked, "zero_loss": len(hist) >= max(len(ours.get("history", [])), len(theirs.get("history", []))),
    "eol": nl.strip(), "indent": ind,
}

# ---- regime_state.json ----
P = "results/regime_state.json"
base_b, ours_b, theirs_b = blobs(P)
ours, theirs = json.loads(ours_b.decode("utf-8-sig")), json.loads(theirs_b.decode("utf-8-sig"))
merged = dict(ours)  # origin-side base key order
for k in ("history", "transitions"):
    merged[k] = union_rows(ours.get(k, []), theirs.get(k, []), "ts")
face_theirs = str(theirs.get("updated", "")) > str(ours.get("updated", ""))
if face_theirs:
    for k in theirs:
        if k not in ("history", "transitions"):
            merged[k] = theirs[k]  # whole face take-new (incl. triggers, r231 E1 law)
json.loads(json.dumps(merged))
nl, ind = eol_indent(base_b)
with open(REPO + "\\" + P.replace("/", "\\"), "w", encoding="utf-8", newline="") as fh:
    fh.write(json.dumps(merged, ensure_ascii=False, indent=ind))
report["regime_state"] = {
    "hist": [len(ours.get("history", [])), len(theirs.get("history", [])), "->", len(merged["history"])],
    "trans": [len(ours.get("transitions", [])), len(theirs.get("transitions", [])), "->", len(merged["transitions"])],
    "face_updated": {"ours": ours.get("updated"), "theirs": theirs.get("updated"), "picked": "theirs" if face_theirs else "ours"},
    "zero_loss": len(merged["history"]) >= max(len(ours.get("history", [])), len(theirs.get("history", []))),
    "eol": nl.strip(), "indent": ind,
}

print(json.dumps(report, ensure_ascii=False))
with open(REPO + r"\results\_r234bmb_resolve_report2.json", "w", encoding="utf-8", newline="\n") as fh:
    json.dump(report, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
sys.exit(0)
