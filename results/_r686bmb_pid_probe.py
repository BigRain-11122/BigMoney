"""r686 bm-b: liveness probe for burn pids (r659 CSV full-scan law)."""
import subprocess

r = subprocess.run(["tasklist", "/FO", "CSV"], capture_output=True)
lines = r.stdout.decode("utf-8", "replace").strip().split("\n")
recs = []
for l in lines[1:]:
    parts = l.split('","')
    if len(parts) >= 2:
        recs.append((parts[0].strip('"'), parts[1].strip('"')))
targets = {"50228": "w3-screen-1of4", "12764": "w2-judge-1of4"}
alive = [(pid, name, targets[pid]) for name, pid in recs if pid in targets]
py = [(name, pid) for name, pid in recs if "python" in name.lower()]
print("target pids alive:", alive if alive else "NONE (both finished)")
print("python proc count:", len(py))
for name, pid in py[:14]:
    print("py:", pid, name)
