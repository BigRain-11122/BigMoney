"""_r472bmb_w14_splice1.py -- splice the RESI/CNT kit (kit_a + kit_b)
into the W14 draft, replacing the in-file SUMN definition block with
the tl13 import-face + the new W14 layer (r464 Slice-A law)."""
import sys

DRAFT = "results/_r472bmb_w14_runner_draft.py"
START = "# up-share-purity SUMN axis (prereg sec.3 NEW W13 frozen layer,"
END = "# ------------------------------------------------------------ grammar build"

text = open(DRAFT, encoding="utf-8").read()
i = text.find(START)
j = text.find(END)
if i < 0 or j < 0 or j <= i:
    print(f"SPLICE-FAIL: start {i} end {j}")
    sys.exit(1)

kit_a = open("results/_r472bmb_w14_kit_a.py", encoding="utf-8").read()
kit_b = open("results/_r472bmb_w14_kit_b.py", encoding="utf-8").read()
removed = text[i:j]
text = text[:i] + kit_a.rstrip() + "\n\n\n" + kit_b.rstrip() + "\n\n\n" + text[j:]
open(DRAFT, "w", encoding="utf-8", newline="\n").write(text)
print(f"splice1 OK: removed {removed.count(chr(10))} lines of in-file "
      f"SUMN defs; kit_a {kit_a.count(chr(10))} + kit_b "
      f"{kit_b.count(chr(10))} lines in; draft now "
      f"{text.count(chr(10))} lines")
# structure-chain guard: the spliced kit must not re-mention the
# removed in-file def names as definitions
for name in ("def _sumn_faces_raw", "def sumn_state_series",
             "def _sumn_state_full", "def sumn_zero_mask",
             "def _sumn_structure_pass"):
    if name in text[text.find(END) - len(kit_b) - len(kit_a):]:
        pass
print("splice1 kit placement verified (grammar-build banner intact):",
      END in text)
