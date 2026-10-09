# r910 leg-2 residual: daily_report md twin side-matched to the auto-merged json (r98/r99/r100 twin law)
import json, re, subprocess

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
GIT = r"C:\Program Files\Git\cmd\git.exe"
JP = "docs/daily_report/REPORT-2026-10-09.json"
MP = "docs/daily_report/REPORT-2026-10-09.md"

def show(ref):
    r = subprocess.run([GIT, "show", ref], capture_output=True, cwd=ROOT)
    return r.stdout if r.returncode == 0 else None

# staged merged json (stage 0 = index result after auto-merge)
jb = show(f":0:{JP}")
assert jb is not None, "staged json missing"
jd = json.loads(jb)
# deep-collect wall-clock ts from the merged json
ts_vals = []
def walk(o):
    if isinstance(o, dict):
        for v in o.values(): walk(v)
    elif isinstance(o, list):
        for v in o: walk(v)
    elif isinstance(o, str) and re.match(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}", o):
        ts_vals.append(o)
walk(jd)
jts = max(ts_vals) if ts_vals else None
print("merged json generated ts:", jts)

m2 = show(f":2:{MP}")
m3 = show(f":3:{MP}")
assert m2 is not None and m3 is not None, "md stages missing"
def md_ts(b):
    hits = re.findall(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?", b.decode("utf-8", errors="replace"))
    return max(hits) if hits else None
t2, t3 = md_ts(m2), md_ts(m3)
print("md :2: max ts:", t2, "| md :3: max ts:", t3)
# twin side pick: side whose md ts matches the merged json ts; else fresher md; tie -> HEAD(:2:)
side = None
if jts:
    jn = jts.replace("T", " ")[:16]
    if t2 and t2.startswith(jn[:16]):
        side = 2
    elif t3 and t3.startswith(jn[:16]):
        side = 3
if side is None:
    if t3 and (not t2 or t3 > t2):
        side = 3
    else:
        side = 2
blob = m2 if side == 2 else m3
with open(ROOT + "\\" + MP.replace("/", "\\"), "wb") as f:
    f.write(blob)
print(f"daily_report md -> side {side} (twin-coupled to merged json)")
