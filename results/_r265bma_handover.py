# -*- coding: utf-8 -*-
"""R265 bm-a 5x HANDOVER reconciliation update (anchor-insert law per r260 bm-b precedent).

Edits (both field-level, fail-closed anchored):
  1. line3 最近核对 chain: prepend bm-a round 265 entry, demote bm-b r260 to 上一次核对.
  2. file end: append round 265 bm-a increment-window row (dual-track per r250 bm-b note).

Byte faces mirrored: UTF-8 no-BOM, CRLF, trailing newline preserved.
Facts (all re-derived this round):
  ledger 186,592 -> 187,585 (CN-REGIME-POLICY +993 R256) -> 187,687 (style_rotation +102 R259)
        -> 187,741 (CN-CORE-SATELLITE +54 R261) -> 187,845 (CN-CORE-DDCTL +104 R263)
  pool 49/49 done; post_review 1038 rows 23 YES / 0 NO / 5 WAIT; orders 83/83 both scans; smoke 25/25.
"""
import io, sys

PATH = 'research/HANDOVER.md'

ANCHOR_LINE3 = '最近核对=bm-b round 260（2026-09-26 16:4x·对账增量=r251-260 bm-b 窗：'
TAIL_LAST_40 = '→export→scorecard→daily_report）+10-01 月度三件套+REGIME_GUARD v3 日期门生效+T-70 中期判读 10-09+10-31 六员首检 all-HOLD+T-34 半档梯 11-01 不变。'

NEW_LINE3_HEAD = (
    '最近核对=bm-a round 265（2026-09-26 19:2x·对账增量=文末 round 265 bm-a 行〔bm-a R256-265 窗+bm-b r261-267 并读：'
    '**T-73 s1/s2/s3 science faces FULLY CLOSED**=CN 原生组合五家族×19 判决格全负 0/19 收口'
    '（research/CN_COMBO_VERDICTS.md v1.0·根因=随机再平衡 null 线 0.5691-0.9527 支配=beta 非 rotation alpha'
    '·互证 T-28 NOT-DEMONSTRATED J4 0.4854；零注册+O-1105 禁翻案+判负族零前向纸盘 GM 裁定 O-1620 域）)；'
    '统一链 187,585→187,845 实读（+260：style_rotation +102 R259·CN-CORE-SATELLITE-P1 +54 R261·CN-CORE-DDCTL-P1 +104 R263）'
    '+post_review 债清零（R256 首击 depth 缓解+bm-b r264 二犯根治=检查锚稳定产物件律；复审 23 YES/0 NO/5 WAIT·1,038 行零 ✗）'
    '+O-1355 法熵令回执=T-83 撞窗让路闭环（bm-a 18:47:11 晚于 bm-b 18:46:30·L9 orders index 83/33 捐赠 s1 业主）'
    '+T-82 deep-bcd 接收腿 4/4 家族跨机恒等闭环（R260）+smoke F7 clock_read 值/类型/格式三面修（R262）；'
    '板 0 open/池 49/49 done/orders 83/83 双扫零未回执；'
    '最近两窗=09-28 周一新 bar 全链接力（cutoff 09-24·中秋 09-25 源缺 bar 周一补拉）'
    '+10-01 月度三件套与 REGIME_GUARD v3 日期门首 enforce 生效窗）；上一次核对=bm-b round 260（2026-09-26 16:4x·对账增量=r251-260 bm-b 窗：'
)

