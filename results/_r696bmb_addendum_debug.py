"""r696 bm-b addendum debug: MARK count in CODELY.md now."""
MARK = "r696 bm-b] daemon tick \u00d7merge"
MARK2 = "daemon tick\u00d7merge"
blob = open("CODELY.md", "rb").read()
txt = blob.decode("utf-8", "replace")
print("MARK count =", txt.count(MARK))
print("MARK2 count =", txt.count(MARK2))
# check the byte-level: does the appended entry exist?
i = txt.find("r696 bm-b] daemon tick")
print("first idx =", i)
if i >= 0:
    print("context:", repr(txt[i:i + 80]))
# tail lines
lines = txt.rstrip().split("\n")
print("last line head:", lines[-1][:100])
print("n lines:", len(lines))
