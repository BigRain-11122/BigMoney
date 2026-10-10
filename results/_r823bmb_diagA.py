import subprocess, re, json

for p, j in (("results/compute_audit.json", 23910),
             ("results/regime_state.json", 156)):
    t = subprocess.run(["git", "show", ":2:" + p],
                       capture_output=True).stdout.decode("utf-8",
                                                          errors="replace")
    lines = t.split("\n")
    A = lines[1:j]
    a = "\n".join(A)
    tss = re.findall(r'"ts": "([0-9: \-T]+)"', a)
    print("==", p, "A_lines=", len(A),
          "A_nested_markers=", a.count("<<<<<<<"),
          "ts_first=", tss[:2], "ts_last=", tss[-2:])
    try:
        d = json.loads(a.replace("\r", ""))
        print("   A parses after raw CR strip; keys=", list(d)[:8])
    except Exception as e:
        print("   A unparseable:", str(e)[:120])
        # locate the fault line
        try:
            json.loads(a.replace("\r", ""))
        except json.JSONDecodeError as je:
            seg = a.replace("\r", "")[max(0, je.pos - 60):je.pos + 60]
            print("   fault ctx:", repr(seg))
