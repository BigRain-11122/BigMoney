"""r2209 (e): final global pass over the report.

The table sweep only looked at lines starting with "|". The same writer also
leaked into indented bullet lines and into rows whose leading pipe was lost, and
the double-percent escapes sit in prose ("8%% vol", "13.53%%/yr") where the
reader sees a stray percent.

Rule stays mechanical and never invents a value:
  * "%%" -> "%"              (a format escape that was never applied)
  * "%s" / "%d" -> "(值丢失)" (a slot whose value is genuinely gone)
"""
import io

P = "round_reports-bm-c.md"

s = io.open(P, encoding="utf-8", newline="").read()
lines = s.split("\n")

pct = 0
slot = 0
touched = []
for i, raw in enumerate(lines):
    had_cr = raw.endswith("\r")
    body = raw[:-1] if had_cr else raw
    if "%%" not in body and "%s" not in body and "%d" not in body:
        continue
    orig = body
    if "%%" in body:
        pct += body.count("%%")
        body = body.replace("%%", "%")
    if "%s" in body or "%d" in body:
        n = body.count("%s") + body.count("%d")
        slot += n
        body = body.replace("%s", "(值丢失)").replace("%d", "(值丢失)")
    if body != orig:
        lines[i] = body + ("\r" if had_cr else "")
        touched.append(i + 1)

io.open(P, "w", encoding="utf-8", newline="").write("\n".join(lines))
print("lines touched:", len(touched))
print("percent escapes unescaped:", pct)
print("slots marked lost:", slot)

s2 = io.open(P, encoding="utf-8", newline="").read()
left = [i for i, l in enumerate(s2.split("\n"), 1) if "%s" in l or "%d" in l or "%%" in l]
print("file lines still carrying a placeholder:", left)
