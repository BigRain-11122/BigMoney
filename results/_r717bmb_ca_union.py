# r717 compute_audit merge-window final union (HEAD vs MERGE_HEAD)
# Heal: theirs history entries double-encoded as JSON strings (bm-a writer drift)
# -> normalize str entries via json.loads, union dedup by ts, sort asc, all-dicts out.
# State fields take-new: theirs latest 07:39:40 > ours 07:21:37.
import subprocess, json, io

def show(sha, path):
    r = subprocess.run(["git","show",f"{sha}:{path}"], capture_output=True)
    assert r.returncode == 0 and len(r.stdout) > 100, f"{sha}:{path} bad ({r.returncode},{len(r.stdout)}B)"
    return r.stdout

jo = json.loads(show("HEAD","results/compute_audit.json"))
jt = json.loads(show("MERGE_HEAD","results/compute_audit.json"))

def norm_entries(raw):
    out, n_str = [], 0
    for e in raw:
        if isinstance(e, str):
            e = json.loads(e); n_str += 1
        assert isinstance(e, dict) and "ts" in e, "entry un-normalizable (r319)"
        out.append(e)
    return out, n_str

ho, so = norm_entries(jo["history"])
ht, st = norm_entries(jt["history"])

by = {}
for e in ho + ht:
    by[e["ts"]] = e
union = sorted(by.values(), key=lambda e: e["ts"])
expected = len(set([e["ts"] for e in ho] + [e["ts"] for e in ht]))
assert len(union) == expected, "union not zero-loss"

payload = dict(jt)                      # latest take-new (theirs 07:39:40)
payload["history"] = union

s = json.dumps(payload, indent=2, ensure_ascii=False)
b_head = show("HEAD","results/compute_audit.json")
if b"\r\n" in b_head: s = s.replace("\n","\r\n")
if b_head.endswith(b"\n"): s += "\r\n" if b"\r\n" in b_head else "\n"
data = s.encode("utf-8")
json.loads(data.decode("utf-8"))        # r185
open("results/compute_audit.json","wb").write(data)
back = open("results/compute_audit.json","rb").read()
assert b"<<<<<<<" not in back and b">>>>>>>" not in back
rp = json.loads(back.decode("utf-8"))
assert rp["history"] == union and rp["latest"] == jt["latest"], "re-read mismatch (r704)"
# all-dict healing assert
assert all(isinstance(e, dict) for e in rp["history"])

rep = (f"compute_audit merge-union: ours={len(jo['history'])}({so} str-healed) "
       f"theirs={len(jt['history'])}({st} str-healed) |AUB|={len(union)} "
       f"latest=theirs({jt['latest']['ts']}) all-dicts-healed")
io.open(r"results\_r717bmb_resolve_report.txt","a",encoding="ascii").write(
    "== merge-window-3 compute_audit final union ==\n" + rep + "\n")
print(rep)
