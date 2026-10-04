# r670 bm-a: strip the BOM the finalize write introduced from gate_attrition.json
# (byte-surgical: 3-byte prefix removal only; content unchanged; parse+count gates)
import json

P = "results/gate_attrition.json"
raw = open(P, "rb").read()
assert raw.startswith(b"\xef\xbb\xbf"), "no BOM to strip"
body = raw[3:]
d = json.loads(body.decode("utf-8"))
n_entries = len(d.get("entries", []))
last = d["entries"][-1]
assert last.get("batch") == "THEME-JUDGE-P1" and last.get("kind") == "judgment", last.get("batch")
with open(P, "wb") as fh:
    fh.write(body)
chk = json.load(open(P, encoding="utf-8"))   # strict utf-8 read = guard's caliber
assert len(chk["entries"]) == n_entries
assert chk["entries"][-1]["batch"] == "THEME-JUDGE-P1"
print(f"BOM stripped: entries={n_entries} intact, last=THEME-JUDGE-P1, strict-utf8 parse PASS")
