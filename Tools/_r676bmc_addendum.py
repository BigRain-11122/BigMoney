# r676 bm-c push-race addendum ledger line (r675 addendum precedent).
# First push claw-blocked (behind-signal phantom deletion), zero --no-verify,
# merge origin/main clean (0 UU), push delivered + ls-tree self-proof.
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))
                       ) if os.path.basename(os.path.dirname(os.path.abspath(__file__))) == 'Tools' \
    else os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
from datetime import datetime, timezone, timedelta
ISO = datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%dT%H:%M:%S+08:00')

RL = 'logs/iteration-loop/round_reports-bm-c.md'
raw = open(RL, 'rb').read()
prev_lines = raw.count(b'\n')
assert raw.count('r676 addendum'.encode('utf-8')) == 0, 'addendum already present'
RLINE = (ISO + ' | r676 addendum | dept:工程 | push-race 收口留痕：①首推 13:0x 被 pre-push 爪拦=behind-signal 幻影删除面'
         '〔delete-set 含 results/trial_labor_w14/prep_state.json——取证三证：本轮 commit 70a30689c --name-status 零 D 零 trial_labor 触碰'
         '＋origin 轮中前进 ef4d111b5→8a354f227 4 commit（bm-a r824=O-1240 BGM 生产同轮执行+回执填毕〔MiniGame fcb994556·3,971,194B·45.023s'
         '·LUFS -18.0/TP -3.3·GateCheck PASS〕+W14 试验漏斗复工〔TRIAL-LABOR-W14-SCREEN 入场件 475b3bffd=该件正主新增〕+autofill 双认领'
         '＋该件在新 origin tip cat-file -e rc0 在场〕——r524/r704 律原文场景·我基座落后非真删除〕→零 --no-verify（逃生口未用）'
         '→正典净路=merge origin/main 集成〔ort 零 UU·11 件全是 bm-a 面与新增件·trial_labor_w14/prep_state.json 6883 行完整收编保全〕'
         '→再推 8a354f227..1f9b18512 DELIVERED＋送达自证（fetch 后 HEAD==origin==1f9b185129f6·ls-tree origin/main 四件实读'
         '〔state-bm-c/fleet-machines-bm-c/trial_labor_w14-prep_state/qa-smoke-r676〕）·本地未达 origin commit 数终值=0'
         '（轮账本主行声明 2=推送前时点值·本 addendum 为终值收口）；②O-1240 令闭环实况：bm-a r824 同轮执行+回执〔本机 sweep-ack 零执行面'
         '判断获验〕·decisions 水位已进 815fa0f2（bm-a r824 消费·下轮 r677 轮首双扫按律捕获消费）；③轮后树态=2 自家 daemon live-face '
         'churn（saturation engine 面·treadmill 正常态·下轮 r677 轮首按 r620 律吸收）。')
out = b''
if not raw.endswith(b'\n'):
    out += b'\r\n'
out += RLINE.encode('utf-8') + b'\r\n'
open(RL, 'ab').write(out)
raw2 = open(RL, 'rb').read()
assert raw2.count(b'\n') == prev_lines + 1, 'ledger line-count guard'
assert raw2.count('r676 addendum'.encode('utf-8')) == 1, 'ledger addendum uniqueness guard'
print('ADDENDUM OK:', ISO)
