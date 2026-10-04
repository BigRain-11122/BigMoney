# r668 bm-b episodes.csv duplicate-burn divergence probe (r446 probe-as-file law)
import subprocess, hashlib

a = subprocess.run(["git", "show", "HEAD:results/theme_judge_p1/episodes.csv"],
                   capture_output=True).stdout
b = open("results/theme_judge_p1/episodes.csv", "rb").read()
ra = a.decode("utf-8", "replace").splitlines()
rb = b.decode("utf-8", "replace").splitlines()
print("HEAD rows:", len(ra), "| now rows:", len(rb))
print("header HEAD:", ra[0][:160])
print("header now :", rb[0][:160])
sa, sb = sorted(ra[1:]), sorted(rb[1:])
print("sorted-rows identical:", sa == sb)
if sa != sb:
    diff_ct = sum(1 for x, y in zip(sa, sb) if x != y)
    print("sorted-position diffs:", diff_ct)
    for x, y in zip(sa, sb):
        if x != y:
            print("HEAD row:", x[:300])
            print("now  row:", y[:300])
            break
    seta, setb = set(ra[1:]), set(rb[1:])
    print("only-in-HEAD:", len(seta - setb), "| only-in-now:", len(setb - seta))
    for x in list(seta - setb)[:2]:
        print("HEAD-only:", x[:300])
    for x in list(setb - seta)[:2]:
        print("now-only :", x[:300])
else:
    print("order-only difference; first raw rows:")
    print("HEAD[1]:", ra[1][:200])
    print("now [1]:", rb[1][:200])
