import io, re, subprocess, sys, tempfile, os
sys.stdout.reconfigure(encoding="utf-8")

# 1) build_status compiles clean
import py_compile
py_compile.compile("monitor/build_status.py", doraise=True)
print("py_compile build_status: OK")

# 2) dashboard.html inline JS -> node --check
html = io.open("dashboard.html", encoding="utf-8").read()
blocks = re.findall(r"<script>(.*?)</script>", html, re.S)
assert blocks, "no inline script block found"
js = max(blocks, key=len)
tf = os.path.join(tempfile.gettempdir(), "_r638bmb_dash_check.js")
io.open(tf, "w", encoding="utf-8").write(js)
r = subprocess.run(["node", "--check", tf], capture_output=True, text=True)
print("node --check dashboard inline JS:", "OK (rc0)" if r.returncode == 0 else "FAIL")
if r.returncode != 0:
    print(r.stderr[:1500]); sys.exit(1)
print("VERIFICATION PASS")
