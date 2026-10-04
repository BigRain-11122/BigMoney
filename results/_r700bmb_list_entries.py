import json, io, sys
d = json.load(open("results/_r700bmb_codely_entries.json", encoding="utf-8"))
out = []
for e in d["entries"]:
    out.append(f"{e['line']:>5} {e['bytes']:>6}B {e['day']} {e['hdr'][:60]}")
open("results/_r700bmb_entries_list.txt", "w", encoding="utf-8").write("\n".join(out))
print("written", len(out), "lines")
