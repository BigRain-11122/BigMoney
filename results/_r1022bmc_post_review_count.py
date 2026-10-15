import io
p = r"results\post_review\REPORT-20261015.md"
s = io.open(p, encoding="utf-8").read()
rows_x = s.count("\u2717")  # x mark
rows_v = s.count("\u2713")  # check mark
print("post_review today: check=%d x=%d" % (rows_v, rows_x))
if rows_x:
    for ln in s.splitlines():
        if "\u2717" in ln:
            print("XROW:", ln.encode("unicode_escape").decode("ascii")[:200])
