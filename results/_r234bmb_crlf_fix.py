# r234 bm-b: CRLF rewrite of the two in-flight conflict resolutions (r223 EOL law repair)
import io
import json
import subprocess

REPO = r"C:\Users\Administrator\Desktop\Bigmoney"
ident = lambda e: json.dumps(e, ensure_ascii=False, sort_keys=True)


def blobs(path):
    def get(stage):
        out = subprocess.run(["git", "show", f":{stage}:{path}"], cwd=REPO, capture_output=True)
        return out.stdout
    return get(2), get(3)


def union_rows(a, b):
    seen, out = set(), []
    for e in a + b:
        k = ident(e)
        if k not in seen:
            seen.add(k)
            out.append(e)
    out.sort(key=lambda e: str(e.get("ts", "")))
    return out


rep = {}
for P in ("results/compute_audit.json", "results/regime_state.json"):
    ours_b, theirs_b = blobs(P)
    ours, theirs = json.loads(ours_b.decode("utf-8-sig")), json.loads(theirs_b.decode("utf-8-sig"))
    if P.endswith("compute_audit.json"):
        hist = union_rows(ours.get("history", []), theirs.get("history", []))
        latest = theirs.get("latest", {}) if str(theirs.get("latest", {}).get("ts", "")) > str(ours.get("latest", {}).get("ts", "")) else ours.get("latest", {})
        merged = {"history": hist, "latest": latest}
    else:
        merged = dict(ours)
        for k in ("history", "transitions"):
            merged[k] = union_rows(ours.get(k, []), theirs.get(k, []))
        if str(theirs.get("updated", "")) > str(ours.get("updated", "")):
            for k in theirs:
                if k not in ("history", "transitions"):
                    merged[k] = theirs[k]
    json.loads(json.dumps(merged))
    with io.open(REPO + "\\" + P.replace("/", "\\"), "w", encoding="utf-8", newline="\r\n") as fh:
        fh.write(json.dumps(merged, ensure_ascii=False, indent=1) + "\n")
    b = open(REPO + "\\" + P.replace("/", "\\"), "rb").read()
    assert b.count(b"<<<<<<<") == 0
    rep[P] = {"crlf": b.count(b"\r\n"), "lf_only": b.count(b"\n") - b.count(b"\r\n")}
print(json.dumps(rep))
