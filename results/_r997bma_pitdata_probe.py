import io, re
raw = open(r"research/pit-data.md", "rb").read()
text = raw.decode("utf-8")
print("total bytes:", len(raw))
print("CRLF count:", raw.count(b"\r\n"), "lone LF:", raw.count(b"\n") - raw.count(b"\r\n"))
lines = text.split("\r\n") if raw.count(b"\r\n") > 10 else text.split("\n")
for i, l in enumerate(lines):
    if l.lstrip().startswith("- [2026") or l.lstrip().startswith("[2026"):
        print(i, "|", len(l.encode("utf-8")), "B |", l[:60])
