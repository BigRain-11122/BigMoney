# -*- coding: utf-8 -*-
# _r1010bmc_wave2_cdn_repair.py -- O-20261014-1855 wave2 CDN delivery-face repair (harvest round)
# Context: wave2 39/39 SAVED at 22:08 (runner PID 24076 exited naturally). Byte-level verify
# (INDEX-SKIP law: harvest must run URL-local identity check) found 25/39 stale CDN rows
# (earlier-wave bytes; tonight's re-burns hit INDEX SKIP -> new bytes never shipped).
# bm-a assembly curls CDN URLs into segments/ -> stale clips would poison tonight's
# full-local cut (10-15 morning CEO deathline). Repair: raw file_upload+PUT of CURRENT mp4
# bytes under fresh tag <sid>_w2r1010, byte-verify via HEAD, append index row, write receipt.
# Race-safety: NEVER touches wave2_r998_progress.json (runner owns it; runner now exited
# but face stays untouched per law); own receipt only. Index appends are single-line writes.
# Lineage: _r1008bmc_wave2_cdn_repair.py (23/23 repaired) -- tag suffix bumped per-round to
# avoid same-tag duplicate index rows (tonight's bytes differ from r1008 repair bytes).
import io, json, os, sys, time, urllib.request

HERE = r"K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\kf-demo-20261012"
sys.path.insert(0, HERE)
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import bmc_night_factory as nf
import tj_mcp

BMC = os.path.join(HERE, "bmc")
I2V = os.path.join(BMC, "i2v")
IDX = os.path.join(BMC, "I2V-URL-INDEX.md")
VERIFY = os.path.join(BMC, "wave2_cdn_verify_r1008.json")
OUT = os.path.join(BMC, "wave2_cdn_repair_r1010.json")
TAG_SUFFIX = "_w2r1010"

v = json.load(io.open(VERIFY, encoding="utf-8"))
targets = sorted(m["sid"] for m in v.get("mismatch", []))
print("repair targets: %d" % len(targets))

rep = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "round": "r1010", "repaired": {},
       "failed": {}, "pending_repair_at_harvest": []}

if not getattr(tj_mcp, "session_id", None):
    tj_mcp.initialize()

def head_len(url):
    import ssl
    req = urllib.request.Request(url, method="HEAD")
    with urllib.request.urlopen(req, timeout=30, context=ssl.create_default_context()) as r:
        return int(r.headers.get("Content-Length", "-1"))

for sid in targets:
    p = os.path.join(I2V, sid + ".mp4")
    if not os.path.isfile(p) or os.path.getsize(p) < 500000:
        rep["failed"][sid] = "local mp4 missing/small"
        continue
    tag = sid + TAG_SUFFIX
    ok_url = None
    for attempt in (1, 2):
        try:
            res = tj_mcp.call_tool("file_upload", {"file_path": p}, timeout=120)
            rec = None
            for c in res.get("content", []):
                if c.get("type") == "resource":
                    try:
                        rec = json.loads(c["resource"]["text"])
                    except Exception:
                        rec = None
            if not rec or not rec.get("upload_url"):
                if rec and rec.get("already_uploaded") and rec.get("file_url"):
                    ok_url = rec["file_url"]
                    break
                print("[%s] no upload_url attempt%d: %s" % (tag, attempt, json.dumps(res)[:150]))
                time.sleep(3)
                continue
            data = io.open(p, "rb").read()
            req = urllib.request.Request(rec["upload_url"], data=data,
                                         headers={"Content-Type": "application/octet-stream"}, method="PUT")
            with urllib.request.urlopen(req, timeout=300) as r:
                code = r.status
            if code != 200:
                print("[%s] PUT code=%d" % (tag, code))
                time.sleep(2)
                continue
            ok_url = rec.get("file_url")
            break
        except Exception as ex:
            if "session" in str(ex).lower():
                tj_mcp.session_id = None
                try:
                    tj_mcp.initialize()
                except Exception:
                    pass
            print("[%s] upload exc attempt%d: %r" % (tag, attempt, ex))
            time.sleep(3)
    if not ok_url:
        rep["failed"][sid] = "upload failed after retries"
        continue
    # byte-verify (belt & suspenders)
    try:
        remote = head_len(ok_url)
    except Exception as ex:
        rep["failed"][sid] = "HEAD verify exc: %r" % ex
        continue
    if remote != os.path.getsize(p):
        rep["failed"][sid] = "byte mismatch after put: cdn=%d local=%d" % (remote, os.path.getsize(p))
        continue
    with io.open(IDX, "a", encoding="utf-8") as f:
        f.write("| %s | %.1fMB | %s |\n" % (tag, os.path.getsize(p) / 1048576.0, ok_url))
    rep["repaired"][sid] = {"url": ok_url, "bytes": os.path.getsize(p), "tag": tag}
    print("[%s] OK %d bytes" % (tag, os.path.getsize(p)))

tmp = OUT + ".tmp"
io.open(tmp, "w", encoding="utf-8").write(json.dumps(rep, ensure_ascii=False, indent=1))
os.replace(tmp, OUT)
print("repair done: ok=%d fail=%d -> %s" % (len(rep["repaired"]), len(rep["failed"]), OUT))
