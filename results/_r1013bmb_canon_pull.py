# r1013 bm-b canon idle-guard-kit pull (group origin, python bytes channel; PS > redirect = UTF-16 trap law)
import subprocess, os, json

GROUP = r"C:\Fluxgroup\FluxGroup"
OUT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\results"
receipt = {"steps": {}}

r = subprocess.run(["git", "-C", GROUP, "fetch", "origin"], capture_output=True, timeout=120)
receipt["steps"]["group_fetch"] = {"rc": r.returncode, "err": r.stderr.decode("utf-8", "replace")[:200]}
if r.returncode != 0:
    print(json.dumps(receipt, ensure_ascii=False)); raise SystemExit(2)

r = subprocess.run(["git", "-C", GROUP, "rev-parse", "origin/main"], capture_output=True)
tip = r.stdout.decode().strip()
receipt["steps"]["group_origin_tip"] = tip

for sub in ("cph4/fleet/idle-guard-kit/", "cph4/fleet/work-bank/"):
    r = subprocess.run(["git", "-C", GROUP, "ls-tree", "--name-only", "origin/main", sub],
                       capture_output=True)
    receipt["steps"]["ls_" + sub] = [l for l in r.stdout.decode().split("\n") if l.strip()]

kit_files = receipt["steps"].get("ls_cph4/fleet/idle-guard-kit/", [])
pulled = {}
for f in kit_files:
    name = f.strip().split("/")[-1]
    r = subprocess.run(["git", "-C", GROUP, "show", "origin/main:" + f.strip()],
                       capture_output=True)
    if r.returncode == 0 and r.stdout:
        dst = os.path.join(OUT, "_r1013bmb_canon_" + name)
        open(dst, "wb").write(r.stdout)
        pulled[name] = len(r.stdout)
receipt["steps"]["pulled"] = pulled

# also pull the work-bank law header (first file, schema evidence) if present
bank_files = receipt["steps"].get("ls_cph4/fleet/work-bank/", [])
for f in bank_files[:1]:
    name = f.strip().split("/")[-1]
    r = subprocess.run(["git", "-C", GROUP, "show", "origin/main:" + f.strip()], capture_output=True)
    if r.returncode == 0 and r.stdout:
        dst = os.path.join(OUT, "_r1013bmb_canon_bank_" + name)
        open(dst, "wb").write(r.stdout)
        receipt["steps"]["bank_schema_pulled"] = {name: len(r.stdout)}

json.dump(receipt, open(os.path.join(OUT, "_r1013bmb_canon_pull.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(json.dumps(receipt["steps"], ensure_ascii=False))
