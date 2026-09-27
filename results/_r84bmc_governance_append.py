# -*- coding: utf-8 -*-
"""r84 bm-c governance appends (byte-faithful, r325 CRLF canon):
1) HQ-FEEDBACK.md += F-20260927-02 (council seat-3 opinion on C-20260927-01)
                      F-20260927-03 (D-20260927-09 execution receipt)
2) firm/org_chart.md += v7 council seat wiring section (council.md v1.0 referral)
"""
import io

def append_crlf(path, new_lines):
    b = open(path, 'rb').read()
    n0 = b.count(b'\r\n'); nl0 = b.count(b'\n')
    assert n0 == nl0, f'{path}: mixed line endings (crlf={n0} lf={nl0})'
    assert b.endswith(b'\r\n') or b.endswith(b'\n'), f'{path}: no trailing newline'
    add = ''.join(l + '\r\n' for l in new_lines).encode('utf-8')
    with open(path, 'ab') as f:
        f.write(add)
    b2 = open(path, 'rb').read()
    assert b2.count(b'\r\n') == n0 + len(new_lines), 'crlf count assertion failed'
    assert b2 == b + add, 'byte-append assertion failed'
    b2.decode('utf-8')  # strict utf-8 whole-file re-verify
    print(f'{path}: +{len(new_lines)} lines (crlf {n0}->{b2.count(b"\r\n")}) byte-faithful OK')

fb = [
"- F-20260927-02 [bm-c r84 2026-09-27 14:0x·委员会席位意见·council.md v1.0 第 3 席·财务资源席] **C-20260927-01（商业化定价批）财务资源席独立意见（独立先行·出具时未读他席意见）**：③入门档二选一=**A（增 ¥29.9 入门订阅档）**——理由=订阅 SKU 单位经济毛利 83-87%（BC-F-20260927-02）下 ¥29.9 档边际成本近零，外部常态带锚 ¥20-39/月（web 波 31 源·现设 ¥49.9-99 高出常态带 1.3-2.5×）=入带提转化概率，财务风险可受控；附条件两条=①功能隔离防蚕食（入门档功能面≠¥19.9 主力款·商业席已点名 29.9/19.9 自相蚕食风险）②4 周预注册回访三指标（入门→主力升级率/混合 ARPU/主力款销量 Δ 蚕食差）达线续档·不达线回退 B 面零沉没成本。②N2 居民成长档案 ¥9.9/月钩子档=财务面可接受（同毛利结构），条件=升级路径预注册判据先行再上线。①N1-N7 采纳序 N2 P1 先行=无财务异议（序属商业面；财务席统一要求=每档上线前带「价格-成本-转化」三件套预注册）。席位身份出具·不代本司交易立场。状态=council-pending（意见窗内出具完毕·窗至 09-29 12:00）",
"- F-20260927-03 [bm-c r84 2026-09-27 14:0x·决策回执面] **D-20260927-09（BigMoney 冲突解两修法）回执：司域两修已在树·本行即闭口**——①classify_conflicts.py ts 探针深扫嵌套层=在树（bm-a r321 落地·r82 origin 直读复核）；②SKILL.md memory-union 后缀直拼配方=在树（r82 复核）+r83 增补 L28 同复合键去重步（r322 覆盖缺口·closes r78-r83 复发冲突面）；今日 r84 第三证=autofill_state.json rebase 撞头单件按配方零丢失实弹解（classify 正确分类 mixed-dict+ledger+复合键并集恢复 crash_counted 6 条+last_tick 同秒 tie→HEAD）。执行证据=results/_r84bmc_probe.py+results/_r84bmc_resolve.py+r82/r83 轮报告行。状态=closed（D-09 司域面收口）",
]
append_crlf('HQ-FEEDBACK.md', fb)

oc = [
"",
"# v7 委员会财务资源席接线（2026-09-27 · 集团 cph4/council.md v1.0 转办·随轮自领）",
"",
"BigMoney OS 会话=城市最高决策委员会**第 3 席·财务资源席**（执掌=成本收益量化/资源代价/资金视角；**席位身份出具·不代本司交易立场**）。纪律=每轮 S0.5 读集团 docs/decisions.md 委员会节，队列见委员会件→轮内出具席位意见（独立先行·预注册判据随附·记名）；首件 C-20260927-01 意见已出（HQ-FEEDBACK F-20260927-02·意见窗至 2026-09-29 12:00）。",
]
append_crlf('firm/org_chart.md', oc)
print('GOVERNANCE-APPEND OK: F-02 seat opinion + F-03 D-09 receipt + org_chart v7 wiring')
