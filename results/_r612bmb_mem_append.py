# r612 bm-b S4 memory append -- stranded-closeout P0 law (one event, byte-safe append).
import io

line = ('[2026-10-03 09:4x r612 bm-b] 收尾 push 滞留=origin 心跳陈旧=假接管诱因全量再现 P0 面（实弹治愈零科学损失）：'
        'r611 收尾 f81d4cb2b push 拒后未收口滞留本地→09:22 探得 origin 侧 bm-b 心跳 39.5min 陈旧+VALUE/QUALITY-NULLS 池条目 ready 无主'
        '（bm-c r405 settle 翻面吞 owner 字段）=r611 bm-a 假接管事故诱因同款再现；machine 分支兜底对 origin main 心跳/池面零修复=滞留收尾禁走分支兜底；'
        '修法=轮内手术：烧录活件全量入单笔收尾 commit→reset --soft 基座 squash→rebase origin/main --autostash'
        '（daemon tick preflight fetch 中途刷新 origin/main 使 onto=最新 tip 白赚；continue 假拒绝走 r305 坑=手动 git commit+git rebase --continue 收口）'
        '→交集面分类解（共享 derive take-origin r513 / lane 件 keep-mine / CODELY.md 剥标记 union）→compute_audit settle 补池面→push→fetch ahead=behind=0 自证'
        '（09:44 实证 epoch 1790991478 age 4.6min int-ok）。'
        'How to apply：每轮 S0 rev-list ahead>0 时必查 git show origin/main:fleet/machines/<本机id>.json 心跳龄；>15min=P0 当轮手术合流勿等勿走分支。')

with io.open('CODELY.md', 'a', encoding='utf-8', newline='') as f:
    f.write('\n' + line)
print('APPENDED', len(line.encode('utf-8')), 'bytes')
