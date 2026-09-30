# r480 bm-b memory hot-cold reorg: r479 lines -> archive verbatim + pointer,
# new r480 pit law appended hot. 10KB hard line compliance (O-20260927-0230).
import sys, os
sys.stdout.reconfigure(encoding="utf-8")

hot = open('CODELY.md', encoding='utf-8').read()
lines = hot.splitlines()
r479 = [l for l in lines if ('r479 bm-b] O-20260930-2054' in l)
        or ('r479 bm-b] merge_lane_views' in l)]
assert len(r479) == 2, f"expected 2 r479 lines, got {len(r479)}"

arch_path = 'research/memory-archive/202609.md'
arch = open(arch_path, encoding='utf-8').read()
section = '\n\n## 热冷整编 2026-09-30 r480 bm-b 窗批\n\n' + '\n'.join(r479) + '\n'
if '热冷整编 2026-09-30 r480 bm-b 窗批' not in arch:
    with open(arch_path, 'a', encoding='utf-8') as f:
        f.write(section)
    print('archive appended', len(section), 'bytes')
else:
    print('archive section already present')

ptr = ('- 冷层指针（r480 合并·指针合并归档 r444 范式）：r479 bm-b O-2054 S2 烧批回执'
       '（550 runs/370.9s·批 3/4）+merge_lane_views owner_since=null 字符串比较坑'
       '（null 键 str(None)="None" 恒胜真时间戳+比较前 or "" 归一修法·selftest 0 FAIL）'
       '——两条全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r480 bm-b 窗批』节。')
new480 = ('- [2026-09-30 r480 bm-b] EOL 异面行级 union 假阳性坑（CODELY.md 15+1 UU 撞车解实弹）：'
          '两侧 EOL 异面（origin 整编版 LF vs 本机旧版 CRLF）时逐行字节比对=全行带 \\r 尾'
          '≠对侧行→33/33 全误判「新行」、prefix-identity 断言 byte0 即败（非真 reorg）；'
          '正解=比对前先归一 EOL（rstrip \\r / 统一 LF 面）再做行级 union。'
          '同窗发现=origin/main 曾提交未清冲突标记件（bm-a r492 的 _attrition_guard_scan.json '
          '携 <<<<<<< HEAD 块）——解=取 marker HEAD 侧行重建+json.loads 验后才写回+轮报告披露。'
          'How to apply：文本面 union 前必先探两侧 EOL 归一；读 origin 件见冲突标记即污染件须当窗修复。')

out = []
inserted_ptr = False
for l in lines:
    if l in r479:
        if not inserted_ptr:
            out.append(ptr)
            inserted_ptr = True
        continue
    out.append(l)
idx = out.index('### Reference')
out.insert(idx, new480)
final = '\n'.join(out) + '\n'
with open('CODELY.md', 'w', encoding='utf-8', newline='') as f:
    f.write(final)
print('hot size:', os.path.getsize('CODELY.md'), 'bytes; lines:', len(out))
assert os.path.getsize('CODELY.md') <= 10240, 'over 10KB hard line'
print('10KB hard line: PASS')
