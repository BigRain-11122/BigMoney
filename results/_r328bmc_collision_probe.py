import subprocess, re
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
def show(p):
    return subprocess.check_output(["git", "show", "origin/main:" + p], cwd=ROOT).decode("utf-8", errors="replace")
def ls_tree(p):
    return subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", p], cwd=ROOT).decode("utf-8", errors="replace")

law = show("research/PERPETUAL_FACES.md")
rows = [l[:52] for l in law.splitlines() if l.startswith("- N1 ") and ("\u6ce2" in l)]
print("LAW_ROWS:", rows)
pf = show("scripts/perpetual_faces.py")
ks = re.findall(r"^\s+(\d+): \{\"a\"", pf, re.M)
print("N1_BANDS_KEYS:", ks)
n1 = show("scripts/perpetual_faces_n1.py")
ks2 = re.findall(r"^\s+(\d+): \{\"batch\"", n1, re.M)
print("WAVE_CONFIGS_KEYS:", ks2)
res = ls_tree("research/")
print("W17_PREREG_ON_ORIGIN:", "PERPETUAL_N1_W17_PREREG" in res)
print("W19_PREREG_ON_ORIGIN:", "PERPETUAL_N1_W19_PREREG" in res)
w19 = show("scripts/perpetual_faces.py")
m17 = re.search(r"17: \{\"a\": \((\d+), (\d+)\), \"b_exit\": \((\d+), (\d+)\)", w19)
print("ORIGIN_N1_BANDS_17:", m17.groups() if m17 else "ABSENT")
m19 = re.search(r"19: \{\"a\": \((\d+), (\d+)\), \"b_exit\": \((\d+), (\d+)\)", w19)
print("ORIGIN_N1_BANDS_19:", m19.groups() if m19 else "ABSENT")
