import re, os, glob
t = open('dashboard.html', encoding='utf-8', errors='replace').read()
print('dashboard.html script srcs:', sorted(set(re.findall(r'src="([^"]+)"', t))))
t2 = open('town.html', encoding='utf-8', errors='replace').read()
print('town.html script srcs:', sorted(set(re.findall(r'src="([^"]+)"', t2))))
print('results dashboard files:', [f for f in os.listdir('results') if 'dashboard' in f.lower()])
print('docs htmls:', glob.glob('docs/**/*.html', recursive=True)[:10])
# check what update_status consumers exist in repo scripts
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ('.git', '__pycache__', 'data', 'Money02', 'legacy', 'node_modules')]
    for f in files:
        if f.endswith('.py') and ('monitor' in root or 'dashboard' in f):
            p = os.path.join(root, f)
            s = open(p, encoding='utf-8', errors='replace').read()
            if 'update_status' in s:
                print('update_status consumer:', p)
