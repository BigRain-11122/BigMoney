import io

path = "logs/iteration-loop/round_reports.md"
with io.open(path, encoding="utf-8", newline="") as fh:
    text = fh.read()
marker = "| 2026-11-01T05:1x+08:00 | r1349"
idx = text.find(marker)
if idx < 0:
    print("marker not found")
elif idx > 0 and text[idx - 1] != "\n":
    text = text[:idx] + "\n" + text[idx:]
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    print("joined row split")
else:
    print("row already on its own line")