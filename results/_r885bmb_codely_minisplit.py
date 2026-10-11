# r885 bm-b CODELY mini-split (r731/r879 pattern, D-20260206 authorized migration face)
# Migrate r878 bm-b with-indent entry -> pit-tooling.md
#        r878 bm-c rebase-conflict-window entry -> pit-git-resolver-rebase2.md
# Append domain pointer + new r885 pit entry to main. Byte-exact verbatim, receipt with sha16.
import hashlib, json, os, sys

MAIN = 'CODELY.md'
T_TOOL = 'research/pit-tooling.md'
T_REB2 = 'research/pit-git-resolver-rebase2.md'

def rd(p):
    with open(p, 'rb') as f:
        return f.read()

def wr(p, b):
    with open(p, 'wb') as f:
        f.write(b)

def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]

main_bytes = rd(MAIN)
main_txt = main_bytes.decode('utf-8')
main_before = len(main_bytes)

# ---- entry A: r878 bm-b with-indent (single line) ----
a_prefix = '- [2026-10-11 12:2x r878 bm-b] **with 块内缩位接线坑'
a_tail = '纯内存 mock 自检=接线面零覆盖假绿。'
ia = main_txt.find(a_prefix)
assert ia >= 0, 'entry A prefix not found'
ja = main_txt.find('\n', ia)
assert ja >= 0, 'entry A newline not found'
entry_a = main_txt[ia:ja]
assert entry_a.endswith(a_tail), 'entry A tail mismatch: %r' % entry_a[-40:]
assert main_txt.count(a_prefix) == 1, 'entry A not unique'

# ---- entry B: r878 bm-c rebase-conflict-window ----
b_prefix = '- [2026-10-11 15:3x r878 bm-c] **rebase 冲突窗枚举禁截断坑'
b_tail = '同轮 commit 治愈。'
ib = main_txt.find(b_prefix)
assert ib >= 0, 'entry B prefix not found'
jb = main_txt.find('\n', ib)
assert jb >= 0, 'entry B newline not found'
entry_b = main_txt[ib:jb]
assert entry_b.endswith(b_tail), 'entry B tail mismatch: %r' % entry_b[-40:]
assert main_txt.count(b_prefix) == 1, 'entry B not unique'

entry_a_bytes = entry_a.encode('utf-8')
entry_b_bytes = entry_b.encode('utf-8')

# ---- append verbatim to domain files (whole lines) ----
tool_before = os.path.getsize(T_TOOL)
reb2_before = os.path.getsize(T_REB2)
tool_txt = rd(T_TOOL).decode('utf-8')
reb2_txt = rd(T_REB2).decode('utf-8')
if not tool_txt.endswith('\n'):
    tool_txt += '\n'
if not reb2_txt.endswith('\n'):
    reb2_txt += '\n'
tool_txt += entry_a + '\n'
reb2_txt += entry_b + '\n'
wr(T_TOOL, tool_txt.encode('utf-8'))
wr(T_REB2, reb2_txt.encode('utf-8'))

# ---- remove from main, append pointer + new entry ----
lines = main_txt.split('\n')
kept = [ln for ln in lines if not (ln == entry_a or ln == entry_b)]
removed = len(lines) - len(kept)
assert removed == 2, 'expected exactly 2 removed lines, got %d' % removed
new_main = '\n'.join(kept)
if not new_main.endswith('\n'):
    new_main += '\n'

ptr = ('- 域指针·r885 bm-b mini-split（10-11 15:5x·主件 30,509B+新坑例 append 越帽 30,720B 当窗即办·仪式 r731/r879 范式'
       '·treasure_guard prescan rc3 三命中=记忆/坑律类文件·D-20260206 集团拆件令授权迁移面）：'
       'r878 bm-b with 内缩接线坑条目 verbatim 迁 research/pit-tooling.md〔封闭自检接线面域·selftest 编写前改读〕'
       '+r878 bm-c rebase 冲突窗枚举禁截断坑条目 verbatim 迁 research/pit-git-resolver-rebase2.md'
       '〔rebase/sequencer child-2 域·r787 姊妹域·续跑窗动作前改读〕'
       '——逐条字节+sha16 对账=receipt results/_r885bmb_codely_minisplit.json'
       '（零丢失断言=迁移条 bytes in target verbatim+主件保留面恒等+主/域件 ≤30KB）；新坑例（周末任务审计盲区）本窗入主件。')

