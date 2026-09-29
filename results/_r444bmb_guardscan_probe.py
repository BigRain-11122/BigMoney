"""r444bm-b probe: _attrition_guard_scan.json UU both-blob face compare (UNKNOWN-class manual adjudication)."""
import subprocess, json

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
PATH = "results/_attrition_guard_scan.json"

def sb(n):
    r = subprocess.run(["git", "show", ":%d:%s" % (n, PATH)], capture_output=True, cwd=REPO)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode("utf-8", "replace"))
    return json.loads(r.stdout.decode("utf-8"))

o, t = sb(2), sb(3)
print("OURS   ts=%s keys=%s" % (o.get("ts"), sorted(o.get("files", {}))))
print("THEIRS ts=%s keys=%s" % (t.get("ts"), sorted(t.get("files", {}))))
for k in sorted(set(o.get("files", {})) | set(t.get("files", {}))):
    ov = o.get("files", {}).get(k)
    tv = t.get("files", {}).get(k)
    same = "SAME" if ov == tv else "DIFF"
    os_ = (ov or {}).get("work_entries"), (ov or {}).get("head_entries")
    ts_ = (tv or {}).get("work_entries"), (tv or {}).get("head_entries")
    print("  %-32s %s ours(w,h)=%s theirs(w,h)=%s" % (k, same, os_, ts_))
for k in sorted(set(o) | set(t)):
    if k == "files":
        continue
    mark = "SAME" if o.get(k) == t.get(k) else "DIFF"
    print("  top %-16s %s ours=%r theirs=%r" % (k, mark, str(o.get(k))[:90], str(t.get(k))[:90]))
