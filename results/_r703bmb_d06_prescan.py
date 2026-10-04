# r703 bm-b: D-06 flow-sink prescan probe — structural map of five oversized pit domain files
# (D-20261002-06 flow-sink leg; entries listed with byte sizes + first 110 chars for flow/law classification)
import io, re

FILES = ['pit-engine', 'pit-pool', 'pit-protocol', 'pit-git-netpath', 'pit-git-surgery']

def main():
    out = io.open('results/_r703bmb_d06_prescan.md', 'w', encoding='utf-8')
    for name in FILES:
        p = 'research/%s.md' % name
        raw = open(p, 'rb').read()
        txt = raw.decode('utf-8')
        lines = txt.split('\n')
        out.write('## %s — %d bytes, %d lines\n' % (name, len(raw), len(lines)))
        for i, l in enumerate(lines):
            if re.match(r'^[-*] ', l) or l.startswith('#'):
                out.write('L%d [%dB] %s\n' % (i + 1, len(l.encode('utf-8')), l[:110]))
        out.write('\n')
    out.close()
    print('probe written')

if __name__ == '__main__':
    main()
