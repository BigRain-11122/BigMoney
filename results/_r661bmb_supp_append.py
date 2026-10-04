# Round 661 supplement append (post push-race merge window) -- safe line-entry append: unconditional \n separator (r439 lesson applied)
import io

SUPP = """
### r661 supplement (09:44): push-race merge window + r439-glue self-heal

- S7 push #1 blocked (claw footer + non-FF behind-6: bm-c r458 x3 + bm-a r662 x2 landed 09:35-09:39 during my S6) -> r437 netpath: absorb post-commit daemon faces (7cebe389a) -> merge origin/main -> **15 UU resolved standalone** (results/_r661bmb_merge_resolve.py): CODELY.md suffix-union+dedup (r453, markers==1) / same-day regen faces take-newer ours 09:36-09:39 vs theirs 09:32 (daily_report+live_usage twins consistent) / compute_audit hist-union 207 rows / token_usage per-key 0-pick -> whole-face ours (per-machine inner-ts superset proof, r456 zero-pick explicit-fallback law) -> reparse ALL PASS -> push #2 **DELIVERED 758a7be5a** (ahead=0 behind=0). No --no-verify used.
- r439-family line-glue self-healed in-merge: my CODELY append script's conditional sep (b"" when file not ending in \n) glued the r661 entry onto the r660 line tail; caught by resolver marker-at-line-start assertion; 1-byte "\n" insert repair, needle-count==1 gate; pushed version clean. Lesson restated (r439 law already covers): line-entry appends ALWAYS prepend \n, never conditional-sep.
- Post-merge trio: V682/Q521/D378 k-counters, burners alive, keepalive dba59ee9c + pool owner_since 09:26:12 stable; next-round watch per main report pointer.
"""

with io.open("logs/iteration-loop/round_reports.md", "rb") as f:
    data = f.read()
# unconditional separator: exactly one \n boundary before the new content block
if not data.endswith(b"\n"):
    data = data + b"\n"
with io.open("logs/iteration-loop/round_reports.md", "wb") as f:
    f.write(data + SUPP.encode("utf-8"))

with io.open("logs/iteration-loop/round_reports.md", "rb") as f:
    chk = f.read()
assert chk.count(b"r661 supplement (09:44)") == 1, "supplement append verify failed"
assert b"push-race merge window" in chk
print("supplement appended | total size:", len(chk))
