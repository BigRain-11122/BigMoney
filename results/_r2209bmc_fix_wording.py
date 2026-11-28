"""r2209 (d): two last wording repairs from the sweep.

1. Line 1905's round column was a %d. The row sits between r1682 and r1683b, so
   the answer is *probably* 1683 -- but "probably" is not a number to print.
   It is recorded as lost with the two neighbours that bracket it, so a reader
   can see the inference instead of trusting it.
2. This round's own row described the defect by quoting the tokens, which the
   sweep then ate. It now says what happened in words.
"""
import io

P = "round_reports-bm-c.md"

REPL = [
    ("| 2026-11-14 23:1x | (值丢失) |",
     "| 2026-11-14 23:1x | (round-lost · 位于 r1682 与 r1683b 之间) |"),
    ("字面 `| (值丢失) | (值丢失) |` 加 `%`",
     "字面百分号占位行加单百分号泄漏"),
]

s = io.open(P, encoding="utf-8", newline="").read()
for old, new in REPL:
    if old in s:
        s = s.replace(old, new, 1)
        print("replaced:", old[:40])
    else:
        print("absent:", old[:40])
io.open(P, "w", encoding="utf-8", newline="").write(s)

s2 = io.open(P, encoding="utf-8", newline="").read()
rows = [l for l in s2.split("\n") if l.startswith("|")]
print("placeholders in table rows:",
      [i for i, l in enumerate(rows, 1) if any(t in l for t in ("%s", "%d", "%%", "(值丢失)"))])
print("round-lost rows:", s2.count("(round-lost"))
print("ts-lost rows:", s2.count("(ts-lost"))
