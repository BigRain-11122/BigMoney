# r561 bm-b S7 bookkeeping: CODELY hot/cold compile (1 flow entry -> archive),
# new pit-law entry append, round report line append. Byte-level, assert-guarded.
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ---------- 1. CODELY.md surgery ----------
p = 'CODELY.md'
raw = open(p, 'rb').read()
c = raw.decode('utf-8')
EOL = '\r\n' if '\r\n' in c else '\n'

MOVED_START = '- [2026-10-01 23:5x r340 bm-c] O-20261001-2355-bm-c'
NEXT_START = '- [2026-10-02 00:5x r341 bm-c]'
i0 = c.find(MOVED_START); i1 = c.find(NEXT_START)
assert i0 > 0 and i1 > i0, 'moved entry bounds not found'
moved = c[i0:i1]
assert '排好单子' in moved and len(moved) < 800, 'moved entry sanity'

# strip trailing EOLs from the moved chunk for verbatim archive
moved_verbatim = moved.rstrip('\r\n')

POINTER = '- 冷层指针（r561 整编）：O-20261001-2355-bm-c 执行记录全文 verbatim=research/memory-archive/202610.md『热冷整编 2026-10-02 r561 bm-b 窗批』节。'
c = c[:i0] + POINTER + EOL + c[i1:]

NEW_ENTRY = (
    '- [2026-10-02 06:5x r561 bm-b] reset --soft 让路重落=stale index 整树面坑（r519 族第 7 犯未遂·删除集自证腿当场拦截零污染）：'
    'push 被拒后按 r513 范式「reset --soft origin/main 分离 staged 差集再干净重落」时——soft 只移 HEAD 不动 index，'
    'index 仍=本机旧 commit 全树；拒收窗内 origin 已进他机新件（本例 bm-c r353 W53 产品+2 工具件）时直接 commit 旧 index'
    '=整树覆写=他机新件以 D 删除面静默蒸发（diff --cached --stat 现场实证 _r352bmc_* 两件 staged 为删除）。'
    '正解三步=①soft 后必 `git reset`（mixed·index 重锚 origin 新基）②`git checkout -- <对侧新件>` 恢复工作树在场'
    '（本机树无该件，不恢复必假删除）③add -A 后删除集断言 `git diff --cached --diff-filter=D --name-only`==预期集'
    '（本例=唯一 inbox 归档移动）才 commit。How to apply：一切「拒收→重落」窗（让路/AA 收敛/yield 收编），'
    'reset --soft 后禁直接 commit 旧 index——index 面=旧全树非差集；先 mixed 重锚+对侧新件恢复+删除集自证后才重落。'
)
if not c.endswith(EOL): c += EOL
c += NEW_ENTRY + EOL
open(p, 'wb').write(c.encode('utf-8'))
print('CODELY.md: moved 1 flow entry out, pointer landed, r561 pit-law appended; size =', len(c.encode('utf-8')))

# ---------- 2. Archive append (verbatim) ----------
ap = 'research/memory-archive/202610.md'
araw = open(ap, 'rb').read()
a = araw.decode('utf-8')
AEOL = '\r\n' if '\r\n' in a else '\n'
SECTION = (
    '## 热冷整编 2026-10-02 r561 bm-b 窗批' + AEOL + AEOL +
    '（D-20260925-01④ 50KB 水位触发·D-20260924-01 范式·行级零丢失校验；流水一行自 CODELY.md 热层 verbatim 迁入，'
    '在役坑律 103 条全留热层·r504 勿为字节归档在役律·水位结构性残留 64KB=集团裁定面 F-20260924-14 已在案）' + AEOL + AEOL +
    moved_verbatim + AEOL
)
if not a.endswith(AEOL): a += AEOL
a += AEOL + SECTION
open(ap, 'wb').write(a.encode('utf-8'))

# line-level zero-loss verification: moved text present verbatim in archive
a2 = open(ap, 'rb').read().decode('utf-8')
assert moved_verbatim in a2, 'zero-loss verification FAILED'
print('archive: verbatim landed + zero-loss verified')

# ---------- 3. Round report append ----------
rp = 'logs/iteration-loop/round_reports.md'
rb = open(rp, 'rb').read()
REOL = '\r\n' if rb.endswith(b'\r\n') else '\n'
LINE = (
    '2026-10-02 06:58 | r561 | FOUR-WAVE CLOSEOUT: W53 same-window dual-finalize AA-convergent (yield to bm-c r353) '
    '+ W54/W55/W56 THREE-WAVE FINALIZE CHAIN delivered (chain W1..W56 FULLY CAUGHT UP, ledger 487,748, K=121,120) '
    '| watermark verdict=GREEN (wm red=false; holiday window legal idle: National Day closure 10-01/02, panel tail 2026-09-30, '
    'all supply lanes honest no-op) | 当前活=post-closeout idle; engine queue empty (W57=bm-a owned burning; bm-b next wave=W58 '
    'freeze at next round per never-dry standing step) | 最近实物=results/perpetual_faces/n1_w54/w55/w56_results.json on origin '
    '(commit 36a11e35e, ledger head 478,948->487,748 this window incl. bm-c W53 +2,200) + prereg S7/S8 mechanical backfill '
    '(W53 verbatim kept from bm-c r353 with their 3 claim-vs-reality corrections; W54-56 by derive-type tool '
    'results/_r561bmb_w5356_backfill.py, all numbers from results JSONs, 4/4 criteria x4 machine-verified, W55 rolling-anchor '
    'mu delta 0.0191 near-line honest disclosure) | 下个里程碑=W58 freeze next round (bm-a r561 gate projection A 159_004..161_003 '
    '/ B 47_601..47_800; own band gate machine-derive mandatory r535 law) + W57 finalize watch (when bm-a 12/12 lands) '
    '| 验证证据=smoke 47/47 + n1 selftest PASS full chain (W53..W57 faces coexist) + r498/r499 AA layered verdict (key-sets equal, '
    'zero float >1e-9 rel, zero hard diff, envelope-only diff) + push-reject yield route r519-family 7th near-miss caught by '
    'deletion-set assertion (soft-reset stale-index face, cured via mixed reset + origin-side restore + add -A + D-set==inbox-move-only) '
    '+ S6 chain 28 legs all rc=0 (dualrun ZERO-DRIFT streak 7/3; paper chain legal skip no-new-bar; holiday no-ops honest) '
    '+ attrition guard CLEAN (1 historical shrink healed note) + loop/watchdog/claw self-heal OK (watchdog S4U re-registered) '
    '+ D-19 decisions SHA MATCH 4FD50184 zero action + orders ack 143/143 (README false-positive excluded) + inbox MSG-0640 '
    'archived to processed (bm-a r561 INSERT-NOT-REPLACE tooling-hardening response seen on origin) + CODELY hot/cold compile '
    '(1 flow entry O-20261001-2355 -> archive 202610.md r561 window-batch verbatim, 103 operative pit-laws kept hot per r504 law, '
    'structural 64KB residue = HQ F-20260924-14 already on board) | 本地未达 origin commit 数=0 (push 36a11e35e landed, '
    'fetch+ls-tree W54/55/56 delivery self-verified) [via bm-b r561]' + REOL
)
if not rb.endswith(b'\n'): rb += b'\n'
rb += LINE.encode('utf-8')
open(rp, 'wb').write(rb)
print('round report: r561 line appended')
print('S7 bookkeeping done')
