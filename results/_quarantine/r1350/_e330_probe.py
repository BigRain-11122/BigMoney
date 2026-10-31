import sys, re
sys.path.insert(0, 'scripts')
import e326_template_parameter_consumers as e326

files = e326.corpus()
lines = 0
mut = 0
add = 0
ex = []
for path, src in files:
    ls = e326.code_lines(src)
    lines += len(ls)
    for n, t in ls:
        if re.search(r"def\s+\w+\s*\([^)]*\w+\s*=\s*(\[\]|\{\})", t):
            mut += 1
            if len(ex) < 3:
                ex.append((e326.relp(path), n, t.strip()[:80]))
        if "add_argument" in t:
            add += 1
print("sources", len(files), "codelines", lines, "mutable_defs", mut, "add_argument", add)
for e in ex:
    print(e)