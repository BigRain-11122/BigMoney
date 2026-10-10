import json, subprocess, io, re
def show_blob(rev, path):
    r = subprocess.run(["git","show",f"{rev}:{path}"], capture_output=True)
    if r.returncode != 0: return None
    return r.stdout.decode("utf-8","replace")
def get_ts(txt, path):
    try:
        j = json.loads(txt)
        for k in ("ts","time","generated","generated_at","asof","updated","updated_at","last_run","now","clock_read"):
            if k in j: return str(j[k])
        return str(sorted(j.keys())[:5])
    except Exception:
        m = re.search(r'"(ts|time|generated[^"]*)":\s*"([^"]+)"', txt)
        return m.group(2) if m else txt[:60]
import sys
files = subprocess.run(["git","diff","--name-only","--diff-filter=U"], capture_output=True, text=True).stdout.split()
for f in files:
    ours = show_blob(":2", f)   # ours (bm-c r843)
    theirs = show_blob(":3", f) # origin/main
    base = show_blob(":1", f)
    print(f, "| ours ts:", get_ts(ours or "", f) if ours else "NONE", "| origin ts:", get_ts(theirs or "", f) if theirs else "NONE")
