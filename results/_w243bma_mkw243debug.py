"""Debug copy of _w243bma_prereg_derive.py: replaces the failing final assert with
occurrence-context diagnostics. Deterministic re-run (git-show facts + live reads
unchanged; engine queue still empty)."""
import re

src = open('results/_w243bma_prereg_derive.py', encoding='utf-8').read()
needle = "assert out.count('541_404..541_603') == 2"
assert needle in src, 'anchor assert not found'
diag = (
    "_cnt = out.count('541_404..541_603')\n"
    "print('COUNT 541_404..541_603 =', _cnt)\n"
    "_pos = 0\n"
    "while True:\n"
    "    _i = out.find('541_404..541_603', _pos)\n"
    "    if _i < 0:\n"
    "        break\n"
    "    print('---occ at', _i, '---')\n"
    "    print(out[max(0, _i-160):_i+160].encode('unicode_escape').decode('ascii')[:700])\n"
    "    _pos = _i + 1\n"
)
# insert diagnostics right before the failing assert, keep the assert (will still fire after printing)
src = src.replace(needle, diag + needle.replace('== 2', '== 2  # kept; diagnostics above'))
open('results/_w243bma_prereg_debug.py', 'w', encoding='utf-8', newline='').write(src)
print('debug copy written')
