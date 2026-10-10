import ast

src = open('scripts/a158_tsgate_probe.py', encoding='utf-8').read()
tree = ast.parse(src)
fns = [n.name for n in tree.body if isinstance(n, ast.FunctionDef)]
consts = []
for n in tree.body:
    if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id.isupper():
        consts.append(n.targets[0].id)
print('functions:', fns)
print('consts:', consts)
print('has_main_guard:', '__main__' in src)
print('subcommands_mentioned:', [w for w in ('finalize', 'status', 'selftest', 'shard') if w in src])
