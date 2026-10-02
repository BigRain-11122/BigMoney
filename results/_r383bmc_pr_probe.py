"""r383 bm-c post_review.jsonl id-audit: my S0 content-union kept 49 local
rows; bm-a r593 reported 'id-set identical both sides = deterministic twin
take-origin'. Verify whether my 49 kept rows duplicate ids already in
origin's row set (=> take origin per r294 id-dedupe law) or carry genuinely
new ids (=> append). Read-only."""
import json, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CN = 0x08000000

def gshow(pathspec):
    r = subprocess.run(["git", "-C", ROOT, "show", pathspec], capture_output=True,
                       creationflags=CN)
    return r.stdout if r.returncode == 0 else None

origin_pr = gshow("origin/main:results/post_review.jsonl").decode("utf-8")
o_rows = [x for x in origin_pr.replace("\r\n", "\n").split("\n") if x.strip()]
o_ids = {}
for row in o_rows:
    d = json.loads(row)
    o_ids.setdefault(d.get("id"), 0)
    o_ids[d["id"]] += 1

with open(ROOT + r"\results\post_review.jsonl", encoding="utf-8") as f:
    l_rows = [x for x in f.read().replace("\r\n", "\n").split("\n") if x.strip()]
l_ids = {}
for row in l_rows:
    d = json.loads(row)
    l_ids.setdefault(d.get("id"), 0)
    l_ids[d["id"]] += 1

print(f"origin rows={len(o_rows)} unique_ids={len(o_ids)} "
      f"max_id_multiplicity={max(o_ids.values())}")
print(f"local rows={len(l_rows)} unique_ids={len(l_ids)} "
      f"max_id_multiplicity={max(l_ids.values())}")
# which local rows are NOT byte-identical to any origin row?
o_set = set(o_rows)
extra = [x for x in l_rows if x not in o_set]
dup_ids = [json.loads(x).get("id") for x in extra
           if json.loads(x).get("id") in o_ids]
new_ids = [json.loads(x).get("id") for x in extra
           if json.loads(x).get("id") not in o_ids]
print(f"local rows not in origin (exact content): {len(extra)}")
print(f"  of which id ALREADY in origin (twin variants): {len(dup_ids)}")
print(f"  of which genuinely NEW ids: {len(new_ids)}")
for x in extra[:3]:
    d = json.loads(x)
    print("sample extra row keys:", sorted(d.keys())[:12])
    print("sample:", {k: d[k] for k in list(d)[:6]})
    break
verdict = "TAKE-ORIGIN" if not new_ids else "UNION-BY-ID"
print("VERDICT:", verdict)
