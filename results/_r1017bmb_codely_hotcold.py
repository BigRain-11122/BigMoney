"""r1017 bm-b CODELY.md hot-cold split (mandated by >10KB hard line, O-20260927-0230).
treasure_guard prescan rc3 (both faces are registry redline) -> sanctioned escape =
摘录存旁 (guard's own named alternative for ledger/memory faces): rows extracted
VERBATIM to archive 202610.md (append-only) BEFORE any CODELY.md edit; zero-loss
assertion post-write; receipt face. No row content is lost anywhere."""
import datetime
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # bigmoney root (script in results/)
CODELY = os.path.join(ROOT, 'CODELY.md')
ARCHIVE = os.path.join(ROOT, 'research', 'memory-archive', '202610.md')
RECEIPT = os.path.join(ROOT, 'results', '_r1017bmb_codely_hotcold_receipt.json')

MOVE_PREFIXES = [
    '- [2026-10-18 22:1x r1011 bm-b]',
    '- [2026-10-18 23:5x r1012 bm-b]',
    '- [2026-10-19 00:1x r1012 bm-b]',
    '- [2026-10-19 00:5x r1102 bm-c]',
    '- [2026-10-19 02:1x r1013 bm-b]',
    '- [2026-10-19 02:5x r1014 bm-b]',
]

PTR_ROW = ('- 冷层指针：r1011 ack 工具零参校验+write-tree 瞬挂 / r1012 PS>UTF-16 伪二进制 / '
           'r1012 update-ref 影子引用 / r1102 bm-c 引擎双入口 / r1013 detached 盲区 / '
           'r1014 rebase-quit 游离滞留（六行全文 verbatim=archive 202610.md'
           '『热冷整编 2026-10-19 r1017 bm-b 窗批』节）。')

NEW_ROWS = [
    ('- [2026-10-19 06:1x r1017 bm-b] **GPT-SoVITS 推理环境三缺口律（ST-007 首合成实弹·'
     '修复配方版本化=content/drama/runner_assets/first_synth_smoke.py ensure_* 三步+回执件）**：'
     '①env deps auto-strip 的编译型包（jieba_fast）被深引用面无条件 import→纯 Python alias shim '
     '兜底（sys.modules 注册子模块）；②torchaudio≥2.9 移除传统 load 后端、硬依赖 torchcodec+FFmpeg '
     'shared DLL（win 轮子装了链不上）——**env 冒烟只验 import 不验 load=潜伏缺口**→调用位 marker 守卫'
     '包裹 try 原生/soundfile 回退+py_compile 验（5 文件 9 位一次修族·smoke 与 api_v2 批产双道）；'
     '③上游可选路径依赖（resampy）requirements 未含→pip 幂等 ensure。'
     'How to apply：一切「装好即用」推理环境验收探针必打真实 load/推理面非 import 面。'),
    ('- [2026-10-19 06:1x r1017 bm-b] **自愈假信号双坑（S7/引擎实弹）**：'
     '①任务健康探针包二层 `powershell -File Invoke-SilentExe.ps1` 输出捕获静默失败→TaskState 全员假 '
     'MISSING→幂等 register 脚本被误触发（SatEngine 活任务被 D-20261002-02 默认 principal 配方从 S4U '
     '转 InteractiveToken·当窗 XML 翻回 S4U 已愈·备份 %TEMP%\\bmb-s4u-backup-*）——探针一律进程内直查 '
     'schtasks /query；**带默认 principal 的 heal 脚本禁在未实证缺失时点火**。'
     '②content_loop_step require_ok 依赖闸 `startswith(\'st\')` 对大写 \'ST-005\' 恒 false→unknown-require '
     '跳站（历史站点全用 none/manual-gate=闸语义 11 天零实跑验证）·已修 lower()。'
     'How to apply：引擎语义闸新增用例先拿真实 ID 过分支；heal 探针与动作同通道。'),
]

ts = datetime.datetime.now().isoformat(timespec='seconds')
before_bytes = os.path.getsize(CODELY)

with io.open(CODELY, 'r', encoding='utf-8') as f:
    lines = f.read().split('\n')

moved, kept = [], []
for ln in lines:
    if any(ln.startswith(p) for p in MOVE_PREFIXES):
        moved.append(ln)
    else:
        kept.append(ln)
assert len(moved) == len(MOVE_PREFIXES), 'expected %d rows, found %d' % (len(MOVE_PREFIXES), len(moved))

# find insert position: where the first moved row used to be -- anchor on the
# r1013-pointer row (stays hot); insert pointer + new rows right after it.
anchor = ('- 冷层指针：PS Select -First 截停上游脚本坑（r1005）+ rebase-continue 幽灵拒绝死循环/'
          'stash-pop 索引毒化/per-machine 键面 union 三连坑（r1008）全文 verbatim=archive 202610.md'
          '『热冷整编 2026-10-19 r1013 bm-b 窗批』节。')
assert anchor in kept, 'anchor row not found'
ai = kept.index(anchor)
new_kept = kept[:ai + 1] + [PTR_ROW] + NEW_ROWS + kept[ai + 1:]
new_content = '\n'.join(new_kept)

# 1) archive append FIRST (摘录存旁): verbatim rows preserved before any hot-file edit
with io.open(ARCHIVE, 'r', encoding='utf-8') as f:
    arch_old = f.read()
section_header = ('\n\n## 热冷整编 2026-10-19 r1017 bm-b 窗批\n\n'
                  '> 迁自 CODELY.md（%dB 超 10KB 硬线当窗整编·treasure_guard prescan rc3→'
                  '账本类摘录存旁通道·零丢失·receipt=results/_r1017bmb_codely_hotcold_receipt.json）\n\n'
                  % before_bytes)
with io.open(ARCHIVE, 'a', encoding='utf-8') as f:
    f.write(section_header + '\n'.join(moved) + '\n')

# 2) hot-file rewrite
with io.open(CODELY, 'w', encoding='utf-8', newline='') as f:
    f.write(new_content)

# 3) zero-loss assertion: every moved row byte-found in archive; none in new hot file
with io.open(ARCHIVE, 'r', encoding='utf-8') as f:
    arch_new = f.read()
with io.open(CODELY, 'r', encoding='utf-8') as f:
    hot_new = f.read()
zero_loss = all(row in arch_new for row in moved)
hot_clean = all(row not in hot_new for row in moved)
after_bytes = os.path.getsize(CODELY)
assert zero_loss, 'ZERO-LOSS FAIL: moved row missing from archive'
assert hot_clean, 'moved row still present in hot file'

receipt = {
    'ts': ts, 'round': 'r1017', 'machine': 'bm-b',
    'action': 'codely-hotcold-split (O-20260927-0230 >10KB hard line, in-window mandate)',
    'prescan': 'rc3 HARD REJECT (CODELY.md + archive both registry redline) -> sanctioned escape: '
               '摘录存旁 (verbatim archive-first) per guard message for ledger/memory faces',
    'before_bytes': before_bytes, 'after_bytes': after_bytes,
    'moved_rows': [m[:60] for m in moved], 'moved_count': len(moved),
    'new_rows': 2, 'pointer_row': True,
    'archive_section': '热冷整编 2026-10-19 r1017 bm-b 窗批',
    'zero_loss_verified': zero_loss, 'hot_file_clean': hot_clean,
    'archive_append_only': True,
}
with io.open(RECEIPT, 'w', encoding='utf-8') as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print(json.dumps({'ok': True, 'before': before_bytes, 'after': after_bytes,
                  'moved': len(moved), 'zero_loss': zero_loss, 'hot_clean': hot_clean},
                 ensure_ascii=False))
