# -*- coding: utf-8 -*-
# r1065 bm-c: extract canon identity-rep exact bytes, diff vs my builder needles
import io

ce = io.open("results/_w259bmc_derive_editor.py", encoding="utf-8", newline="").read()

def extract_rep_call(tag):
    i = ce.find(f', 1, "{tag}")')
    assert i >= 0, tag
    # walk back to the start of the enclosing rep(...) call
    j = ce.rfind("\nrep(", 0, i)
    return ce[j+1:i+len(f', 1, "{tag}")')+1]

for tag in ["P5e-tail-bassert2", "P5e-tail-bclean"]:
    txt = extract_rep_call(tag)
    print("==== %s (%d chars) ====" % (tag, len(txt)))
    print(repr(txt))
    print()

# diff check vs my builder's needles: compare the canon bassert2 vs my needle form
my_bassert2_old = '''rep(age(age_prev3(age_prev2(age_prev(age_prev255('            "W254 B 1-HOP own-A RESERVATION CASCADE face: the naive continuation "')),
    ))), age(age_prev3(age_prev2(age_prev(age_prev255('            "W254 B 1-HOP own-A RESERVATION CASCADE face: the naive continuation "'))))), 1, "P5e-tail-bassert2")'''
canon_bassert2 = extract_rep_call("P5e-tail-bassert2")
print("bassert2 == my-needle form:", canon_bassert2 == my_bassert2_old)
if canon_bassert2 != my_bassert2_old:
    # find first diff position
    for k, (a, b) in enumerate(zip(canon_bassert2, my_bassert2_old)):
        if a != b:
            print("first diff @", k)
            print("canon:", repr(canon_bassert2[max(0,k-40):k+40]))
            print("mine :", repr(my_bassert2_old[max(0,k-40):k+40]))
            break
    print("len canon=%d mine=%d" % (len(canon_bassert2), len(my_bassert2_old)))
