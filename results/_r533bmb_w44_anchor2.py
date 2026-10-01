import re
src = open("scripts/perpetual_faces_n1.py", encoding="utf-8").read()
m = re.search(r"\n(43: \{.*?\"engine_owner\": \"bm-c\"\},)\n(\s+})", src, re.S)
print("entry found:", bool(m))
if m:
    print("--- exact 43 entry text ---")
    print(repr(m.group(1)))
    print("--- closing ---")
    print(repr(m.group(2)))
# N1_BANDS 43 entry in perpetual_faces.py
src2 = open("scripts/perpetual_faces.py", encoding="utf-8").read()
m2 = re.search(r"\n(\s*43: \{.*?\"engine_owner\": \"bm-c\"\},)\n(\s*})", src2, re.S)
print("--- N1_BANDS 43 entry ---")
print(repr(m2.group(1)) if m2 else "NOT FOUND")
print(repr(m2.group(2)) if m2 else "")
