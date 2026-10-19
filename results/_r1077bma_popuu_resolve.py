import subprocess

r1 = subprocess.run(["git", "add", "results/watermark_red.json"], capture_output=True, text=True)
print("add rc", r1.returncode, r1.stderr.strip())
r2 = subprocess.run(["git", "stash", "drop", "stash@{0}"], capture_output=True, text=True)
print("drop rc", r2.returncode, r2.stdout.strip(), r2.stderr.strip())
r3 = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
print("status rc", r3.returncode)
print(r3.stdout)
r4 = subprocess.run(["git", "stash", "list"], capture_output=True, text=True)
print("stash list after:")
print(r4.stdout)
