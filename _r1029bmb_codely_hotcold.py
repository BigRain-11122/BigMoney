# r1029 bm-b CODELY hot-cold integration (10KB hard-line breach heal, O-20260927-0230).
# Prescan rc3 recorded (registry hits CODELY.md + archive 202610.md) = authorized face
# per r1009 precedent (additive verbatim migration + line-level zero-loss assertion).
import datetime
import io
import json
import os

ROOT = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
CODELY = os.path.join(ROOT, 'CODELY.md')
ARCHIVE = os.path.join(ROOT, 'research', 'memory-archive', '202610.md')
RECEIPT = os.path.join(ROOT, 'results', '_r1029bmb_codely_hotcold_receipt.json')
NOW = datetime.datetime.now().isoformat(timespec='seconds')
SECTION = '## 热冷整编 2026-10-19 r1029 bm-b 窗批'
TARGET_PREFIXES = [
    '- [2026-10-19 10:2x r1020 bm-b]',
    '- [2026-10-19 10:3x r1020 bm-b]',
    '- [2026-10-19 10:5x r1021 bm-b]',
    '- [2026-10-19 14:2x r1024 bm-b]',
]
POINTER = ('- 冷层指针：r1020 轮号双面漂移坑（收口脚本必双写腿·轮首两面 round_no 不一致以仓根为准当窗 heal）'
           '+ r1020 git 排除面顺序坑（先 add -A 后 restore --staged·收口 git show --stat 自检）'
           '+ r1021 名义半音≠实测半音（分档分离门一律在合成输出实测面上校验·批产站=逐行校验-调整环）'
           '+ r1024 CONTENT-LOOP 站点直执正法（夜窗站 held 卡死后站·白天直执走 exec 脚本模板·禁裸 JSON 编辑 queue.json）'
           '四行全文 verbatim=archive 202610.md『热冷整编 2026-10-19 r1029 bm-b 窗批』节。')
NEW_PIT = ('- [2026-10-19 17:1x r1029 bm-b] **NATS CLI 子路径坑（实弹）**：稳定根 C:\\Fluxgroup\\Tools\\nats 下直呼 '
           'nats.exe=CommandNotFound——CLI 实际在 bin\\ 子目录（nats.exe/nats-server.exe 皆在 '
           'C:\\Fluxgroup\\Tools\\nats\\bin\\）；伴生脚本（register-nats-bus/fleet-live-status）内路径已正确=手工探针裸调用时才踩。'
           'How to apply：一切总线手工探针/kv get 一律用全路径 C:\\Fluxgroup\\Tools\\nats\\bin\\nats.exe。')


def detect_ending(raw):
    crlf = raw.count(b'\r\n')
    lf = raw.count(b'\n') - crlf
    return '\r\n' if crlf >= lf else '\n'


def main():
    raw = open(CODELY, 'rb').read()
    size_before = len(raw)
    ending = detect_ending(raw)
    text = raw.decode('utf-8')
    lines = text.splitlines()
    # uniform-ending guard: reassembly must be byte-identical
    assert ''.join(l + ending for l in lines) == text, 'mixed line endings -- abort, no write'
    # find targets
    idx = {}
    for p in TARGET_PREFIXES:
        hits = [i for i, l in enumerate(lines) if l.startswith(p)]
        assert len(hits) == 1, 'prefix not unique/found: %s -> %r' % (p, hits)
        idx[p] = hits[0]
    migrated = [lines[idx[p]] for p in TARGET_PREFIXES]
    # build new CODELY: remove migrated lines, append pointer + new pit at EOF
    kept = [l for i, l in enumerate(lines) if i not in set(idx.values())]
    kept.append(POINTER)
    kept.append(NEW_PIT)
    new_text = ''.join(l + ending for l in kept)
    new_raw = new_text.encode('utf-8')
    assert len(new_raw) <= 10240, 'post-integration size %d still >10KB hard line' % len(new_raw)
    # append archive section verbatim
    araw = open(ARCHIVE, 'rb').read()
    a_ending = detect_ending(araw)
    atext = araw.decode('utf-8')
    if not atext.endswith('\n'):
        atext += a_ending
    section_text = atext + a_ending + SECTION + a_ending + a_ending \
        + a_ending.join(migrated) + a_ending
    with io.open(ARCHIVE, 'w', encoding='utf-8', newline='') as f:
        f.write(section_text)
    # zero-loss verification: each migrated line present verbatim as a full line in archive
    back = io.open(ARCHIVE, 'r', encoding='utf-8', newline='').read()
    back_lines = back.splitlines()
    for m in migrated:
        assert m in back_lines, 'zero-loss FAILED: line not in archive: %s...' % m[:60]
    # write new CODELY only after archive verified
    with io.open(CODELY, 'w', encoding='utf-8', newline='') as f:
        f.write(new_text)
    # re-read verify
    chk = open(CODELY, 'rb').read()
    assert len(chk) == len(new_raw)
    for m in migrated:
        assert (m + ending) not in chk.decode('utf-8'), 'migrated line still in CODELY'
    receipt = {
        'ts': NOW, 'round': 1029, 'machine': 'bm-b',
        'law_ref': 'O-20260927-0230 10KB hard line + S4 watermark law; r1009 authorized-face precedent',
        'prescan': {'CODELY.md': 'rc3 registry hit (redline)', 'archive_202610.md': 'rc3 registry hit (redline)',
                    'authorization': 'hot-cold integration IS the mandated action for these exact faces '
                                     '(10KB hard line in file header); additive verbatim migration, zero deletion'},
        'size_before': size_before, 'size_after': len(chk),
        'breach_healed': size_before > 10240 and len(chk) <= 10240,
        'migrated_prefixes': TARGET_PREFIXES, 'migrated_lines': len(migrated),
        'zero_loss_verified': True, 'pointer_row_added': True, 'new_pit_row_added': True,
        'section': SECTION,
    }
    with io.open(RECEIPT, 'w', encoding='utf-8') as f:
        json.dump(receipt, f, ensure_ascii=False, indent=1)
    print(json.dumps({'ok': True, 'size_before': size_before, 'size_after': len(chk),
                      'migrated': len(migrated), 'zero_loss': True}, ensure_ascii=False))


if __name__ == '__main__':
    main()
