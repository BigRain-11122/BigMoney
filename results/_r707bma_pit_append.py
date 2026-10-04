import io

p = r'research\pit-engine.md'
with io.open(p, 'rb') as f:
    raw = f.read()
crlf = raw.count(b'\r\n')
lf = raw.count(b'\n') - crlf
print('CRLF:', crlf, 'bare LF:', lf)
eol = b'\r\n' if crlf > lf else b'\n'
print('host EOL:', eol)
assert raw.endswith(eol), 'file must end with EOL'

entry = (
    "- [2026-10-05 02:1x r707 bm-a] judge 波 12 分片连环崩溃 fuse 全拒·worker state 缺 grammar 键坑"
    "（r121 bm-c crash#1「GRAMMAR rides initargs」同族新变体·W15 judge 首夜实弹）："
    "perpetual_faces_n2 cmd_judge 手搓 st 字典缺顶层 grammar 键——spawn worker 重导入 tl1 模块后 GRAMMAR=None，"
    "run_candidate_curve_w14 L1512 真候选腿（rng_matrix is None）tl1.GRAMMAR[\"faces\"][mk] NoneType subscript；"
    "screen 波全过=假安全感面（_leg_state_shared 自带 grammar 键，judge 波手搓 st 绕开了该正典构造器）；"
    "12 分片各烧 ~60s 于首个 future 崩、fuse count=1 即拒（14 refusals）=烧录面零 checkpoint 零产出纯空转。"
    "正法=st[\"grammar\"]=tl1.GRAMMAR 一行（_init_worker 文档契约照抄 screen 面）；autofill code_changed 墓碑自动清 fuse 免手工。"
    "How to apply：任何 ProcessPool 波的 worker state 手搓字典必须逐键对照 _init_worker 读取面（grammar/_ST 全键清单），"
    "能用 _leg_state_shared 正典构造器禁手搓；新波 judge 腿先单分片实弹验证再入池（本例 24 cell/2min 一腿自证）。"
)
with io.open(p, 'ab') as f:
    f.write(eol + entry.encode('utf-8'))
with io.open(p, 'rb') as f:
    after = f.read()
assert after.startswith(raw), 'prefix intact'
print('appended bytes:', len(after) - len(raw))
print('tail ok:', after[-60:].decode('utf-8', errors='replace'))
