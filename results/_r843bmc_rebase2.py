import subprocess, re
def blob(rev):
    r = subprocess.run(["git","show",f"{rev}:results/update_status.json"], capture_output=True)
    return r.stdout.decode("utf-8","replace") if r.returncode==0 else None
def ts(txt):
    m = re.search(r'"(ts|updated|last_run|time)":\s*"([^"]+)"', txt or "")
    return m.group(2) if m else "?"
o, t = blob(":2"), blob(":3")
print("ours ts:", ts(o), "| origin ts:", ts(t))