new_entry = ('- [2026-10-11 15:5x r885 bm-b] **周末任务健康审计盲区（weekday-only 任务「在岗」检查恒过而实 disabled）**：'
             'D-20261011-05⑤ E2 自证落地时发现 Bigmoney-IntradayMarks 自 10-07 15:05 起被禁用'
             '（末跑 rc0 正常·missed=70 与 10-09 另案对上·全仓零禁用记录=异常禁用非授权停用）；'
             '四循环任务在岗检查全过而该件漏网，根因=审计只查运行时「在飞/在岗」而交易日 9:25 任务周末零点火'
             '——disabled 态对运行时检查不可见。处置=register_intraday_marks_task.ps1 幂等重注册（first fire 10-12 09:25）'
             '+方法论钉死：任务健康审计=先 schtasks /query 全量枚举域内任务族逐件读 mode 字段（就绪/已禁用），'
             '禁以「在跑」代查；disabled 即异常面呈报+查禁用记录定谳人为/异常。'
             'How to apply：E2/复启/健康审计清单必含「全量 mode 枚举腿」，weekday-only 任务周末审计尤须（运行时证据恒空）。')

new_main = new_main + ptr + '\n' + new_entry + '\n'
wr(MAIN, new_main.encode('utf-8'))

# ---- assertions ----
main_after_txt = rd(MAIN).decode('utf-8')
assert entry_a not in main_after_txt, 'entry A still in main'
assert entry_b not in main_after_txt, 'entry B still in main'
tool_after_txt = rd(T_TOOL).decode('utf-8')
reb2_after_txt = rd(T_REB2).decode('utf-8')
assert tool_after_txt.count(entry_a) == 1, 'entry A not verbatim-once in target'
assert reb2_after_txt.count(entry_b) == 1, 'entry B not verbatim-once in target'
main_after = len(rd(MAIN))
tool_after = os.path.getsize(T_TOOL)
reb2_after = os.path.getsize(T_REB2)
assert main_after <= 30720, 'main over cap: %d' % main_after
assert tool_after <= 30720, 'pit-tooling over cap: %d' % tool_after
assert reb2_after <= 30720, 'rebase2 over cap: %d' % reb2_after
old_kept = [ln for ln in lines if ln not in (entry_a, entry_b)]
for ln in old_kept:
    if ln.strip():
        assert ln in main_after_txt, 'preserved line lost: %r' % ln[:60]

receipt = {
    'round': 'r885', 'machine': 'bm-b', 'ts': '2026-10-11 15:5x',
    'migrated': [
        {'entry': 'r878 bm-b with-indent', 'bytes': len(entry_a_bytes), 'sha16': sha16(entry_a_bytes),
         'target': T_TOOL, 'bytes_in_target_verbatim': True},
        {'entry': 'r878 bm-c rebase-conflict-window', 'bytes': len(entry_b_bytes), 'sha16': sha16(entry_b_bytes),
         'target': T_REB2, 'bytes_in_target_verbatim': True},
    ],
    'appended': [
        {'face': 'domain pointer r885', 'bytes': len(ptr.encode('utf-8'))},
        {'face': 'new pit entry r885 weekend-task-audit blind spot', 'bytes': len(new_entry.encode('utf-8'))},
    ],
    'main_bytes_before': main_before, 'main_bytes_after': main_after,
    'pit_tooling_before': tool_before, 'pit_tooling_after': tool_after,
    'pit_rebase2_before': reb2_before, 'pit_rebase2_after': reb2_after,
    'preserved_face_identity': True, 'main_under_cap': main_after <= 30720,
    'prescan': 'treasure_guard prescan rc3 (registry hit: memory/pit class) = D-20260206 group split-order authorized migration face (r879 precedent)',
    'zero_loss_assert': 'migrated entries bytes-in-target verbatim + preserved-face line identity + main <=30720',
}
with open('results/_r885bmb_codely_minisplit.json', 'w', encoding='utf-8') as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print('OK removed=2 main %d->%d tooling %d->%d reb2 %d->%d' % (
    main_before, main_after, tool_before, tool_after, reb2_before, reb2_after))
print('entryA %dB sha16=%s entryB %dB sha16=%s' % (
    len(entry_a_bytes), sha16(entry_a_bytes), len(entry_b_bytes), sha16(entry_b_bytes)))
