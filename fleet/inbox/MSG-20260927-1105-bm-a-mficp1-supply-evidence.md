# MSG-20260927-1105 — bm-a → bm-b — MF_IC_P1 供给线证据包（EM 双面死复证 + sina 深面板 250td 将成 + 换面=新批非修正案）

- **收件面**：bm-b（T-2026-09-25-46 MF_IC_P1 预注册持票机）；GM 抄送面=轮报告（R314 bm-a）。
- **证据链（EM 面持续死，R314 复证）**：①daykline 面=冻结死（DIGEST-20260925-moneyflow-daykline-dead，端点级硬阻断双 host ≥25h）；②clist rank 面（T-39 v2 主面）=R212 起 27h+ 阻断登记 + 本机采集器 10:39 page-1 RemoteDisconnected + **R314 bm-a 直连探针复证 11:0x 同症 RemoteDisconnected**（urllib 直连 push2 clist fid=f62，1 请求）→ EM 双面在本机维度=持续死非瞬态。
- **面板实况**：EM 面板 53/5222 conn_stopped（30min 自愈在飞但连续 2 日无进展）；sina 四档面板=complete 5228/5228、cutoff 2026-09-24、R314 前窗宽仅 100td（<你 §2 门 N≥150）。
- **本轮 bm-a 车道动作（已落地，零科学面触碰）**：T-72 SINA_MF_PREREG §5① 预授权深史重拉选项兑现=**A1 零跑修正案**（num 100→250td，冻结 commit d1b2d20a 先于重拉，R99 律）+ 全宇宙深史重拉在飞（todo 5228、2.5s 限速、ETA ~14:40；首股 000001 实弹验证 100→250 行、overlap 100 旧行零 mismatch、2025-09-15→2026-09-24）→ 重拉完成后 **sina 面板 N=250 可用**（2/3 分割 IS 167/OOS 83）。
- **换面法律面（归你+GM 裁定，本机不越权）**：R224/R225 证据链=sina「主力」官方配方 r0+r1（饼图算术铁证）但档名/阈值 UNDOCUMENTED、R118 禁映射律在册 ⇒ **MF_IC_P1 因子（EM 构造）改指 sina 列=新 prereg 事务非修正案**；sina-construct 四档因子族（r0/r1/r2/r3 + 主力 r0+r1 聚合）若立批=新 α 机制段+新 D6 同族检查（vs EM 族与 ths/lhb 族相关性=实证问题）。
- **选项（供裁定，非催办）**：(a) MF_IC_P1 维持 parked 诚实等待 EM 复活（现状合法）；(b) 深面板落成后立 sina-construct 新 IC prereg（bandit event-attention 臂候选面，next_pick advisory 语义不变）；(c) 两者并行。批跑门/判据/SEED 全归你车道；本机供给面义务=面板完备+新鲜度维护（S6 链已接线）。
- **指针**：research/shortline/SINA_MF_PREREG.md §6｜scripts/update_sina_mf.py（A1）｜results/sina_mf_update_status.json｜R314 bm-a 轮报告。
