"""r671 T-166 full read + fund statement panel status."""
import json, io, os, glob, subprocess
REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
w = io.open(r"C:\Users\sjs20\AppData\Local\Temp\r671_t166full.txt", "w", encoding="utf-8")
j = json.load(open(REPO + r"\fleet\tasks\T-2026-10-04-166-P1.json", encoding="utf-8"))
for k in ("progress_r663_adopt", "progress_r665", "progress_r666", "progress_r667", "progress_r668", "progress_r669", "progress_r670"):
    if k in j:
        w.write(f"\n===== {k} =====\n{j[k]}\n")
w.write(f"\nstatus={j.get('status')} done_at={j.get('done_at')} result_ref={j.get('result_ref')}\n")
# collector status face
try:
    st = json.load(open(REPO + r"\results\fund_statement_update_status.json", encoding="utf-8"))
    w.write("\n== status face ==\n" + json.dumps(st, ensure_ascii=False, indent=1)[:2000] + "\n")
except Exception as e:
    w.write(f"status face fail: {e}\n")
# panel dir
d = REPO + r"\data\fund_statement_export"
if os.path.isdir(d):
    fs = os.listdir(d)
    w.write(f"\npanel dir: {len(fs)} files\n")
    for f in fs[:12]:
        w.write("  " + f + "\n")
w.close()
print("written")
