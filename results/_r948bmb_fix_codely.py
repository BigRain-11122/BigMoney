import subprocess, sys
bm = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
p = bm + r'\CODELY.md'
b = open(p, 'rb').read()
print('first8', b[:8].hex())
orig = subprocess.run(['git','-C',bm,'cat-file','blob','HEAD:CODELY.md'],capture_output=True).stdout
print('orig_len', len(orig), 'disk_len', len(b), 'prefix_match', b[:len(orig)] == orig)
if b[:len(orig)] != orig:
    print('ABORT: disk prefix != HEAD blob (unexpected)')
    sys.exit(1)
tail = b[len(orig):]
print('tail_len', len(tail), 'tail_head_hex', tail[:20].hex())
new_line = ("\r\n[2026-10-14 20:41] bm-b git 仓二灭（r947 窗）恢复判例+新坑律（详档 results/_r948bmb_forensics_addendum.md）："
 "\u2460git 进程击杀必须杀树（taskkill /T 或按出生时间+cmdline 验真体）——Start-Process git 返回 cmd-shim PID，杀 shim=真体孤儿化持 index.lock（worker 全 face rc128 实锤），且 Remove-Item 在 EAP=Continue 下对被占用锁静默失败假报 cleared；"
 "\u2461清锁一律 -ErrorAction Stop + Test-Path 复核断言；"
 "\u2462被杀轮 25 条命令全审计+sli-reconcile 脚本=双清白，.git 毁损者仍未归案（USN 19:36-19:55 窗+他 lane transcript 待查）；"
 "\u2463data 面同样被毁（r947「幸存」=顶层存在性误判）——字母序扫荡在 logs 边界被中断论复活，两次同边界=单次递归删除撞 25min runner 击杀形态；data 面靠 S6 链重拉（zt_pool/minute_feed 前向史料不可逆损失）。\r\n")
if b[:2] == b'\xff\xfe':
    enc = 'utf-16-le'
elif b[:2] == b'\xfe\xff':
    enc = 'utf-16-be'
else:
    enc = 'utf-8'
out = b[:len(orig)] + new_line.encode(enc)
open(p, 'wb').write(out)
print('written_enc', enc, 'new_len', len(out), 'delta', len(out) - len(orig))
