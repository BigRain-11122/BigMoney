import subprocess, json

def blob(s, p):
    return subprocess.run(["git", "show", f":{s}:{p}"], capture_output=True).stdout

o_raw = blob(2, "results/compute_audit.json")
t_raw = blob(3, "results/compute_audit.json")
o = json.loads(o_raw.decode("utf-8"))
t = json.loads(t_raw.decode("utf-8"))

def rk(r):
    return json.dumps(r, sort_keys=True, ensure_ascii=False)

o_rows = {rk(r): r for r in o["history"]}
t_rows = {rk(r): r for r in t["history"]}
union = dict(o_rows)
union.update(t_rows)
merged = sorted(union.values(), key=lambda r: r.get("ts", ""))
expected = len(o_rows) + len(set(t_rows) - set(o_rows))
assert len(merged) == expected, f"{len(merged)}!={expected}"
latest = o["latest"] if o["latest"].get("ts", "") >= t["latest"].get("ts", "") else t["latest"]
doc = {"latest": latest, "history": merged}
crlf = b"\r\n" in o_raw[:2000]
body = json.dumps(doc, ensure_ascii=False, indent=1)
if crlf:
    body = body.replace("\n", "\r\n")
tail = "\r\n" if crlf else "\n"
if not body.endswith(tail):
    body += tail
enc = "utf-8-sig" if o_raw.startswith(b"\xef\xbb\xbf") else "utf-8"
with open("results/compute_audit.json", "w", encoding=enc, newline="") as f:
    f.write(body)
json.loads(open("results/compute_audit.json", "rb").read().decode(enc))
print("compute_audit union: ours=%d theirs=%d -> %d rows (zero-loss PASS), latest ts=%s" % (
    len(o["history"]), len(t["history"]), len(merged), latest.get("ts")))
