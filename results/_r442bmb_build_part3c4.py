"""r442 bm-b: fixup v4 -- line-based edits with content verification."""
SRC = open('results/_r442bmb_stage3c.py', encoding='utf-8').read()
lines = SRC.split('\n')
fails = []


def edit(line_no, expected_substr, new_lines, tag):
    """Insert new_lines AFTER line_no (1-based)."""
    idx = line_no - 1
    if expected_substr not in lines[idx]:
        fails.append(f'[{tag}] line {line_no} content mismatch: '
                     f'{lines[idx][:80]!r}')
        return
    lines[idx + 1:idx + 1] = new_lines


def verify(line_no, expected_substr, tag):
    if expected_substr not in lines[line_no - 1]:
        fails.append(f'[{tag}] line {line_no} mismatch: '
                     f'{lines[line_no - 1][:80]!r}')


# locate sites fresh
def find_all(substr):
    return [i + 1 for i, l in enumerate(lines) if substr in l]


metas = find_all('"amp_meta": amp_meta, "mom_meta": mom_meta,')
print('metas sites:', metas)
for ln in metas:
    indent = len(lines[ln - 1]) - len(lines[ln - 1].lstrip())
    edit(ln, '"amp_meta": amp_meta, "mom_meta": mom_meta,',
         [' ' * indent + '"std_meta": std_meta,'], f'metas@{ln}')

momdec = find_all("f\"{mom_meta['L']['decidable_days']}\")")
print('mom print end sites:', momdec)
for ln in momdec:
    indent = len(lines[ln - 1]) - len(lines[ln - 1].lstrip())
    std_print = [
        ' ' * indent + 'print(f"std meta L 120-bar-warmup "',
        ' ' * indent + 'f"{std_meta[\'L\'][\'open_days\']}open/"',
        ' ' * indent + 'f"{std_meta[\'L\'][\'closed_days\']}closed '
                       'decidable "',
        ' ' * indent + 'f"{std_meta[\'L\'][\'decidable_days\']} '
                       'std10-open "',
        ' ' * indent + 'f"{std_meta[\'L\'][\'std10_open_days\']}")',
    ]
    edit(ln, "f\"{mom_meta['L']['decidable_days']}\")", std_print,
         f'jprep-print@{ln}')
    break  # only the first (judge-prep) site

SRC = '\n'.join(lines)
open('results/_r442bmb_stage3c.py', 'w', encoding='utf-8').write(SRC)
print('fails:', fails)
