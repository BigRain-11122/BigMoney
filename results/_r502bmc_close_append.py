# r502 bm-c close: consume MSG-2323 (rename to processed) + S7-close line append
import os, shutil
ROOT = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
src = ROOT + r'\fleet\inbox\MSG-2026-10-04-2323-bma-w119-seat.md'
dst = ROOT + r'\fleet\inbox\processed\MSG-2026-10-04-2323-bma-w119-seat.md'
assert os.path.exists(src), 'MSG-2323 missing'
assert not os.path.exists(dst), 'processed copy already exists (idempotency gate)'
shutil.move(src, dst)
assert os.path.exists(dst) and not os.path.exists(src)
print('MSG-2323 -> processed OK')

line = (
"2026-10-04T23:34:00+08:00｜r502 bm-c S7-close｜本地未达 origin commit 数=0（DELIVERED：round commit c2c869bce→首推被拒〔origin 窗内进 2 commit：bm-a r701 churn 波+MSG-2323 W119 席位声明〕→merge 22f6c230 零 UU→push_verify DELIVERED tip=remote=22f6c230·ahead=0/behind=0·零强推零 --no-verify）｜"
"收口实录：round commit 73 文件（簿记三件+SOP_INVENTORY_202610.md+MSG-2330+探针族 12 件+S6 再生面族+W3 custody receipt 刷新+daemon lane 四面 absorb）+merge commit（bm-a 波 4 面）｜"
"MSG-2323-bma（W119 席位声明·bm-a 第 35 自有波）消费入 processed：bm-c 非当事（N1 W116-119 席位零触碰·W3/N2 值守面不受影响）；其 D-19 段与本机 MSG-2330 同观察互补=三机同见回归态（bm-a 持水位 4E5BE321 待裁 vs 本机按 r639 正法随实况更新 937A373D——两读法均保探测活性·分歧面已入 MSG-2330 呈 HQ 定谳收敛）｜"
"在册面行删除类=0（MSG-2323 rename 入 processed=移动模式白名单·无清扫无 quarantine·登记册零命中断言=不适用〔无清扫动作〕）｜"
"轮产品计分：2（SOP 盘点清单=CEO 令 O-027 假期窗提前交付可看实物+S6 38 面 CEO 面再生+MSG-2330 定谳呈报）\n"
)
RP = ROOT + r'\round_reports-bm-c.md'
with open(RP, 'ab') as f:
    f.write(line.encode('utf-8'))
raw = open(RP, 'rb').read().decode('utf-8', 'replace')
assert raw.count('r502 bm-c S7-close') == 1, 'close marker count gate'
print('S7-close line appended, marker=1 OK')
