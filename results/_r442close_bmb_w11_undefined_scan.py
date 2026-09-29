"""r442-close per-function undefined-name scan (upgraded from module
net): proper function-local scope analysis. Catches landmines of the
r242 surgery family that py_compile/import/selftest cannot see
(generate crashed 23:30:01 on _amp_state_full; screen-finalize carried
stf/std_seg/gvvvsktsams_seg unassigned).

Scope model per function F: builtins + module imports/assigns/defs +
F args + any Store/NamedExpr target within F (coarse includes nested
comprehension vars -- false-negative prone only for UnboundLocalError
ordering class, which this scan deliberately does not chase).
"""
import ast
import builtins

SRC = "scripts/trial_labor_w11.py"
tree = ast.parse(open(SRC, encoding="utf-8").read())
bi = set(dir(builtins))

mod_names = set()
for n in ast.walk(tree):
    if isinstance(n, (ast.Import, ast.ImportFrom)):
        for a in n.names:
            if isinstance(n, ast.Import):
                mod_names.add((a.asname or a.name).split(".")[0])
            elif a.name != "*":
                mod_names.add(a.asname or a.name)
    elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef,
                       ast.ClassDef)):
        mod_names.add(n.name)
    elif isinstance(n, (ast.Assign, ast.AnnAssign, ast.For,
                         ast.comprehension, ast.ExceptHandler,
                         ast.Global, ast.Nonlocal)):
        for t in ast.walk(n):
            if isinstance(t, ast.Name) and isinstance(t.ctx, ast.Store):
                mod_names.add(t.id)
            elif isinstance(t, ast.NamedExpr):
                if isinstance(t.target, ast.Name):
                    mod_names.add(t.target.id)
    elif isinstance(n, ast.NamedExpr) and isinstance(n.target, ast.Name):
        mod_names.add(n.target.id)
    elif isinstance(n, ast.Lambda):
        mod_names.update(a.arg for a in
                         n.args.args + n.args.kwonlyargs)
    elif isinstance(n, ast.arguments):
        pass


def stores_in(node):
    out = set()
    for t in ast.walk(node):
        if isinstance(t, ast.Name) and isinstance(t.ctx, ast.Store):
            out.add(t.id)
        elif isinstance(t, ast.NamedExpr):
            if isinstance(t.target, ast.Name):
                out.add(t.target.id)
        elif isinstance(t, (ast.FunctionDef, ast.AsyncFunctionDef,
                            ast.Lambda)):
            a = t.args
            out.update(x.arg for x in
                       list(getattr(a, "posonlyargs", []))
                       + list(a.args) + list(a.kwonlyargs))
            if a.vararg:
                out.add(a.vararg.arg)
            if a.kwarg:
                out.add(a.kwarg.arg)
        elif isinstance(t, (ast.ExceptHandler,)):
            if t.name:
                out.add(t.name)
        elif isinstance(t, (ast.Global, ast.Nonlocal)):
            out.update(x.split(".")[0] for x in t.names)
    return out


probs = []
for fn in [x for x in ast.walk(tree)
           if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef))]:
    local = stores_in(fn)
    args = set()
    a = fn.args
    args.update(x.arg for x in list(getattr(a, "posonlyargs", []))
                + list(a.args) + list(a.kwonlyargs))
    if a.vararg:
        args.add(a.vararg.arg)
    if a.kwarg:
        args.add(a.kwarg.arg)
    scope = bi | mod_names | local | args | {"__file__", "__name__",
                                             "__doc__"}
    for t in ast.walk(fn):
        if (isinstance(t, ast.Name) and isinstance(t.ctx, ast.Load)
                and t.id not in scope):
            probs.append((fn.name, t.lineno, t.id))

probs.sort()
print("PER-FUNCTION UNDEFINED:", len(probs))
for fnname, ln, nm in probs[:60]:
    print(f"  {fnname} L{ln}: {nm}")
if not probs:
    print("CLEAN -- zero function-scope undefined names")
