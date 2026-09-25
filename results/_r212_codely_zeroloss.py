"""R212 CODELY conflict deep-check: are the 29-ish lines missing from bm-b's side
archived in research/memory-archive/202609.md (their commits) or LOST?"""
import subprocess, sys, io
sys.stdout.reconfigure(encoding="utf-8")

def side_lines(path, n):
    r = subprocess.run(["git", "show", f":{n}:{path}"], capture_output=True)
    return r.stdout.decode("utf-8", errors="replace").splitlines()

ours = side_lines("CODELY.md", 2)      # bm-b r221 (origin)
theirs = side_lines("CODELY.md", 3)    # my R212
o_set, t_set = set(ours), set(theirs)
only_theirs = [l for l in theirs if l not in o_set and l.strip()]
only_ours = [l for l in ours if l not in t_set and l.strip()]
print("lines only in MY side (bm-b r221 lacks):", len(only_theirs))
for l in only_theirs:
    print("  MY>", l[:100])
print("lines only in bm-b side (I lack):", len(only_ours))
for l in only_ours:
    print("  BB>", l[:100])

# zero-loss check: does origin's memory archive contain the only_theirs lines?
r = subprocess.run(["git", "show", ":2:research/memory-archive/202609.md"], capture_output=True)
arch = r.stdout.decode("utf-8", errors="replace") if r.returncode == 0 else ""
missing = [l for l in only_theirs if l not in arch]
print("archive file present:", bool(arch), "| archive chars:", len(arch))
print("only_theirs lines NOT in bm-b archive:", len(missing))
for l in missing:
    print("  LOST>", l[:130])
