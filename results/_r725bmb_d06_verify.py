import glob, json, hashlib

rows, bad = [], []
for f in sorted(glob.glob(r"research\pit-*.md")):
    b = open(f, "rb").read()
    ok = len(b) <= 30 * 1024
    rows.append({"file": f, "bytes": len(b), "kb": round(len(b) / 1024, 1),
                 "le30": ok, "md5": hashlib.md5(b).hexdigest()[:16]})
    if not ok:
        bad.append((f, len(b)))
rep = {"round": "r725 bm-b",
       "purpose": "D-06 domain-file <=30KB re-verify (feeds 10-07 12:00 group closeout)",
       "files": rows, "total": len(rows), "over_limit": bad, "all_pass": not bad}
with open(r"results\_r725bmb_d06_verify.json", "w", encoding="utf-8") as fh:
    json.dump(rep, fh, indent=1, ensure_ascii=False)
print("total files:", len(rows), "| all <=30KB:", not bad)
for x in rows:
    print("  %6.1fKB  %s  %s" % (x["kb"], "OK  " if x["le30"] else "OVER", x["file"]))
