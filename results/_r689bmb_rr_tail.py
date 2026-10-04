# r689: round_reports tail region dump (bytes-mode read, r641 mixed-encoding law)
import io, os
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rp = os.path.join(root, "logs", "iteration-loop", "round_reports.md")
with io.open(rp, "rb") as f:
    lines = f.read().decode("utf-8", "replace").splitlines()
out = os.path.join(root, "results", "_r689bmb_rr_tail.txt")
with io.open(out, "w", encoding="utf-8", newline="\n") as w:
    w.write("total_lines %d\n" % len(lines))
    for i, ln in enumerate(lines[-16:], start=len(lines) - 16):
        w.write("L%d: %s\n" % (i, ln[:400]))
print("dumped", out)
