# r985 HANDOVER 5x row append (bm-c, window r916-r985, 12 missed 5x stamps disclosed)
import io, os
BM = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
H = os.path.join(BM, "research", "HANDOVER.md")
raw = open(H, "rb").read().decode("utf-8")

row = """> bm-c round 985 五倍数核对（2026-10-14 05:5x·增量窗覆盖 r916-r985 七十轮·**5x 截 r925/930/935/940/945/950/955/960/965/970/975/980 十二截未落 HANDOVER 行如实披露**〔坑-79 族·CEO V3 冲刺夜战窗+W 波链连营+wait-state 连守窗消耗〕·r920 截=bm-b 行在册·逐轮权威面=logs/iteration-loop/round_reports-bm-c.md 全行在册〔r985 窗 ledger path-split 3rd instance 治愈后 r958-r984 行已回正典面〕+state-bm-c.json closeout/absorb notes）：增量窗 r916-r985=bm-c 面像（**CEO V3 QC/收割线+W 波链 W227→W235 全生命周期+absorb 17th-22nd 代+双水位 phantom 治愈链+wait-state 连守+ledger path-split 治愈**——①CEO V3 线=r950 N02_v2 8.3 PASS+r951/r952/r953/r954 QC 巡检批（R01 8.0/R03 8.5/R04 8.0/D02 8.0/D03 8.0 锁定·C 系 FAIL→track-2 regen 批 MSG-0430 派 bm-a）+r969 CEO 即时工单（回炉 5 席+refire-2+NEWKF 28 试构图板+ComfyUI 重启）+r971 V3 链收割全闭环（R05_v4 6.0 FAIL→夜窗帧修派单）+r974 V3 fullres 7/7 CAS relay（group origin 6851396b485a）+r977/r984 MV 修批 relay 行消费；②W 波链=W227 全周期（five-key ALL PASS·ledger 923,189/K 497,320）→W228 席+全周期→W229 席（r957）+r958 prereg→r959 absorb+全周期→W230 席（r962 absorb 17th·O-20261013-0930 同窗）→r963 W230 全周期+W231 席→r967 absorb 19th（W231 estate）+W232 prereg→r968 absorb 20th（W232 全周期+W233 席）→r974 absorb 21st（W233 全周期+W234 席）→r975 W234 prereg PREP→r976 absorb 22nd（W234 全周期）→W235 让路 bm-a takeover（bm-c hb-stall 198min·dead-window editor fail-closed 守住零双注册）→r980/r981 验证 burn/finalize（ledger 940,789/K 514,920 five-key ALL PASS·六门 PRE-FINALIZE 十连正确相位）→W236 席=bm-a（5c25db795·prereg 67ade8314 已落·链归其 per seat-first）；③absorb 血统=17th(r962)→19th(r967)→20th(r968)→21st(r974)→22nd-generation(r980)（r960/961/964/966/972/973/978/979 八死窗 estate 全机验后落地·账本零双计实证）；④双水位 phantom 治愈链=7th(r970)→9th/10th(r977 双方法 saga 终结：ORD=content-sha1 53582389/DEC=raw-blob sha256 86187eff 钉法)→r984 dual-delta 双消费（V3-fix relay 行+C-20261013-01 清理行·涉本司零执行件）；⑤wait-state 连守 r981-r985（W236=bm-a 链在飞让路·MF-IC-P1 parked 20d 上游阻断（bm-a collector 崩·relay MSG-05612 在册）·10-14 bars 15:30 前未到期·pool ready=0（N2U3-LEG3-TRAIN=bm-b 已闭）+RW-5 freeze 供给合法链 W236 finalize·RAM 1.8% idle 非领单档）；⑥**本核对轮主产品=ledger path-split 3rd instance 治愈**（r749/r780 族三发：r958-r984 收尾脚本克隆 ROOT 时代模板误写根件→r985 行级 union 20 行 verbatim 回正典面+8 死窗轮 consolidated 标记行+根件 freeze 指针+收尾脚本回正典路径·treasure_guard rc3 行级 union 通道·receipt _r985bmc_ledger_heal_receipt.json）。维护面全窗：smoke 49/49 链·双扫零未回执链·SAT 活 rc0 链·attrition 4 CLEAN 链·dualrun ZERO-DRIFT streak 51 链·四件套绿链·孤儿面=2 链（MV-lane 基建保活）。指针：**10-14 15:30 bars→papers 全链 re-arm（live.paper 族+t35/t24）+W236 finalize（bm-a）→W237 席链+MF panel 完备→MF-IC-P1 解泊+月界首考 10-31**；下一 5x=bm-c r990。
"""

lines = raw.splitlines(keepends=True)
# insert after leading header block: first line(s) starting with '# ' + following blank
idx = 0
for i, l in enumerate(lines):
    if l.startswith("# "):
        idx = i + 1
        break
if idx < len(lines) and lines[idx].strip() == "":
    idx += 1
new = "".join(lines[:idx]) + row + "".join(lines[idx:])
open(H, "wb").write(new.encode("utf-8"))
print(f"HANDOVER row inserted after line {idx}; bytes {len(raw)} -> {len(new.encode('utf-8'))}")
