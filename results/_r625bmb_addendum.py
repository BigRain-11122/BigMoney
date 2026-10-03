# Append r625 addendum line to the shared round ledger (UTF-8, CRLF face).
LINE = ("2026-10-03T17:26+08:00 | R625 bm-b addendum: push 撞车环合实录 -- pre-push 爪拦=陈旧基座警报器正确触发"
        "（origin 真tip 轮中前移=bm-a r632 双 commit @16:47~16:5x，我方基座 r624@16:31 陈旧，4 件 bm-a 属主删除集 "
        "（_r632bma_* 族）被拦，r621 律禁 --no-verify 绕行）；正解=merge origin/main 环合（r619 收口集成优 merge 律·"
        "origin-only 4 件自动落正侧·在飞 burn daemon 面零 pick 重放险）；17 UU=正典分类器 10 分类+7 手工定性（LIVE×4/"
        "attrition_scan/scorecard×2=快照同族），resolver=results/_r625bmb_resolve.py 留痕：CODELY.md memory-union 尾块"
        "（r624 删除维持=已 verbatim 迁 pit-git，bm-a r632 containment 条保留）+compute_audit history union 201|206→207 "
        "零丢失+latest take-new 17:00:49+regime_state state take-new+history union 2|2→2+快照族 12 件 ts 探针全 take-new "
        "ours（17:00~17:05>16:47~16:49·同秒 tie 取 HEAD r140）+dashboard_status.js/js-wrapper whole-bytes+LIVE md 孪生"
        "成对同侧；dashboard 面我侧写入=合法 stale-takeover（bm-a 心跳 36min 陈旧·O-2100 s2.4 STALE_MIN 律·fetch 后已回鲜）；"
        "merge 后 push 爪全过·本地未达 origin commit 数=0 自证\n")
p = 'logs/iteration-loop/round_reports.md'
b = open(p, 'rb').read()
eol = b'\r\n' if b.count(b'\r\n') > (b.count(b'\n') - b.count(b'\r\n')) else b'\n'
add = eol if (b.endswith(b'\r\n') or b.endswith(b'\n')) else eol
open(p, 'ab').write(add + LINE.encode('utf-8').replace(b'\n', eol))
print('ADDENDUM_OK')
