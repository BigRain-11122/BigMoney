# -*- coding: utf-8 -*-
"""r910 bm-c: W212 prereg §7/§8 debt-heal backfill (five-key + six-gate probes landed this window).
Count-asserted anchors (buildgen law): every old string asserted count==1; loud abort on drift."""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'research', 'PERPETUAL_N1_W212_PREREG.md')
t = open(P, encoding='utf-8').read()
eol = '\r\n' if t.count('\r\n') > (t.count('\n') - t.count('\r\n')) else '\n'

old7 = '- **诚实披露**：§5 五预键机证探针+pre-finalize 六门探针未在本窗重跑（死亡会话链 r898-r906 同族债务·W209/W211 §7/§8 回填亦在债——下窗补；本 finalize 走 FAIL-CLOSED 五重守卫〔pit-95/shard 完备/overlap-gap/重名/账本恒等〕全过=门活机证）。'
new7 = old7 + eol + '  - **r910 债务愈合回填（bm-c r910 窗·机证件=results/_r910bmc_w212_fivekey_probe.py+_r910bmc_w212_fivekey_log.txt）**：§5 五预键 post-hoc 探针本窗补跑全过——key1 w212-only vs merged |Δmu|=**0.0055**<0.02 PASS（merged **−0.09267005**·w212-only **−0.08721705** 机读）；key2 sigma 相对变化 **+0.004783%**<±10% PASS（**0.24512048**）；key3 A 档 p95 **0.3282** vs W211 锚 **0.3134** 差 **0.0148**<0.05 PASS；key4 K-lift **+0.0001**≤±0.02 PASS（line 1.1902→**1.1903**@n_eff 887,989）；key5 W213+ 投影承接=W213 注册行机读兑现（registry WAVE_CONFIGS a_seed_base=483,404=483,403+1 恰如 §5.5 投影强制·阶梯第七十三例+own-A 互斥 B=485_404..485_603）PASS。se_mu 收窄链 W211 **0.000361**→W212 **0.000360**。pre-finalize 六门事实本窗全验（席位 MSG 已归档/五面冻结已落/12 分片/registry 带位行在/prereg 已 commit/上游链头恒等 887,989）——**§5/六门双债就此清账**。'
assert t.count(old7) == 1, t.count(old7)
t = t.replace(old7, new7, 1)

old8 = '③本窗为 r907 吸收窗（r898-r906 九死亡会话无 closeout·state 滞后 r897——本窗一次性愈合）。'
new8 = '③本窗为 r907 吸收窗（r898-r906 九死亡会话无 closeout·state 滞后 r897——本窗一次性愈合）。' + eol + '  - **r910 追记**：①§5 五预键/pre-finalize 六门探针债已由 r910 窗补跑清账（机证见 §7 回填行·五键全过+六门全验·r908 W213 prereg 构建时 47 count-asserted rolls 已先证 W212 物理字节·本窗探针补全 §5 对锚机证面）；②W209/W211 §7/§8 回填债已由 r909 窗愈合（a9401c82c 三波回填+三波探针·本窗如实注记非本窗功）；③W213 全周期已由 r908/r909 落地（席位 4f3b0d6a8→prereg eeda85145→冻结 a24069f4c→自燃 12/12→finalize a9401c82c K=466,520·账本头 892,389）——§8「下窗第一动作=W213 席位」兑现完毕。'
assert t.count(old8) == 1, t.count(old8)
t = t.replace(old8, new8, 1)

open(P, 'wb').write(t.encode('utf-8'))
print('W212 prereg §7/§8 debt-heal backfill LANDED')
print('size:', len(t.encode('utf-8')), 'eol:', 'CRLF' if eol == '\r\n' else 'LF')
