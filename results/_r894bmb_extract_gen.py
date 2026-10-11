# r894 bm-b: extract generate_copyright.py + README from FluxGroup origin/main blob (zero tree touch)
import subprocess, sys

REPO = r"C:\Fluxgroup\FluxGroup"
OUT = r"C:\Users\Administrator\AppData\Local\Temp\gen_copyright.py"
OUT_README = r"C:\Users\Administrator\AppData\Local\Temp\gen_copyright_README.md"

def blob(path):
    r = subprocess.run(["git", "-C", REPO, "show", "origin/main:" + path],
                       capture_output=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr.decode("utf-8", "replace"))
        sys.exit(2)
    return r.stdout

d = blob("\u8f6f\u8457\u7533\u8bf7\u6750\u6599/generate_copyright.py")  # 软著申请材料/generate_copyright.py
open(OUT, "wb").write(d)
print("script bytes:", len(d))

try:
    rd = blob("\u8f6f\u8457\u7533\u8bf7\u6750\u6599/README.md")
    open(OUT_README, "wb").write(rd)
    print("readme bytes:", len(rd))
except SystemExit:
    print("readme missing (non-fatal)")
