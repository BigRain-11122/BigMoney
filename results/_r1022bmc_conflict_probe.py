import subprocess, difflib
def stage(n):
    return subprocess.run(["git","show",f":{n}:results/post_review.jsonl"],capture_output=True).stdout.decode("utf-8").splitlines()
a = stage(2)  # ours = origin/bm-a side
b = stage(3)  # theirs = mine
print("lines", len(a), len(b))
diff = [l for l in difflib.unified_diff(a, b, lineterm="", n=0)]
print("diff lines:", len(diff))
for l in diff[:16]:
    print(l[:180].encode("unicode_escape").decode("ascii"))
