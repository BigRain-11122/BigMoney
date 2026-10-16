# -*- coding: utf-8 -*-
# r1058 debug: diff the actual post-blanket downstream face vs my reconstruction
import io, re

t0 = io.open("results/_w255bmc_freeze_edits.py", encoding="utf-8").read()
t = t0
t = t.replace("(251, 250, 249, 248, 247, 246, 245, 244, 243, 242)",
              "(252, 251, 250, 249, 248, 247, 246, 245, 244, 243)")
t = t.replace('def fmt(n):  # 576301 -> "576_301"', 'def fmt(n):  # 578501 -> "578_501"')
t = t.replace("W256", "W257")
t = t.replace("255", "256")
t = t.replace("254", "255")

i = t.find("W257 = next free number")
actual = t[i:i + 1600] if i >= 0 else "NOT FOUND"

src = io.open("results/_w256bmc_derive_editor.py", encoding="utf-8").read()
m = re.search(r"_DOWNSTREAM_W254 = '''(.*?)'''", src, re.S)
lit = m.group(1)

def age_prev(s):
    s = s.replace("W255", "W256")
    s = s.replace("254", "255")
    s = s.replace("253", "254")
    return s

def age(s):
    s = s.replace("W256", "W257")
    s = s.replace("255", "256")
    s = s.replace("254", "255")
    return s

n = age_prev(lit)
n = n.replace("A naive 576101..578100 CLEAN", "A naive 578301..580300 CLEAN", 1)
n = n.replace("B naive 576301..576500 hops=0 CLEAN at naive, first-clean 576301..576500 BUT",
              "B naive 578501..578700 hops=0 CLEAN at naive, first-clean 578501..578700 BUT", 1)
n = n.replace("naive A window start 576_101 lands INSIDE the registered W255 B band 576_101..576_300",
              "naive A window start 578_301 lands INSIDE the registered W255 B band 578_301..578_500", 1)
n = n.replace("staircase face continuation since W252", "staircase face continuation since W251", 1)
mine = age(n)

print("ACTUAL len", len(actual))
print("MINE len", len(mine))
aw = actual.split(" ")
mw = mine.split(" ")
for k in range(min(len(aw), len(mw))):
    if aw[k] != mw[k]:
        print("first word diff at", k, repr(aw[k]), repr(mw[k]))
        print("ACTUAL ctx:", " ".join(aw[max(0, k - 12):k + 12]))
        print("MINE   ctx:", " ".join(mw[max(0, k - 12):k + 12]))
        break
else:
    print("word-prefix equal up to the shorter one")
print("---ACTUAL HEAD 400---")
print(actual[:400])
print("---MINE HEAD 400---")
print(mine[:400])
