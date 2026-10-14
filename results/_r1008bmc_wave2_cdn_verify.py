# -*- coding: utf-8 -*-
# _r1008bmc_wave2_cdn_verify.py -- verify wave2 SAVED slots' CDN URLs point to current local bytes
# Law: INDEX rows are append-only; wave2 marks INDEX-SKIP as UPLOAD_FAIL_OR_SKIPPED (cosmetic).
# This probe HEADs each CDN URL and compares Content-Length vs local mp4 size. Mismatch = real repair need.
import json, io, os, re, urllib.request, ssl

BMC = r"K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\kf-demo-20261012\bmc"
IDX = os.path.join(BMC, "I2V-URL-INDEX.md")
PROG = os.path.join(BMC, "wave2_r998_progress.json")
OUT = os.path.join(BMC, "wave2_cdn_verify_r1008.json")

if os.environ.get("PYTHONIOENCODING") != "utf-8":
    os.environ["PYTHONIOENCODING"] = "utf-8"

rows = {}
for line in io.open(IDX, encoding="utf-8"):
    m = re.match(r"\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*(https?://\S+?)\s*\|", line)
    if m:
        rows[m.group(1).strip()] = m.group(3).strip()

sh = json.load(io.open(PROG, encoding="utf-8"))["shots"]
ssl_ctx = ssl.create_default_context()
report = {"ts": __import__("time").strftime("%Y-%m-%dT%H:%M:%S"), "checked": 0,
          "match": 0, "mismatch": [], "no_row": [], "head_fail": []}
for sid, v in sorted(sh.items()):
    if not (isinstance(v, dict) and v.get("status") == "SAVED"):
        continue
    local = v.get("mp4")
    if not local or not os.path.isfile(local):
        continue
    url = rows.get(sid)
    if not url:
        report["no_row"].append(sid)
        continue
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=30, context=ssl_ctx) as r:
            clen = int(r.headers.get("Content-Length", "-1"))
    except Exception as ex:
        report["head_fail"].append({"sid": sid, "err": repr(ex)[:120]})
        continue
    report["checked"] += 1
    if clen == os.path.getsize(local):
        report["match"] += 1
    else:
        report["mismatch"].append({"sid": sid, "cdn_bytes": clen,
                                   "local_bytes": os.path.getsize(local), "url": url})

tmp = OUT + ".tmp"
io.open(tmp, "w", encoding="utf-8").write(json.dumps(report, ensure_ascii=False, indent=1))
os.replace(tmp, OUT)
print("checked=%d match=%d mismatch=%d no_row=%d head_fail=%d" %
      (report["checked"], report["match"], len(report["mismatch"]),
       len(report["no_row"]), len(report["head_fail"])))
if report["mismatch"]:
    for m in report["mismatch"]:
        print("MISMATCH", m["sid"], m["cdn_bytes"], "vs", m["local_bytes"])
if report["no_row"]:
    print("NO_ROW", report["no_row"])
if report["head_fail"]:
    print("HEAD_FAIL", [x["sid"] for x in report["head_fail"]])
