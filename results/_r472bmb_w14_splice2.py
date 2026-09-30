"""_r472bmb_w14_splice2.py -- replace the W13-shaped grammar builder
in the draft with the W14 builder payload."""
import sys

DRAFT = "results/_r472bmb_w14_runner_draft.py"
START = "def build_grammar_w14():"
END = "# ------------------------------------------------------------ Sobol draw leg"

text = open(DRAFT, encoding="utf-8").read()
i = text.find(START)
j = text.find(END)
if i < 0 or j < 0 or j <= i:
    print(f"SPLICE2-FAIL: start {i} end {j}")
    sys.exit(1)
payload = open("results/_r472bmb_w14_kit_grammar.py",
               encoding="utf-8").read()
old_lines = text[i:j].count("\n")
text = text[:i] + payload.rstrip() + "\n\n\n" + text[j:]
open(DRAFT, "w", encoding="utf-8", newline="\n").write(text)
print(f"splice2 OK: grammar builder {old_lines} -> "
      f"{payload.count(chr(10))} lines")
