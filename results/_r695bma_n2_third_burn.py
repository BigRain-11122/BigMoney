# r695 bm-a: n2_w15 third-burn face probe (process + autofill + pool three-face)
import json, subprocess, io, os

# 1) any live generate runner process? (dual-form: CIM full scan + cmdline match)
out = subprocess.run(
    ["powershell", "-NoProfile", "-Command",
     "Get-CimInstance Win32_Process | Where-Object {$_.CommandLine -match "
     "'perpetual_faces_n2|n2_w15|trial_labor_w2'} | Select-Object ProcessId,CommandLine | "
     "ConvertTo-Json -Compress"],
    capture_output=True)
print("live n2-related processes:", out.stdout.decode("utf-8", "replace")[:600] or "NONE")

# 2) autofill state: recent claims by my daemon
for fp in (r"results\autofill_state.bm-a.json",):
    d = json.loads(open(fp, "rb").read().decode("utf-8"))
    txt = json.dumps(d, ensure_ascii=False)
    i = txt.find("n2-w15-generate")
    print("autofill_state n2-w15 mention:", txt[max(0, i - 120):i + 260] if i >= 0 else "NONE")

# 3) pool faces: shared + lane mirror, entry n2-w15-generate-0of1 shards owner
for fp in (r"results\runnable_pool.json", r"results\runnable_pool.bm-a.json"):
    d = json.loads(open(fp, "rb").read().decode("utf-8"))
    for e in d.get("entries", []):
        if "N2-W15-GENERATE" in str(e.get("id", "")):
            sh = e.get("shards", [])
            print("%s entry owner=%s since=%s shards=%s" % (
                os.path.basename(fp), e.get("owner"), e.get("owner_since"),
                json.dumps([{k: s.get(k) for k in ("key", "owner", "owner_since", "status")}
                            for s in sh], ensure_ascii=False)[:500]))

# 4) crash fuse: any n2 entry?
d = json.loads(open(r"results\crash_fuse.json", "rb").read().decode("utf-8"))
for k, v in d.get("sigs", {}).items():
    if "n2" in k.lower() or "n2" in str(v).lower():
        print("fuse:", k, json.dumps(v, ensure_ascii=False)[:200])

# 5) candidates file quick shape check
c = json.loads(open(r"results\n2_w15\n2_w15_candidates.json", "rb").read().decode("utf-8"))
ks = list(c.keys()) if isinstance(c, dict) else ["<list len %d>" % len(c)]
print("candidates top-level keys:", ks[:8])
if isinstance(c, dict):
    for k in ("generated", "ts", "meta", "n", "count"):
        if k in c:
            print("  %s=%r" % (k, str(c[k])[:120]))
print("PROBE_OK")
