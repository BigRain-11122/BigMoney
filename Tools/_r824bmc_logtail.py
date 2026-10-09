# r824 bm-c: sanitize a log file (CR/tqdm/binary) to pure-ascii tail for shell display
import io, re, sys

src, dst, n = sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 25
t = io.open(src, "r", encoding="utf-8", errors="replace")
raw = t.read().replace("\r", "\n")
lines = [l for l in raw.splitlines() if l.strip()]
out = [re.sub(r"[^\x20-\x7e]", "", l) for l in lines[-n:]]
open(dst, "w", encoding="ascii", errors="replace").write("\n".join(out))
print("wrote", dst, len(out), "lines")
