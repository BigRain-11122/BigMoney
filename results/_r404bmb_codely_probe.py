import subprocess

t2 = subprocess.run(["git", "show", ":2:CODELY.md"], capture_output=True).stdout.decode("utf-8").splitlines()
t3 = subprocess.run(["git", "show", ":3:CODELY.md"], capture_output=True).stdout.decode("utf-8").splitlines()
print("stage2 lines:", len(t2), "| stage3 lines:", len(t3))
# common prefix
i = 0
while i < len(t2) and i < len(t3) and t2[i] == t3[i]:
    i += 1
print("common prefix lines:", i)
print("--- stage2 unique lines (vs stage3 set) ---")
s3 = set(t3)
for n, l in enumerate(t2):
    if l not in s3:
        print(f"[2:{n}] {l[:150]}")
print("--- stage3 unique lines (vs stage2 set) ---")
s2 = set(t2)
for n, l in enumerate(t3):
    if l not in s2:
        print(f"[3:{n}] {l[:150]}")
