# r273: append migration fact line to user-level machine memory (append-only, face-mirrored)
p = r'C:\Users\Administrator\.codely-cli\CODELY.md'
b = open(p, 'rb').read()
crlf_tail = b.endswith(b'\r\n')
line = ('- [2026-09-26 20:5x] 机队基地统一迁移（O-20260926-2000-bm-c·CEO 直令）：本机（bm-b）base 迁至 '
        'E:\\Fluxgroup（九件骨架）——MiniGame 产线区=E:\\Fluxgroup\\MiniGame（原 E:\\Minigame 整树改名）、'
        'BigMoney 仓=E:\\Fluxgroup\\FluxGroup\\quant\\bigmoney（原 C:\\Users\\Administrator\\Desktop\\Bigmoney '
        'robocopy 迁移+旧根改名 .migrated-20260926 备份）；19 个计划任务定义已改指新根；'
        '执行器=results/_r273bmb_fluxgroup_migration.ps1（bm-a r267 范式）、'
        '日志=C:\\Users\\Administrator\\fluxgroup-migration-journal.log、'
        '回执=新根 results/fluxgroup_migration_receipt_bmb.json；'
        '正典=E:\\Fluxgroup\\MiniGame\\MiniGame\\Design\\configs\\GLOBAL\\基地布局正典.md v2.0（U238）。')
with open(p, 'ab') as f:
    f.write(line.encode('utf-8') + (b'\r\n' if crlf_tail else b'\n'))
print('user-level memory line appended, crlf_tail=', crlf_tail)
