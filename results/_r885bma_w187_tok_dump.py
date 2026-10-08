# -*- coding: utf-8 -*-
import ast
import io
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
t = io.open(r"results/_r881bma_w186_prereg_build.py", encoding="utf-8").read()
tree = ast.parse(t)


def ev(n):
    if isinstance(n, ast.Constant):
        return n.value
    raise AssertionError("unsupported %r" % ast.dump(n)[:60])


for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and \
       isinstance(node.targets[0], ast.Name) and node.targets[0].id == "TOK186":
        out = []
        for el in node.value.elts:
            if isinstance(el, ast.Tuple) and len(el.elts) == 2:
                out.append((ev(el.elts[0]), ev(el.elts[1])))
            elif isinstance(el, ast.Tuple) and len(el.elts) == 3:
                out.append((ev(el.elts[0]), ev(el.elts[1])))
        f = io.open(r"results/_r885bma_tok186_dump.txt", "w", encoding="utf-8")
        for old, tok in out:
            f.write("=== %s (old %d bytes) ===\n%r\n\n" % (tok, len(old), old[:400]))
        f.close()
        print("TOK186 entries:", len(out))
        # print the vestigial ones and short ones
        for old, tok in out:
            if "N17" in tok or "N170" in tok or "N169" in tok:
                print("VESTIGIAL", tok, repr(old))
