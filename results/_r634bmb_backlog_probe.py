"""r634 bm-b: moneyflow panel status + PLAN.md s7 backlog probe."""
import json
import re

# 1) moneyflow panel state
try:
    mf = json.load(open(r"data/moneyflow/panel_status.json", encoding="utf-8"))
except Exception as e:
    try:
        import glob
        cands = glob.glob(r"data/moneyflow/*status*.json") + glob.glob(r"results/*moneyflow*status*.json")
        print("panel_status not at default path; candidates:", cands)
        mf = json.load(open(cands[0], encoding="utf-8")) if cands else {"err": str(e)}
    except Exception as e2:
        mf = {"err": str(e2)}
print("MF_PANEL:", json.dumps(mf, ensure_ascii=False)[:600])

# 2) watermark_red full content
wr = json.load(open(r"results/watermark_red.json", encoding="utf-8"))
print("WM_RED:", json.dumps(wr, ensure_ascii=False)[:500])

# 3) PLAN.md section 7 backlog
plan = open(r"PLAN.md", encoding="utf-8", errors="replace").read()
m = re.search(r"#+\s*7[\.、]?[^\n]*\n(.*)$", plan, re.S)
if m:
    tail = m.group(1)
else:
    tail = plan[-3000:]
open(r"results/_r634bmb_plan_s7.txt", "w", encoding="utf-8").write(tail[:6000])
print("PLAN_S7 written, tail chars:", len(tail))
