import io, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
src = open(r"K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\kf-demo-20261012\JAY-REDO-PACK-v1.py", encoding="utf-8").read().splitlines()
print("total lines", len(src))
pat = re.compile(r"^([A-Z_][A-Z0-9_]*)\s*=")
for i, l in enumerate(src, 1):
    m = pat.match(l)
    if m:
        print(i, l[:160])
# also find where I2V full prompts might live: search for 'locked frame'
print("--- locked-frame occurrences ---")
for i, l in enumerate(src, 1):
    if "locked" in l.lower():
        print(i, l.strip()[:220])
