import subprocess, json, sys

GIT = r"C:\Program Files\Git\cmd\git.exe"

def show(path, ref="HEAD"):
    b = subprocess.run([GIT, "show", f"{ref}:{path}"], capture_output=True)
    return json.loads(b.stdout.decode("utf-8"))

h = show("state-bm-a.json")
print("HEAD last_round=", h.get("last_round"), "round_no=", h.get("round_no"), "orders_sha=", h.get("last_orders_sha"))

# origin tip
o = show("state-bm-a.json", "origin/main")
print("ORIGIN last_round=", o.get("last_round"), "round_no=", o.get("round_no"), "orders_sha=", o.get("last_orders_sha"))

d = json.load(open("state-bm-a.json", encoding="utf-8"))
print("DISK  last_round=", d.get("last_round"), "round_no=", d.get("round_no"), "orders_sha=", d.get("last_orders_sha"))
