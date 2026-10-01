import io

LINE = (
    "- [2026-10-01 20:1x r519 bm-b] closeout 扫树第 4 犯·外科标签不免疫面（bm-a r533 closeout "
    "c209aa962「surgical onto b1e585dff」把 bm-c r331 刚推的 W20 finalize 产品+W20 prereg §7/§8 "
    "回退+_r331bmc 工具件+195x 消息无档删除，一并从 origin 蒸发——「surgical onto 最新 origin」"
    "不等于安全：外科树基取自本机 stale 工作树快照时，对侧窗内增量在树里「不存在」→树写必丢"
    "（r516/r513/r525 族第 4 犯，首次打到引擎波产品+prereg 回填面）。治愈（本例 d855bc650）="
    "发现方按持有 commit 字节 checkout 恢复+audit.machine 归属三验+json.loads/ledger_head derive "
    "自证+MSG 通知+processed 补档；根治面=pre-push ownership claw（F-20261001-03）升级为强催："
    "一切 surgical/closeout push 必跑 git show --diff-filter=D --name-only 删除集自证+D 面 "
    "audit.machine 归属门，缺腿=禁推（MSG-195x bm-a 已自背书该建议的同窗 closeout 又犯=第 4 犯 "
    "实证）。How to apply：closeout/外科推送前对 D 面逐件归属验（r525/r513 律的 surgical 面补全）；"
    "发现 origin 缺件先查持有 commit 再动手，禁按「文件应该在那」直觉重建。\n"
)

with io.open('CODELY.md', 'a', encoding='utf-8', newline='') as f:
    f.write('\n' + LINE)

import os
print('appended; new size:', os.path.getsize('CODELY.md'))
