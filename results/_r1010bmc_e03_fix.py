# -*- coding: utf-8 -*-
# _r1010bmc_e03_fix.py -- E03_gaze_meet floor-exempt re-upload (444KB legit small clip
# below the 500KB guard in _r1010bmc_wave2_cdn_repair.py). Same lineage: raw upload+PUT+
# HEAD byte-verify+index row+receipt update.
import io, json, os, sys, urllib.request

HERE = r"K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\kf-demo-20261012"
sys.path.insert(0, HERE)
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import bmc_night_factory as nf  # inserts MCP_DIR into sys.path (L30) before tj_mcp resolves
import tj_mcp

BMC = os.path.join(HERE, "bmc")
p = os.path.join(BMC, "i2v", "E03_gaze_meet.mp4")
size = os.path.getsize(p)
print("E03 local bytes:", size)
if not getattr(tj_mcp, "session_id", None):
    tj_mcp.initialize()
res = tj_mcp.call_tool("file_upload", {"file_path": p}, timeout=120)
rec = None
for c in res.get("content", []):
    if c.get("type") == "resource":
        try:
            rec = json.loads(c["resource"]["text"])
        except Exception:
            rec = None
if rec and rec.get("upload_url"):
    data = io.open(p, "rb").read()
    req = urllib.request.Request(rec["upload_url"], data=data,
                                 headers={"Content-Type": "application/octet-stream"}, method="PUT")
    with urllib.request.urlopen(req, timeout=300) as r:
        code = r.status
    url = rec.get("file_url")
    print("PUT", code, url)
    import ssl
    rq = urllib.request.Request(url, method="HEAD")
    with urllib.request.urlopen(rq, timeout=30, context=ssl.create_default_context()) as rr:
        remote = int(rr.headers.get("Content-Length", "-1"))
    print("HEAD verify:", remote, "== local", size, "->", remote == size)
    if remote == size:
        tag = "E03_gaze_meet_w2r1010"
        with io.open(os.path.join(BMC, "I2V-URL-INDEX.md"), "a", encoding="utf-8") as f:
            f.write("| %s | %.1fMB | %s |\n" % (tag, size / 1048576.0, url))
        rp = os.path.join(BMC, "wave2_cdn_repair_r1010.json")
        rep = json.load(io.open(rp, encoding="utf-8"))
        rep["repaired"]["E03_gaze_meet"] = {"url": url, "bytes": size, "tag": tag,
                                            "note": "floor-exempt legit small clip 444KB below 500KB guard"}
        rep["failed"].pop("E03_gaze_meet", None)
        io.open(rp + ".tmp", "w", encoding="utf-8").write(json.dumps(rep, ensure_ascii=False, indent=1))
        os.replace(rp + ".tmp", rp)
        print("RECEIPT UPDATED: repaired=%d failed=%d" % (len(rep["repaired"]), len(rep["failed"])))
else:
    print("no upload_url:", json.dumps(res)[:200])
