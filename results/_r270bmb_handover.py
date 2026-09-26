# r270 bm-b -- HANDOVER 5x recon: anchor head refresh (r265 demoted to last-recon) + end-of-file increment row.
# Byte faces: no BOM, LF-only, trailing newline preserved (probed this round).
import io

P = "research/HANDOVER.md"
txt = io.open(P, encoding="utf-8", newline="").read()
old_head = "最近核对=bm-a round 265（2026-09-26 19:2x"
new_head = ("最近核对=bm-b round 270（2026-09-26 19:5x·对账增量=文末 round 270 bm-b 行〔bm-b r268-270 窗："
            "r268 T-83 s2 治理检测面/r269 T-81 闭票〔post_review x4 YES〕/r270 post_review sha 锚机器面振荡 "
            "P0 根修〔生产者 EOL 归一×4 站点+criteria 4 锚 LF 再锚定→reviewer 28 YES/0 NO〕+T-76 face (a) "
            "常态通道周度机器差分=wave-10 五面全闭；统一链 187,845 平持=本窗零批 finalize〕）；"
            "上次=bm-a round 265（2026-09-26 19:2x")
assert txt.count(old_head) == 1, "anchor head token not unique"
txt = txt.replace(old_head, new_head, 1)

row = ("- 开发队列增量窗（接续版）**round 270 bm-b（5x 核对本轮），2026-09-26 19:5x 补核；对账区间=增量 bm-b "
       "r268-270（基线=round 265 bm-a 行·bm-b r261-267 并读窗），统一链 187,845 平持实读（本窗零批 finalize："
       "T-83 s2=检测面零批、T-81=只读 marks 道 +0、r270=修红+常态通道零批）**：①**r268=T-83 s2 冲突/重复/死面"
       "检测面交付**（O-1355 纪律 1 零正典编辑：scripts/governance_audit_s2.py selftest 9/9+重跑字节恒等+快照 "
       "results/governance_s2_20260926.json D1-D10+报告 research/AUDIT-20260926-S2.md+检测器自病两例报告前自捕"
       "〔jsonl 截断假死链+报告数字复读实值修正〕+post_review 行 T-83-S2-DETECTION YES）；②**r269=T-81 适用域"
       "判断票闭票**（post_review 注册 x4 行→reviewer 4/4 YES→票 done flip+progress_r269；零 science 触碰）；"
       "③**r270（本轮）=post_review sha 锚机器面振荡 P0 根修+T-76 face (a) 收口**——P0 实弹：T-81 三行 prereg "
       "sha 检查同机 5 分钟内 YES x4→NO x3 翻面（19:25:45 reviewer 判 bm-a 面旧件、19:26:46 bm-b 再生 scorecard "
       "后同判据翻 NO），根因=criteria 锚=CRLF 工作树面（freeze 期记录值）vs 产品字段=hashlib(原始磁盘字节) 每轮 "
       "S6 由当值机重算=判读随最后再生机器振荡（R253 家族新参）；根修双端=生产者 hash 前 LF 归一"
       "（strategy_scorecard ×3+market_clock_call L3·R253 f11 idiom）+criteria 4 锚再编码 LF 规范面"
       "（results/_r270bmb_sha_reanchor.py·事实自证 sha256(文件 CRLF 面)==旧锚字节恒等+_reconciled r270 留痕"
       "·R256 同一冻结事实律·diff 4+/4-）→scorecard 再生+reviewer 28 YES/0 NO/5 WAIT（x3 全 re-derive 翻绿零"
       "台账自改）；face (a)：三通道周度机器差分（hibor run-5 3 新/3 淌=260925 周报三件在册族定期刊物不深捕"
       "+金工日报缺位观测 09-28 判别指针留开放；jisilu run-9 1 新=516978 期货实盘流水帖零方法论不深捕；"
       "guorn run-3 0/0 三连零滚动=低频通道判读·bm-b 通道面=schannel 换道诚实注〔python urllib SSL 自签链失败"
       "一次重试成功〕）+digest DIGEST-20260926-wave10-facea-channels.md+票 progress_r270=wave-10 五面 "
       "(a)(b)(c)(d)(e) 全闭；④窗口维护面：S6 链逐轮全绿（周末条件腿合法 no-op·cutoff 09-24）、MF_IC_P1 门="
       "诚实 exit 2（面板 bm-a 车道 53/5222 conn_stopped 自愈窗 legal wait）、watermark py_low_board_clear"
       "（板 0 open/池 49/49 done/bandit next_pick=MF IC legal park）、smoke 25/25 逐轮、orders 83/83 双扫零未回执；"
       "⑤窗口内他机：bm-a R265 后心跳停更（19:19:30 末 commit·本轮拉取无新面）；bm-c r71 后结构性停摆维持。"
       "**指针：09-28 周一开市窗=新 bar 全链接力（update_daily→live.paper REGIME_GUARD v3 enforce→t35v→t24×2"
       "→aggr 20 账→grid 5 账首拍 marks→export→scorecard→daily_report）+T-76 通道 run-6/10/4+金工日报 260928 "
       "入窗判别（r182 指针）+T-78 GRID marks；10-01 月界三件套（science_audit/monthly_briefing/self_review）"
       "+REGIME_GUARD v3 日期门生效（三重门·勿手改）；10-31 公决首检 all-HOLD 不变；T-34 半年报 11-01 不变。")
if not txt.endswith("\n"):
    txt += "\n"
txt += row + "\n"
io.open(P, "w", encoding="utf-8", newline="").write(txt)
print("HANDOVER: anchor head refreshed r265->r270 (demoted to 上次=), increment row appended [%d chars]" % len(row))
