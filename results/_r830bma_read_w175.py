import io, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
t = io.open('research/PERPETUAL_N1_W175_PREREG.md', encoding='utf-8').read()
i = t.find('带位')
print(t[i:i+3000])
