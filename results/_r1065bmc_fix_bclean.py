# -*- coding: utf-8 -*-
# r1065 bm-c: FIX identity-6level-bclean needle/replacement in _r1065bmc_build_editor.py
# Method: derive correct forms MECHANICALLY from canon bytes (no eyeball paren counting).
#  - needle  == canon rep-call text (trailing \n stripped, matching bassert2 needle convention)
#  - replacement == canon text transformed to 6-level:
#        age(age_prev3( -> age(age_prev4(age_prev3(   (x2)
#        first-chain close  ",\n    )))," -> ",\n    )))),"   (+1 paren)
#        second-chain close "'))))), 1, \"" -> "')))))), 1, \"" (+1 paren)
import io, sys

BUILDER = "results/_r1065bmc_build_editor.py"
CANON = "results/_w259bmc_derive_editor.py"

ce = io.open(CANON, encoding="utf-8", newline="").read()
bs = io.open(BUILDER, encoding="utf-8", newline="").read()

def extract_rep_call(txt, tag):
    i = txt.find(', 1, "%s")' % tag)
    assert i >= 0, "tag not found in canon: " + tag
    j = txt.rfind("\nrep(", 0, i)
    assert j >= 0, "rep( start not found for " + tag
    end = i + len(', 1, "%s")' % tag)
    return txt[j+1:end]

def to_6level(t):
    assert t.count("age(age_prev3(") == 2, "age(age_prev3( count!=2"
    t2 = t.replace("age(age_prev3(", "age(age_prev4(age_prev3(")
    assert t2.count("age(age_prev4(age_prev3(") == 2
    assert t2.count("),\n    ))),") == 1, "first-chain close marker count!=1"
    t3 = t2.replace("),\n    ))),", "),\n    )))),")
    assert t3.count("'), 1, \"") == 0 and t3.count("'))))), 1, \"") == 1, "second-chain close marker count!=1"
    t4 = t3.replace("'))))), 1, \"", "')))))), 1, \"")
    # paren balance check on the whole call
    assert t4.count("(") == t4.count(")"), "unbalanced parens in 6-level form: %d vs %d" % (t4.count("("), t4.count(")"))
    return t4

def builder_block(src, tag):
    # locate rep(...,\n    1, "tag") block in builder source; walk back to the rep(""" start
    marker = '1, "%s")' % tag
    i = src.find(marker)
    assert i >= 0, "builder block not found: " + tag
    j = src.rfind("\nrep(", 0, i)
    assert j >= 0, "builder rep( start not found: " + tag
    end = i + len(marker)
    return j+1, end, src[j+1:end]

changed = []
for tag in ["P5e-tail-bassert2", "P5e-tail-bclean"]:
    idtag = "identity-6level-" + tag.split("-")[-1]
    canon_t = extract_rep_call(ce, tag)
    if canon_t.endswith("\n"):
        canon_t = canon_t[:-1]
    needle = canon_t
    repl6 = to_6level(canon_t)
    s, e, block = builder_block(bs, idtag)
    # parse the two triple-quoted literals inside the block
    a = block.find('"""'); assert a >= 0
    b = block.find('"""', a+3); assert b >= 0
    c = block.find('"""', b+3); assert c >= 0
    d = block.find('"""', c+3); assert d >= 0
    old_needle = block[a+3:b]
    old_repl = block[c+3:d]
    print("[%s] builder needle == canon: %s (needle %dB, canon %dB)" % (idtag, old_needle == needle, len(old_needle), len(needle)))
    print("[%s] builder repl == derived-6level: %s (repl %dB, derived %dB)" % (idtag, old_repl == repl6, len(old_repl), len(repl6)))
    if old_needle != needle or old_repl != repl6:
        newblock = 'rep("""' + needle + '""",\n    """' + repl6 + '""",\n    1, "%s")' % idtag
        bs = bs[:s] + newblock + bs[e:]
        changed.append(idtag)
        print("[%s] REWRITTEN." % idtag)

if changed:
    io.open(BUILDER, "w", encoding="utf-8", newline="").write(bs)
    print("builder updated, changed blocks:", changed)
else:
    print("builder already correct, nothing changed")

# ---- post-fix verification ----
bs2 = io.open(BUILDER, encoding="utf-8", newline="").read()
for tag in ["P5e-tail-bassert2", "P5e-tail-bclean"]:
    idtag = "identity-6level-" + tag.split("-")[-1]
    canon_t = extract_rep_call(ce, tag)
    if canon_t.endswith("\n"):
        canon_t = canon_t[:-1]
    needle = canon_t
    assert bs2.count(needle) == 1, "post-fix: needle for %s not found exactly once in builder (count=%d)" % (idtag, bs2.count(needle))
    # needle must hit canon exactly once
    assert ce.count(needle) == 1, "needle for %s count in canon != 1 (=%d)" % (idtag, ce.count(needle))
    s, e, block = builder_block(bs2, idtag)
    a = block.find('"""'); b = block.find('"""', a+3)
    c = block.find('"""', b+3); d = block.find('"""', c+3)
    assert block[a+3:b] == needle, idtag + " needle mismatch post-fix"
    repl = block[c+3:d]
    assert repl.count("(") == repl.count(")"), idtag + " repl paren unbalanced"
    assert "age_prev4(" in repl and repl.count("age(age_prev4(age_prev3(") == 2, idtag + " repl 6-level form wrong"
    print("[%s] POST-FIX VERIFIED: needle==canon(x1 in canon), repl balanced+6level" % idtag)

import py_compile
py_compile.compile(BUILDER, doraise=True)
print("BUILDER COMPILES OK")
