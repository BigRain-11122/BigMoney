# r503 bm-c S7-close: CODELY pit entry + round-report close line (bytes mode, self-consistent markers) 
# -*- coding: utf-8 -*-
import time

ROOT = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
now = time.time()
clock = time.strftime('%Y-%m-%dT%H:%M:%S+08:00', time.localtime(now))

# --- 1. CODELY.md pit entry (new-pit-first-here convention per r700 bm-b entry; idempotence guard) ---
cp = ROOT + r'\CODELY.md'
raw = open(cp, 'rb').read()
needle = b'[2026-10-04 23:3x r700 bm-b] schtasks /query /xml'
assert raw.count(needle) == 1, 'anchor entry (bm-b r700) not unique'
eol = b'\r\n' if raw.count(b'\r\n') >= (raw.count(b'\n') - raw.count(b'\r\n')) else b'\n'
entry = ("[2026-10-04 23:5x r503 bm-c] S7 簿记脚本自洽性两连坑（r679/r485 家族新变体·三跑三追加当场治愈零 origin 伤害）："
         "①幂等门标记与追加行内容不自洽——r679 门用 marker（b'r503 bm-c'=S7-close 行惯例串）≠轮账行内实际标签（' | r503 | dept:'）"
         "→pre-gate 恒 count==0 通过+post-verify 恒 count!=1 炸→脚本 exit 1 但 append 已落盘→盲目重跑=逐次再追加"
         "（本窗三跑三追加·_r503bmc_report_heal.py bytes 保首截余+字节对账治愈）。"
         "②roundtrip 门与写盘 EOL 形态错配——r502 血统簿记脚本 io.open 文本态写盘产 CRLF 而门用 LF-redump 比对"
         "→次轮同脚本恒假红（本窗 state/心跳实测 32 CRLF/0 LF·raw==redump.replace 双形态验证=标准 dump+宿主 CRLF 面）。"
         "正法=v2 脚本：门与写盘皆按探测到的宿主 EOL（bytes 二进制写保 CRLF·r485 律）+marker 取追加行内真标签（pre/post 同串自洽）。"
         "How to apply：append 型簿记脚本见 exit 1 先查已落盘行数（部分落盘≠零写入）勿盲目重跑；复制血统簿记脚本先核 marker 对与 EOL 门两处自洽性。")
entry_b = entry.encode('utf-8')
own_marker = entry_b[:60]  # unique prefix of this entry
cnt_own = raw.count(own_marker)
if cnt_own == 1:
    print('CODELY pit entry already present (idempotence guard), skip append')
elif cnt_own == 0:
    with open(cp, 'ab') as f:
        f.write(entry_b + eol)
    raw2 = open(cp, 'rb').read()
    assert raw2.count(entry_b) == 1, 'CODELY entry count verify failed'
    print('CODELY pit entry appended (%dB)' % len(entry_b))
else:
    raise SystemExit('CODELY entry duplicated x%d -- manual adjudication' % cnt_own)

# --- 2. round report S7-close line ---
rp = ROOT + r'\round_reports-bm-c.md'
raw_rp = open(rp, 'rb').read()
close_marker = b'r503 bm-c S7-close'
round_marker = b' | r503 | dept:'
assert raw_rp.count(close_marker) == 0, 'close marker already present'
assert raw_rp.count(round_marker) == 1, 'round line must be exactly 1'
rp_eol = b'\r\n' if raw_rp.count(b'\r\n') >= (raw_rp.count(b'\n') - raw_rp.count(b'\r\n')) else b'\n'
line_str = (clock + "｜r503 bm-c S7-close｜本地未达 origin commit 数=0（DELIVERED：round commit 538d6c301 63 文件→首推被拒〔origin 窗内进 10 commit：bm-a r701/r702 席位+W119 FREEZE+SHARD-2 done 翻面 23:44:03+bm-b r700 D-06 CODELY 拆件批一+r701/r702 merge close〕"
        "→churn absorb c05d98bbc→merge 1eb54cb73 19-UU 同窗再生面族逐面解〔_r503bmc_merge_resolve.py r501/r698 血统+三增腿：CEO 面+dashboard twin=ours-fresh 23:45>23:28·compute_audit history-union 203 零丢失〔r188/R208 律〕·token per-key union side_pick=21·runnable_pool tie→theirs=SHARD-2 done owner=bm-a canonical 后验过〕"
        "→二推再拒〔origin 再进 3：bm-a W120 FREEZE+bm-b keepalive〕→merge-2 零 UU ort 自动收口→push_verify DELIVERED tip=remote=adfb3bd495·ahead=0/behind=0·零强推零 --no-verify）｜"
        "收口实录：簿记 v3=宿主 EOL 门+轮账三重追加坑当场治愈（r679 标记不自洽变体·保首截二·字节对账 608251→605183·律已入 CODELY）；"
        "S0.5 双扫 154/154 双键消费两连（orders F06E044F=Biggame 两翻牌行零动作+3BF0F16E=孤儿链 O-027~030 三覆写再补回·回执不重复立案；decisions 4E5BE321=HQ 75c14df 误删找回=MSG-2330 实质裁决）；"
        "SHARD-2 claim 撞车如实注记（本机 daemon 23:40:38 接管 vs bm-a 23:40:42 认领·bm-a 产品先落 canonical·零双烧·N2-W15 12/12 达成）；"
        "inbox 三件消费入 processed（MSG-2330-bmb 同族取证/bmc 自件使命已成〔bm-a r702 已引用〕/bma W120 席位非当事）")
line = line_str.encode('utf-8')
with open(rp, 'ab') as f:
    f.write(line + rp_eol)
raw2 = open(rp, 'rb').read()
assert raw2.count(close_marker) == 1, 'close line count verify failed'
print('round report close line appended')
