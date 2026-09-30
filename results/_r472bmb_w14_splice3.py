"""_r472bmb_w14_splice3.py -- replace the exclusion loader + _excluded
in the draft with the W14 14-source payload."""
import sys

DRAFT = "results/_r472bmb_w14_runner_draft.py"
START = "# ------------------------------------------------ exclusion (25 real-reads)"
END = "# -------------------------------------------- effective face + engine curves"

text = open(DRAFT, encoding="utf-8").read()
i = text.find(START)
j = text.find(END)
if i < 0 or j < 0 or j <= i:
    print(f"SPLICE3-FAIL: start {i} end {j}")
    sys.exit(1)
payload = open("results/_r472bmb_w14_kit_excl.py", encoding="utf-8").read()
old_lines = text[i:j].count("\n")
text = text[:i] + payload.rstrip() + "\n\n\n" + text[j:]
open(DRAFT, "w", encoding="utf-8", newline="\n").write(text)
print(f"splice3 OK: exclusion loader {old_lines} -> "
      f"{payload.count(chr(10))} lines")
