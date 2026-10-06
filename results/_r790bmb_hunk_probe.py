import subprocess, json, os, re
ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
os.chdir(ROOT)

for p in ["CODELY.md", "research/pit-git-resolver.md"]:
    c = open(p, "rb").read().decode("utf-8", "replace")
    lines = c.splitlines()
    n = 0
    print("="*90)
    print("FILE:", p, "total_lines:", len(lines))
    i = 0
    while i < len(lines):
        if lines[i].startswith("<<<<<<<"):
            # find block end
            j = i
            base_a, base_b, mid, close = [], None, [], None
            stage = "a"
            while j < len(lines) and not lines[j].startswith(">>>>>>>"):
                if lines[j].startswith("<<<<<<<"): stage="a"
                elif lines[j].startswith("|||||||"): stage="base"; base_b=[]
                elif lines[j].startswith("======="): stage="b"
                else:
                    if stage=="a": base_a.append(lines[j])
                    elif stage=="base": base_b.append(lines[j])
                    else: mid.append(lines[j])
                j += 1
            close = j
            n += 1
            print(f"--- HUNK {n}: lines {i+1}..{close+1} | ours {len(base_a)} lines | base {len(base_b) if base_b is not None else 'N/A'} | theirs {len(mid)} lines")
            print("  [OURS-replay] first/last:", (base_a[0][:110] if base_a else None), "||", (base_a[-1][:110] if base_a else None))
            print("  [THEIRS-origin] first/last:", (mid[0][:110] if mid else None), "||", (mid[-1][:110] if mid else None))
            if base_b is not None:
                print("  [BASE-ancestor] first/last:", (base_b[0][:110] if base_b else None), "||", (base_b[-1][:110] if base_b else None))
            i = close + 1
        else:
            i += 1
    print("hunks:", n)

print("="*90)
p = "results/_attrition_guard_scan.json"
def blob(ref):
    r = subprocess.run(["git", "show", f"{ref}:{p}"], capture_output=True)
    return r.stdout
for ref, name in ((":2", "stage2=origin/onto"), (":3", "stage3=ours-replay")):
    b = blob(ref)
    d = json.loads(b.decode("utf-8"))
    print(name, "keys:", list(d.keys())[:10])
    for k in ("generated", "ts", "updated", "generated_at", "scanned_at"):
        if k in d: print("   ", k, "=", d[k])
