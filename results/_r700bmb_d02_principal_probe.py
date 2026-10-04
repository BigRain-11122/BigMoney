# r700 bm-b: D-20261002-02 principal self-attestation probe (default principal full-line, r576 bm-b lineage)
# Evidence: schtasks /query /xml LogonType for Bigmoney task family on bm-b.
import subprocess, os, json, sys

TASKS = ["Bigmoney-IterationLoop", "Bigmoney-LoopWatchdog", "Bigmoney-SatEngine-bm-b",
         "Bigmoney-IntradayMarks", "Bigmoney-Autofill", "Bigmoney-AutofillWatchdog"]
out = {}
rows = []
for t in TASKS:
    r = subprocess.run(["schtasks", "/query", "/tn", t, "/xml"], capture_output=True, timeout=60)
    xml = r.stdout.decode("utf-16", errors="replace") if r.returncode == 0 else ""
    if not xml:
        rows.append({"task": t, "exists": False})
        continue
    lt = logon = ""
    import re
    m = re.search(r"<LogonType>([^<]+)</LogonType>", xml)
    if m: lt = m.group(1).strip()
    m2 = re.search(r"<UserId>([^<]+)</UserId>", xml)
    if m2: logon = m2.group(1).strip()
    rows.append({"task": t, "exists": True, "logon_type": lt, "user_id": logon})
# enumerate any other Bigmoney-* tasks actually registered (belt+braces full-line audit)
r2 = subprocess.run(["schtasks", "/query", "/fo", "CSV"], capture_output=True, timeout=120)
lines = r2.stdout.decode("gbk", errors="replace").splitlines()
fam = [ln.split(",")[0].strip('"') for ln in lines if "bigmoney" in ln.lower() and ln.startswith('"')]
extra = sorted(set(fam) - {t for t in TASKS})
verdict_rows_bad = [x for x in rows if x.get("exists") and x["logon_type"] in ("S4U", "2")]
res = {
  "probe": "r700bmb_d02_principal_selfattest",
  "decision_ref": "D-20261002-02 (default principal full-line; S4U 0x80070005 not installable in this env)",
  "lineage": "bm-b default-principal single-source since r576; r676 three-source adjudication",
  "tasks": rows,
  "other_bigmoney_tasks": extra,
  "s4u_found": bool(verdict_rows_bad),
  "verdict": "PASS" if not verdict_rows_bad else "FAIL",
}
p = os.path.join("results", "_r700bmb_d02_principal_selfattest.json")
open(p, "w", encoding="utf-8").write(json.dumps(res, ensure_ascii=False, indent=1))
print("verdict:", res["verdict"], "| tasks_checked:", len(rows), "| extra:", extra)
for x in rows:
    print(f"  {x['task']}: exists={x.get('exists')} logon_type={x.get('logon_type','-')} user={x.get('user_id','-')}")
