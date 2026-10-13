import re
p = 'results/_w235bma_freeze_edits.py'
lines = open(p, encoding='utf-8').read().split('\n')
suspicious = []
for idx, l in enumerate(lines):
    s = l.rstrip()
    # string-literal list item that does NOT end with a comma and next line starts a new string literal
    if re.match(r'^\s*(f?\'[^\']*(\'\'\')?\'|f?"[^"]*")$', s):
        # does not end with comma
        if not s.endswith(','):
            nxt = lines[idx + 1].lstrip() if idx + 1 < len(lines) else ''
            if nxt.startswith(('f"', '"', "f'", "'")):
                suspicious.append((idx + 1, s[:80], nxt[:60]))
print("adjacent-string-no-comma suspects:", len(suspicious))
for s in suspicious:
    print(s)
# also compile check
import py_compile
try:
    py_compile.compile(p, doraise=True)
    print("py_compile: OK")
except Exception as e:
    print("py_compile FAIL:", e)
