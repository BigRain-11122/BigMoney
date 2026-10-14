import io
out = io.open(r"results\_r997bma_queue_rows.txt","w",encoding="utf-8")
for f in ('state/queue/tech.md','state/queue/explore.md'):
    t = io.open(f,encoding="utf-8").read()
    out.write("==== %s ====\n" % f)
    for l in t.splitlines():
        s=l.strip()
        if s.startswith('|') and ('T2' in s[:6] or 'E1' in s[:6] or 'E2' in s[:6]):
            out.write(s + "\n\n")
out.close()
print("done")
