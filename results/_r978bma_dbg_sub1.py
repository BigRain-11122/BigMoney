import subprocess

GIT = r"C:\Program Files\Git\cmd\git.exe"
r = subprocess.run([GIT, "show", "d311a5439:research/PERPETUAL_N1_W237_PREREG.md"], capture_output=True)
tpl = r.stdout.decode("utf-8")
line1 = tpl.splitlines()[0]

src = open("results/_w238bma_prereg_derive.py", encoding="utf-8").read()
start = src.index("A(('# PERPETUAL-N1-W237")
seg = src[start + 4:]
end = seg.index("',\n   '# PERPETUAL-N1-W238")
old_mine = seg[:end]

# find all diff positions
n = len(line1)
for i in range(n):
    a = line1[i] if i < len(line1) else None
    b = old_mine[i] if i < len(old_mine) else None
    if a != b:
        print(f"pos {i}: tpl={a!r} (U+{ord(a):04X})  mine={b!r} (U+{ord(b):04X})")
        print("   tpl ctx :", line1[max(0,i-25):i+25])
        print("   mine ctx:", old_mine[max(0,i-25):i+25])