NEW_END_ROW = (
    '- 开发队列增量窗（接续版）**round 265 bm-a（5x 核对本轮），2026-09-26 19:2x 补核；'
    '对账区间=bm-a R256-265 增量+bm-b r261-267 并读（基线=round 255 bm-a 补核），'
    '统一链 186,592→187,845 实读（+1,253 全窗：CN-REGIME-POLICY-P1 +993 R256 判负〔r260 bm-b line3 锚已收讫窗〕'
    '+t73_s2 style_rotation +102 R259〔2 判决面+100 置换 nulls·基金事件包络守卫 clean_value 桥接+prev-echo guard 双坑修〕'
    '+CN-CORE-SATELLITE-P1 +54 R261〔G1\'v2 0/4·SAT40_bare 0.4586<线 0.5664·s3 五模型全负链收口〕'
    '+CN-CORE-DDCTL-P1 +104 R263〔死轮残骸收养四连撞修复后第 5 发 22.3s 落地·4 cells 分化核证·G1 判负=R261 doctrine 残余消费〕'
    '——**五家族判决批全部判负收口**）**：'
    '①**bm-a R256-265=T-73 全线收口+复审债清零窗**——'
    'R256 CN-REGIME-POLICY-P1 993 判负入链+post_review rot 首击（git_log_file depth 参数缓解）；'
    'R257-259 s2 尾三片收线（slice-C 零换手羊群律=首个过全门 s2 律 TO20/h10 OOS ic -0.0635 全纪元负活律'
    '/slice-D 因子史〔低波全纪元均匀一律+SIZE 小盘溢价 2017-2020 核心资产纪翻面政体依赖披露'
    '+bars osh=当前截面 ffilled 回填血统诚实面+派生侧车历史变动性探针对账门〕'
    '/slice-E 风格轮动〔年→季双尺度活律薄边际 1.04x/1.08x·run1 缺陷档保全不删律〕）'
    '+R260 T-82 deep-bcd 接收腿（6 blob sha 全配+行多重集字节恒等 8294×2=双机独立重跑零分歧实证）；'
    'R261-263 s3 尾二模型批判负（CORE-SATELLITE/CORE-DDCTL）'
    '+R264 判决合并账本 research/CN_COMBO_VERDICTS.md v1.0（五家族×19 格 0/19 全负'
    '·W252_bare 0.7371 最接近线 0.9527 但 512890 单持有 0.7039=轮动增量 +0.033 边际'
    '·分配线 x1 读数诚实非门标注 O-1145）'
    '+smoke F7 clock_read 三面修 R262（值+类型+格式同修·iteration_prompt 例值钉死防再犯）；'
    '②**bm-b r261-267=容量面收尾+裁判深读+T-83 s1 治理盘点窗**（并读）——'
    'r262 T-73 s2 slice-D size 因子 688 volume 归一锚裁定（文档 lore=raw 源面≠运营缓存面'
    '·独立锚实测 amount/volume≈close 裁定）+会话身份误读律（r191 家族新维）；'
    'r263 T-78 s5a 网格带可达性律（带窗排除当日=带离场死码自捕）；'
    'r264 post_review R256 二犯根治（热票 depth 缓解非根治·检查锚「唯一 commit 触及的稳定产物件」律）'
    '+T-76 wave-10 QRS 深读复核关闭；'
    'r265 T-81 slice-4 LANDING-HOOKS 全弧（三族冻结判词面消费零落地确认〔CN 五模型全负链/GRID 0/0/WILD 0/25〕钩挂载）；'
    'r266 T-76 wave-10 裁判深读 #1（arXiv 2609.27051 anytime-valid e-BH 冻结裁判 5-11x 更少假准入'
    '=冻结门栈外部回执·消费面冻结 science_gates 方法论面零采纳）；'
    'r267 T-83 s1 九层全量盘点交付（research/AUDIT-20260926-FULL.md 九层/十观察零裁剪·O-1355 治理审视'
    '·bm-a L9 orders index 捐赠接入）；'
    '③观测：bm-c r71 后结构性停摆维持（P-49 rebuild-or-retire 裁决 09-26 11:52 已过）；'
    '④指针：**09-28 周一开市新 bar 全链接力**（update_daily→live.paper REGIME_GUARD v3 enforce→t35v→t24×2'
    '→aggr 20 账→grid 5 账首拍 marks→export→scorecard→daily_report）'
    '+10-01 月度三件套（science_audit/monthly_briefing/self_review）'
    '+REGIME_GUARD v3 日期门生效（三重门=批准件+2026-10-01 日期门+环境请求·勿手改）'
    '+T-70 C-arm 中期判读 10-09+10-31 六员首检 all-HOLD+T-34 半档梯 11-01 不变。'
)


def main():
    raw = open(PATH, 'rb').read()
    text = raw.decode('utf-8')
    assert not raw.startswith(b'\xef\xbb\xbf'), 'BOM face drifted'
    assert '\r\n' in text, 'CRLF face drifted'
    assert text.count(ANCHOR_LINE3) == 1, 'line3 anchor not unique: %d' % text.count(ANCHOR_LINE3)
    assert text.rstrip('\r\n').endswith(TAIL_LAST_40), 'file-end anchor drifted'
    assert NEW_END_ROW[:40] not in text, 'row already applied (idempotence guard)'

    # edit 1: line3 chain prepend (recent -> previous demotion)
    text2 = text.replace(ANCHOR_LINE3, NEW_LINE3_HEAD, 1)
    assert text2.count('最近核对=bm-a round 265（') == 1
    assert text2.count('上一次核对=bm-b round 260（') == 1

    # edit 2: append end-of-file increment row (CRLF preserved, trailing newline preserved)
    if not text2.endswith('\r\n'):
        text2 += '\r\n'
    text2 += NEW_END_ROW + '\r\n'

    out = text2.encode('utf-8')
    assert out.count(NEW_END_ROW.encode('utf-8')) == 1
    open(PATH, 'wb').write(out)
    print('OK: line3 prepended, end row appended; size %d -> %d (+%d bytes)'
          % (len(raw), len(out), len(out) - len(raw)))


if __name__ == '__main__':
    main()
