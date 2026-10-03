# r622 bm-b: DOM-equivalent live-fire acceptance for fund_family face fix
# (execute the exact render JS from dashboard.html against the real
#  dashboard_status.js data via MiniRacer, then assert DIVLOWVOL visible)
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

try:
    from py_mini_racer import MiniRacer
except Exception as e:
    print("SKIP: py_mini_racer unavailable:", e)
    sys.exit(0)

js_data = open("results/dashboard_status.js", encoding="utf-8").read()
seg = open("results/_r622bmb_render_fund.txt", encoding="utf-8").read()
data_obj = js_data[js_data.find("{"):].rstrip().rstrip(";")

ctx = MiniRacer()
ctx.eval("var D = " + data_obj + ";")
ctx.eval("var rows=[]; var esc=function(s){return String(s==null?'':s);}; "
         "var n2=function(s){return s==null?'-':String(s);};")
ctx.eval("var chainRow=function(a,b,c,d){return {label:a,text:b,cls:c,tip:d};};")
seg_clean = seg.replace("el.innerHTML = rows.join(\"\")", "").replace(
    "el.innerHTML = rows.join(\"\") || '<div class=\"empty\">'", "")
ctx.eval(seg_clean)
rendered = ctx.eval("rows.map(r=>r.label+' :: '+r.text).join('\\n')")
open("results/_r622bmb_dom_verdict.txt", "w", encoding="utf-8").write(rendered)

lines = rendered.split("\n")
ff_lines = [l for l in lines if "VALUE" in l or "QUALITY" in l or "DIVLOWVOL" in l]
ok_div = any("DIVLOWVOL" in l for l in ff_lines)
ok_val = any("VALUE[" in l for l in ff_lines)
ok_qlt = any("QUALITY[" in l for l in ff_lines)
print("PASS-divlowvol-visible:", ok_div)
print("PASS-value-visible:", ok_val)
print("PASS-quality-visible:", ok_qlt)
print("VERDICT:", "PASS" if (ok_div and ok_val and ok_qlt) else "FAIL")
sys.exit(0 if (ok_div and ok_val and ok_qlt) else 1)
