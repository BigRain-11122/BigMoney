import subprocess


def blob(s):
    return subprocess.run(["git", "show", f":{s}:CODELY.md"], capture_output=True).stdout.decode("utf-8")


base, mine, theirs = blob("1"), blob("3"), blob("2")
bl, ml, tl = base.splitlines(), mine.splitlines(), theirs.splitlines()
bs, ms, ts_ = set(bl), set(ml), set(tl)

print(f"base={len(bl)} lines | mine(:3:)={len(ml)} | theirs(:2:)={len(tl)}")
their_new = [ln for ln in tl if ln not in bs and ln not in ms]
my_new = [ln for ln in ml if ln not in bs and ln not in ts_]
base_removed_by_theirs = [ln for ln in bl if ln not in tl and ln in ms]
base_removed_by_mine = [ln for ln in bl if ln not in ml and ln in ts_]
print(f"their_new={len(their_new)} my_new={len(my_new)} base_removed_by_theirs(also-in-mine)={len(base_removed_by_theirs)} base_removed_by_mine(also-in-theirs)={len(base_removed_by_mine)}")
for ln in their_new:
    print("THEIR-NEW:", ln[:150])
for ln in my_new:
    print("MY-NEW:", ln[:110])
for ln in base_removed_by_theirs:
    print("THEIRS-REMOVED(kept in mine):", ln[:110])
for ln in base_removed_by_mine:
    print("MINE-REMOVED(kept in theirs):", ln[:110])
