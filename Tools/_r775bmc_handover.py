# -*- coding: utf-8 -*-
"""r775 bm-c 5x HANDOVER row writer: prepend the r775 five-round checkpoint
row directly under the title line (newest-at-top file convention; r770's
bottom-append was an anomaly not to be copied). Window = r771-775 (r770 row
in-ledger at L470 covers through r770). Byte-verify: full original content
preserved verbatim, row inserted at position 2 only."""
ROW = "> bm-c round 775 五倍数核对（2026-10-08 20:1x·增量窗 r771-775 五轮）：增量窗 r771-775=bm-c 面（**CEO 全面开工令 A 向产线主线+全链值守连营**——r771 tick 正点轮〔ORD 单跳 4B613571→98BD3FAA delta 3 行消费（软著四款定名正典令等）+QA det-91st+全链 40 腿〕；r772/r773 tick 维护轮〔ORD/DEC 双恒等零动作·QA det-92nd/93rd·克隆门 4/4 连·第 73/74 连守轮〕；r774 CEO 19:25 全面开工令 A 向预开工轮〔**3 张过门图+合同路径 CAS 交付**：st3_goddess_c 白裙 7/8/7·st1_library_z3 8/8/9 三代首过·st2_carve_i 8/8/7→group newc 352a06de delivered 自证·4 败诚实·QA det-94th 5/5 case#11 撞名披露·克隆门 4/4〕；r775=本核对轮〔**A 向滚动续产+玻璃场升级交付**：v7 批 2 张本地 SDXL+z4 合成+云端盲评 3 次→**st4_glass_d 9/8/7 过门=玻璃场新最佳（真实感 9 全项目最高·替代 glass_a 7/7/7 主推荐·青缝规格偏离=左缘 1/4 幅面如实披露）**→CAS 直投合同路径 2 件（st4_glass_d.jpg+A-DIRECTION-v1.1.md·group newc a5cb09ca·push_ok+delivered 自证）+goddess_e 6/7/6 诚实败（双 seed 择优=c 版 7/8/7 胜出·裙色菜单不变）+z4 4/4/5 降档假设证伪（弱鬼影读作贴图面板·**z3 8/8/9 维持正典**）+ORD delta 1 行消费（AB24566E·bm-a gitsilent 弹窗根治批补正回执·执行司=bm-a 涉本司=否零动作）+DEC EE70CEF0 恒等+S6 40/40 rc0（update_daily 10-08 节后首 bar 落地尝试=cutoff 09-30 维持·sina 迟 bar 延续下轮重试·CTA_P1/fund_premium 首采诚实等 bar）+QA det-95th 5/5 **零撞名首写**（93 trades·equity 1,017,839 冻结恒等·determinism=True·png 66,221B）+克隆门 4/4（stale774=0·QA clean-first-write 叙事修正+10-08 首 bar 窗叙事）+孤儿面=1 只读+idle 非绿实工轮〕〕）。产物清单漂移=Tools/_r775bmc_{clone,style_gen_v7,outbound_v7,s05,s6,s6_ignite,qa_ignite}.py〔七件〕+results/_r775bmc_{clone_receipt.json,s05_facts.json,s6_log.txt,s6.out,smoke.txt,qa_runner.out,qa_runner.err,outbound_cas.json,ord_delta.txt}+qa/smoke-r775.md+qa/equity-curve-r775.png〔QA det-95th〕+fleet/mv0001-handover/outbound/{st4_glass_d.jpg,A-DIRECTION-v1.1.md}〔group CAS newc a5cb09ca〕+results/mv_work/kf/ v7 批（st3_goddess_e+st4_glass_d+st1_library_z4_composite+style_v7_manifest.json·frozen-lane untracked 留档）+本行 research/HANDOVER.md；维护面：smoke 49/49·orders 51/51 双扫零未回执·SAT 活 rc0（W189 席位 bm-a 预留·引擎车道零触碰）·WM 绿（red=false·next_pick=claimed moneyflow IC）·attrition CLEAN·自愈四件全绿。指针：**CEO 勾 A/B/C 后视频段解冻施工（A 向弹药三重加固：z3 8/8/9+carve_i 8/8/7+玻璃 d 9/8/7+裙色双版）；sina 10-08 bar 落地→CTA_P1 首接线+fund_premium 10-08 NAV 首采；下一 5x=bm-c r780**。"
PATH_MD = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\research\HANDOVER.md"

import sys

def main():
    with open(PATH_MD, "rb") as fh:
        data = fh.read()
    bom = data.startswith(b"\xef\xbb\xbf")
    if bom:
        data = data[3:]
    text = data.decode("utf-8")
    eol = "\r\n" if text[-400:].count("\r\n") >= (text[-400:].count("\n") - text[-400:].count("\r\n")) else "\n"
    lines = text.split(eol)
    assert lines[0].startswith("# Bigmoney"), "header line missing"
    assert "round 775" not in text, "r775 row already present"
    new_lines = [lines[0], ROW] + lines[1:]
    out = eol.join(new_lines)
    # byte-verify: original content preserved verbatim
    assert all(l in new_lines for l in lines), "original line lost"
    assert out.count(ROW) == 1, "row count != 1"
    payload = out.encode("utf-8")
    if bom:
        payload = b"\xef\xbb\xbf" + payload
    with open(PATH_MD, "wb") as fh:
        fh.write(payload)
    print("HANDOVER_OK r775 row prepended lines=%d->%d eol=%r bom=%s"
          % (len(lines), len(new_lines), eol, bom))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
