# r703 bm-b: pit-engine entry map for D-06 batch-2 sub-split (r439/r441 mechanism)
# Parses top-level law entries (bullet + continuation lines), byte-exact, EOL-aware.
# Output: results/_r703bmb_pit_engine_entrymap.txt
import io, re

SRC = 'research/pit-engine.md'

def main():
    raw = open(SRC, 'rb').read()
    crlf = raw.count(b'\r\n')
    lf = raw.count(b'\n') - crlf
    txt = raw.decode('utf-8')
    lines = txt.split('\n')
    out = io.open('results/_r703bmb_pit_engine_entrymap.txt', 'w', encoding='utf-8')
    out.write('FILE %s bytes=%d lines=%d CRLF_pairs=%d bare_LF=%d\n\n' % (SRC, len(raw), len(lines), crlf, lf))
    # entry starts: top-level bullets '- ['
    starts = [i for i, l in enumerate(lines) if l.startswith('- [')]
    for k, s in enumerate(starts):
        e = starts[k + 1] if k + 1 < len(starts) else len(lines)
        seg = '\n'.join(lines[s:e])
        # bytes of the entry segment including its trailing newline(s) as in raw join
        nb = len(seg.encode('utf-8'))
        first = lines[s][:130]
        out.write('E%02d L%d-L%d %dB | %s\n' % (k + 1, s + 1, e, nb, first))
    preface_end = starts[0] if starts else len(lines)
    pre = '\n'.join(lines[:preface_end])
    out.write('\nPREFACE L1-L%d %dB\n' % (preface_end, len(pre.encode('utf-8'))))
    total_entries = 0
    for k, s in enumerate(starts):
        e = starts[k + 1] if k + 1 < len(starts) else len(lines)
        total_entries += len('\n'.join(lines[s:e]).encode('utf-8'))
    out.write('ENTRIES_TOTAL_BYTES=%d\n' % total_entries)
    out.close()
    print('entry map written:', len(starts), 'entries')

if __name__ == '__main__':
    main()
