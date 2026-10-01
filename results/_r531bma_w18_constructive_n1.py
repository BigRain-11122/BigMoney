"""r531 bm-a: constructive merge of perpetual_faces_n1.py (theirs base + my W18 blocks).

Mechanical hunk-union produced interleaved frankenstein (verified: my W18 leg
tail spliced inside their W19 leg + broken PASS string). Constructive approach:
start from origin/main (bm-b W19 v3 superset), insert my three W18 blocks at
exact anchors, apply the single mandatory coherence fix to their stale
"no 15/18" prior-wave pin (W18 now registered -> expected list must include 18;
derive-from-keys law unchanged; disclosed in commit message).
"""
import subprocess, os, re, ast, sys

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
OUT = os.path.join(os.environ["TEMP"], "r531_surgical")
THEIRS = subprocess.check_output(["git", "-C", REPO, "rev-parse", "origin/main"]).decode().strip()
MINE = subprocess.check_output(["git", "-C", REPO, "rev-parse", "HEAD"]).decode().strip()
BASE = "c0c632b22"
PATH = "scripts/perpetual_faces_n1.py"

def show(rev):
    return subprocess.check_output(["git", "-C", REPO, "show", f"{rev}:{PATH}"]).decode("utf-8")

theirs = show(THEIRS)
mine = show(MINE)
base = show(BASE)

def added_lines(base_text, new_text):
    """Return the contiguous block(s) new_text added over base_text, as list of line-ranges."""
    bl, nl = base_text.split("\n"), new_text.split("\n")
    import difflib
    sm = difflib.SequenceMatcher(None, bl, nl, autojunk=False)
    blocks = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag in ("insert", "replace"):
            blocks.append((tag, i1, i2, j1, j2))
    return blocks, nl

blocks, mlines = added_lines(base, mine)
print("my additions over base (n1):", [(b[0], b[3], b[4]) for b in blocks])

# --- extract my three blocks from MINE (by line ranges from diff) ---
# Block A: WAVE_CONFIGS W18 row+comment; Block B: W18 selftest leg;
# Block C: PASS face segment. Identify by content anchors instead of diff
# ranges (more robust): find in MINE the block boundaries.

# Block A: from the '# W18 (r530 bm-a' comment line to the engine_owner line
a_start = mine.find("    # W18 (r530 bm-a")
assert a_start != -1
a_end = mine.find('"engine_owner": "bm-a"},', a_start)
assert a_end != -1
a_end = mine.find("\n", a_end) + 1
block_a = mine[a_start:a_end]

# Block B: from '# --- wave-18 face' to the restoring finally
b_start = mine.find("    # --- wave-18 face")
assert b_start != -1
b_end_marker = "    finally:\n        _set_wave(2)\n"
# the W18 leg's finally: find the marker AFTER b_start
b_end = mine.find(b_end_marker, b_start)
assert b_end != -1
b_end += len(b_end_marker)
block_b = mine[b_start:b_end]

# Block C: PASS face segment: text between the W17-face tail and the
# T-141 tail (string-literal pieces + newlines splice cleanly).
c_anchor = "law sec.4 W17 row, r328 bm-c] "
c_start = mine.find(c_anchor)
assert c_start != -1
c_start += len(c_anchor)
c_end_anchor = "+ T-141 s2 engine-lane claim "
c_end = mine.find(c_end_anchor, c_start)
assert c_end != -1
block_c = mine[c_start:c_end]

print("block A lines:", block_a.count("\n"), "| block B lines:", block_b.count("\n"),
      "| block C lines:", block_c.count("\n"))

# --- apply to THEIRS ---
m = theirs

# A: insert my W18 row before their W19 row comment
t19_cfg = m.find("    # W19 (")
assert t19_cfg != -1, "W19 config comment anchor missing in theirs"
m = m[:t19_cfg] + block_a + m[t19_cfg:]

# B: insert my W18 leg before their wave-19 selftest leg comment
t19_leg = m.find("    # --- wave-19 face")
assert t19_leg != -1, "wave-19 leg anchor missing"
m = m[:t19_leg] + block_b + "\n" + m[t19_leg:]

# C: insert my face into the PASS string between W17 face and W19 face
c_anchor_t = "law sec.4 W17 row, r328 bm-c] + W19 materializer face "
assert c_anchor_t in m, "PASS W19 face anchor missing"
m = m.replace(c_anchor_t,
              "law sec.4 W17 row, r328 bm-c] " + block_c + "+ W19 materializer face ", 1)

# Coherence fix (disclosed): their W19 prior-wave pin said no-18; W18 is now
# registered by the W18 freeze -> expected list gains 18. Derive law intact.
old_pin = ('assert sorted(w for w in WAVE_CONFIGS if w < 19) == \\\n'
           '            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17], \\\n'
           '            "W19 prior-wave set must derive from registry keys (no 15/18)"')
new_pin = ('assert sorted(w for w in WAVE_CONFIGS if w < 19) == \\\n'
           '            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18], \\\n'
           '            "W19 prior-wave set must derive from registry keys (no 15; " \\\n'
           '            "18 registered by W18 freeze r531 bm-a -- pin updated per " \\\n'
           '            "post-freeze coherence, derive law unchanged)"')
assert old_pin in m, "W19 prior-wave pin anchor missing"
m = m.replace(old_pin, new_pin, 1)

ast.parse(m)
merged_path = os.path.join(OUT, "merged_scripts__perpetual_faces_n1.py")
with open(merged_path, "w", encoding="utf-8", newline="") as f:
    f.write(m)
print("CONSTRUCTIVE MERGE OK ->", merged_path)
# sanity: orders
print("WAVE_CONFIGS keys:", re.findall(r"^\s+(\d+): \{.batch.: .PERPETUAL-N1", m, re.M))
print("_set_wave order:", re.findall(r"_set_wave\((\d+)\)", m))
print("faces in PASS:", [k for k in ("W18 materializer face", "W19 materializer face") if k in m])
print("T-141 count:", m.count("T-141 s2 engine-lane claim"))
