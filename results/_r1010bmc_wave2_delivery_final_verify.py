# -*- coding: utf-8 -*-
# _r1010bmc_wave2_delivery_final_verify.py -- FINAL delivery-face gate for wave2 harvest:
# all 39 SAVED slots must have a CDN URL whose bytes == tonight's local mp4.
# URL resolution per slot: repair receipt (wave2_cdn_repair_r1010.json) first, else the
# original I2V-URL-INDEX row. HEAD Content-Length vs local size, 39/39 == PASS.
import io, json, os, re, ssl, time, urllib.request

HERE = r"K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\kf-demo-20261012"
BMC = os.path.join(HERE, "bmc")
I2V = os.path.join(BMC, "i2v")
IDX = os.path.join(BMC, "I2V-URL-INDEX.md")
REP = os.path.join(BMC, "wave2_cdn_repair_r1010.json")
OUT = os.path.join(BMC, "wave2_delivery_final_verify_r1010.json")

rep = json.load(io.open(REP, encoding="utf-8"))["repaired"]
rows = {}
for line in io.open(IDX, encoding="utf-8"):
    m = re.match(r"\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*(https?://\S+?)\s*\|", line)
    if m:
        rows[m.group(1).strip()] = m.group(3).strip()

prog = json.load(io.open(os.path.join(BMC, "wave2_r998_progress.json"), encoding="utf-8"))["shots"]
ssl_ctx = ssl.create_default_context()
report = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "total": 0, "pass": 0, "fail": []}

for sid, v in sorted(prog.items()):
    if not (isinstance(v, dict) and v.get("status") == "SAVED"):
        continue
    local = os.path.join(I2V, sid + ".mp4")
    if not os.path.isfile(local):
        report["fail"].append({"sid": sid, "err": "local missing"})
        continue
    lsize = os.path.getsize(local)
    if sid in rep:
        url, src = rep[sid]["url"], "repair_r1010"
    else:
        url, src = rows.get(sid), "index_original"
    report["total"] += 1
    if not url:
        report["fail"].append({"sid": sid, "err": "no url resolved"})
        continue
    try:
        rq = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(rq, timeout=30, context=ssl_ctx) as r:
            clen = int(r.headers.get("Content-Length", "-1"))
    except Exception as ex:
        report["fail"].append({"sid": sid, "err": repr(ex)[:100], "url": url})
        continue
    if clen == lsize:
        report["pass"] += 1
    else:
        report["fail"].append({"sid": sid, "cdn": clen, "local": lsize, "src": src, "url": url})

io.open(OUT + ".tmp", "w", encoding="utf-8").write(json.dumps(report, ensure_ascii=False, indent=1))
os.replace(OUT + ".tmp", OUT)
print("FINAL DELIVERY VERIFY: total=%d pass=%d fail=%d -> %s" %
      (report["total"], report["pass"], len(report["fail"]), OUT))
for f in report["fail"]:
    print("FAIL", json.dumps(f)[:160])
