with open(r'logs\iteration-loop\round_reports.md', 'rb') as f:
    data = f.read()
tail = data[-2200:]
lines = [l for l in tail.split(b'\n') if l.strip()]
out = []
out.append('RR last_byte=%r size=%d' % (data[-1:], len(data)))
out.append('RR last line (decoded-verb):')
out.append(lines[-1].decode('utf-8', 'replace'))
out.append('')
with open(r'research\HANDOVER.md', 'rb') as f:
    h = f.read()
out.append('HO last_byte=%r size=%d' % (h[-1:], len(h)))
hlines = [l for l in h[-3000:].split(b'\n') if l.strip()]
out.append('HO last line head (200ch):')
out.append(hlines[-1].decode('utf-8', 'replace')[:200])
with open(r'results\_r975bmb_tail_probe.txt', 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(out))
print('written results/_r975bmb_tail_probe.txt')
